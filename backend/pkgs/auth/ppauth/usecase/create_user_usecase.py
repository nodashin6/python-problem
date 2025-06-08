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
from ..domain.entities.enums import UserRole
from ..domain.services.user_service import UserService


class CreateUserCommand(IUseCaseCommand):
    """Command for creating a user"""

    username: str
    display_name: str
    email: str
    password: str
    avatar_url: str | None = None
    bio: str | None = None
    role: UserRole = UserRole.USER


class CreateUserResult(IUseCaseResult):
    """Result for creating a user"""

    user_id: UUID
    username: str
    display_name: str
    email: str
    avatar_url: str | None = None
    bio: str | None = None
    is_active: bool


class CreateUserUseCase(IUseCase[CreateUserCommand, CreateUserResult]):
    """Use case for creating a user"""

    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def execute(self, command: CreateUserCommand) -> CreateUserResult:
        """Execute the create user use case"""
        try:
            # Create user through domain service
            user = await self.user_service.register_user(
                email=command.email,
                username=command.username,
                display_name=command.display_name,
                password=command.password,
                avatar_url=command.avatar_url,
                bio=command.bio,
                role=command.role,
            )

            return CreateUserResult(
                user_id=user.id,
                username=user.username,
                display_name=user.display_name,
                email=user.email,
                avatar_url=user.avatar_url,
                bio=user.bio,
                is_active=user.is_active,
            )

        except Exception as e:
            raise UseCaseExecutionError(
                f"Failed to create user: {e!s}",
            ) from e
