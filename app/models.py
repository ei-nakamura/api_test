# models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from settings import Base

# ユーザテーブル
class User(Base):
    __tablename__ = 'm_user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_nm = Column(String(50), nullable=False, unique=True)
    pw_hash = Column(String(255), nullable=False)
    backlog_access_token = Column(String(255), nullable=True)
    backlog_refresh_token = Column(String(255), nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

# お気に入りテーブル
class Favorite(Base):
    __tablename__ = 'm_favorites'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('m_user.id'), nullable=False)
    activity_id = Column(String(50), nullable=False)
    activity_title = Column(String(255), nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship('User', back_populates='favorites')

User.favorites = relationship('Favorite', order_by=Favorite.id, back_populates='user')
