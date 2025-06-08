"""
Core domain models for problem management and user management.
Follows Domain-Driven Design principles with proper entity and value object separation.
"""

from pydantic import BaseModel, Field, UUID4, ConfigDict, validator
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any, Union, Set
from uuid import UUID, uuid4

from ...const import DifficultyLevel, ProblemStatus, UserRole, JudgeCaseType
from ...shared.events import DomainEvent


# Base Entity and Value Object Classes
class Entity(BaseModel):
    """Base entity with domain events capability"""

    id: UUID4 = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(arbitrary_types_allowed=True, validate_assignment=True, use_enum_values=True)

    # Private attributes for domain events
    _events: List[DomainEvent]

    def __init__(self, **data):
        super().__init__(**data)
        self._events = []

    def add_event(self, event: DomainEvent) -> None:
        """Add domain event"""
        self._events.append(event)

    def clear_events(self) -> List[DomainEvent]:
        """Clear and return domain events"""
        events = self._events.copy()
        self._events.clear()
        return events


class ValueObject(BaseModel):
    """Base value object"""

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)


# Value Objects
class Tag(ValueObject):
    """Problem tag value object - aligned with actual DB schema"""

    name: str = Field(..., min_length=1, max_length=50)
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")

    @field_validator("name")
    def validate_name(cls, v):
        return v.strip().lower()


class ProblemMetadata(ValueObject):
    """Problem metadata value object"""

    time_limit_ms: int = Field(default=2000, ge=100, le=10000)
    memory_limit_mb: int = Field(default=256, ge=16, le=1024)
    expected_solution_length: Optional[int] = None
    hints: List[str] = Field(default_factory=list)


class UserProfile(ValueObject):
    """User profile value object"""

    display_name: str = Field(..., min_length=1, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = None
    github_username: Optional[str] = None
    preferred_language: str = Field(default="ja")


# Domain Events
class ProblemCreated(DomainEvent):
    problem_id: UUID4
    title: str
    author_id: UUID4


class ProblemPublished(DomainEvent):
    problem_id: UUID4
    published_by: UUID4


class JudgeCaseAdded(DomainEvent):
    problem_id: UUID4
    judge_case_id: UUID4
    is_sample: bool


class UserRegistered(DomainEvent):
    user_id: UUID4
    email: str
    role: UserRole


# Entities
class User(Entity):
    """User entity"""

    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")
    username: str = Field(..., min_length=3, max_length=50)
    password_hash: str
    role: UserRole = Field(default=UserRole.USER)
    profile: UserProfile
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    last_login_at: Optional[datetime] = None

    def __init__(self, **data):
        super().__init__(**data)
        if not hasattr(self, "_events") or not self._events:
            self.add_event(UserRegistered(user_id=self.id, email=self.email, role=self.role))

    def update_profile(self, profile: UserProfile) -> None:
        """Update user profile"""
        self.profile = profile
        self.updated_at = datetime.utcnow()

    def verify_email(self) -> None:
        """Verify user email"""
        self.is_verified = True
        self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        """Deactivate user"""
        self.is_active = False
        self.updated_at = datetime.utcnow()


class Problem(Entity):
    """Problem entity"""

    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    difficulty: DifficultyLevel = Field(default=DifficultyLevel.EASY)
    status: ProblemStatus = Field(default=ProblemStatus.DRAFT)
    tags: Set[Tag] = Field(default_factory=set)
    metadata: ProblemMetadata = Field(default_factory=ProblemMetadata)
    author_id: UUID4
    book_id: Optional[UUID4] = None

    # Statistics
    submission_count: int = Field(default=0, ge=0)
    accepted_count: int = Field(default=0, ge=0)

    def __init__(self, **data):
        super().__init__(**data)
        self.add_event(ProblemCreated(problem_id=self.id, title=self.title, author_id=self.author_id))

    @property
    def acceptance_rate(self) -> float:
        """Calculate acceptance rate"""
        if self.submission_count == 0:
            return 0.0
        return round(self.accepted_count / self.submission_count * 100, 2)

    def add_tag(self, tag: Tag) -> None:
        """Add tag to problem"""
        self.tags.add(tag)
        self.updated_at = datetime.utcnow()

    def remove_tag(self, tag_name: str) -> None:
        """Remove tag from problem"""
        self.tags = {tag for tag in self.tags if tag.name != tag_name.lower()}
        self.updated_at = datetime.utcnow()

    def publish(self) -> None:
        """Publish problem"""
        if self.status == ProblemStatus.DRAFT:
            self.status = ProblemStatus.PUBLISHED
            self.updated_at = datetime.utcnow()
            self.add_event(ProblemPublished(problem_id=self.id, published_by=self.author_id))

    def archive(self) -> None:
        """Archive problem"""
        self.status = ProblemStatus.ARCHIVED
        self.updated_at = datetime.utcnow()

    def update_statistics(self, submission_count: int, accepted_count: int) -> None:
        """Update problem statistics"""
        self.submission_count = submission_count
        self.accepted_count = accepted_count
        self.updated_at = datetime.utcnow()


class Book(Entity):
    """Problem book entity"""

    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="")
    author_id: UUID4
    is_published: bool = Field(default=False)
    cover_image_url: Optional[str] = None

    def publish(self) -> None:
        """Publish book"""
        self.is_published = True
        self.updated_at = datetime.utcnow()

    def unpublish(self) -> None:
        """Unpublish book"""
        self.is_published = False
        self.updated_at = datetime.utcnow()


class JudgeCase(Entity):
    """Judge case entity"""

    problem_id: UUID4
    name: str = Field(..., min_length=1, max_length=100)
    input_data: str
    expected_output: str
    case_type: JudgeCaseType = Field(default=JudgeCaseType.HIDDEN)
    display_order: int = Field(default=0, ge=0)
    points: int = Field(default=1, ge=0)

    def __init__(self, **data):
        super().__init__(**data)
        self.add_event(
            JudgeCaseAdded(
                problem_id=self.problem_id,
                judge_case_id=self.id,
                is_sample=(self.case_type == JudgeCaseType.SAMPLE),
            )
        )

    def make_sample(self) -> None:
        """Make this judge case a sample"""
        self.case_type = JudgeCaseType.SAMPLE
        self.updated_at = datetime.utcnow()

    def make_hidden(self) -> None:
        """Make this judge case hidden"""
        self.case_type = JudgeCaseType.HIDDEN
        self.updated_at = datetime.utcnow()


class ProblemContent(Entity):
    """Problem content for internationalization"""

    problem_id: UUID4
    language: str = Field(..., min_length=2, max_length=5)
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    input_format: str = Field(default="")
    output_format: str = Field(default="")
    constraints: str = Field(default="")
    sample_explanation: str = Field(default="")


class Editorial(Entity):
    """Editorial entity"""

    problem_id: UUID4
    author_id: UUID4
    is_published: bool = Field(default=False)

    def publish(self) -> None:
        """Publish editorial"""
        self.is_published = True
        self.updated_at = datetime.utcnow()


class EditorialContent(Entity):
    """Editorial content for internationalization"""

    editorial_id: UUID4
    language: str = Field(..., min_length=2, max_length=5)
    content: str = Field(..., min_length=1)
    approach: str = Field(default="")
    complexity_analysis: str = Field(default="")
    code_samples: Dict[str, str] = Field(default_factory=dict)  # language -> code


# Legacy compatibility (keeping the old models for migration)
class Content(Entity):
    """Content entity for various content types"""

    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    content_type: str = Field(..., min_length=1)  # Using string instead of ContentType enum for now
    author_id: UUID4
    is_published: bool = Field(default=False)
    language: str = Field(default="en", min_length=2, max_length=5)
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def publish(self) -> None:
        """Publish content"""
        self.is_published = True
        self.updated_at = datetime.utcnow()

    def unpublish(self) -> None:
        """Unpublish content"""
        self.is_published = False
        self.updated_at = datetime.utcnow()


class CaseFile(BaseModel):
    """テストケースの入力・出力ファイル (Legacy)"""

    id: UUID4
    url: str
    created_at: datetime
    updated_at: datetime
