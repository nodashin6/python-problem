from typing import Optional
from uuid import UUID

from pydddi import (
    IUseCase,
    IUseCaseCommand,
    IUseCaseResult,
    UseCaseCommandError,
    UseCaseExecutionError,
    UseCaseResultError,
)

from ..domain.entities import UserEntity
from ..domain.services.user_service import UserService


class UpdateUserCommand(IUseCaseCommand):
    """Command for updating a user"""

    user_id: UUID
    username: str | None = None
    display_name: str | None = None
    email: str | None = None
    password: str | None = None  # 新しいパスワード (平文)
    avatar_url: str | None = None
    bio: str | None = None
    is_active: bool | None = None


class UpdateUserResult(IUseCaseResult):
    """Result for updating a user"""

    user_id: UUID
    username: str
    display_name: str
    email: str
    avatar_url: str | None = None
    bio: str | None = None
    is_active: bool


class UpdateUserUseCase(IUseCase[UpdateUserCommand, UpdateUserResult]):
    """Use case for updating a user"""

    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def execute(self, command: UpdateUserCommand) -> UpdateUserResult:
        """Execute the update user use case"""
        try:
            # Get existing user
            user = await self._get_existing_user(command.user_id)

            # Update user fields
            await self._update_user_fields(user, command)

            # Update user in repository
            updated_user = await self.user_service.user_repo.update(command.user_id, user)

            return self._create_result(updated_user)

        except Exception as e:
            raise UseCaseExecutionError(
                f"Failed to update user: {e!s}",
            ) from e

    async def _get_existing_user(self, user_id: UUID) -> UserEntity:
        """Get existing user or raise error if not found"""
        user = await self.user_service.user_repo.read(user_id)
        if not user:
            raise UseCaseExecutionError(f"User with ID {user_id} not found")
        return user

    async def _update_user_fields(self, user: UserEntity, command: UpdateUserCommand) -> None:
        """Update user fields based on command"""
        await self._update_username(user, command.username)
        await self._update_email(user, command.email)
        self._update_simple_fields(user, command)

    async def _update_username(self, user: UserEntity, new_username: str | None) -> None:
        """Update username if provided and available"""
        if new_username is not None:
            if not await self.user_service.is_username_available(new_username):
                if user.username != new_username:  # 同じユーザー名の場合は許可
                    raise UseCaseExecutionError("Username is already taken")
            user.username = new_username

    async def _update_email(self, user: UserEntity, new_email: str | None) -> None:
        """Update email if provided and available"""
        if new_email is not None:
            if not await self.user_service.is_email_available(new_email):
                if user.email != new_email:  # 同じメールアドレスの場合は許可
                    raise UseCaseExecutionError("Email is already taken")
            user.email = new_email

    def _update_simple_fields(self, user: UserEntity, command: UpdateUserCommand) -> None:
        """Update simple fields that don't require validation"""
        if command.display_name is not None:
            user.display_name = command.display_name

        if command.password is not None:
            user.password_hash = self.user_service.password_manager.hash_password(command.password)

        if command.avatar_url is not None:
            user.avatar_url = command.avatar_url

        if command.bio is not None:
            user.bio = command.bio

        if command.is_active is not None:
            user.is_active = command.is_active

    def _create_result(self, updated_user: UserEntity) -> UpdateUserResult:
        """Create the result from updated user entity"""
        return UpdateUserResult(
            user_id=updated_user.id,
            username=updated_user.username,
            display_name=updated_user.display_name,
            email=updated_user.email,
            avatar_url=updated_user.avatar_url,
            bio=updated_user.bio,
            is_active=updated_user.is_active,
        )
