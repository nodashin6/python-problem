"""Book domain schemas for unified Book management"""

from datetime import datetime
from uuid import UUID

from pydddi import ICreateSchema, IReadSchema, IUpdateSchema


class CreateBookSchema(ICreateSchema):
    """Schema for creating a book"""

    title: str
    description: str = ""
    author_id: UUID


class UpdateBookSchema(IUpdateSchema):
    """Schema for updating a book"""

    title: str | None = None
    description: str | None = None
    is_published: bool | None = None
    cover_image_url: str | None = None


class ReadBookSchema(IReadSchema):
    """Schema for reading a book"""

    id: UUID
    title: str
    description: str
    author_id: UUID | None
    is_published: bool
    cover_image_url: str | None
    published_at: datetime | None
    archived_at: datetime | None
    created_at: datetime
    updated_at: datetime
