"""
Problem Domain Model
問題ドメインモデル
"""

from datetime import datetime
from enum import Enum

from pydantic import UUID4, Field

from .base import BaseModel


class DifficultyLevel(str, Enum):
    """Problem difficulty levels"""

    BEGINNER = "beginner"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class ProblemStatus(str, Enum):
    """Problem status"""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Problem(BaseModel):
    """
    Problem aggregate root model
    問題集約ルート - 問題とその関連データのビジネスロジック
    """

    title: str = Field(...)
    description: str = Field(...)
    difficulty: DifficultyLevel = Field(...)
    status: ProblemStatus = Field(default=ProblemStatus.DRAFT)
    author_id: UUID4 = Field(...)
    book_id: UUID4 | None = Field(default=None)
    tags: list[str] = Field(default_factory=list)

    def publish(self) -> None:
        """Publish the problem"""
        if self.status == ProblemStatus.DRAFT:
            self.status = ProblemStatus.PUBLISHED
            self.updated_at = datetime.now()

    def archive(self) -> None:
        """Archive the problem"""
        self.status = ProblemStatus.ARCHIVED
        self.updated_at = datetime.now()

    def add_tag(self, tag: str) -> None:
        """Add a tag to the problem"""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now()

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the problem"""
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.now()

    def is_published(self) -> bool:
        """Check if problem is published"""
        return self.status == ProblemStatus.PUBLISHED
