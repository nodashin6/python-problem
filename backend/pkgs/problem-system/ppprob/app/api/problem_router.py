"""
Enhanced Problem System API Router
Enhanced problem endpoints with frontend integration support
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

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
from ..dependencies import (
    get_create_book_usecase,
    get_create_problem_usecase,
    get_read_book_by_id_usecase,
    get_read_problem_by_id_usecase,
    get_read_problems_by_book_id_usecase,
    get_read_published_books_usecase,
    get_read_published_problems_usecase,
)

problem_router = APIRouter(prefix="/api/problems", tags=["problems"])

# Enhanced Response Models for Frontend
class BookListResponse(BaseModel):
    """Book list response for frontend"""
    id: str
    title: str
    description: str
    author_id: str | None
    published_at: str | None
    problem_count: int = 0
    difficulty_level: str = "beginner"


class ProblemListResponse(BaseModel):
    """Problem list response for frontend"""
    id: str
    book_id: str
    title: str
    description: str
    tags: List[str] = Field(default_factory=list)
    difficulty_level: str = "beginner"
    status: str = "published"
    created_at: str | None = None


class ProblemDetailResponse(BaseModel):
    """Problem detail response for frontend"""
    id: str
    book_id: str
    title: str
    description: str
    content_markdown: str
    tags: List[str] = Field(default_factory=list)
    difficulty_level: str = "beginner"
    status: str = "published"
    time_limit_ms: int = 2000
    memory_limit_mb: int = 256
    created_at: str | None = None
    updated_at: str | None = None


class CreateProblemRequest(BaseModel):
    """Create problem request"""
    book_id: str
    title: str
    description: str
    content_markdown: str
    tags: List[str] = Field(default_factory=list)
    time_limit_ms: int = 2000
    memory_limit_mb: int = 256


class CreateBookRequest(BaseModel):
    """Create book request"""
    title: str
    description: str = ""
    author_id: str | None = None
    difficulty_level: str = "beginner"


# Book Endpoints
@problem_router.get("/books", response_model=List[BookListResponse])
async def get_books(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    usecase: ReadPublishedBooksUseCase = Depends(get_read_published_books_usecase),
) -> List[BookListResponse]:
    """Get list of published books for frontend"""
    try:
        command = ReadPublishedBooksCommand()
        result = await usecase.execute(command)

        return [
            BookListResponse(
                id=str(book.id),
                title=book.title,
                description=book.description or "",
                author_id=str(book.author_id) if book.author_id else None,
                published_at=book.published_at.isoformat() if book.published_at else None,
                problem_count=0,  # Would need separate query
                difficulty_level="beginner",  # Would come from book entity
            )
            for book in result.books[offset:offset + limit]
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch books: {str(e)}"
        )


@problem_router.get("/books/{book_id}", response_model=BookListResponse)
async def get_book(
    book_id: str,
    usecase: ReadBookByIdUseCase = Depends(get_read_book_by_id_usecase),
) -> BookListResponse:
    """Get book by ID for frontend"""
    try:
        command = ReadBookByIdCommand(book_id=UUID(book_id))
        result = await usecase.execute(command)

        if not result.book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )

        book = result.book
        return BookListResponse(
            id=str(book.id),
            title=book.title,
            description=book.description or "",
            author_id=str(book.author_id) if book.author_id else None,
            published_at=book.published_at.isoformat() if book.published_at else None,
            problem_count=0,  # Would need separate query
            difficulty_level="beginner",  # Would come from book entity
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid book ID format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch book: {str(e)}"
        )


@problem_router.post("/books", response_model=BookListResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    request: CreateBookRequest,
    usecase: CreateBookUseCase = Depends(get_create_book_usecase),
) -> BookListResponse:
    """Create a new book"""
    try:
        command = CreateBookCommand(
            title=request.title,
            description=request.description,
            author_id=UUID(request.author_id) if request.author_id else None,
        )
        result = await usecase.execute(command)

        return BookListResponse(
            id=str(result.book_id),
            title=result.title,
            description=result.description,
            author_id=str(result.author_id) if result.author_id else None,
            published_at=None,
            problem_count=0,
            difficulty_level=request.difficulty_level,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid author ID format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create book: {str(e)}"
        )


# Problem Endpoints
@problem_router.get("/list", response_model=List[ProblemListResponse])
async def get_problems(
    book_id: str | None = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    problems_by_book_usecase: ReadProblemsByBookIdUseCase = Depends(get_read_problems_by_book_id_usecase),
    published_problems_usecase: ReadPublishedProblemsUseCase = Depends(get_read_published_problems_usecase),
) -> List[ProblemListResponse]:
    """Get list of problems for frontend, optionally filtered by book ID"""
    try:
        if book_id:
            command = ReadProblemsByBookIdCommand(book_id=UUID(book_id))
            result = await problems_by_book_usecase.execute(command)
            problems = result.problems
        else:
            command = ReadPublishedProblemsCommand()
            result = await published_problems_usecase.execute(command)
            problems = result.problems

        return [
            ProblemListResponse(
                id=str(problem.id),
                book_id=str(problem.book_id),
                title=problem.title,
                description=problem.description or "",
                tags=problem.tags or [],
                difficulty_level="beginner",  # Would come from problem entity
                status="published",  # Would come from problem entity
                created_at=problem.created_at.isoformat() if problem.created_at else None,
            )
            for problem in problems[offset:offset + limit]
        ]
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid book ID format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch problems: {str(e)}"
        )


@problem_router.get("/{problem_id}", response_model=ProblemDetailResponse)
async def get_problem(
    problem_id: str,
    usecase: ReadProblemByIdUseCase = Depends(get_read_problem_by_id_usecase),
) -> ProblemDetailResponse:
    """Get problem detail by ID for frontend"""
    try:
        command = ReadProblemByIdCommand(problem_id=UUID(problem_id))
        result = await usecase.execute(command)

        if not result.problem:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Problem not found"
            )

        problem = result.problem
        return ProblemDetailResponse(
            id=str(problem.id),
            book_id=str(problem.book_id),
            title=problem.title,
            description=problem.description or "",
            content_markdown=problem.content_markdown or "",
            tags=problem.tags or [],
            difficulty_level="beginner",  # Would come from problem entity
            status="published",  # Would come from problem entity
            time_limit_ms=2000,  # Would come from problem entity
            memory_limit_mb=256,  # Would come from problem entity
            created_at=problem.created_at.isoformat() if problem.created_at else None,
            updated_at=problem.updated_at.isoformat() if problem.updated_at else None,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid problem ID format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch problem: {str(e)}"
        )


@problem_router.post("/", response_model=ProblemListResponse, status_code=status.HTTP_201_CREATED)
async def create_problem(
    request: CreateProblemRequest,
    usecase: CreateProblemUseCase = Depends(get_create_problem_usecase),
) -> ProblemListResponse:
    """Create a new problem"""
    try:
        command = CreateProblemCommand(
            book_id=UUID(request.book_id),
            title=request.title,
            description=request.description,
            tags=request.tags,
            content_markdown=request.content_markdown,
        )
        result = await usecase.execute(command)

        return ProblemListResponse(
            id=str(result.problem_id),
            book_id=str(result.book_id),
            title=result.title,
            description=result.description,
            tags=result.tags or [],
            difficulty_level="beginner",
            status="draft",  # New problems start as draft
            created_at=None,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid book ID format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create problem: {str(e)}"
        )


# Health check endpoint
@problem_router.get("/health")
async def problem_system_health():
    """Problem system health check"""
    return {
        "status": "healthy",
        "service": "problem-system",
        "version": "1.0.0",
        "endpoints": {
            "books": "/api/problems/books",
            "problems": "/api/problems/list",
            "problem_detail": "/api/problems/{problem_id}",
        }
    }