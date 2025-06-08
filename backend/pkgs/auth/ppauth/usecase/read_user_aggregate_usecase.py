from pydddi import IUseCase, IUseCaseCommand, UseCaseExecutionError

from ..domain.models.user import User
from ..domain.repositories.user_aggreate_read_repository import UserAggregateReadRepository


class ReadUserAggregateByEmailCommand(IUseCaseCommand):
    """Command for reading a user aggregate by email"""

    email: str


class ReadUserAggregateByUsernameCommand(IUseCaseCommand):
    """Command for reading a user aggregate by username"""

    username: str


class ReadActiveUsersCommand(IUseCaseCommand):
    """Command for reading active users"""

    limit: int = 100
    offset: int = 0


class ReadUserAggregateByEmailUseCase(IUseCase[ReadUserAggregateByEmailCommand, User]):
    """Use case for reading a user aggregate by email"""

    def __init__(self, user_aggregate_repo: UserAggregateReadRepository):
        self.user_aggregate_repo = user_aggregate_repo

    async def execute(self, command: ReadUserAggregateByEmailCommand) -> User:
        """Execute the read user aggregate by email use case"""
        try:
            user = await self.user_aggregate_repo.read_by_email(command.email)
            if not user:
                raise UseCaseExecutionError(f"User with email {command.email} not found")

            return user

        except Exception as e:
            raise UseCaseExecutionError(
                f"Failed to read user aggregate by email: {e!s}",
            ) from e


class ReadUserAggregateByUsernameUseCase(IUseCase[ReadUserAggregateByUsernameCommand, User]):
    """Use case for reading a user aggregate by username"""

    def __init__(self, user_aggregate_repo: UserAggregateReadRepository):
        self.user_aggregate_repo = user_aggregate_repo

    async def execute(self, command: ReadUserAggregateByUsernameCommand) -> User:
        """Execute the read user aggregate by username use case"""
        try:
            user = await self.user_aggregate_repo.read_by_username(command.username)
            if not user:
                raise UseCaseExecutionError(f"User with username {command.username} not found")

            return user

        except Exception as e:
            raise UseCaseExecutionError(
                f"Failed to read user aggregate by username: {e!s}",
            ) from e


class ReadActiveUsersUseCase(IUseCase[ReadActiveUsersCommand, list[User]]):
    """Use case for reading active users"""

    def __init__(self, user_aggregate_repo: UserAggregateReadRepository):
        self.user_aggregate_repo = user_aggregate_repo

    async def execute(self, command: ReadActiveUsersCommand) -> list[User]:
        """Execute the read active users use case"""
        try:
            users = await self.user_aggregate_repo.list_active_users(
                limit=command.limit, offset=command.offset
            )
            return users

        except Exception as e:
            raise UseCaseExecutionError(
                f"Failed to read active users: {e!s}",
            ) from e
