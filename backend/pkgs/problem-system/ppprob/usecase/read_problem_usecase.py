"""
Read Problem UseCase
問題読み取りユースケース

Author: Judge System Team
Date: 2025-06-30
"""

from uuid import UUID

from pydddi import (
    IUseCase,
    IUseCaseCommand,
    IUseCaseResult,
    UseCaseExecutionError,
)

from ..domain.entities.problem import ProblemEntity
from ..domain.services.problem_service import ProblemApplicationService


class ReadProblemByIdCommand(IUseCaseCommand):
    """Command for reading a problem by ID"""

    problem_id: UUID


class ReadProblemByIdResult(IUseCaseResult):
    """Result for reading a problem by ID"""

    problem: ProblemEntity | None


class ReadProblemsByBookIdCommand(IUseCaseCommand):
    """Command for reading problems by book ID"""

    book_id: UUID


class ReadProblemsByBookIdResult(IUseCaseResult):
    """Result for reading problems by book ID"""

    problems: list[ProblemEntity]


class ReadPublishedProblemsCommand(IUseCaseCommand):
    """Command for reading published problems"""


class ReadPublishedProblemsResult(IUseCaseResult):
    """Result for reading published problems"""

    problems: list[ProblemEntity]


class ReadProblemByIdUseCase(IUseCase[ReadProblemByIdCommand, ReadProblemByIdResult]):
    """Use case for reading a problem by ID"""

    def __init__(self, problem_service: ProblemApplicationService):
        self.problem_service = problem_service

    async def execute(self, command: ReadProblemByIdCommand) -> ReadProblemByIdResult:
        """Execute the read problem by ID use case"""
        try:
            problem = await self.problem_service.get_problem_by_id(command.problem_id)
            return ReadProblemByIdResult(problem=problem)

        except Exception as e:
            raise UseCaseExecutionError(f"Failed to read problem: {e!s}") from e


class ReadProblemsByBookIdUseCase(IUseCase[ReadProblemsByBookIdCommand, ReadProblemsByBookIdResult]):
    """Use case for reading problems by book ID"""

    def __init__(self, problem_service: ProblemApplicationService):
        self.problem_service = problem_service

    async def execute(self, command: ReadProblemsByBookIdCommand) -> ReadProblemsByBookIdResult:
        """Execute the read problems by book ID use case"""
        try:
            problems = await self.problem_service.get_problems_by_book_id(command.book_id)
            return ReadProblemsByBookIdResult(problems=problems)

        except Exception as e:
            raise UseCaseExecutionError(f"Failed to read problems by book ID: {e!s}") from e


class ReadPublishedProblemsUseCase(IUseCase[ReadPublishedProblemsCommand, ReadPublishedProblemsResult]):
    """Use case for reading published problems"""

    def __init__(self, problem_service: ProblemApplicationService):
        self.problem_service = problem_service

    async def execute(self, command: ReadPublishedProblemsCommand) -> ReadPublishedProblemsResult:
        """Execute the read published problems use case"""
        try:
            problems = await self.problem_service.get_published_problems()
            return ReadPublishedProblemsResult(problems=problems)

        except Exception as e:
            raise UseCaseExecutionError(f"Failed to read published problems: {e!s}") from e
