from abc import abstractmethod
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydddi import ICreateSchema, ICrudRepository, IReadSchema, IUpdateSchema

from ..entities import UserRoleEntity
from ..entities.enums import UserRole


class CreateUserRoleSchema(ICreateSchema):
    """Schema for creating a user role"""

    user_id: UUID
    role: UserRole


class UpdateUserRoleSchema(IUpdateSchema):
    """Schema for updating a user role"""

    role: UserRole


class ReadUserRoleSchema(IReadSchema):
    """Schema for reading a user role"""

    id: UUID
    user_id: UUID
    role: UserRole
    created_at: datetime
    updated_at: datetime


class UserRoleRepository(
    ICrudRepository[UserRoleEntity, CreateUserRoleSchema, ReadUserRoleSchema, UpdateUserRoleSchema]
):
    """User role repository interface"""

    @abstractmethod
    async def find_by_user_id(self, user_id: UUID) -> list[UserRoleEntity]:
        """Find all user roles by user ID"""

    @abstractmethod
    async def exists_by_user_id_and_role(self, user_id: UUID, role: UserRole) -> bool:
        """Check if a specific role exists for a user"""

    @abstractmethod
    async def delete_user_role(self, user_id: UUID, role: UserRole) -> bool:
        """Delete specific role from user"""

    @abstractmethod
    async def delete_all_user_roles(self, user_id: UUID) -> bool:
        """Delete all roles for a user"""

    @abstractmethod
    async def find_by_role(self, role: UserRole, limit: int = 100, offset: int = 0) -> list[UserRoleEntity]:
        """Find user roles by role type with pagination"""

    @abstractmethod
    async def count_by_role(self, role: UserRole) -> int:
        """Count users with specific role"""

    @abstractmethod
    async def delete_by_user_id(self, user_id: UUID) -> bool:
        """Delete all roles for a user (alias for delete_all_user_roles)"""
