"""
Core Domain Infrastructure - Repository layer
"""

from .interfaces import (
    BookRepositoryInterface,
    ProblemRepositoryInterface,
    JudgeCaseRepositoryInterface,
    UserProblemStatusRepositoryInterface,
)

from .supabase_repositories import (
    SupabaseBookRepository,
    SupabaseProblemRepository,
    SupabaseJudgeCaseRepository,
    SupabaseUserProblemStatusRepository,
)

__all__ = [
    # Interfaces
    "BookRepositoryInterface",
    "ProblemRepositoryInterface",
    "JudgeCaseRepositoryInterface",
    "UserProblemStatusRepositoryInterface",
    # Implementations
    "SupabaseBookRepository",
    "SupabaseProblemRepository",
    "SupabaseJudgeCaseRepository",
    "SupabaseUserProblemStatusRepository",
]
