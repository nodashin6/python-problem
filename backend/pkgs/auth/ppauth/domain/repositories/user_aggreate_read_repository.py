from abc import abstractmethod
from typing import Optional
from uuid import UUID

from pydddi import IReadAggregateRepository, IReadAggregateSchema

from ..enums import Permission, UserRole
from ..models.user import User
from ..schemas.user_schemas import ReadAggregateUserSchema


class UserAggregateReadRepository(IReadAggregateRepository[User, ReadAggregateUserSchema]):
    """Repository for reading user aggregates with role and permission data"""

    @abstractmethod
    async def read_by_email(self, email: str) -> User | None:
        """Find user aggregate by email"""

    @abstractmethod
    async def read_by_user_name(self, user_name: str) -> User | None:
        """Find user aggregate by user_name"""

    @abstractmethod
    async def list_active_users(self, limit: int | None = None, offset: int | None = None) -> list[User]:
        """List active user aggregates"""

    def _schema_to_model(self, schema: ReadAggregateUserSchema) -> User:
        """Convert schema to User model"""
        return User(
            id=schema.id,
            email=schema.email,
            user_name=schema.user_name,
            display_name=schema.display_name,
            role=schema.role,
            permissions=schema.permissions,
        )
