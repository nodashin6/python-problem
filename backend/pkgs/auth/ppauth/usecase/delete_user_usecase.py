from uuid import UUID

from pydddi import (
    IUseCase,
    IUseCaseCommand,
    IUseCaseResult,
    UseCaseCommandError,
    UseCaseExecutionError,
    UseCaseResultError,
)

from ..domain.services.user_service import UserService


class DeleteUserCommand(IUseCaseCommand):
    """Command for deleting a user"""

    user_id: UUID
    soft_delete: bool = True  # ソフトデリートかハードデリートか


class DeleteUserResult(IUseCaseResult):
    """Result for deleting a user"""

    user_id: UUID
    deleted: bool
    soft_deleted: bool


class DeleteUserUseCase(IUseCase[DeleteUserCommand, DeleteUserResult]):
    """Use case for deleting a user"""

    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def execute(self, command: DeleteUserCommand) -> DeleteUserResult:
        """Execute the delete user use case"""
        try:
            # Check if user exists
            user = await self.user_service.user_repo.read(command.user_id)
            if not user:
                raise UseCaseExecutionError(f"User with ID {command.user_id} not found")

            if command.soft_delete:
                # Soft delete - deactivate user
                success = await self.user_service.deactivate_user(command.user_id)
                return DeleteUserResult(
                    user_id=command.user_id,
                    deleted=success,
                    soft_deleted=True,
                )
            else:
                # Hard delete - remove from database
                await self.user_service.user_repo.delete(command.user_id)

                # Also delete associated user roles
                await self.user_service.user_role_repo.delete_by_user_id(command.user_id)

                return DeleteUserResult(
                    user_id=command.user_id,
                    deleted=True,
                    soft_deleted=False,
                )

        except Exception as e:
            raise UseCaseExecutionError(
                f"Failed to delete user: {e!s}",
            ) from e
