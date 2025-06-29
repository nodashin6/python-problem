"""
User Repository Interface
ユーザーリポジトリインターフェース
"""

from abc import abstractmethod
from uuid import UUID

from pydddi import ICrudRepository

from ..entities.user import UserEntity
from ..schemas.user_schemas import CreateUserSchema, ReadUserSchema, UpdateUserSchema


class UserRepository(ICrudRepository[UserEntity, CreateUserSchema, ReadUserSchema, UpdateUserSchema]):
    """User repository interface"""

    @abstractmethod
    async def find_by_email(self, email: str) -> UserEntity | None:
        """Find user by email"""
        ...

    @abstractmethod
    async def find_by_username(self, username: str) -> UserEntity | None:
        """Find user by username"""
        ...

    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email"""
        ...

    @abstractmethod
    async def exists_by_username(self, username: str) -> bool:
        """Check if user exists by username"""
        ...

    @abstractmethod
    async def update_last_login(self, user_id: UUID) -> bool:
        """Update user's last login timestamp"""
        ...

    @abstractmethod
    async def deactivate_user(self, user_id: UUID) -> bool:
        """Deactivate user account"""
        ...
