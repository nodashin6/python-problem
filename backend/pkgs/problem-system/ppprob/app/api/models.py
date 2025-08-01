"""
API Request and Response Models for Problem System
問題システムのAPIリクエスト・レスポンスモデル

Author: Judge System Team
Date: 2025-06-30
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

# =============================================================================
# Book Request/Response Models
# =============================================================================


class CreateBookRequest(BaseModel):
    """問題集作成リクエスト"""

    title: str
    description: str = ""
    author_id: UUID


class UpdateBookRequest(BaseModel):
    """問題集更新リクエスト"""

    title: str | None = None
    description: str | None = None


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


# =============================================================================
# Problem Request/Response Models
# =============================================================================


class CreateProblemRequest(BaseModel):
    """問題作成リクエスト"""

    book_id: UUID
    title: str
    description: str
    tags: list[str] = Field(default_factory=list)
    content_markdown: str


class UpdateProblemRequest(BaseModel):
    """問題更新リクエスト"""

    title: str | None = None
    description: str | None = None
    tags: list[str] | None = None
    content_markdown: str | None = None


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
