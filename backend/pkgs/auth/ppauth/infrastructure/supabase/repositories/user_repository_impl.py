"""
User repository implementation using Supabase
Unified User + UserRole management
"""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from ppcore.domain.repositories import DatabaseRepositoryBase
from ppcore.infrastructure.supabase.repositories import SupabaseRepository

from ....domain.protocols import Logger

from ....domain.entities.user import RoleEntity, UserEntity
from ....domain.repositories.user_repository import UserRepositoryBase
from ....domain.schemas.user_schemas import CreateUserSchema, ReadUserSchema, UpdateUserSchema

class UserRepository(UserRepositoryBase, SupabaseRepository):
    """User repository implementation with Supabase - Unified User + UserRole management"""

    def __init__(self, supabase_client, logger: Optional[Logger] = None):
        super().__init__(supabase_client)
        self.logger = logger
        self.users_table = "users"
        self.user_roles_table = "user_roles"

    async def create_user_with_role(self, schema: CreateUserSchema) -> UserEntity:
        """Create a new user with role in a transaction"""
        try:
            # Start transaction-like operation
            user_data = {
                "user_name": schema.user_name,
                "display_name": schema.display_name,
                "email": schema.email,
                "password_hash": schema.password_hash,
                "avatar_url": schema.avatar_url,
                "bio": schema.bio,
            }

            # Create user
            user_result = self.supabase_client.table(self.users_table).insert(user_data).execute()

            if not user_result.data:
                raise Exception("Failed to create user")

            user_row = user_result.data[0]
            user_id = user_row["id"]

            # Create user role
            role_data = {
                "user_id": user_id,
                "role": schema.role.value,
            }

            role_result = self.supabase_client.table(self.user_roles_table).insert(role_data).execute()

            if not role_result.data:
                # Rollback: delete the user
                self.supabase_client.table(self.users_table).delete().eq("id", user_id).execute()
                raise Exception("Failed to create user role")

            # Convert to entity with role
            return self._to_entity_with_role(user_row, role_result.data[0])

        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to create user with role: {e}")
            raise

    async def update_user_with_role(self, user_id: UUID, schema: UpdateUserSchema) -> UserEntity | None:
        """Update user and role in a transaction"""
        try:
            # Prepare user update data (only non-None values)
            user_data = {}
            if schema.user_name is not None:
                user_data["user_name"] = schema.user_name
            if schema.display_name is not None:
                user_data["display_name"] = schema.display_name
            if schema.email is not None:
                user_data["email"] = schema.email
            if schema.password_hash is not None:
                user_data["password_hash"] = schema.password_hash
            if schema.avatar_url is not None:
                user_data["avatar_url"] = schema.avatar_url
            if schema.bio is not None:
                user_data["bio"] = schema.bio
            if schema.is_active is not None:
                user_data["is_active"] = schema.is_active

            user_data["updated_at"] = datetime.now().isoformat()

            # Update user if there's user data to update
            user_result = None
            if user_data:
                user_result = (
                    self.supabase_client.table(self.users_table).update(user_data).eq("id", str(user_id)).execute()
                )
                if not user_result.data:
                    return None

            # Update role if specified
            role_result = None
            if schema.role is not None:
                role_update_data = {
                    "role": schema.role.value,
                    "updated_at": datetime.now().isoformat(),
                }
                role_result = (
                    self.supabase_client.table(self.user_roles_table)
                    .update(role_update_data)
                    .eq("user_id", str(user_id))
                    .execute()
                )

            # Get current user with role
            return await self.find_by_id_with_role(user_id)

        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to update user with role {user_id}: {e}")
            raise

    async def find_by_email(self, email: str) -> UserEntity | None:
        """Find user by email with role information"""
        try:
            query = """
                *,
                user_roles(*)
            """

            result = self.supabase_client.table(self.users_table).select(query).eq("email", email).single().execute()

            if result.data:
                user_row = result.data
                role_row = user_row["user_roles"][0] if user_row.get("user_roles") else None
                return self._to_entity_with_role(user_row, role_row)
            return None

        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to find user by email {email}: {e}")
            return None

    async def find_by_user_name(self, user_name: str) -> UserEntity | None:
        """Find user by user_name with role information"""
        try:
            query = """
                *,
                user_roles(*)
            """

            result = (
                self.supabase_client.table(self.users_table)
                .select(query)
                .eq("user_name", user_name)
                .single()
                .execute()
            )

            if result.data:
                user_row = result.data
                role_row = user_row["user_roles"][0] if user_row.get("user_roles") else None
                return self._to_entity_with_role(user_row, role_row)
            return None

        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to find user by user_name {user_name}: {e}")
            return None

    async def find_by_id_with_role(self, user_id: UUID) -> UserEntity | None:
        """Find user by ID with role information"""
        try:
            query = """
                *,
                user_roles(*)
            """

            result = (
                self.supabase_client.table(self.users_table).select(query).eq("id", str(user_id)).single().execute()
            )

            if result.data:
                user_row = result.data
                role_row = user_row["user_roles"][0] if user_row.get("user_roles") else None
                return self._to_entity_with_role(user_row, role_row)
            return None

        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to find user by ID {user_id}: {e}")
            return None

    async def list_active_users(self, limit: int = 100, offset: int = 0) -> list[UserEntity]:
        """Find active users with role information"""
        try:
            query = """
                *,
                user_roles(*)
            """

            result = (
                self.supabase_client.table(self.users_table)
                .select(query)
                .eq("is_active", True)
                .range(offset, offset + limit - 1)
                .execute()
            )

            users = []
            if result.data:
                for user_row in result.data:
                    role_row = user_row["user_roles"][0] if user_row.get("user_roles") else None
                    users.append(self._to_entity_with_role(user_row, role_row))

            return users

        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to list active users: {e}")
            raise

    def _to_entity_with_role(self, user_row: dict[str, Any], role_row: dict[str, Any] | None) -> UserEntity:
        """Convert database rows to UserEntity with RoleEntity"""
        # Create RoleEntity if role data exists
        role_entity = None
        if role_row:
            role_entity = RoleEntity(
                id=role_row["id"],
                user_id=role_row["user_id"],
                role=role_row["role"],
                created_at=datetime.fromisoformat(role_row["created_at"]),
                updated_at=datetime.fromisoformat(role_row["updated_at"]),
            )

        # Create UserEntity
        return UserEntity(
            id=user_row["id"],
            user_name=user_row["user_name"],
            display_name=user_row["display_name"],
            email=user_row["email"],
            password_hash=user_row["password_hash"],
            avatar_url=user_row.get("avatar_url"),
            bio=user_row.get("bio"),
            is_active=user_row["is_active"],
            created_at=datetime.fromisoformat(user_row["created_at"]),
            updated_at=datetime.fromisoformat(user_row["updated_at"]),
            role_entity=role_entity,
        )

    # Legacy methods for compatibility (delegating to new unified methods)
    async def create(self, entity: UserEntity) -> UserEntity:
        """Legacy create method - converts to new schema format"""
        from ....domain.enums import UserRole

        schema = CreateUserSchema(
            user_name=entity.user_name,
            display_name=entity.display_name,
            email=entity.email,
            password_hash=entity.password_hash,
            role=entity.role_entity.role if entity.role_entity else UserRole.USER,
            avatar_url=entity.avatar_url,
            bio=entity.bio,
        )
        return await self.create_user_with_role(schema)

    async def get(self, entity_id: UUID) -> UserEntity | None:
        """Legacy get method"""
        return await self.find_by_id_with_role(entity_id)

    async def update(self, entity_id: UUID, entity: UserEntity) -> UserEntity | None:
        """Legacy update method"""
        schema = UpdateUserSchema(
            user_name=entity.user_name,
            display_name=entity.display_name,
            email=entity.email,
            password_hash=entity.password_hash,
            avatar_url=entity.avatar_url,
            bio=entity.bio,
            is_active=entity.is_active,
            role=entity.role_entity.role if entity.role_entity else None,
        )
        return await self.update_user_with_role(entity_id, schema)

    async def delete(self, entity_id: UUID) -> bool:
        """Delete user and associated role"""
        try:
            # Delete user role first
            self.supabase_client.table(self.user_roles_table).delete().eq("user_id", str(entity_id)).execute()

            # Delete user
            result = self.supabase_client.table(self.users_table).delete().eq("id", str(entity_id)).execute()
            return len(result.data) > 0

        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to delete user {entity_id}: {e}")
            raise

    async def list(self, limit: int | None = None, offset: int | None = None) -> list[UserEntity]:
        """Legacy list method"""
        return await self.list_active_users(limit or 100, offset or 0)
