"""
User domain service
"""

from datetime import timedelta
from typing import Optional
from uuid import UUID

from pydddi import IDomainService

from ..entities import UserEntity, UserRoleEntity
from ..entities.enums import UserRole
from ..repositories.user_repository import UserRepository
from ..repositories.user_role_respository import UserRoleRepository
from .auth_service import JWTManager, PasswordManager


class UserService(IDomainService):
    """User domain service for user-related business logic"""

    def __init__(
        self,
        user_repo: UserRepository,
        user_role_repo: UserRoleRepository,
        password_manager: PasswordManager,
        token_manager: JWTManager,
    ):
        self.user_repo = user_repo
        self.user_role_repo = user_role_repo
        self.password_manager = password_manager
        self.token_manager = token_manager

    async def is_email_available(self, email: str) -> bool:
        """Check if email is available for registration"""
        return not await self.user_repo.exists_by_email(email)

    async def is_username_available(self, username: str) -> bool:
        """Check if username is available for registration"""
        return not await self.user_repo.exists_by_username(username)

    async def register_user(
        self,
        email: str,
        username: str,
        display_name: str,
        password: str,
        avatar_url: str | None = None,
        bio: str | None = None,
        role: UserRole = UserRole.USER,
    ) -> UserEntity:
        """Register a new user"""
        # Validate email and username availability
        if not await self.is_email_available(email):
            raise ValueError("Email already exists")

        if not await self.is_username_available(username):
            raise ValueError("Username already exists")

        # Hash password
        password_hash = self.password_manager.hash_password(password)

        # Create user entity
        user = UserEntity(
            username=username,
            display_name=display_name,
            email=email,
            password_hash=password_hash,
            avatar_url=avatar_url,
            bio=bio,
        )

        # Save user
        created_user = await self.user_repo.create(user)

        # Create user role
        user_role = UserRoleEntity(
            user_id=created_user.id,
            role=role,
        )
        await self.user_role_repo.create(user_role)

        return created_user

    async def authenticate_user(self, email: str, password: str) -> UserEntity | None:
        """Authenticate user with email and password"""
        user = await self.user_repo.find_by_email(email)

        if not user or not user.is_active:
            return None

        if not self.password_manager.verify_password(password, user.password_hash):
            return None

        # Update last login (実装は具体的なリポジトリで)
        await self.user_repo.update_last_login(user.id)

        return user

    async def get_user_role(self, user_id: UUID) -> UserRoleEntity | None:
        """Get primary role for a user"""
        return await self.user_role_repo.find_by_user_id(user_id)

    async def get_user_roles(self, user_id: UUID) -> list[UserRoleEntity]:
        """Get all roles for a user (legacy support)"""
        return await self.user_role_repo.list_roles_by_user_id(user_id)

    async def change_password(self, user_id: UUID, old_password: str, new_password: str) -> bool:
        """Change user password"""
        user = await self.user_repo.read(user_id)
        if not user:
            return False

        # Verify old password
        if not self.password_manager.verify_password(old_password, user.password_hash):
            return False

        # Hash new password
        new_password_hash = self.password_manager.hash_password(new_password)

        # Update user
        user.password_hash = new_password_hash
        await self.user_repo.update(user_id, user)

        return True

    async def reset_password(self, email: str) -> str | None:
        """Generate password reset token"""
        user = await self.user_repo.find_by_email(email)
        if not user or not user.is_active:
            return None

        # Generate reset token (expires in 1 hour)
        reset_token = self.token_manager.create_token(
            {"user_id": str(user.id), "type": "password_reset"},
            expires_delta=timedelta(hours=1),
        )

        return reset_token

    async def confirm_password_reset(self, token: str, new_password: str) -> bool:
        """Confirm password reset with token"""
        try:
            payload = self.token_manager.verify_token(token)
            if not payload or payload.get("type") != "password_reset":
                return False

            user_id = UUID(payload["user_id"])
            new_password_hash = self.password_manager.hash_password(new_password)

            user = await self.user_repo.read(user_id)
            if not user:
                return False

            user.password_hash = new_password_hash
            await self.user_repo.update(user_id, user)
            return True

        except Exception:
            return False

    async def deactivate_user(self, user_id: UUID) -> bool:
        """Deactivate user account"""
        user = await self.user_repo.read(user_id)
        if not user:
            return False

        user.is_active = False
        await self.user_repo.update(user_id, user)

        return True

    async def assign_role(self, user_id: UUID, new_role: UserRole) -> bool:
        """Assign a new role to user"""
        # Check if role already exists
        if await self.user_role_repo.exists_by_user_id_and_role(user_id, new_role):
            return False

        user_role = UserRoleEntity(
            user_id=user_id,
            role=new_role,
        )

        await self.user_role_repo.create(user_role)
        return True

    async def remove_role(self, user_id: UUID, role: UserRole) -> bool:
        """Remove a role from user"""
        return await self.user_role_repo.delete_user_role(user_id, role)
