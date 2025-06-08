"""
User repository implementation using Supabase
"""

import builtins
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from supabase import Client

from ppcore.infra.supabase.repository import SupabaseRepository
from src.utils import get_logger

from ....domain.entities import UserEntity
from ....domain.repositories.user_repository import (
    CreateUserSchema,
    ReadUserSchema,
    UpdateUserSchema,
    UserRepository,
)

logger = get_logger(__name__)


class UserRepositoryImpl(UserRepository, SupabaseRepository):
    """User repository implementation with Supabase"""

    def __init__(self, client: Client):
        super().__init__(client)
        self.table_name = "users"

    async def create(self, entity: UserEntity) -> UserEntity:
        """Create a new user"""
        try:
            data = {
                "id": str(entity.id),
                "username": entity.username,
                "display_name": entity.display_name,
                "email": entity.email,
                "password_hash": entity.password_hash,
                "avatar_url": entity.avatar_url,
                "bio": entity.bio,
                "is_active": entity.is_active,
            }

            result = self.client.table(self.table_name).insert(data).execute()

            if result.data:
                return self._to_entity(result.data[0])
            else:
                raise Exception("Failed to create user")

        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise

    async def get(self, entity_id: UUID) -> UserEntity | None:
        """Get user by ID"""
        try:
            result = self.client.table(self.table_name).select("*").eq("id", str(entity_id)).execute()

            if result.data:
                return self._to_entity(result.data[0])
            return None

        except Exception as e:
            logger.error(f"Failed to get user {entity_id}: {e}")
            raise

    async def update(self, entity_id: UUID, entity: UserEntity) -> UserEntity | None:
        """Update user"""
        try:
            data = {
                "username": entity.username,
                "display_name": entity.display_name,
                "email": entity.email,
                "password_hash": entity.password_hash,
                "avatar_url": entity.avatar_url,
                "bio": entity.bio,
                "is_active": entity.is_active,
                "updated_at": datetime.now().isoformat(),
            }

            result = self.client.table(self.table_name).update(data).eq("id", str(entity_id)).execute()

            if result.data:
                return self._to_entity(result.data[0])
            return None

        except Exception as e:
            logger.error(f"Failed to update user {entity_id}: {e}")
            raise

    async def delete(self, entity_id: UUID) -> bool:
        """Delete user"""
        try:
            result = self.client.table(self.table_name).delete().eq("id", str(entity_id)).execute()
            return len(result.data) > 0

        except Exception as e:
            logger.error(f"Failed to delete user {entity_id}: {e}")
            raise

    async def select(self, limit: int = 100, offset: int = 0) -> list[UserEntity]:
        """List users with pagination"""
        try:
            result = (
                self.client.table(self.table_name).select("*").range(offset, offset + limit - 1).execute()
            )

            return [self._to_entity(row) for row in result.data]

        except Exception as e:
            logger.error(f"Failed to list users: {e}")
            raise

    async def find_by_email(self, email: str) -> UserEntity | None:
        """Find user by email"""
        try:
            result = self.client.table(self.table_name).select("*").eq("email", email).execute()

            if result.data:
                return self._to_entity(result.data[0])
            return None

        except Exception as e:
            logger.error(f"Failed to find user by email {email}: {e}")
            raise

    async def find_by_username(self, username: str) -> UserEntity | None:
        """Find user by username"""
        try:
            result = self.client.table(self.table_name).select("*").eq("username", username).execute()

            if result.data:
                return self._to_entity(result.data[0])
            return None

        except Exception as e:
            logger.error(f"Failed to find user by username {username}: {e}")
            raise

    async def list_active_users(self, limit: int = 100, offset: int = 0) -> builtins.list[UserEntity]:
        """Find active users with pagination"""
        try:
            result = (
                self.client.table(self.table_name)
                .select("*")
                .eq("is_active", True)
                .range(offset, offset + limit - 1)
                .execute()
            )

            return [self._to_entity(row) for row in result.data]

        except Exception as e:
            logger.error(f"Failed to list active users: {e}")
            raise

    async def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email"""
        try:
            result = self.client.table(self.table_name).select("id").eq("email", email).execute()
            return len(result.data) > 0

        except Exception as e:
            logger.error(f"Failed to check email existence {email}: {e}")
            raise

    async def exists_by_username(self, username: str) -> bool:
        """Check if user exists by username"""
        try:
            result = self.client.table(self.table_name).select("id").eq("username", username).execute()
            return len(result.data) > 0

        except Exception as e:
            logger.error(f"Failed to check username existence {username}: {e}")
            raise

    async def update_last_login(self, user_id: UUID) -> bool:
        """Update last login timestamp"""
        try:
            # Note: last_loginカラムがSQLスキーマに存在しない場合は追加が必要
            # 今回はupdated_atで代用
            data = {"updated_at": datetime.now().isoformat()}
            result = self.client.table(self.table_name).update(data).eq("id", str(user_id)).execute()
            return len(result.data) > 0

        except Exception as e:
            logger.error(f"Failed to update last login for user {user_id}: {e}")
            raise

    async def deactivate_user(self, user_id: UUID) -> bool:
        """Deactivate user account"""
        try:
            data = {"is_active": False, "updated_at": datetime.now().isoformat()}
            result = self.client.table(self.table_name).update(data).eq("id", str(user_id)).execute()
            return len(result.data) > 0

        except Exception as e:
            logger.error(f"Failed to deactivate user {user_id}: {e}")
            raise

    def _to_entity(self, row: dict[str, Any]) -> UserEntity:
        """Convert database row to UserEntity"""
        return UserEntity(
            id=UUID(row["id"]),
            username=row["username"],
            display_name=row["display_name"],
            email=row["email"],
            password_hash=row["password_hash"],
            avatar_url=row.get("avatar_url"),
            bio=row.get("bio"),
            is_active=row["is_active"],
            created_at=datetime.fromisoformat(row["created_at"])
            if row.get("created_at")
            else datetime.now(),
            updated_at=datetime.fromisoformat(row["updated_at"])
            if row.get("updated_at")
            else datetime.now(),
        )
