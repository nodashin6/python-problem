"""
Application Controllers for the Problem System
問題システムのアプリケーションコントローラー

Author: Judge System Team
Date: 2025-01-12
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from ..domain.entities import BookEntity, ProblemEntity
from ..domain.enums import ProblemStatus

# =============================================================================
# Request/Response Models
# =============================================================================


class CreateBookRequest(BaseModel):
    """問題集作成リクエスト"""

    title: str
    description: str = ""
    author_id: UUID


class BookResponse(BaseModel):
    """問題集レスポンス"""

    id: UUID
    title: str
    description: str
    author_id: UUID | None
    published_at: datetime | None
    archived_at: datetime | None
    created_at: datetime
    updated_at: datetime


class CreateProblemRequest(BaseModel):
    """問題作成リクエスト"""

    book_id: UUID
    title: str
    description: str
    tags: list[str] = Field(default_factory=list)
    content_markdown: str


class ProblemResponse(BaseModel):
    """問題レスポンス"""

    id: UUID
    book_id: UUID
    title: str
    description: str
    tags: list[str]
    published_at: datetime | None
    archived_at: datetime | None
    created_at: datetime
    updated_at: datetime


class ProblemDetailResponse(ProblemResponse):
    """問題詳細レスポンス"""

    content_markdown: str


# =============================================================================
# Controllers
# =============================================================================


class BookController:
    """問題集コントローラー"""

    def __init__(self, book_service):
        self.book_service = book_service

    async def get_books(self) -> list[BookResponse]:
        """公開されている問題集一覧を取得"""
        books = await self.book_service.get_published_books()
        return [self._entity_to_response(book) for book in books]

    async def get_book(self, book_id: UUID) -> BookResponse:
        """問題集詳細を取得"""
        book = await self.book_service.get_book_by_id(book_id)
        if not book:
            raise ValueError("Book not found")
        return self._entity_to_response(book)

    async def create_book(self, request: CreateBookRequest) -> BookResponse:
        """新しい問題集を作成"""
        book = await self.book_service.create_book(
            title=request.title, description=request.description, author_id=request.author_id
        )
        return self._entity_to_response(book)

    def _entity_to_response(self, entity: BookEntity) -> BookResponse:
        """エンティティをレスポンスに変換"""
        return BookResponse(
            id=entity.id,
            title=entity.title,
            description=entity.description,
            author_id=entity.author_id,
            published_at=entity.published_at,
            archived_at=entity.archived_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )


class ProblemController:
    """問題コントローラー"""

    def __init__(self, problem_service):
        self.problem_service = problem_service

    async def get_problems(self, book_id: UUID | None = None) -> list[ProblemResponse]:
        """公開されている問題一覧を取得"""
        if book_id:
            problems = await self.problem_service.get_problems_by_book_id(book_id)
        else:
            problems = await self.problem_service.get_published_problems()
        return [self._entity_to_response(problem) for problem in problems]

    async def get_problem(self, problem_id: UUID, user_id: str | None = None) -> ProblemDetailResponse:
        """問題詳細を取得"""
        problem = await self.problem_service.get_problem_by_id(problem_id)
        if not problem:
            raise ValueError("Problem not found")

        return ProblemDetailResponse(
            id=problem.id,
            book_id=problem.book_id,
            title=problem.title,
            description=problem.description,
            tags=problem.tags,
            published_at=problem.published_at,
            archived_at=problem.archived_at,
            created_at=problem.created_at,
            updated_at=problem.updated_at,
            content_markdown=problem.content_markdown or "",
        )

    async def create_problem(self, request: CreateProblemRequest) -> ProblemResponse:
        """新しい問題を作成"""
        problem = await self.problem_service.create_problem(
            title=request.title,
            description=request.description,
            book_id=request.book_id,
            tags=request.tags,
            content_markdown=request.content_markdown,
        )
        return self._entity_to_response(problem)

    def _entity_to_response(self, entity: ProblemEntity) -> ProblemResponse:
        """エンティティをレスポンスに変換"""
        return ProblemResponse(
            id=entity.id,
            book_id=entity.book_id,
            title=entity.title,
            description=entity.description,
            tags=entity.tags,
            published_at=entity.published_at,
            archived_at=entity.archived_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
