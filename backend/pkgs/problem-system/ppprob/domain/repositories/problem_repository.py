from abc import abstractmethod
from datetime import datetime
from typing import Optional

from pydantic import UUID4, Field, field_validator
from pydddi import ICreateSchema, ICrudRepository, IReadSchema, IUpdateSchema

from ..entities import ProblemEntity
from ..enums import Language
from .shared.has_domain_repository import HasDomainRepository


class CreateProblemSchema(ICreateSchema):
    """Schema for creating a problem"""

    book_id: UUID4
    title: str
    description: str
    tags: list[str] = Field(default_factory=list)
    published_at: str | None = None
    content_markdown: str | None = None
    content_created_at: datetime | None = None
    content_updated_at: datetime | None = None
    language: Language = Language.JAPANESE


class ReadProblemSchema(IReadSchema):
    """Schema for reading a problem"""

    id: UUID4
    book_id: UUID4
    title: str
    description: str
    tags: list[str] = Field(default_factory=list)
    published_at: str | None = None
    created_at: datetime
    updated_at: datetime

    content_markdown: str | None = None
    content_created_at: datetime | None = None
    content_updated_at: datetime | None = None
    language: Language = Language.JAPANESE


class UpdateProblemSchema(IUpdateSchema):
    """Schema for updating a problem"""

    id: UUID4
    book_id: UUID4 | None = None
    title: str | None = None
    description: str | None = None
    tags: list[str] = Field(default_factory=list)
    published_at: str | None = None
    content_markdown: str | None = None
    content_created_at: datetime | None = None


class ProblemRepositoryBase(
    ICrudRepository[ProblemEntity, CreateProblemSchema, ReadProblemSchema, UpdateProblemSchema],
    HasDomainRepository,
):
    """Problem repository interface"""

    @abstractmethod
    async def find_by_title(self, title: str) -> ProblemEntity | None:
        """Find problem by exact title"""

    @abstractmethod
    async def find_by_book(self, book_id: UUID4) -> list[ProblemEntity]:
        """Find problems by book ID"""

    @abstractmethod
    async def find_published(self, limit: int = 50, offset: int = 0) -> list[ProblemEntity]:
        """Find published problems with pagination"""

    @abstractmethod
    async def search_by_title(self, title_query: str, limit: int = 20) -> list[ProblemEntity]:
        """Search problems by title (partial match)"""
