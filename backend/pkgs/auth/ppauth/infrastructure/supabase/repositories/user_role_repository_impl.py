"""
User role repository implementation using Supabase
"""

from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID

from supabase import Client

from ppcore.infra.supabase.repository import SupabaseRepository
from src.utils import get_logger

from ....domain.entities import UserRoleEntity
from ....domain.entities.enums import UserRole
from ....domain.repositories.user_role_respository import (
    CreateUserRoleSchema,
    ReadUserRoleSchema,
    UpdateUserRoleSchema,
    UserRoleRepository,
)

logger = get_logger(__name__)


class UserRoleRepositoryImpl(UserRoleRepository, SupabaseRepository):
    """User role repository implementation with Supabase"""

    def __init__(self, client: Client):
        super().__init__(client)
        self.table_name = "user_roles"

    async def create(self, entity: UserRoleEntity) -> UserRoleEntity:
        """Create a new user role"""
        try:
            data = {
                "id": str(entity.id),
                "user_id": str(entity.user_id),
                "role": entity.role.value,
            }

            result = self.client.table(self.table_name).insert(data).execute()

            if result.data:
                return self._to_entity(result.data[0])
            else:
                raise Exception("Failed to create user role")

        except Exception as e:
            logger.error(f"Failed to create user role: {e}")
            raise

    async def get(self, entity_id: UUID) -> UserRoleEntity | None:
        """Get user role by ID"""
        try:
            result = self.client.table(self.table_name).select("*").eq("id", str(entity_id)).execute()

            if result.data:
                return self._to_entity(result.data[0])
            return None

        except Exception as e:
            logger.error(f"Failed to get user role {entity_id}: {e}")
            raise

    async def update(self, entity_id: UUID, entity: UserRoleEntity) -> UserRoleEntity | None:
        """Update user role"""
        try:
            data = {
                "role": entity.role.value,
                "updated_at": datetime.now().isoformat(),
            }

            result = self.client.table(self.table_name).update(data).eq("id", str(entity_id)).execute()

            if result.data:
                return self._to_entity(result.data[0])
            return None

        except Exception as e:
            logger.error(f"Failed to update user role {entity_id}: {e}")
            raise

    async def delete(self, entity_id: UUID) -> bool:
        """Delete user role"""
        try:
            result = self.client.table(self.table_name).delete().eq("id", str(entity_id)).execute()
            return len(result.data) > 0

        except Exception as e:
            logger.error(f"Failed to delete user role {entity_id}: {e}")
            raise

    async def select(self, limit: int = 100, offset: int = 0) -> list[UserRoleEntity]:
        """List user roles with pagination"""
        try:
            result = (
                self.client.table(self.table_name).select("*").range(offset, offset + limit - 1).execute()
            )

            return [self._to_entity(row) for row in result.data]

        except Exception as e:
            logger.error(f"Failed to list user roles: {e}")
            raise

    async def find_by_user_id(self, user_id: UUID) -> UserRoleEntity | None:
        """Find primary user role by user ID"""
        try:
            result = (
                self.client.table(self.table_name)
                .select("*")
                .eq("user_id", str(user_id))
                .order("created_at")
                .limit(1)
                .execute()
            )

            if result.data:
                return self._to_entity(result.data[0])
            return None

        except Exception as e:
            logger.error(f"Failed to find user role by user_id {user_id}: {e}")
            raise

    async def list_roles_by_user_id(self, user_id: UUID) -> list[UserRoleEntity]:
        """List all roles for a given user ID"""
        try:
            result = (
                self.client.table(self.table_name)
                .select("*")
                .eq("user_id", str(user_id))
                .order("created_at")
                .execute()
            )

            return [self._to_entity(row) for row in result.data]

        except Exception as e:
            logger.error(f"Failed to list roles for user {user_id}: {e}")
            raise

    async def exists_by_user_id_and_role(self, user_id: UUID, role: UserRole) -> bool:
        """Check if a specific role exists for a user"""
        try:
            result = (
                self.client.table(self.table_name)
                .select("id")
                .eq("user_id", str(user_id))
                .eq("role", role.value)
                .execute()
            )

            return len(result.data) > 0

        except Exception as e:
            logger.error(f"Failed to check role existence for user {user_id}, role {role}: {e}")
            raise

    async def delete_user_role(self, user_id: UUID, role: UserRole) -> bool:
        """Delete specific role from user"""
        try:
            result = (
                self.client.table(self.table_name)
                .delete()
                .eq("user_id", str(user_id))
                .eq("role", role.value)
                .execute()
            )

            return len(result.data) > 0

        except Exception as e:
            logger.error(f"Failed to delete role {role} from user {user_id}: {e}")
            raise

    async def delete_all_user_roles(self, user_id: UUID) -> bool:
        """Delete all roles for a user"""
        try:
            result = self.client.table(self.table_name).delete().eq("user_id", str(user_id)).execute()

            return len(result.data) > 0

        except Exception as e:
            logger.error(f"Failed to delete all roles for user {user_id}: {e}")
            raise

    def _to_entity(self, row: dict[str, Any]) -> UserRoleEntity:
        """Convert database row to UserRoleEntity"""
        return UserRoleEntity(
            id=UUID(row["id"]),
            user_id=UUID(row["user_id"]),
            role=UserRole(row["role"]),
            created_at=datetime.fromisoformat(row["created_at"])
            if row.get("created_at")
            else datetime.now(),
            updated_at=datetime.fromisoformat(row["updated_at"])
            if row.get("updated_at")
            else datetime.now(),
        )
