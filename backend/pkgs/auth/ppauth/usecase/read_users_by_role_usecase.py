from pydddi import IUseCase, IUseCaseCommand, UseCaseExecutionError

from ..domain.enums import UserRole
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
            # 専用のlist_users_by_roleメソッドを使用
            users = await self.user_service.user_repo.list_users_by_role(
                role=command.role,
                limit=command.limit,
                offset=command.offset,
            )

            user_results = [UserResult(user=user) for user in users]

            # 実際の実装では、SQLでのCOUNTクエリを使用すべき
            # 今回は簡易実装として現在の結果数を返す
            total_count = len(users)

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
