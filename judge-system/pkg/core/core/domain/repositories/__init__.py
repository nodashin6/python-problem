"""
Core domain repository interfaces
"""

from .repository_base import CoreRepositoryBase
from .user_repository import UserRepository
from .problem_repository import ProblemRepository
from .judge_case_repository import JudgeCaseRepository
from .book_repository import BookRepository
from .content_repository import (
    ProblemContentRepository,
    EditorialRepository,
    EditorialContentRepository,
)

__all__ = [
    "CoreRepositoryBase",
    "UserRepository",
    "ProblemRepository",
    "JudgeCaseRepository",
    "BookRepository",
    "ProblemContentRepository",
    "EditorialRepository",
    "EditorialContentRepository",
]
