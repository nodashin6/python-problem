"""
User Domain Model
ユーザードメインモデル
"""

from datetime import datetime

from pydantic import UUID4, Field

from .base import BaseModel


class User(BaseModel):
    """
    User aggregate root model
    ユーザー集約ルート - 認証済みユーザーの情報とビジネスロジック
    """

    username: str = Field(...)
    display_name: str = Field(...)
    email: str = Field(...)
    avatar_url: str | None = Field(default=None)
    bio: str | None = Field(default=None)
    is_active: bool = Field(default=True)

    def is_available(self) -> bool:
        """Check if user is available for operations"""
        return self.is_active

    def update_profile(
        self, display_name: str, bio: str | None = None, avatar_url: str | None = None
    ) -> None:
        """Update user profile"""
        self.display_name = display_name
        self.bio = bio
        self.avatar_url = avatar_url
        self.updated_at = datetime.now()

    def deactivate(self) -> None:
        """Deactivate user account"""
        self.is_active = False
        self.updated_at = datetime.now()

    def activate(self) -> None:
        """Activate user account"""
        self.is_active = True
        self.updated_at = datetime.now()
