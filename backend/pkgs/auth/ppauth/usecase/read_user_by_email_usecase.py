from pydddi import IUseCase, IUseCaseCommand, UseCaseExecutionError

from ..domain.services.user_service import UserService
from .user_types import UserResult


class ReadUserByEmailCommand(IUseCaseCommand):
    """Command for reading a user by email"""

    email: str


class ReadUserByEmailUseCase(IUseCase[ReadUserByEmailCommand, UserResult]):
    """Use case for getting a user by email"""

    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def execute(self, command: ReadUserByEmailCommand) -> UserResult:
        """Execute the read user by email use case"""
        try:
            user = await self.user_service.user_repo.find_by_email(command.email)
            if not user:
                raise UseCaseExecutionError(f"User with email {command.email} not found")

            return UserResult(
                user=user,
            )

        except Exception as e:
            raise UseCaseExecutionError(
                f"Failed to read user by email: {e!s}",
            ) from e


# Type alias for compatibility
ReadUserByEmailResult = UserResult
