"""
Book Entity
書籍エンティティ - 永続化用データ構造
"""

from pydantic import UUID4, Field
from pydddi import IEntity


class BookEntity(IEntity[UUID4]):
    """
    Book entity for persistence
    書籍エンティティ - データベース永続化用
    """

    title: str = Field(...)
    description: str = Field(default="")
    author_id: UUID4 | None = Field(default=None)
    is_published: bool = Field(default=False)
    cover_image_url: str | None = Field(default=None)
