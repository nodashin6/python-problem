"""
User domain service
"""

import hashlib
import secrets
from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta

from ..models import User, UserProfile
from ..repositories import UserRepository
from ....const import UserRole
from ....shared.auth import PasswordManager, TokenManager
from ....shared.events import EventBus


class UserDomainService:
    """User domain service for user-related business logic"""

    def __init__(
        self,
        user_repo: UserRepository,
        password_manager: PasswordManager,
        token_manager: TokenManager,
        event_bus: EventBus,
    ):
        self.user_repo = user_repo
        self.password_manager = password_manager
        self.token_manager = token_manager
        self.event_bus = event_bus

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
        password: str,
        profile: UserProfile,
        role: UserRole = UserRole.USER,
    ) -> User:
        """Register a new user"""
        # Validate email and username availability
        if not await self.is_email_available(email):
            raise ValueError("Email already exists")

        if not await self.is_username_available(username):
            raise ValueError("Username already exists")

        # Hash password
        password_hash = self.password_manager.hash_password(password)

        # Create user entity
        user = User(
            email=email,
            username=username,
            password_hash=password_hash,
            profile=profile,
            role=role,
        )

        # Save user
        created_user = await self.user_repo.create(user)

        # Publish domain events
        for event in created_user.clear_events():
            await self.event_bus.publish(event)

        return created_user

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = await self.user_repo.find_by_email(email)

        if not user or not user.is_active:
            return None

        if not self.password_manager.verify_password(password, user.password_hash):
            return None

        # Update last login
        await self.user_repo.update_last_login(user.id)

        return user

    async def change_password(
        self, user_id: UUID, old_password: str, new_password: str
    ) -> bool:
        """Change user password"""
        user = await self.user_repo.get(user_id)
        if not user:
            return False

        # Verify old password
        if not self.password_manager.verify_password(old_password, user.password_hash):
            return False

        # Hash new password
        new_password_hash = self.password_manager.hash_password(new_password)

        # Update user
        await self.user_repo.update(user_id, {"password_hash": new_password_hash})

        return True

    async def reset_password(self, email: str) -> Optional[str]:
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
            if payload.get("type") != "password_reset":
                return False

            user_id = UUID(payload["user_id"])
            new_password_hash = self.password_manager.hash_password(new_password)

            await self.user_repo.update(user_id, {"password_hash": new_password_hash})
            return True

        except Exception:
            return False

    async def verify_user_email(self, user_id: UUID) -> bool:
        """Verify user email"""
        user = await self.user_repo.get(user_id)
        if not user:
            return False

        user.verify_email()
        await self.user_repo.update(user_id, user)

        return True

    async def deactivate_user(self, user_id: UUID) -> bool:
        """Deactivate user account"""
        user = await self.user_repo.get(user_id)
        if not user:
            return False

        user.deactivate()
        await self.user_repo.update(user_id, user)

        return True

    async def promote_user(self, user_id: UUID, new_role: UserRole) -> bool:
        """Promote user to a new role"""
        user = await self.user_repo.get(user_id)
        if not user:
            return False

        await self.user_repo.update(user_id, {"role": new_role})

        return True
