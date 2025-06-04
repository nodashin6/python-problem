"""
User repository implementation using Supabase
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime

from supabase import Client

from ...domain.repositories import UserRepository
from ...domain.models import User, UserProfile
from ....const import UserRole
from ....shared.database import DatabaseManager
from ....shared.logging import get_logger

logger = get_logger(__name__)


class UserRepositoryImpl(UserRepository):
    """User repository implementation with Supabase"""

    def __init__(self, db_manager: DatabaseManager):
        super().__init__(db_manager)
        self.table_name = "users"

    async def create(self, user: User) -> User:
        """Create a new user"""
        try:
            user_data = {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "password_hash": user.password_hash,
                "role": user.role.value,
                "display_name": user.profile.display_name,
                "bio": user.profile.bio,
                "avatar_url": user.profile.avatar_url,
                "github_username": user.profile.github_username,
                "preferred_language": user.profile.preferred_language,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "last_login_at": (
                    user.last_login_at.isoformat() if user.last_login_at else None
                ),
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat(),
            }

            result = await self.db_manager.execute(
                f"""
                INSERT INTO {self.table_name} 
                (id, email, username, password_hash, role, display_name, bio, 
                 avatar_url, github_username, preferred_language, is_active, 
                 is_verified, last_login_at, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
                """,
                (
                    user_data["id"],
                    user_data["email"],
                    user_data["username"],
                    user_data["password_hash"],
                    user_data["role"],
                    user_data["display_name"],
                    user_data["bio"],
                    user_data["avatar_url"],
                    user_data["github_username"],
                    user_data["preferred_language"],
                    user_data["is_active"],
                    user_data["is_verified"],
                    user_data["last_login_at"],
                    user_data["created_at"],
                    user_data["updated_at"],
                ),
            )

            logger.info(f"Created user: {user.email}")
            return self._map_to_entity(result[0])

        except Exception as e:
            logger.error(f"Failed to create user {user.email}: {e}")
            raise

    async def get(self, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        try:
            result = await self.db_manager.fetch_one(
                f"SELECT * FROM {self.table_name} WHERE id = %s", (str(user_id),)
            )

            return self._map_to_entity(result) if result else None

        except Exception as e:
            logger.error(f"Failed to get user {user_id}: {e}")
            raise

    async def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email"""
        try:
            result = await self.db_manager.fetch_one(
                f"SELECT * FROM {self.table_name} WHERE email = %s", (email,)
            )

            return self._map_to_entity(result) if result else None

        except Exception as e:
            logger.error(f"Failed to find user by email {email}: {e}")
            raise

    async def find_by_username(self, username: str) -> Optional[User]:
        """Find user by username"""
        try:
            result = await self.db_manager.fetch_one(
                f"SELECT * FROM {self.table_name} WHERE username = %s", (username,)
            )

            return self._map_to_entity(result) if result else None

        except Exception as e:
            logger.error(f"Failed to find user by username {username}: {e}")
            raise

    async def find_by_role(self, role: UserRole) -> List[User]:
        """Find users by role"""
        try:
            results = await self.db_manager.fetch_all(
                f"SELECT * FROM {self.table_name} WHERE role = %s ORDER BY created_at DESC",
                (role.value,),
            )

            return [self._map_to_entity(row) for row in results]

        except Exception as e:
            logger.error(f"Failed to find users by role {role}: {e}")
            raise

    async def find_active_users(self, limit: int = 100, offset: int = 0) -> List[User]:
        """Find active users with pagination"""
        try:
            results = await self.db_manager.fetch_all(
                f"""
                SELECT * FROM {self.table_name} 
                WHERE is_active = true 
                ORDER BY created_at DESC 
                LIMIT %s OFFSET %s
                """,
                (limit, offset),
            )

            return [self._map_to_entity(row) for row in results]

        except Exception as e:
            logger.error(f"Failed to find active users: {e}")
            raise

    async def count_by_role(self, role: UserRole) -> int:
        """Count users by role"""
        try:
            result = await self.db_manager.fetch_one(
                f"SELECT COUNT(*) as count FROM {self.table_name} WHERE role = %s",
                (role.value,),
            )

            return result["count"] if result else 0

        except Exception as e:
            logger.error(f"Failed to count users by role {role}: {e}")
            raise

    async def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email"""
        try:
            result = await self.db_manager.fetch_one(
                f"SELECT 1 FROM {self.table_name} WHERE email = %s", (email,)
            )

            return result is not None

        except Exception as e:
            logger.error(f"Failed to check user existence by email {email}: {e}")
            raise

    async def exists_by_username(self, username: str) -> bool:
        """Check if user exists by username"""
        try:
            result = await self.db_manager.fetch_one(
                f"SELECT 1 FROM {self.table_name} WHERE username = %s", (username,)
            )

            return result is not None

        except Exception as e:
            logger.error(f"Failed to check user existence by username {username}: {e}")
            raise

    async def update_last_login(self, user_id: UUID) -> None:
        """Update user's last login timestamp"""
        try:
            await self.db_manager.execute(
                f"""
                UPDATE {self.table_name} 
                SET last_login_at = %s, updated_at = %s 
                WHERE id = %s
                """,
                (
                    datetime.utcnow().isoformat(),
                    datetime.utcnow().isoformat(),
                    str(user_id),
                ),
            )

            logger.debug(f"Updated last login for user {user_id}")

        except Exception as e:
            logger.error(f"Failed to update last login for user {user_id}: {e}")
            raise

    async def update(self, user_id: UUID, data) -> User:
        """Update user"""
        try:
            if isinstance(data, User):
                update_data = {
                    "email": data.email,
                    "username": data.username,
                    "password_hash": data.password_hash,
                    "role": data.role.value,
                    "display_name": data.profile.display_name,
                    "bio": data.profile.bio,
                    "avatar_url": data.profile.avatar_url,
                    "github_username": data.profile.github_username,
                    "preferred_language": data.profile.preferred_language,
                    "is_active": data.is_active,
                    "is_verified": data.is_verified,
                    "updated_at": datetime.utcnow().isoformat(),
                }
            else:
                update_data = dict(data)
                update_data["updated_at"] = datetime.utcnow().isoformat()

            # Build SET clause
            set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
            values = list(update_data.values()) + [str(user_id)]

            result = await self.db_manager.execute(
                f"UPDATE {self.table_name} SET {set_clause} WHERE id = %s RETURNING *",
                values,
            )

            logger.info(f"Updated user: {user_id}")
            return self._map_to_entity(result[0])

        except Exception as e:
            logger.error(f"Failed to update user {user_id}: {e}")
            raise

    async def delete(self, user_id: UUID) -> None:
        """Delete user (soft delete by setting is_active = false)"""
        try:
            await self.db_manager.execute(
                f"UPDATE {self.table_name} SET is_active = false, updated_at = %s WHERE id = %s",
                (datetime.utcnow().isoformat(), str(user_id)),
            )

            logger.info(f"Soft deleted user: {user_id}")

        except Exception as e:
            logger.error(f"Failed to delete user {user_id}: {e}")
            raise

    def _map_to_entity(self, row: dict) -> User:
        """Map database row to User entity"""
        profile = UserProfile(
            display_name=row["display_name"],
            bio=row["bio"],
            avatar_url=row["avatar_url"],
            github_username=row["github_username"],
            preferred_language=row["preferred_language"],
        )

        return User(
            id=UUID(row["id"]),
            email=row["email"],
            username=row["username"],
            password_hash=row["password_hash"],
            role=UserRole(row["role"]),
            profile=profile,
            is_active=row["is_active"],
            is_verified=row["is_verified"],
            last_login_at=(
                datetime.fromisoformat(row["last_login_at"])
                if row["last_login_at"]
                else None
            ),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
