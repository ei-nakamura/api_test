# auth.py
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from database import SessionLocal
from utils import verify_password
from env_config import Configs
from crud import get_user_by_username

# OAuth2のトークン取得設定
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# データベースセッションの依存関係
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_access_token(data: dict):
    """
    トークンを作成

    :param data: トークンに含めるデータ
    :return: 作成されたトークン
    """

    to_encode = data.copy()
    access_token_expires = datetime.utcnow() + timedelta(minutes=Configs.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": access_token_expires})
    
    encoded_jwt = jwt.encode(to_encode, Configs.SECRET_KEY, algorithm=Configs.ALGORITHM)
    return encoded_jwt

# トークンからユーザを取得
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    トークンからユーザーを取得

    :param token: トークン
    :param db: データベースセッション
    :return: ユーザー
    :raises HTTPException: トークンの検証に失敗した場合
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="トークンの検証に失敗しました",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # JWTトークンをデコード
        payload = jwt.decode(token, Configs.SECRET_KEY, algorithms=[Configs.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # デコードしたusernameでデータベースからユーザーを取得
    user = get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user

def user_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    ユーザーログイン

    :param form_data: フォームデータ
    :param db: データベースセッション
    :return: トークン
    :raises HTTPException: トークンの検証に失敗した場合
    """
    user = get_user_by_username(db, username=form_data.username)
    if not user or not verify_password(form_data.password, user.pw_hash):
        # ユーザー名またはパスワードが間違っている場合はエラーを返す
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="username、またはpasswordが間違っています",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # トークンを作成
    access_token = create_access_token(data={"sub": user.user_nm})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }