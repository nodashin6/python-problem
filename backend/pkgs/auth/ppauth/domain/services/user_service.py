"""
User domain service
"""

from datetime import timedelta
from typing import Optional
from uuid import UUID

from pydddi import IDomainService

from ..entities.user import UserEntity
from ..enums import UserRole
from ..helpers.authentificator import Authentificator
from ..repositories.user_repository import UserRepository
from ..schemas.user_schemas import CreateUserSchema, UpdateUserSchema


class UserService(IDomainService):
    """User domain service for user-related business logic"""

    def __init__(
        self,
        user_repo: UserRepository,
        authentificator: Authentificator,
    ):
        self.user_repo = user_repo
        self.authentificator = authentificator

    async def is_email_available(self, email: str) -> bool:
        """Check if email is available for registration"""
        user = await self.user_repo.find_by_email(email)
        return user is None

    async def is_user_name_available(self, user_name: str) -> bool:
        """Check if user_name is available for registration"""
        user = await self.user_repo.find_by_user_name(user_name)
        return user is None

    async def register_user(
        self,
        email: str,
        user_name: str,
        display_name: str,
        password: str,
        avatar_url: str | None = None,
        bio: str | None = None,
        role: UserRole = UserRole.USER,
    ) -> UserEntity:
        """Register a new user with role"""
        # Validate email and user_name availability
        if not await self.is_email_available(email):
            raise ValueError("Email already exists")

        if not await self.is_user_name_available(user_name):
            raise ValueError("user_name already exists")

        # Hash password
        password_hash = self.authentificator.hash_password(password)

        # Create user schema
        schema = CreateUserSchema(
            user_name=user_name,
            display_name=display_name,
            email=email,
            password_hash=password_hash,
            role=role,
            avatar_url=avatar_url,
            bio=bio,
        )

        # Create user with role
        return await self.user_repo.create_user_with_role(schema)

    async def authenticate_user(self, email: str, password: str) -> UserEntity | None:
        """Authenticate user with email and password"""
        user = await self.user_repo.find_by_email(email)

        if not user or not user.is_active:
            return None

        if not self.authentificator.verify_password(password, user.password_hash):
            return None

        return user

    async def change_password(self, user_id: UUID, old_password: str, new_password: str) -> bool:
        """Change user password"""
        user = await self.user_repo.find_by_id_with_role(user_id)
        if not user:
            return False

        # Verify old password
        if not self.authentificator.verify_password(old_password, user.password_hash):
            return False

        # Hash new password
        new_password_hash = self.authentificator.hash_password(new_password)

        # Update user
        schema = UpdateUserSchema(password_hash=new_password_hash)
        updated_user = await self.user_repo.update_user_with_role(user_id, schema)

        return updated_user is not None

    async def update_user_profile(
        self,
        user_id: UUID,
        user_name: str | None = None,
        display_name: str | None = None,
        avatar_url: str | None = None,
        bio: str | None = None,
    ) -> UserEntity | None:
        """Update user profile information"""
        schema = UpdateUserSchema(
            user_name=user_name,
            display_name=display_name,
            avatar_url=avatar_url,
            bio=bio,
        )
        return await self.user_repo.update_user_with_role(user_id, schema)

    async def deactivate_user(self, user_id: UUID) -> bool:
        """Deactivate user account"""
        schema = UpdateUserSchema(is_active=False)
        updated_user = await self.user_repo.update_user_with_role(user_id, schema)
        return updated_user is not None

    async def change_user_role(self, user_id: UUID, new_role: UserRole) -> UserEntity | None:
        """Change user role"""
        schema = UpdateUserSchema(role=new_role)
        return await self.user_repo.update_user_with_role(user_id, schema)
