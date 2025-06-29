from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import UUID4, Field
from pydddi import IEntity

from ._role_entity import RoleEntity


# Entities
class UserEntity(IEntity[UUID4]):
    """User entity - usersテーブルに対応"""

    id: UUID4 = Field(default_factory=uuid4)
    user_name: str = Field(..., min_length=3, max_length=50)
    display_name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")
    password_hash: str = Field(...)
    avatar_url: str | None = None
    bio: str | None = Field(None, max_length=500)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    role_entity: RoleEntity | None = Field(default=None, alias="role_entity")

    def get_id(self) -> UUID4:
        """Get user ID"""
        return self.id

    def is_email_verified(self) -> bool:
        """Check if email is verified"""
        # 実装はシンプルに、メール認証機能は後で追加
        return self.is_active

    def can_login(self) -> bool:
        """Check if user can login"""
        return self.is_active
