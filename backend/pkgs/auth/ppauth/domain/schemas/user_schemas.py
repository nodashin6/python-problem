"""User domain schemas for unified User + UserRole management"""

from datetime import datetime
from uuid import UUID

from pydddi import ICreateSchema, IReadAggregateSchema, IReadSchema, IUpdateSchema

from ..enums import Permission, UserRole


# Unified User Schemas (User + UserRole を一体として扱う)
class CreateUserSchema(ICreateSchema):
    """Schema for creating a user with role"""

    user_name: str
    display_name: str
    email: str
    password_hash: str  # すでにハッシュ化済み
    role: UserRole  # 作成時にroleを指定
    avatar_url: str | None = None
    bio: str | None = None


class UpdateUserSchema(IUpdateSchema):
    """Schema for updating a user with role"""

    user_name: str | None = None
    display_name: str | None = None
    email: str | None = None
    password_hash: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    is_active: bool | None = None
    role: UserRole | None = None  # roleも更新可能


class ReadUserSchema(IReadSchema):
    """Schema for reading a user with role"""

    id: UUID
    user_name: str
    display_name: str
    email: str
    avatar_url: str | None = None
    bio: str | None = None
    is_active: bool
    role: UserRole
    created_at: datetime
    updated_at: datetime


class ReadAggregateUserSchema(IReadAggregateSchema):
    """Schema for reading user aggregate data"""

    id: UUID
    user_name: str
    display_name: str
    email: str
    avatar_url: str | None = None
    bio: str | None = None
    is_active: bool
    role: UserRole  # Single primary role
    permissions: list[Permission]  # Derived from role
