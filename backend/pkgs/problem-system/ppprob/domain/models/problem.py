"""
Problem Domain Model
問題ドメインモデル
"""

from datetime import datetime

from pydantic import BaseModel, UUID4, Field, ConfigDict

from ..enums import DifficultyLevel, ProblemStatus


class Problem(BaseModel):
    """
    Problem aggregate root model
    問題集約ルート - 問題とその関連データのビジネスロジック
    Remove pydddi dependency for cleaner architecture
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True, use_enum_values=True, validate_assignment=True)

    # Core fields
    id: UUID4 = Field(...)
    title: str = Field(...)
    description: str = Field(...)
    difficulty: DifficultyLevel = Field(...)
    status: ProblemStatus = Field(default=ProblemStatus.DRAFT)
    author_id: UUID4 = Field(...)
    book_id: UUID4 | None = Field(default=None)
    tags: list[str] = Field(default_factory=list)
    
    # Timestamps
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)
    
    # Optional metadata
    problem_statement: str | None = Field(default=None, description="Detailed problem statement")
    constraints: str | None = Field(default=None, description="Problem constraints")
    examples: list[dict] | None = Field(default=None, description="Input/output examples")

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
        
    def get_id(self) -> UUID4:
        """Get problem ID"""
        return self.id
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return self.model_dump()
