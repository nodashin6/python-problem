"""
Read Book UseCase
問題集読み取りユースケース

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


class ReadBookByIdCommand(IUseCaseCommand):
    """Command for reading a book by ID"""

    book_id: UUID


class ReadBookByIdResult(IUseCaseResult):
    """Result for reading a book by ID"""

    book: BookEntity | None


class ReadPublishedBooksCommand(IUseCaseCommand):
    """Command for reading published books"""


class ReadPublishedBooksResult(IUseCaseResult):
    """Result for reading published books"""

    books: list[BookEntity]


class ReadBookByIdUseCase(IUseCase[ReadBookByIdCommand, ReadBookByIdResult]):
    """Use case for reading a book by ID"""

    def __init__(self, book_service: BookService):
        self.book_service = book_service

    async def execute(self, command: ReadBookByIdCommand) -> ReadBookByIdResult:
        """Execute the read book by ID use case"""
        try:
            book = await self.book_service.get_book_by_id(command.book_id)
            return ReadBookByIdResult(book=book)

        except Exception as e:
            raise UseCaseExecutionError(f"Failed to read book: {e!s}") from e


class ReadPublishedBooksUseCase(IUseCase[ReadPublishedBooksCommand, ReadPublishedBooksResult]):
    """Use case for reading published books"""

    def __init__(self, book_service: BookService):
        self.book_service = book_service

    async def execute(self, command: ReadPublishedBooksCommand) -> ReadPublishedBooksResult:
        """Execute the read published books use case"""
        try:
            books = await self.book_service.get_published_books()
            return ReadPublishedBooksResult(books=books)

        except Exception as e:
            raise UseCaseExecutionError(f"Failed to read published books: {e!s}") from e
