# main.py
import httpx, secrets
from fastapi import FastAPI, Depends, HTTPException, status, Response, Query
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal
from schemas import UserCreate, UserResponse, Activity, ActivityDetail, FavoriteCreate
from typing import List, Optional
from env_config import Configs
import crud, utils, auth, models, backlog

# FastAPIインスタンス
app = FastAPI()

# データベースセッション
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 一時的なコードを保存するためのストレージ（メモリ内）
temporary_codes = {}

# CORS設定
origins = [
    Configs.APP_API_URL, 
    Configs.APP_UI_URL,  # フロントエンドのオリジンを許可
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # フロントエンドのオリジン
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#  ユーザログイン(トークン取得)
@app.post("/token", response_model=dict)
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    # トークンを作成
    tokens = auth.user_login(form_data=form_data, db=db)
    return tokens

#  ユーザ登録
@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # ユーザーを新規登録
    response = crud.create_user(db=db, user=user)
    return {
        "id": response.id,
        "username": response.user_nm,
    }

# Backlog認証画面へのリダイレクト
@app.get("/auth/backlog")
def redirect_to_backlog_oauth():
    params = {
        "client_id": Configs.BACKLOG_CLIENT_ID,
        "redirect_uri": Configs.BACKLOG_REDIRECT_URI,
        "response_type": "code",
        "state": "your_state_value"
    }
    url = f"{Configs.BACKLOG_AUTHORIZE_URL}?{httpx.QueryParams(params)}"
    return RedirectResponse(url)

# Backlog認証後のコールバックエンドポイント
@app.get("/auth/backlog/callback")
async def backlog_oauth_callback(code: str, state: str):
    # トークンを取得
    response = await backlog.get_backlog_tokens(code)
    tokens = response.json()
    # 一時的なコードを生成してフロントエンドに返す
    temp_code = secrets.token_urlsafe(16)
    temporary_codes[temp_code] = {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"]
    }

    # フロントエンドのトークン保存用ページにリダイレクト
    url = f"{Configs.APP_UI_URL}/save-tokens?temp_code={temp_code}"
    return RedirectResponse(url)

# アクセストークンとリフレッシュトークンを保存するエンドポイント
@app.post("/auth/backlog/save_tokens")
def save_backlog_tokens(temp_code: str = Query(...), current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    # 一時的なコードからトークンを取得
    tokens = temporary_codes.pop(temp_code, None)
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid or expired temporary code"
        )

    # トークンをデータベースに保存
    crud.update_user_tokens(
            db, 
            current_user.id, 
            tokens["access_token"], 
            tokens["refresh_token"]
        )

    return {"message": "トークンを保存しました"}

# 検索エンドポイント
@app.get("/activities/search", response_model=List[Activity])
async def search_activities(keyword: Optional[str] = None, current_user: models.User = Depends(auth.get_current_user)):

    # Backlog API(最近の更新の取得)を呼び出す
    params = {}
    activity_response = await backlog.call_backlog_api(
        f"/space/activities", 
        params, 
        current_user
    )
    # レスポンスから最近の更新を取得
    activities = activity_response.json()

    # 画面に表示する情報を設定する
    matched_activities = []
    for activity in activities:
        # キーワードにテキスト項目が部分一致した場合、またはキーワード指定がなかった場合のみ更新情報を取得する
        if utils.contains_keyword(activity, keyword):
            # 更新情報を取得する
            disp_activity = backlog.get_disp_activity(activity)
            matched_activities.append(disp_activity)
    return matched_activities

# ログインユーザに紐づくお気に入りリストを取得し、Backlog APIから更新情報を取得するエンドポイント
@app.get("/favorites-search", response_model=List[ActivityDetail])
async def get_favorites(db: Session = Depends(get_db), current_user: UserResponse = Depends(auth.get_current_user)):
    favorites = crud.get_favorites_all(db, current_user.id)
    # お気に入りテーブルに一致するデータが見つからない場合はエラーを返す
    if not favorites:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No favorites found for the current user"
        )

    # お気に入りテーブルの更新情報IDから更新情報を取得
    favorite_activities = []
    for favorite in favorites:
        params = {}
        response = await backlog.call_backlog_api(
            f"/activities/{favorite.activity_id}",
            params, 
            current_user
        )
        activity = response.json()

        # 更新情報を取得する
        disp_activity = backlog.get_disp_activity(activity)
        disp_activity.update(favorite_id=favorite.id)
        favorite_activities.append(disp_activity)
    return favorite_activities

# お気に入り登録エンドポイント
@app.post("/favorites", response_model=dict)
def regist_favorite(favorite: FavoriteCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    # お気に入りテーブルへ登録
    favorite_id = crud.add_favorite(
        db, 
        current_user.id, 
        favorite.activity_id, 
        favorite.activity_title
    )
    return {"message": "お気に入りを登録しました", "favorite_id": favorite_id}

# お気に入り削除エンドポイント
@app.delete("/favorites/{favorite_id}", response_model=dict)
def delete_favorite(favorite_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):

    # お気に入りテーブルから削除
    crud.delete_favorite(db, favorite_id, current_user.id)

    return {"message": "お気に入りを削除しました"}
