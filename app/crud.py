# crud.py
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import models
from schemas import UserCreate
from utils import get_password_hash

def get_user_by_username(db: Session, username: str):
    """usernameで指定されたユーザーを取得

    Args:
        db (Session): DBセッション
        username (str): ユーザー名

    Returns:
        User: ユーザーインスタンス Noneの場合は見つからない
    """
    return db.query(models.User).filter(models.User.user_nm == username).first()

def create_user(db: Session, user: UserCreate):
    """新規ユーザー登録

    Args:
        db (Session): DBセッション
        user (UserCreate): ユーザ情報

    Returns:
        User: ユーザーインスタンス
    """
    existing_user = get_user_by_username(db, username=user.username)
    if existing_user:
        # 既にユーザーが登録されている場合はエラーを返す
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    
    hashed_password = get_password_hash(user.password)
    db_user = models.User(user_nm=user.username, pw_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_tokens(db: Session, user_id: int, access_token: str, refresh_token: str):
    """Backlogのアクセストークンをデータベースに保存

    Args:
        db (Session): DBセッション
        user_id (int): ユーザーID
        access_token (str): アクセストークン
        refresh_token (str): リフレッシュトークン
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.backlog_access_token = access_token
        user.backlog_refresh_token = refresh_token
        db.commit()
        db.refresh(user)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザが存在しないため、トークンを更新できません",
        )


def add_favorite(db: Session, user_id: int, activity_id: int, activity_title: str):
    """お気に入りテーブルへ更新情報を登録

    Args:
        db (Session): DBセッション
        user_id (int): ユーザーID
        activity_id (int): 更新情報ID
        activity_title (str): 更新情報名

    Returns:
        int: お気に入りID
    """

    # ユーザの存在チェック
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが存在しないため、お気に入り登録できません",
        )
    # お気に入りに登録
    db_favorite = models.Favorite(user_id=user_id, activity_id=activity_id, activity_title=activity_title)
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)

    return db_favorite.id

def get_favorites_all(db: Session, user_id: int):
    """指定されたユーザーのお気に入り情報を取得

    Args:
        db (Session): DBセッション
        user_id (int): ユーザーID

    Returns:
        list[Favorite]: お気に入り情報リスト
    """
    return db.query(models.Favorite).filter(models.Favorite.user_id == user_id).all()

def delete_favorite(db: Session, favorite_id: int, user_id: int):
    """指定されたお気に入り情報を削除

    Args:
        db (Session): DBセッション
        favorite_id (int): お気に入りID
        user_id (int): ユーザーID

    Raises:
        HTTPException: お気に入りデータが見つからない場合
    """
    #　お気に入りテーブルにデータが見つからない場合はエラーを返す 
    db_favorite = db.query(models.Favorite).filter(
        models.Favorite.id == favorite_id, 
        models.Favorite.user_id == user_id
        ).first()
    if not db_favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="お気に入りデータが見つかりませんでした"
        )

    # お気に入りテーブルから削除
    db.delete(db_favorite)
    db.commit()