# test_crud.py
import pytest, sys, os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from fastapi import HTTPException

# /appディレクトリをパスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import Base
from crud import (
    get_user_by_username,
    create_user,
    update_user_tokens,
    add_favorite,
    get_favorites_all,
    delete_favorite,
)
from schemas import UserCreate

# テスト用のDBセッションをセットアップ
@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

# テスト用のインメモリデータベースを作成
DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_create_user(db: Session):
    """
    正常系: 新規ユーザーを作成するテスト

    GIVEN: ユーザーが存在しない
    WHEN: 新規ユーザーを作成
    THEN: ユーザーが正しく作成される
    """
    user_data = UserCreate(username="testuser", password="password123")
    user = create_user(db, user=user_data)

    # ユーザーが正しく作成されたかチェック
    assert user.user_nm == "testuser"

def test_create_user_existing_username(db: Session):
    """
    異常系: 既に存在するユーザー名で作成するテスト

    GIVEN: ユーザー名が既に存在
    WHEN: 新規ユーザーを作成
    THEN: HTTPExceptionが発生し、400ステータスと
    "Username already registered"という詳細メッセージが返る
    """
    
    user_data = UserCreate(username="testuser", password="password123")
    create_user(db, user=user_data)
    
    # 同じユーザー名で再作成しようとした場合のチェック
    with pytest.raises(HTTPException) as exc_info:
        create_user(db, user=user_data)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Username already registered"

def test_get_user_by_username(db: Session):
    """
    正常系: ユーザーが正しく取得できるかチェック

    GIVEN: ユーザーが存在する
    WHEN: ユーザーを取得
    THEN: ユーザーインスタンスが返る
    """
    
    user_data = UserCreate(username="testuser", password="password123")
    create_user(db, user=user_data)
    user = get_user_by_username(db, username="testuser")

    assert user is not None
    assert user.user_nm == "testuser"

def test_get_user_by_username_not_found(db: Session):
    """
    異常系: 存在しないユーザーを取得しようとするテスト

    GIVEN: 存在しないユーザー名
    WHEN: ユーザーを取得
    THEN: Noneが返る
    """
    user = get_user_by_username(db, username="nonexistentuser")
    assert user is None

def test_update_user_tokens(db: Session):
    # 正常系: トークン更新のテスト
    """
    正常系: トークン更新のテスト

    GIVEN: ユーザーが存在する
    WHEN: トークンを更新
    THEN: トークンが更新される
    """
    user_data = UserCreate(username="testuser", password="password123")
    user = create_user(db, user=user_data)

    update_user_tokens(db, user_id=user.id, access_token="new_access", refresh_token="new_refresh")

    updated_user = get_user_by_username(db, username="testuser")
    assert updated_user.backlog_access_token == "new_access"
    assert updated_user.backlog_refresh_token == "new_refresh"

def test_update_user_tokens_user_not_found(db: Session):
    """
    異常系: 存在しないユーザーIDでトークン更新しようとするテスト

    GIVEN: 存在しないユーザーID
    WHEN: トークン更新を実行
    THEN: HTTPExceptionが発生し、404ステータスと
    "ユーザーが存在しないため、トークンを更新できません"という詳細メッセージが返る
    """
    with pytest.raises(HTTPException) as exc_info:
        update_user_tokens(db, user_id=9999, access_token="new_access", refresh_token="new_refresh")
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "ユーザが存在しないため、トークンを更新できません"

def test_add_favorite(db: Session):
    """
    正常系: お気に入り追加のテスト
    
    GIVEN: ユーザーが存在する
    WHEN: お気に入りを追加
    THEN: お気に入りテーブルに1件追加される
    """
    user_data = UserCreate(username="testuser", password="password123")
    user = create_user(db, user=user_data)

    favorite_id = add_favorite(db, user_id=user.id, activity_id="activity_1", activity_title="Test Activity")

    favorites = get_favorites_all(db, user_id=user.id)
    assert len(favorites) == 1
    assert favorites[0].id == favorite_id
    assert favorites[0].activity_title == "Test Activity"

def test_add_favorite_user_not_found(db: Session):
    """
    異常系: 存在しないユーザーIDでお気に入りを追加しようとするテスト

    GIVEN: 存在しないユーザーID
    WHEN: お気に入りを追加
    THEN: HTTPExceptionが発生し、404ステータスと
    "ユーザーが存在しないため、お気に入り登録できません"という詳細メッセージが返る
    """
    with pytest.raises(HTTPException) as exc_info:
        add_favorite(db, user_id=9999, activity_id="activity_1", activity_title="Test Activity")
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "ユーザーが存在しないため、お気に入り登録できません"

def test_get_favorites_all(db: Session):
    """
    正常系: お気に入りの取得テスト

    GIVEN: ユーザーが存在し、お気に入りが1件登録されている
    WHEN: お気に入りの取得を実行
    THEN: お気に入り1件が取得される
    """
    user_data = UserCreate(username="testuser", password="password123")
    user = create_user(db, user=user_data)
    add_favorite(db, user_id=user.id, activity_id="activity_1", activity_title="Test Activity")

    favorites = get_favorites_all(db, user_id=user.id)
    assert len(favorites) == 1

def test_get_favorites_all_no_favorites(db: Session):
    """
    異常系: お気に入りが存在しないユーザーの取得テスト

    GIVEN: ユーザーが存在する
    WHEN: お気に入りテーブルにデータが見つからない
    THEN:空のリストを返す
    """
    user_data = UserCreate(username="testuser", password="password123")
    user = create_user(db, user=user_data)

    favorites = get_favorites_all(db, user_id=user.id)
    assert len(favorites) == 0

def test_delete_favorite(db: Session):
    """
    正常系: お気に入り削除のテスト

    1. ユーザーを作成
    2. お気に入りを追加
    3. お気に入りを削除
    4. お気に入りの取得テスト
    """
    user_data = UserCreate(username="testuser", password="password123")
    user = create_user(db, user=user_data)
    favorite_id = add_favorite(db, user_id=user.id, activity_id="activity_1", activity_title="Test Activity")

    delete_favorite(db, favorite_id=favorite_id, user_id=user.id)

    favorites = get_favorites_all(db, user_id=user.id)
    assert len(favorites) == 0

def test_delete_favorite_not_found(db: Session):
    """
    異常系: 存在しないお気に入りIDで削除しようとするテスト

    GIVEN: 存在しないお気に入りID
    WHEN: 削除を実行
    THEN: HTTPExceptionが発生し、404ステータスと
    "お気に入りデータが見つかりませんでした"という詳細メッセージが返る
    """
    user_data = UserCreate(username="testuser", password="password123")
    user = create_user(db, user=user_data)

    with pytest.raises(HTTPException) as exc_info:
        delete_favorite(db, favorite_id=9999, user_id=user.id)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "お気に入りデータが見つかりませんでした"