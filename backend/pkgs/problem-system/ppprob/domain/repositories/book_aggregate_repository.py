from pydantic import Field
from pydddi import IReadAggregateRepository, IReadAggregateSchema

from ..models import Book
from .shared.has_domain_repository import HasDomainRepository


class BookReadAggregateSchema(IReadAggregateSchema):
    """Schema for reading a book aggregate"""

    id: str
    title: str
    description: str
    author_id: str
    published_at: str | None = None
    archived_at: str | None = None
    created_at: str
    updated_at: str

    # 関連する問題の統計情報
    problem_count: int = Field(default=0, description="Total number of problems in this book")
    published_problem_count: int = Field(default=0, description="Number of published problems")

    # Author情報 (集約で必要)
    author_name: str = Field(description="Name of the book author")
    author_email: str = Field(description="Email of the book author")


class BookAggregateRepository(IReadAggregateRepository[Book, BookReadAggregateSchema], HasDomainRepository):
    """Repository interface for book aggregates."""

    async def find_by_id(self, book_id: str) -> Book | None:
        """Find a book aggregate by its ID."""
        raise NotImplementedError("This method should be implemented in the concrete repository.")

    async def find_all(self, limit: int = 50, offset: int = 0) -> list[Book]:
        """Find all book aggregates with pagination."""
        raise NotImplementedError("This method should be implemented in the concrete repository.")
