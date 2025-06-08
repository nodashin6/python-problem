from datetime import datetime

from pydantic import UUID4, Field, field_validator
from pydddi import IEntity


class BookEntity(IEntity):
    """
    Represents a book entity.
    This class should contain fields that represent the book's properties.
    """

    id: UUID4
    title: str
    description: str
    author_id: UUID4
    published_at: datetime
    created_at: datetime
    updated_at: datetime
