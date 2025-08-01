"""
Create Book UseCase
問題集作成ユースケース

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

from ..domain.entities.book import BookEntity
from ..domain.services.book_service import BookService


class CreateBookCommand(IUseCaseCommand):
    """Command for creating a book"""

    title: str
    description: str = ""
    author_id: UUID


class CreateBookResult(IUseCaseResult):
    """Result for creating a book"""

    book_id: UUID
    title: str
    description: str
    author_id: UUID | None


class CreateBookUseCase(IUseCase[CreateBookCommand, CreateBookResult]):
    """Use case for creating a book"""

    def __init__(self, book_service: BookService):
        self.book_service = book_service

    async def execute(self, command: CreateBookCommand) -> CreateBookResult:
        """Execute the create book use case"""
        # Validate command
        if not command.title.strip():
            raise UseCaseCommandError("Book title cannot be empty")

        try:
            # Create book through domain service
            book_entity = await self.book_service.create_book(
                title=command.title,
                description=command.description,
                author_id=command.author_id,
            )

            # Return result
            return CreateBookResult(
                book_id=book_entity.id,
                title=book_entity.title,
                description=book_entity.description,
                author_id=book_entity.author_id,
            )

        except Exception as e:
            raise UseCaseExecutionError(f"Failed to create book: {e!s}") from e
