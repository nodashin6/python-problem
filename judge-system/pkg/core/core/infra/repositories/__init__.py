"""
Core Domain Infrastructure - Repository layer
"""

from .interfaces import (
    BookRepositoryInterface,
    ProblemRepositoryInterface,
    JudgeCaseRepositoryInterface,
    # UserProblemStatusRepositoryInterface,  # TODO: 未実装のため一時コメントアウト
)

from .supabase_repositories import (
    SupabaseBookRepository,
    SupabaseProblemRepository,
    SupabaseJudgeCaseRepository,
    # SupabaseUserProblemStatusRepository,  # TODO: 未実装のため一時コメントアウト
)

__all__ = [
    # Interfaces
    "BookRepositoryInterface",
    "ProblemRepositoryInterface",
    "JudgeCaseRepositoryInterface",
    # "UserProblemStatusRepositoryInterface",  # TODO: 未実装のため一時コメントアウト
    # Implementations
    "SupabaseBookRepository",
    "SupabaseProblemRepository",
    "SupabaseJudgeCaseRepository",
    # "SupabaseUserProblemStatusRepository",  # TODO: 未実装のため一時コメントアウト
]
