"""
Problem System Package
問題システムパッケージ - 問題の提供・識別

責任領域:
- 問題(Problem)の管理
- 書籍(Book)の管理
- 問題コンテンツの多言語対応
- 問題の検索・フィルタリング
"""

# Domain Models (Aggregate Roots)
# API Controllers
from .app.api.controllers import BookController, ProblemController

# Domain Entities (Persistence Objects)
from .domain.entities import BookEntity, ProblemEntity
from .domain.models import Book, Problem

# Domain Services
from .domain.services import BookDomainService, ProblemDomainService

# Use Cases
from .usecase import (
    CreateProblemUseCase,
    PublishProblemUseCase,
    SearchProblemsUseCase,
    UpdateProblemUseCase,
)

__all__ = [
    # Models
    "Problem",
    "Book",
    # Entities
    "ProblemEntity",
    "BookEntity",
    # Services
    "ProblemDomainService",
    "BookDomainService",
    # Use Cases
    "CreateProblemUseCase",
    "UpdateProblemUseCase",
    "PublishProblemUseCase",
    "SearchProblemsUseCase",
    # Controllers
    "ProblemController",
    "BookController",
]
