from datetime import datetime

from pydantic import UUID4, Field, field_validator
from pydddi import IEntity


class ProblemEntity(IEntity):
    """
    Represents a problem entity.
    This class should contain fields that represent the problem's properties.
    """

    id: UUID4
    title: str
    description: str
    published_at: datetime | None = None
    
    created_at: datetime
    updated_at: datetime

    @field_validator("title")
    def validate_title(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Title cannot be empty")
        return value.strip()
