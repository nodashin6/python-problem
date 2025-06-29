from pydantic import UUID4, Field, field_validator
from pydddi import IReadAggregateRepository, IReadAggregateSchema

from ..models import Problem
from .shared.has_domain_repository import HasDomainRepository


class ProblemReadAggregateSchema(IReadAggregateSchema):
    """Schema for reading a problem aggregate"""

    id: str
    book_id: str
    title: str
    description: str
    tags: list[str] = Field(default_factory=list)
    published_at: str | None = None
    content_markdown: str
    content_created_at: str | None = None
    content_updated_at: str | None = None


class ProblemAggregateRepository(
    IReadAggregateRepository[Problem, ProblemReadAggregateSchema], HasDomainRepository
): ...
