"""Use Cases package for Problem System"""

from .create_book_usecase import CreateBookCommand, CreateBookResult, CreateBookUseCase
from .create_problem_usecase import CreateProblemCommand, CreateProblemResult, CreateProblemUseCase
from .read_book_usecase import (
    ReadBookByIdCommand,
    ReadBookByIdResult,
    ReadBookByIdUseCase,
    ReadPublishedBooksCommand,
    ReadPublishedBooksResult,
    ReadPublishedBooksUseCase,
)
from .read_problem_usecase import (
    ReadProblemByIdCommand,
    ReadProblemByIdResult,
    ReadProblemByIdUseCase,
    ReadProblemsByBookIdCommand,
    ReadProblemsByBookIdResult,
    ReadProblemsByBookIdUseCase,
    ReadPublishedProblemsCommand,
    ReadPublishedProblemsResult,
    ReadPublishedProblemsUseCase,
)

__all__ = [
    # Create Book
    "CreateBookCommand",
    "CreateBookResult",
    "CreateBookUseCase",
    # Create Problem
    "CreateProblemCommand",
    "CreateProblemResult",
    "CreateProblemUseCase",
    # Read Book
    "ReadBookByIdCommand",
    "ReadBookByIdResult",
    "ReadBookByIdUseCase",
    "ReadPublishedBooksCommand",
    "ReadPublishedBooksResult",
    "ReadPublishedBooksUseCase",
    # Read Problem
    "ReadProblemByIdCommand",
    "ReadProblemByIdResult",
    "ReadProblemByIdUseCase",
    "ReadProblemsByBookIdCommand",
    "ReadProblemsByBookIdResult",
    "ReadProblemsByBookIdUseCase",
    "ReadPublishedProblemsCommand",
    "ReadPublishedProblemsResult",
    "ReadPublishedProblemsUseCase",
]
