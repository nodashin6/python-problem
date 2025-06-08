"""
User aggregate read repository implementation using Supabase
"""

from typing import Any
from uuid import UUID

from pydantic import UUID4
from supabase import Client

from ppcore.infra.supabase.repository import SupabaseRepository
from src.utils import get_logger

from ....domain.entities.enums import ROLE_PERMISSIONS, UserRole
from ....domain.models.user import User
from ....domain.repositories.user_aggreate_read_repository import (
    ReadAggregateUserSchema,
    UserAggregateReadRepository,
)

logger = get_logger(__name__)


class UserAggregateReadRepositoryImpl(UserAggregateReadRepository, SupabaseRepository):
    """User aggregate read repository implementation with Supabase"""

    def __init__(self, client: Client):
        super().__init__(client)
        self.users_table = "users"
        self.user_roles_table = "user_roles"

    async def read(self, id: UUID4) -> User:
        """Read user aggregate by ID"""
        try:
            user_data = await self._get_user_with_role(id)

            if not user_data:
                from pydddi.infrastructure.repository import RecordNotFoundError

                raise RecordNotFoundError(f"User with id {id} not found")

            return self._schema_to_model(user_data)

        except Exception as e:
            logger.error(f"Failed to read user aggregate {id}: {e}")
            raise

    async def read_optional(self, id: UUID4) -> User | None:
        """Read user aggregate by ID, returning None if not found"""
        try:
            user_data = await self._get_user_with_role(id)

            if not user_data:
                return None

            return self._schema_to_model(user_data)

        except Exception as e:
            logger.error(f"Failed to read user aggregate {id}: {e}")
            return None

    async def read_by_email(self, email: str) -> User | None:
        """Find user aggregate by email"""
        try:
            result = (
                self.client.table(self.users_table)
                .select("*, user_roles!inner(role)")
                .eq("email", email)
                .eq("is_active", True)
                .limit(1)
                .execute()
            )

            if not result.data:
                return None

            user_data = self._process_user_with_role(result.data[0])
            return self._schema_to_model(user_data)

        except Exception as e:
            logger.error(f"Failed to find user by email {email}: {e}")
            return None

    async def read_by_username(self, username: str) -> User | None:
        """Find user aggregate by username"""
        try:
            result = (
                self.client.table(self.users_table)
                .select("*, user_roles!inner(role)")
                .eq("username", username)
                .eq("is_active", True)
                .limit(1)
                .execute()
            )

            if not result.data:
                return None

            user_data = self._process_user_with_role(result.data[0])
            return self._schema_to_model(user_data)

        except Exception as e:
            logger.error(f"Failed to find user by username {username}: {e}")
            return None

    async def list_active_users(self, limit: int | None = None, offset: int | None = None) -> list[User]:
        """List active user aggregates"""
        try:
            query = (
                self.client.table(self.users_table)
                .select("*, user_roles!inner(role)")
                .eq("is_active", True)
                .order("created_at", desc=True)
            )

            if limit and offset:
                query = query.range(offset, offset + limit - 1)
            elif limit:
                query = query.limit(limit)

            result = query.execute()

            users = []
            for row in result.data:
                user_data = self._process_user_with_role(row)
                users.append(self._schema_to_model(user_data))

            return users

        except Exception as e:
            logger.error(f"Failed to list active users: {e}")
            return []

    async def select(self, limit: int | None = None, offset: int | None = None, **filters) -> list[User]:
        """List user aggregates with optional pagination and filtering"""
        try:
            query = (
                self.client.table(self.users_table)
                .select("*, user_roles!inner(role)")
                .order("created_at", desc=True)
            )

            # Apply filters
            for key, value in filters.items():
                if value is not None:
                    query = query.eq(key, value)

            if limit and offset:
                query = query.range(offset, offset + limit - 1)
            elif limit:
                query = query.limit(limit)

            result = query.execute()

            users = []
            for row in result.data:
                user_data = self._process_user_with_role(row)
                users.append(self._schema_to_model(user_data))

            return users

        except Exception as e:
            logger.error(f"Failed to list users: {e}")
            return []

    async def _get_user_with_role(self, user_id: UUID4) -> ReadAggregateUserSchema | None:
        """Get user with role data"""
        try:
            result = (
                self.client.table(self.users_table)
                .select("*, user_roles!inner(role)")
                .eq("id", str(user_id))
                .limit(1)
                .execute()
            )

            if not result.data:
                return None

            return self._process_user_with_role(result.data[0])

        except Exception as e:
            logger.error(f"Failed to get user with role {user_id}: {e}")
            return None

    def _process_user_with_role(self, row: dict[str, Any]) -> ReadAggregateUserSchema:
        """Process user row with role data"""
        # Extract role from joined data
        user_roles = row.get("user_roles", [])
        role = UserRole.USER  # Default role

        if user_roles:
            # Get the first (primary) role
            if isinstance(user_roles, list) and user_roles:
                role = UserRole(user_roles[0]["role"])
            elif isinstance(user_roles, dict):
                role = UserRole(user_roles["role"])

        # Get permissions from role
        permissions = ROLE_PERMISSIONS.get(role, [])

        return ReadAggregateUserSchema(
            id=UUID(row["id"]),
            username=row["username"],
            display_name=row["display_name"],
            email=row["email"],
            avatar_url=row.get("avatar_url"),
            bio=row.get("bio"),
            is_active=row["is_active"],
            role=role,
            permissions=permissions,
        )

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
