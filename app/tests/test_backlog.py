# test_backlog.py
import pytest, sys, os, json, pytz
from unittest.mock import patch, AsyncMock, mock_open
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

# /appディレクトリをパスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backlog import (
    redirect_to_backlog_oauth, 
    get_backlog_tokens, 
    refresh_access_token, 
    call_backlog_api, 
    get_disp_activity
)
from models import User

# テスト用のモックデータ
class MockConfigs:
    BACKLOG_CLIENT_ID = "test_client_id"
    BACKLOG_REDIRECT_URI = "https://example.com/callback"
    BACKLOG_AUTHORIZE_URL = "https://example.com/oauth2/authorize"
    BACKLOG_TOKEN_URL = "https://example.com/oauth2/token"
    BACKLOG_API_URL = "https://example.com/api/v2"
    BACKLOG_CLIENT_SECRET = "test_client_secret"
    
@pytest.fixture
def mock_user():
    
    return User(id=1, backlog_access_token="test_access_token", backlog_refresh_token="test_refresh_token")

@pytest.fixture
def mock_db():
    return AsyncMock(Session)

@pytest.fixture
def mock_configs(monkeypatch):
    monkeypatch.setattr('backlog.Configs', MockConfigs)

def test_redirect_to_backlog_oauth(mock_configs):
    # 正常系: Backlogの認証画面にリダイレクトするテスト
    response = redirect_to_backlog_oauth()
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert response.headers["location"].startswith(MockConfigs.BACKLOG_AUTHORIZE_URL)

@pytest.mark.asyncio
async def test_get_backlog_tokens_success(mock_configs):
    # 正常系: Backlogのアクセストークンを取得するテスト
    mock_response_data = {"access_token": "test_access_token", "refresh_token": "test_refresh_token"}

    # 非同期のjson関数をモック
    mock_response = AsyncMock(status_code=200)
    mock_response.json = AsyncMock(return_value=mock_response_data)

    with patch("httpx.AsyncClient.post", return_value=mock_response) as mock_post:
        response = await get_backlog_tokens(code="test_code")
        tokens = await response.json()
        assert tokens["access_token"] == "test_access_token"
        assert tokens["refresh_token"] == "test_refresh_token"
        mock_post.assert_called_once()

@pytest.mark.asyncio
async def test_get_backlog_tokens_failure(mock_configs):
    # 異常系: Backlogのアクセストークン取得が失敗するテスト
    with patch("httpx.AsyncClient.post", return_value=AsyncMock(status_code=400)) as mock_post:
        with pytest.raises(HTTPException) as exc_info:
            await get_backlog_tokens(code="test_code")
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Backlogのアクセストークン取得に失敗しました"
        mock_post.assert_called_once()

# @pytest.mark.asyncio
# async def test_refresh_access_token_success(mock_user, mock_db, mock_configs):
#     # 正常系: Backlogのアクセストークンを更新するテスト
#     mock_response_data = {"access_token": "new_access_token", "refresh_token": "new_refresh_token"}

#     with patch("httpx.AsyncClient.post", return_value=AsyncMock(status_code=200, json=AsyncMock(return_value=mock_response_data))) as mock_post:
#         response = await refresh_access_token(user=mock_user, db=mock_db)
#         assert response.status_code == 200
#         tokens = await response.json()
#         assert tokens["access_token"] == "new_access_token"
#         assert tokens["refresh_token"] == "new_refresh_token"
#         mock_post.assert_called_once()

@pytest.mark.asyncio
async def test_refresh_access_token_failure(mock_user, mock_db, mock_configs):
    # 異常系: Backlogのアクセストークン更新が失敗するテスト
    with patch("httpx.AsyncClient.post", return_value=AsyncMock(status_code=401)) as mock_post:
        with pytest.raises(HTTPException) as exc_info:
            await refresh_access_token(user=mock_user, db=mock_db)
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Backlogのアクセストークン更新に失敗しました"
        mock_post.assert_called_once()

@pytest.mark.asyncio
async def test_call_backlog_api_success(mock_user, mock_db, mock_configs):
    # 正常系: Backlog API呼び出しが成功するテスト
    mock_response = AsyncMock(status_code=200, json=AsyncMock(return_value={"key": "value"}))

    with patch("httpx.AsyncClient.get", return_value=mock_response) as mock_get:
        response = await call_backlog_api(url="/test", params={}, current_user=mock_user, db=mock_db)
        assert response.status_code == 200
        assert await response.json() == {"key": "value"}
        mock_get.assert_called_once()

# @pytest.mark.asyncio
# async def test_call_backlog_api_token_refresh(mock_user, mock_db, mock_configs):
#     # 正常系: Backlog API呼び出し中にアクセストークンが無効でリフレッシュされるテスト
#     mock_response_401 = AsyncMock(status_code=401)
#     mock_response_200 = AsyncMock(status_code=200, json=AsyncMock(return_value={"key": "value"}))

#     with patch("httpx.AsyncClient.get", side_effect=[mock_response_401, mock_response_200]) as mock_get, \
#          patch("backlog.refresh_access_token", return_value=AsyncMock(status_code=200, json=AsyncMock(return_value={"access_token": "new_access_token"}))) as mock_refresh:
#         response = await call_backlog_api(url="/test", params={}, current_user=mock_user, db=mock_db)
#         assert response.status_code == 200
#         assert await response.json() == {"key": "value"}
#         assert mock_get.call_count == 2
#         mock_refresh.assert_called_once()

@pytest.mark.asyncio
async def test_call_backlog_api_failure(mock_user, mock_db, mock_configs):
    # 異常系: Backlog API呼び出しが失敗するテスト
    with patch("httpx.AsyncClient.get", return_value=AsyncMock(status_code=500)) as mock_get:
        with pytest.raises(HTTPException) as exc_info:
            await call_backlog_api(url="/test", params={}, current_user=mock_user, db=mock_db)
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Backlog API呼び出しに失敗しました"
        mock_get.assert_called_once()

# def test_get_disp_activity(monkeypatch):
#     # 正常系: 更新情報をUI表示用に整形するテスト
#     mock_activity = {
#         "id": 1,
#         "project": {"name": "Test Project"},
#         "type": 2,
#         "content": {"summary": "Test Summary"},
#         "createdUser": {"name": "Test User"},
#         "created": "2024-09-07T11:08:06Z"
#     }

#     mock_activity_types = {
#         "2": "課題の追加"
#     }

#     # unittest.mock の mock_open を使用してファイル読み込みをモック
#     m = mock_open(read_data=json.dumps(mock_activity_types))

#     # モックされたファイル読み込みが convert_to_tz のタイムゾーンデータに影響を与えないように、mock_openのスコープを限定
#     with patch("builtins.open", m):
#         # pytzのタイムゾーン取得をモックして、正常に動作するようにします。
#         with patch("pytz.timezone", return_value=pytz.timezone("Asia/Tokyo")):
#             result = get_disp_activity(mock_activity)
#             assert result == {
#                 "id": 1,
#                 "project_name": "Test Project",
#                 "type": "2",
#                 "type_name": "課題の追加",
#                 "content_summary": "Test Summary",
#                 "created_user_name": "Test User",
#                 "created": "2024-09-07 20:08:06"
#             }