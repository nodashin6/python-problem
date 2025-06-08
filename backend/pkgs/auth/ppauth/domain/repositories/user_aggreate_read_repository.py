from abc import abstractmethod
from typing import Optional
from uuid import UUID

from pydddi import IReadAggregateRepository, IReadAggregateSchema

from ..entities.enums import Permission, UserRole
from ..models.user import User


class ReadAggregateUserSchema(IReadAggregateSchema):
    """Schema for reading user aggregate data"""

    id: UUID
    username: str
    display_name: str
    email: str
    avatar_url: str | None = None
    bio: str | None = None
    is_active: bool
    role: UserRole  # Single primary role
    permissions: list[Permission]  # Derived from role


class UserAggregateReadRepository(IReadAggregateRepository[User, ReadAggregateUserSchema]):
    """Repository for reading user aggregates with role and permission data"""

    @abstractmethod
    async def read_by_email(self, email: str) -> User | None:
        """Find user aggregate by email"""

    @abstractmethod
    async def read_by_username(self, username: str) -> User | None:
        """Find user aggregate by username"""

    @abstractmethod
    async def list_active_users(self, limit: int | None = None, offset: int | None = None) -> list[User]:
        """List active user aggregates"""

    def _schema_to_model(self, schema: ReadAggregateUserSchema) -> User:
        """Convert schema to User model"""
        return User(
            id=schema.id,
            email=schema.email,
            username=schema.username,
            display_name=schema.display_name,
            role=schema.role,
            permissions=schema.permissions,
        )
