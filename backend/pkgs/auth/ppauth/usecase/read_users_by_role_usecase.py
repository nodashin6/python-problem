from pydddi import IUseCase, IUseCaseCommand, UseCaseExecutionError

from ..domain.entities.enums import UserRole
from ..domain.services.user_service import UserService
from .user_types import ReadUserListResult, UserResult


class ReadUsersByRoleCommand(IUseCaseCommand):
    """Command for reading users by role"""

    role: UserRole
    limit: int = 100
    offset: int = 0


class ReadUsersByRoleUseCase(IUseCase[ReadUsersByRoleCommand, ReadUserListResult]):
    """Use case for getting users by role"""

    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def execute(self, command: ReadUsersByRoleCommand) -> ReadUserListResult:
        """Execute the read users by role use case"""
        try:
            # Get user IDs with the specified role
            user_roles = await self.user_service.user_role_repo.find_by_role(
                command.role, limit=command.limit, offset=command.offset
            )

            user_results = []
            for user_role in user_roles:
                user = await self.user_service.user_repo.read(user_role.user_id)
                if user:
                    user_results.append(UserResult(user=user))

            # Get total count for pagination
            total_count = await self.user_service.user_role_repo.count_by_role(command.role)

            return ReadUserListResult(
                users=user_results,
                total_count=total_count,
            )

        except Exception as e:
            raise UseCaseExecutionError(
                f"Failed to read users by role: {e!s}",
            ) from e


# Type alias for compatibility
ReadUsersByRoleResult = ReadUserListResult
