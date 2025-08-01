from abc import abstractmethod
from datetime import datetime
from typing import Optional

from pydantic import UUID4, Field, field_validator
from pydddi import ICreateSchema, ICrudRepository, IReadSchema, IUpdateSchema

from ..entities import BookEntity
from .shared.has_domain_repository import HasDomainRepository


class CreateBookSchema(ICreateSchema):
    """Schema for creating a book"""

    title: str
    author_id: UUID4 | None
    published_at: str | None = None
    archived_at: str | None = None


class ReadBookSchema(IReadSchema):
    """Schema for reading a book"""

    id: UUID4
    title: str
    author_id: UUID4 | None
    published_at: str | None = None
    archived_at: str | None = None
    created_at: str
    updated_at: str


class UpdateBookSchema(IUpdateSchema):
    """Schema for updating a book"""

    id: UUID4
    title: str | None = None
    author_id: UUID4 | None = None
    published_at: str | None = None
    archived_at: str | None = None
    created_at: str | None = None


class BookRepositoryBase(
    ICrudRepository[BookEntity, CreateBookSchema, ReadBookSchema, UpdateBookSchema],
    HasDomainRepository,
):
    """Book repository interface"""

    @abstractmethod
    async def find_by_title(self, title: str) -> BookEntity | None:
        """Find book by exact title"""

    @abstractmethod
    async def find_by_author(self, author_id: UUID4) -> list[BookEntity]:
        """Find books by author"""

    @abstractmethod
    async def find_published(self, limit: int = 50, offset: int = 0) -> list[BookEntity]:
        """Find published books with pagination"""

    @abstractmethod
    async def search_by_title(self, title_query: str, limit: int = 20) -> list[BookEntity]:
        """Search books by title (partial match)"""

    @abstractmethod
    async def count_by_author(self, author_id: UUID4) -> int:
        """Count books by author"""

    @abstractmethod
    async def count_published(self) -> int:
        """Count published books"""

    @abstractmethod
    async def delete_all(self) -> None:
        """Delete all books"""
