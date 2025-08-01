"""
Problem Entity
問題エンティティ - 永続化用データ構造
"""

from pydantic import UUID4, Field
from pydddi import IEntity

from ..models.problem import DifficultyLevel, ProblemStatus


class ProblemEntity(IEntity[UUID4]):
    """
    Problem entity for persistence
    問題エンティティ - データベース永続化用
    """

    title: str = Field(...)
    description: str = Field(...)
    content_markdown: str | None = Field(default=None)
    difficulty: DifficultyLevel = Field(...)
    status: ProblemStatus = Field(default=ProblemStatus.DRAFT)
    author_id: UUID4 = Field(...)
    book_id: UUID4 | None = Field(default=None)
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, str] = Field(default_factory=dict)
