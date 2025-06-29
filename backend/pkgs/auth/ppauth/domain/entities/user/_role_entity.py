from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import UUID4, Field
from pydddi import IEntity

from ... import enums


class RoleEntity(IEntity[UUID4]):
    """User role entity - user_rolesテーブルに対応"""

    id: UUID4 = Field(default_factory=uuid4)
    user_id: UUID4
    role: enums.UserRole
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def get_id(self) -> UUID4:
        """Get role ID"""
        return self.id

    def get_permissions(self) -> list[enums.Permission]:
        """Get permissions for this role"""
        return enums.ROLE_PERMISSIONS.get(self.role, [])
