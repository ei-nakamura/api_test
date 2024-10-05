# test_auth.py
import pytest, sys, os
from unittest.mock import patch, AsyncMock, MagicMock
from jose import jwt
from fastapi import HTTPException, status

# /appディレクトリをパスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from auth import create_access_token, get_current_user, user_login
from models import User
from env_config import Configs

# モック用の設定
class MockConfigs:
    SECRET_KEY = "test_secret"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

# テスト用のモックユーザー
@pytest.fixture
def mock_user():
    return User(id=1, user_nm="testuser", pw_hash="hashedpassword")

@pytest.fixture
def mock_db():
    return AsyncMock()

@pytest.fixture
def mock_configs(monkeypatch):
    monkeypatch.setattr('auth.Configs', MockConfigs)

def test_create_access_token(mock_configs):
    # 正常系: トークンが正しく作成されるかのテスト
    data = {"sub": "testuser"}
    token = create_access_token(data)

    # トークンが正しくエンコードされているか確認
    decoded_data = jwt.decode(token, MockConfigs.SECRET_KEY, algorithms=[MockConfigs.ALGORITHM])
    assert decoded_data["sub"] == "testuser"

# @pytest.mark.asyncio
# async def test_get_current_user_success(mock_user, mock_db, mock_configs):
#     # 正常系: トークンからユーザーを正しく取得するテスト
#     token = create_access_token({"sub": "testuser"})

#     with patch('crud.get_user_by_username', return_value=mock_user):
#         user = await get_current_user(token=token, db=mock_db)
#         assert user.user_nm == "testuser"

@pytest.mark.asyncio
async def test_get_current_user_invalid_token(mock_db, mock_configs):
    # 異常系: 無効なトークンのテスト
    invalid_token = "invalid_token"

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token=invalid_token, db=mock_db)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "トークンの検証に失敗しました"

# @pytest.mark.asyncio
# async def test_get_current_user_user_not_found(mock_db, mock_configs):
#     # 異常系: トークンは有効だがユーザーが見つからない場合のテスト
#     token = create_access_token({"sub": "nonexistentuser"})

#     with patch('crud.get_user_by_username', return_value=None):
#         with pytest.raises(HTTPException) as exc_info:
#             await get_current_user(token=token, db=mock_db)
#         assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
#         assert exc_info.value.detail == "トークンの検証に失敗しました"

# def test_user_login_success(mock_user, mock_db, mock_configs):
#     # 正常系: 正しいユーザー名とパスワードでログインするテスト
#     with patch('crud.get_user_by_username', return_value=mock_user), \
#          patch('utils.verify_password', return_value=True):
#         form_data = MagicMock(username="testuser", password="password")
#         response = user_login(form_data=form_data, db=mock_db)
        
#         assert "access_token" in response
#         assert response["token_type"] == "bearer"

# def test_user_login_invalid_credentials(mock_db, mock_configs):
#     # 異常系: 不正なユーザー名またはパスワードでログインするテスト
#     with patch('crud.get_user_by_username', return_value=None), \
#          patch('utils.verify_password', return_value=False):
#         form_data = MagicMock(username="testuser", password="wrongpassword")

#         with pytest.raises(HTTPException) as exc_info:
#             user_login(form_data=form_data, db=mock_db)
#         assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
#         assert exc_info.value.detail == "username、またはpasswordが間違っています"
