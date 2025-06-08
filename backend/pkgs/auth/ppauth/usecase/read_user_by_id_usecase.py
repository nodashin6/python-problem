from uuid import UUID

from pydddi import IUseCase, IUseCaseCommand, UseCaseExecutionError

from ..domain.services.user_service import UserService
from .user_types import UserResult


class ReadUserByIdCommand(IUseCaseCommand):
    """Command for reading a user by ID"""

    user_id: UUID


class ReadUserByIdUseCase(IUseCase[ReadUserByIdCommand, UserResult]):
    """Use case for getting a user by ID"""

    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def execute(self, command: ReadUserByIdCommand) -> UserResult:
        """Execute the read user by ID use case"""
        try:
            user = await self.user_service.user_repo.read(command.user_id)
            if not user:
                raise UseCaseExecutionError(f"User with ID {command.user_id} not found")

            return UserResult(
                user=user,
            )

        except Exception as e:
            raise UseCaseExecutionError(
                f"Failed to read user: {e!s}",
            ) from e


# Type alias for compatibility
ReadUserByIdResult = UserResult
