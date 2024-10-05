# env_config.py
import os

class Configs:
    # JWT設定
    SECRET_KEY = os.environ.get("SECRET_KEY")
    ALGORITHM = os.environ.get("ALGORITHM")

    # アクセストークンの有効期限
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES"))

    # APIのベースURL
    APP_API_URL = os.environ.get("APP_API_URL")

    # UIのベースURL
    APP_UI_URL = os.environ.get("APP_UI_URL")

    # BacklogのベースURL
    BACKLOG_BASE_URL = os.environ.get("BACKLOG_BASE_URL")

    # Backlog APIのベースURL
    BACKLOG_API_URL = f"{BACKLOG_BASE_URL}/api/v2"

    # Backlog APIの認証用URL
    BACKLOG_REDIRECT_URI = f"{APP_API_URL}/auth/backlog/callback"  # Backlog認証後のコールバックURL
    BACKLOG_TOKEN_URL = f"{BACKLOG_API_URL}/oauth2/token"          # Backlog認証トークン取得URL
    BACKLOG_AUTHORIZE_URL = f"{BACKLOG_BASE_URL}/OAuth2AccessRequest.action"  # Backlog認証トークン取得URL

    # 環境変数からOAuth2の設定を取得
    BACKLOG_CLIENT_ID = os.getenv("BACKLOG_CLIENT_ID")
    BACKLOG_CLIENT_SECRET = os.getenv("BACKLOG_CLIENT_SECRET")