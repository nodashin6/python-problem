"""
Dependency injection for Problem System application
問題システムアプリケーションの依存性注入

Author: Judge System Team
Date: 2025-06-30
"""

import os
from functools import lru_cache

from fastapi import Depends
from supabase import Client
from ppcore.infrastructure.supabase.client import create_client

from ..domain.models.domain_config import DomainConfig
from ..domain.repositories.book_repository import BookRepositoryBase
from ..domain.repositories.problem_repository import ProblemRepositoryBase
from ..domain.services.book_service import BookService
from ..domain.services.problem_service import ProblemApplicationService
from ..infrastructure.supabase.repositories.book_repository_impl import BookRepositoryImpl
from ..infrastructure.supabase.repositories.problem_repository_impl import ProblemRepositoryImpl
from ..usecase.create_book_usecase import CreateBookUseCase
from ..usecase.create_problem_usecase import CreateProblemUseCase
from ..usecase.read_book_usecase import ReadBookByIdUseCase, ReadPublishedBooksUseCase
from ..usecase.read_problem_usecase import (
    ReadProblemByIdUseCase,
    ReadProblemsByBookIdUseCase,
    ReadPublishedProblemsUseCase,
)

# =============================================================================
# Infrastructure Dependencies
# =============================================================================


@lru_cache
def get_supabase_client() -> Client:
    """Get Supabase client using enhanced auto-loading client"""
    return create_client()


@lru_cache
def get_domain_config() -> DomainConfig:
    """Get domain configuration"""
    # TODO: Implement proper domain config loading
    return DomainConfig()


# =============================================================================
# Repository Dependencies
# =============================================================================


def get_book_repository(
    supabase_client: Client = Depends(get_supabase_client),
    config: DomainConfig = Depends(get_domain_config),
) -> BookRepositoryBase:
    """Get book repository"""
    return BookRepositoryImpl(supabase_client, config)


def get_problem_repository(
    supabase_client: Client = Depends(get_supabase_client),
    config: DomainConfig = Depends(get_domain_config),
) -> ProblemRepositoryBase:
    """Get problem repository"""
    return ProblemRepositoryImpl(supabase_client, config)


# =============================================================================
# Service Dependencies
# =============================================================================


def get_book_service(
    book_repository: BookRepositoryBase = Depends(get_book_repository),
) -> BookService:
    """Get book domain service"""
    return BookService(book_repository)


def get_problem_service(
    problem_repository: ProblemRepositoryBase = Depends(get_problem_repository),
) -> ProblemApplicationService:
    """Get problem domain service"""
    return ProblemApplicationService(problem_repository)


# =============================================================================
# UseCase Dependencies
# =============================================================================


def get_create_book_usecase(
    book_service: BookService = Depends(get_book_service),
) -> CreateBookUseCase:
    """Get create book use case"""
    return CreateBookUseCase(book_service)


def get_read_book_by_id_usecase(
    book_service: BookService = Depends(get_book_service),
) -> ReadBookByIdUseCase:
    """Get read book by ID use case"""
    return ReadBookByIdUseCase(book_service)


def get_read_published_books_usecase(
    book_service: BookService = Depends(get_book_service),
) -> ReadPublishedBooksUseCase:
    """Get read published books use case"""
    return ReadPublishedBooksUseCase(book_service)


def get_create_problem_usecase(
    problem_service: ProblemApplicationService = Depends(get_problem_service),
) -> CreateProblemUseCase:
    """Get create problem use case"""
    return CreateProblemUseCase(problem_service)


def get_read_problem_by_id_usecase(
    problem_service: ProblemApplicationService = Depends(get_problem_service),
) -> ReadProblemByIdUseCase:
    """Get read problem by ID use case"""
    return ReadProblemByIdUseCase(problem_service)


def get_read_problems_by_book_id_usecase(
    problem_service: ProblemApplicationService = Depends(get_problem_service),
) -> ReadProblemsByBookIdUseCase:
    """Get read problems by book ID use case"""
    return ReadProblemsByBookIdUseCase(problem_service)


def get_read_published_problems_usecase(
    problem_service: ProblemApplicationService = Depends(get_problem_service),
) -> ReadPublishedProblemsUseCase:
    """Get read published problems use case"""
    return ReadPublishedProblemsUseCase(problem_service)
