"""
Create Problem UseCase
問題作成ユースケース

Author: Judge System Team
Date: 2025-06-30
"""

from uuid import UUID

from pydddi import (
    IUseCase,
    IUseCaseCommand,
    IUseCaseResult,
    UseCaseCommandError,
    UseCaseExecutionError,
)

from ..domain.entities.problem import ProblemEntity
from ..domain.services.problem_service import ProblemApplicationService


class CreateProblemCommand(IUseCaseCommand):
    """Command for creating a problem"""

    book_id: UUID
    title: str
    description: str
    tags: list[str]
    content_markdown: str


class CreateProblemResult(IUseCaseResult):
    """Result for creating a problem"""

    problem_id: UUID
    book_id: UUID
    title: str
    description: str
    tags: list[str]


class CreateProblemUseCase(IUseCase[CreateProblemCommand, CreateProblemResult]):
    """Use case for creating a problem"""

    def __init__(self, problem_service: ProblemApplicationService):
        self.problem_service = problem_service

    async def execute(self, command: CreateProblemCommand) -> CreateProblemResult:
        """Execute the create problem use case"""
        # Validate command
        if not command.title.strip():
            raise UseCaseCommandError("Problem title cannot be empty")

        try:
            # Create problem through domain service
            problem_entity = await self.problem_service.create_problem(
                book_id=command.book_id,
                title=command.title,
                description=command.description,
                tags=command.tags,
                content_markdown=command.content_markdown,
            )

            # Return result
            return CreateProblemResult(
                problem_id=problem_entity.id,
                book_id=problem_entity.book_id,
                title=problem_entity.title,
                description=problem_entity.description,
                tags=problem_entity.tags,
            )

        except Exception as e:
            raise UseCaseExecutionError(f"Failed to create problem: {e!s}") from e
