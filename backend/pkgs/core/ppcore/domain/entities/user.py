"""
User Entity
ユーザーエンティティ - 永続化用データ構造
"""

from pydantic import Field

from .base import BaseEntity


class UserEntity(BaseEntity):
    """
    User entity for persistence
    ユーザーエンティティ - データベース永続化用
    """

    username: str = Field(...)
    display_name: str = Field(...)
    email: str = Field(...)
    password_hash: str = Field(...)
    avatar_url: str | None = Field(default=None)
    bio: str | None = Field(default=None)
    is_active: bool = Field(default=True)
