from abc import abstractmethod
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydddi import ICreateSchema, ICrudRepository, IReadSchema, IUpdateSchema

from ..entities import UserEntity


class CreateUserSchema(ICreateSchema):
    """Schema for creating a user"""

    username: str
    display_name: str
    email: str
    password_hash: str  # すでにハッシュ化済み
    avatar_url: str | None = None
    bio: str | None = None


class UpdateUserSchema(IUpdateSchema):
    """Schema for updating a user"""

    username: str | None = None
    display_name: str | None = None
    email: str | None = None
    password_hash: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    is_active: bool | None = None


class ReadUserSchema(IReadSchema):
    """Schema for reading a user"""

    id: UUID
    username: str
    display_name: str
    email: str
    avatar_url: str | None = None
    bio: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserRepository(ICrudRepository[UserEntity, CreateUserSchema, ReadUserSchema, UpdateUserSchema]):
    """User repository interface"""

    @abstractmethod
    async def find_by_email(self, email: str) -> UserEntity | None:
        """Find user by email"""

    @abstractmethod
    async def find_by_username(self, username: str) -> UserEntity | None:
        """Find user by username"""

    @abstractmethod
    async def list_active_users(self, limit: int = 100, offset: int = 0) -> list[UserEntity]:
        """Find active users with pagination"""

    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email"""

    @abstractmethod
    async def exists_by_username(self, username: str) -> bool:
        """Check if user exists by username"""

    @abstractmethod
    async def update_last_login(self, user_id: UUID) -> bool:
        """Update last login timestamp"""

    @abstractmethod
    async def deactivate_user(self, user_id: UUID) -> bool:
        """Deactivate user account"""
