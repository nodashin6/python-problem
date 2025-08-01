"""User Repository for User + UserRole unified management"""

from abc import abstractmethod
from typing import Optional
from uuid import UUID

from pydddi import ICrudRepository

from ..entities import UserEntity
from ..enums import UserRole
from ..schemas import CreateUserSchema, ReadUserSchema, UpdateUserSchema


class UserRepositoryBase(ICrudRepository[UserEntity, CreateUserSchema, ReadUserSchema, UpdateUserSchema]):
    """統合されたUser repository - User + UserRole を一体として管理"""

    @abstractmethod
    async def create_user_with_role(self, schema: CreateUserSchema) -> UserEntity:
        """
        ユーザーとロールを同時に作成
        1. users テーブルに挿入
        2. user_roles テーブルに挿入
        Transaction内で実行される
        """

    @abstractmethod
    async def update_user_with_role(self, user_id: UUID, schema: UpdateUserSchema) -> UserEntity | None:
        """
        ユーザーとロールを同時に更新
        1. users テーブルを更新 (該当フィールドのみ)
        2. role が指定されていれば user_roles テーブルを更新
        Transaction内で実行される
        """

    @abstractmethod
    async def find_by_email(self, email: str) -> UserEntity | None:
        """Find user by email with role information"""

    @abstractmethod
    async def find_by_user_name(self, user_name: str) -> UserEntity | None:
        """Find user by user_name with role information"""

    @abstractmethod
    async def find_by_id_with_role(self, user_id: UUID) -> UserEntity | None:
        """Find user by ID with role information"""

    @abstractmethod
    async def list_active_users(self, limit: int = 100, offset: int = 0) -> list[UserEntity]:
        """Find active users with role information"""

    @abstractmethod
    async def list_users_by_role(
        self, role: UserRole, limit: int = 100, offset: int = 0
    ) -> list[UserEntity]:
        """Find users by role with pagination"""

    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email"""

    @abstractmethod
    async def exists_by_user_name(self, user_name: str) -> bool:
        """Check if user exists by user_name"""

    @abstractmethod
    async def update_last_login(self, user_id: UUID) -> bool:
        """Update last login timestamp"""

    @abstractmethod
    async def deactivate_user(self, user_id: UUID) -> bool:
        """Deactivate user account (usersテーブルのis_activeを更新)"""

    @abstractmethod
    async def change_user_role(self, user_id: UUID, new_role: UserRole) -> bool:
        """
        ユーザーのロールを変更
        user_roles テーブルの既存レコードを削除し、新しいロールを挿入
        """

    @abstractmethod
    async def get_user_role(self, user_id: UUID) -> UserRole | None:
        """Get current user role"""


# Alias for backward compatibility
UserRepository = UserRepositoryBase
