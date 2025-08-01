"""Problem domain schemas for unified Problem management"""

from datetime import datetime
from uuid import UUID

from pydddi import ICreateSchema, IReadSchema, IUpdateSchema

from ..models.problem import DifficultyLevel, ProblemStatus


class CreateProblemSchema(ICreateSchema):
    """Schema for creating a problem"""

    title: str
    description: str
    book_id: UUID
    tags: list[str]
    content_markdown: str
    difficulty: DifficultyLevel = DifficultyLevel.EASY
    author_id: UUID


class UpdateProblemSchema(IUpdateSchema):
    """Schema for updating a problem"""

    title: str | None = None
    description: str | None = None
    tags: list[str] | None = None
    content_markdown: str | None = None
    difficulty: DifficultyLevel | None = None
    status: ProblemStatus | None = None


class ReadProblemSchema(IReadSchema):
    """Schema for reading a problem"""

    id: UUID
    title: str
    description: str
    book_id: UUID
    tags: list[str]
    content_markdown: str | None
    difficulty: DifficultyLevel
    status: ProblemStatus
    author_id: UUID
    published_at: datetime | None
    archived_at: datetime | None
    created_at: datetime
    updated_at: datetime
