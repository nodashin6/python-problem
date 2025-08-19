"""
Unified Domain and System Events for the Judge System.

This module centralizes all event definitions used within the judge system
and for interaction with other domains, eliminating duplication and ensuring consistency.
"""
import uuid
from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Any, Dict, Optional


# --- Events originating from the Core Domain ---

@dataclass(frozen=True)
class ProblemCreatedEvent:
    """Event for when a new problem is created."""
    problem_id: str
    title: str
    difficulty: str
    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    correlation_id: Optional[uuid.UUID] = None
    source_domain: str = "core"


@dataclass(frozen=True)
class ProblemUpdatedEvent:
    """Event for when a problem's details are updated."""
    problem_id: str
    changes: Dict[str, Any]
    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    correlation_id: Optional[uuid.UUID] = None
    source_domain: str = "core"


@dataclass(frozen=True)
class JudgeCaseUpdatedEvent:
    """Event for when a judge case is updated."""
    problem_id: str
    judge_case_id: str
    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    correlation_id: Optional[uuid.UUID] = None
    source_domain: str = "core"


@dataclass(frozen=True)
class UserRegisteredEvent:
    """Event for when a new user is registered."""
    user_id: str
    user_name: str
    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    correlation_id: Optional[uuid.UUID] = None
    source_domain: str = "core"


# --- Events originating from the Judge System ---

@dataclass(frozen=True)
class SubmissionCreatedEvent:
    """Event for when a new submission is created."""
    submission_id: str
    user_id: str
    problem_id: str
    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    correlation_id: Optional[uuid.UUID] = None
    source_domain: str = "judge"


@dataclass(frozen=True)
class JudgeStartedEvent:
    """Event for when the judging process for a submission starts."""
    judge_id: str
    submission_id: str
    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    correlation_id: Optional[uuid.UUID] = None
    source_domain: str = "judge"


@dataclass(frozen=True)
class JudgeCompletedEvent:
    """Event for when the judging process for a submission is completed."""
    judge_id: str
    submission_id: str
    user_id: str
    result: str
    score: Optional[float] = None
    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    correlation_id: Optional[uuid.UUID] = None
    source_domain: str = "judge"


@dataclass(frozen=True)
class JudgeErrorEvent:
    """Event for when an error occurs during the judging process."""
    judge_id: str
    submission_id: str
    error: str
    context: Dict[str, Any] = field(default_factory=dict)
    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    correlation_id: Optional[uuid.UUID] = None
    source_domain: str = "judge"
