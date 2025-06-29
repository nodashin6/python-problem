"""
User Repository Implementation for Supabase
SupabaseユーザーリポジトリImplementation
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from supabase import Client

from ...domain.entities.user import UserEntity
from ...domain.repositories.user_repository import UserRepository
from ...domain.schemas.user_schemas import CreateUserSchema, ReadUserSchema, UpdateUserSchema
from .repository_base import SupabaseRepository


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
            validated_data = self._validate_response(result)

            if validated_data:
                return self._to_entity(validated_data[0])
            else:
                raise Exception("Failed to create user")

        except Exception as e:
            self._handle_supabase_error(e)

    async def get(self, entity_id: UUID) -> UserEntity | None:
        """Get user by ID"""
        try:
            result = self.client.table(self.table_name).select("*").eq("id", str(entity_id)).execute()
            validated_data = self._validate_response(result)

            if validated_data:
                return self._to_entity(validated_data[0])
            return None

        except Exception as e:
            self._handle_supabase_error(e)
            return None

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
            validated_data = self._validate_response(result)

            if validated_data:
                return self._to_entity(validated_data[0])
            return None

        except Exception as e:
            self._handle_supabase_error(e)
            return None

    async def delete(self, entity_id: UUID) -> bool:
        """Delete user"""
        try:
            result = self.client.table(self.table_name).delete().eq("id", str(entity_id)).execute()
            validated_data = self._validate_response(result)
            return len(validated_data) > 0 if validated_data else False

        except Exception as e:
            self._handle_supabase_error(e)
            return False

    async def list(self, limit: int = 100, offset: int = 0) -> list[UserEntity]:
        """List users with pagination"""
        try:
            result = (
                self.client.table(self.table_name).select("*").range(offset, offset + limit - 1).execute()
            )
            validated_data = self._validate_response(result)

            if validated_data:
                return [self._to_entity(row) for row in validated_data]
            return []

        except Exception as e:
            self._handle_supabase_error(e)
            return []

    async def find_by_email(self, email: str) -> UserEntity | None:
        """Find user by email"""
        try:
            result = self.client.table(self.table_name).select("*").eq("email", email).execute()
            validated_data = self._validate_response(result)

            if validated_data:
                return self._to_entity(validated_data[0])
            return None

        except Exception as e:
            self._handle_supabase_error(e)
            return None

    async def find_by_username(self, username: str) -> UserEntity | None:
        """Find user by username"""
        try:
            result = self.client.table(self.table_name).select("*").eq("username", username).execute()
            validated_data = self._validate_response(result)

            if validated_data:
                return self._to_entity(validated_data[0])
            return None

        except Exception as e:
            self._handle_supabase_error(e)
            return None

    async def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email"""
        user = await self.find_by_email(email)
        return user is not None

    async def exists_by_username(self, username: str) -> bool:
        """Check if user exists by username"""
        user = await self.find_by_username(username)
        return user is not None

    async def update_last_login(self, user_id: UUID) -> bool:
        """Update user's last login timestamp"""
        try:
            data = {
                "updated_at": datetime.now().isoformat(),
            }
            result = self.client.table(self.table_name).update(data).eq("id", str(user_id)).execute()
            validated_data = self._validate_response(result)
            return len(validated_data) > 0 if validated_data else False

        except Exception as e:
            self._handle_supabase_error(e)
            return False

    async def deactivate_user(self, user_id: UUID) -> bool:
        """Deactivate user account"""
        try:
            data = {
                "is_active": False,
                "updated_at": datetime.now().isoformat(),
            }
            result = self.client.table(self.table_name).update(data).eq("id", str(user_id)).execute()
            validated_data = self._validate_response(result)
            return len(validated_data) > 0 if validated_data else False

        except Exception as e:
            self._handle_supabase_error(e)
            return False

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
