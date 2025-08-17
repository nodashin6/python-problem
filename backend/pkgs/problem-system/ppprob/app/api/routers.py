"""
Problem System API endpoints
問題システムのAPIエンドポイント

Author: Judge System Team
Date: 2025-06-30
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..dependencies import (
    get_create_book_usecase,
    get_create_problem_usecase,
    get_read_book_by_id_usecase,
    get_read_problem_by_id_usecase,
    get_read_problems_by_book_id_usecase,
    get_read_published_books_usecase,
    get_read_published_problems_usecase,
)
from ...usecase.create_book_usecase import CreateBookCommand, CreateBookUseCase
from ...usecase.create_problem_usecase import CreateProblemCommand, CreateProblemUseCase
from ...usecase.read_book_usecase import (
    ReadBookByIdCommand,
    ReadBookByIdUseCase,
    ReadPublishedBooksCommand,
    ReadPublishedBooksUseCase,
)
from ...usecase.read_problem_usecase import (
    ReadProblemByIdCommand,
    ReadProblemByIdUseCase,
    ReadProblemsByBookIdCommand,
    ReadProblemsByBookIdUseCase,
    ReadPublishedProblemsCommand,
    ReadPublishedProblemsUseCase,
)
from .models import (
    BookResponse,
    CreateBookRequest,
    CreateProblemRequest,
    ProblemDetailResponse,
    ProblemResponse,
)

router = APIRouter()


# =============================================================================
# Book Endpoints
# =============================================================================


@router.get("/books", response_model=list[BookResponse])
async def get_books(
    usecase: ReadPublishedBooksUseCase = Depends(get_read_published_books_usecase),
) -> list[BookResponse]:
    """Get list of published books"""
    command = ReadPublishedBooksCommand()
    result = await usecase.execute(command)

    return [
        BookResponse(
            id=book.id,
            title=book.title,
            description=book.description,
            author_id=book.author_id,
            published_at=book.published_at,
            archived_at=book.archived_at,
            created_at=book.created_at,
            updated_at=book.updated_at,
        )
        for book in result.books
    ]


@router.get("/books/{book_id}", response_model=BookResponse)
async def get_book(
    book_id: UUID,
    usecase: ReadBookByIdUseCase = Depends(get_read_book_by_id_usecase),
) -> BookResponse:
    """Get book by ID"""
    command = ReadBookByIdCommand(book_id=book_id)
    result = await usecase.execute(command)

    if not result.book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    book = result.book
    return BookResponse(
        id=book.id,
        title=book.title,
        description=book.description,
        author_id=book.author_id,
        published_at=book.published_at,
        archived_at=book.archived_at,
        created_at=book.created_at,
        updated_at=book.updated_at,
    )


@router.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    request: CreateBookRequest,
    usecase: CreateBookUseCase = Depends(get_create_book_usecase),
) -> BookResponse:
    """Create a new book"""
    command = CreateBookCommand(
        title=request.title,
        description=request.description,
        author_id=request.author_id,
    )
    result = await usecase.execute(command)

    # Note: Since the result doesn't contain all fields, we need to fetch the book again
    # In a real implementation, you might want to include more fields in the result
    from datetime import datetime
    now = datetime.now()
    return BookResponse(
        id=result.book_id,
        title=result.title,
        description=result.description,
        author_id=result.author_id,
        published_at=None,  # New books are not published by default
        archived_at=None,
        created_at=now,  # Set to current time for new books
        updated_at=now,  # Set to current time for new books
    )


# =============================================================================
# Problem Endpoints
# =============================================================================


@router.get("/problems", response_model=list[ProblemResponse])
async def get_problems(
    book_id: UUID | None = Query(None),
    problems_by_book_usecase: ReadProblemsByBookIdUseCase = Depends(get_read_problems_by_book_id_usecase),
    published_problems_usecase: ReadPublishedProblemsUseCase = Depends(get_read_published_problems_usecase),
) -> list[ProblemResponse]:
    """Get list of problems, optionally filtered by book ID"""
    if book_id:
        command = ReadProblemsByBookIdCommand(book_id=book_id)
        result = await problems_by_book_usecase.execute(command)
        problems = result.problems
    else:
        command = ReadPublishedProblemsCommand()
        result = await published_problems_usecase.execute(command)
        problems = result.problems

    return [
        ProblemResponse(
            id=problem.id,
            book_id=problem.book_id,
            title=problem.title,
            description=problem.description,
            tags=problem.tags,
            published_at=problem.published_at,
            archived_at=problem.archived_at,
            created_at=problem.created_at,
            updated_at=problem.updated_at,
        )
        for problem in problems
    ]


@router.get("/problems/{problem_id}", response_model=ProblemDetailResponse)
async def get_problem(
    problem_id: UUID,
    usecase: ReadProblemByIdUseCase = Depends(get_read_problem_by_id_usecase),
) -> ProblemDetailResponse:
    """Get problem detail by ID"""
    command = ReadProblemByIdCommand(problem_id=problem_id)
    result = await usecase.execute(command)

    if not result.problem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")

    problem = result.problem
    return ProblemDetailResponse(
        id=problem.id,
        book_id=problem.book_id,
        title=problem.title,
        description=problem.description,
        tags=problem.tags,
        content_markdown=problem.content_markdown or "",
        published_at=problem.published_at,
        archived_at=problem.archived_at,
        created_at=problem.created_at,
        updated_at=problem.updated_at,
    )


@router.post("/problems", response_model=ProblemResponse, status_code=status.HTTP_201_CREATED)
async def create_problem(
    request: CreateProblemRequest,
    usecase: CreateProblemUseCase = Depends(get_create_problem_usecase),
) -> ProblemResponse:
    """Create a new problem"""
    command = CreateProblemCommand(
        book_id=request.book_id,
        title=request.title,
        description=request.description,
        tags=request.tags,
        content_markdown=request.content_markdown,
    )
    result = await usecase.execute(command)

    from datetime import datetime
    now = datetime.now()
    return ProblemResponse(
        id=result.problem_id,
        book_id=result.book_id,
        title=result.title,
        description=result.description,
        tags=result.tags,
        published_at=None,  # New problems are not published by default
        archived_at=None,
        created_at=now,  # Set to current time for new problems
        updated_at=now,  # Set to current time for new problems
    )
