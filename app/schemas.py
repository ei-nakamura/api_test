# schemas.py
from pydantic import BaseModel

# ユーザー登録モデル
class UserCreate(BaseModel):
    username: str
    password: str

# ユーザーモデル
class UserInDB(BaseModel):
    id: int
    username: str
    password_hash: str

# ログインモデル
class Token(BaseModel):
    access_token: str
    token_type: str

# ユーザーモデル
class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True

# 更新情報モデル
class Activity(BaseModel):
    id: int
    project_name: str
    type: str   # typeは数値ではなく文字列で設定
    type_name: str
    content_summary: str
    created_user_name: str
    created: str

#  お気に入り更新情報モデル
class ActivityDetail(BaseModel):
    id: int
    project_name: str
    type: str   # typeは数値ではなく文字列で設定
    type_name: str
    content_summary: str
    created_user_name: str
    created: str
    favorite_id: int

    class Config:
        orm_mode = True

# お気に入り登録モデル
class FavoriteCreate(BaseModel):
    activity_id: str
    activity_title: str
