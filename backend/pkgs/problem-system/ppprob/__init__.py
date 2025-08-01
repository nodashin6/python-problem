"""
Problem System Package
問題システムパッケージ - 問題の提供・識別

責任領域:
- 問題(Problem)の管理
- 書籍(Book)の管理
- 問題コンテンツの多言語対応
- 問題の検索・フィルタリング
"""

# Domain Entities (Persistence Objects)
from .domain.entities import BookEntity, ProblemEntity
from .domain.models import Book, Problem

# Domain Services
from .domain.services import BookService, ProblemApplicationService

# Use Cases
from .usecase.create_book_usecase import CreateBookUseCase
from .usecase.create_problem_usecase import CreateProblemUseCase
from .usecase.read_book_usecase import ReadBookByIdUseCase, ReadPublishedBooksUseCase
from .usecase.read_problem_usecase import (
    ReadProblemByIdUseCase,
    ReadProblemsByBookIdUseCase,
    ReadPublishedProblemsUseCase,
)

__all__ = [
    # Models
    "Problem",
    "Book",
    # Entities
    "ProblemEntity",
    "BookEntity",
    # Services
    "ProblemApplicationService",
    "BookService",
    # Use Cases
    "CreateBookUseCase",
    "CreateProblemUseCase",
    "ReadBookByIdUseCase",
    "ReadPublishedBooksUseCase",
    "ReadProblemByIdUseCase",
    "ReadProblemsByBookIdUseCase",
    "ReadPublishedProblemsUseCase",
]
