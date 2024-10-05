# backlog.py
import httpx, json
from fastapi import Depends, HTTPException, status, Response, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import SessionLocal
from crud import update_user_tokens
from utils import convert_to_tz
from models import User
from env_config import Configs

# データベースセッション
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def redirect_to_backlog_oauth():
    """
    Backlogの認証画面にリダイレクト
    """
    params = {
        "client_id": Configs.BACKLOG_CLIENT_ID,
        "redirect_uri": Configs.BACKLOG_REDIRECT_URI,
        "response_type": "code",
        "state": "your_state_value"
    }
    url = f"{Configs.BACKLOG_AUTHORIZE_URL}?{httpx.QueryParams(params)}"
    return RedirectResponse(url)

async def get_backlog_tokens(code: str):
    """
    Backlogのアクセストークンを取得

    :param code: authorization_code
    :param response: Response object
    :return: dict with access_token and refresh_token
    :raises HTTPException: Backlog API呼び出しに失敗した場合
    """
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": Configs.BACKLOG_REDIRECT_URI,
        "client_id": Configs.BACKLOG_CLIENT_ID,
        "client_secret": Configs.BACKLOG_CLIENT_SECRET,
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(Configs.BACKLOG_TOKEN_URL, data=data)

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code, 
            detail="Backlogのアクセストークン取得に失敗しました"
        )

    return response

async def refresh_access_token(user: User, db: Session):
    """
    Backlogのアクセストークンを更新

    :param user: ユーザー
    :param db: データベースセッション
    :return: 新しいアクセストークン
    :raises HTTPException: Backlog API呼び出しに失敗した場合
    """

    data = {
        "grant_type": "refresh_token",
        "refresh_token": user.backlog_refresh_token,
        "client_id": "your_client_id",
        "client_secret": "your_client_secret",
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(Configs.BACKLOG_TOKEN_URL , data=data)
    
    if response.status_code == 200:
        # DB上のアクセストークンの更新
        tokens = response.json()
        new_access_token = tokens.get("access_token")
        new_refresh_token = tokens.get("refresh_token")
        update_user_tokens(
            db=db, 
            user_id=user.id, 
            access_token=new_access_token, 
            refresh_token=new_refresh_token
        )
        return response
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Backlogのアクセストークン更新に失敗しました"
        )

async def call_backlog_api(url:str, params:dict, current_user:User, db: Session = Depends(get_db)):
    """
    Backlog APIを呼び出す

    :param url: Backlog APIのエンドポイント
    :param params: Backlog APIのパラメータ
    :param current_user: ログインユーザ
    :param db: データベースセッション
    :return: Backlog APIのレスポンス
    :raises HTTPException: Backlog API呼び出しに失敗した場合
    """
    
    # データベースからアクセストークンを取得
    access_token = current_user.backlog_access_token
    headers = {"Authorization": f"Bearer {access_token}"}

    # Backlog APIを呼び出す
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{Configs.BACKLOG_API_URL}{url}", 
            headers=headers, 
            params=params
        )

    # アクセストークンが無効または期限切れの場合、リフレッシュトークンを使用して更新
    if response.status_code == 401:  # Unauthorized
        token_response = await refresh_access_token(current_user, db)
        refreshed_access_token = token_response.json().get("access_token")
        headers["Authorization"] = f"Bearer {refreshed_access_token}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)

    # レスポンスのステータスコードが200以外の場合はエラーを返す
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code, 
            detail="Backlog API呼び出しに失敗しました"
        )

    return response

def get_disp_activity(activity:dict):
    """
    Backlog API から取得した更新情報を、UIに表示する形式に整形する

    Args:
        activity (dict): Backlog API から取得した更新情報

    Returns:
        dict: UIに表示する形式に整形された更新情報
    """
    
    # 更新種別の表示名をjsonファイルから取得する
    with open('./activity_types.json', 'r', encoding='utf-8') as file:
        activity_types = json.load(file)
        
    return {
        "id":activity["id"],
        "project_name":activity["project"]["name"],
        "type":str(activity["type"]),   # typeは数値ではなく文字列で設定
        "type_name":activity_types[str(activity["type"])],
        "content_summary":activity["content"].get("summary", " - "),
        "created_user_name":activity["createdUser"]["name"],
        "created":convert_to_tz(activity["created"]),
    }
