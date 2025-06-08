"""
Judge Domain module
ジャッジドメインモジュール
"""

# Domain Models
from .models import (
    Submission,
    CodeExecution,
    JudgeQueue,
    ExecutionResult,
    JudgeCaseResult,
    ExecutionStatus,
    JudgeResult,
    Language,
    SubmissionCreatedEvent,
    SubmissionJudgedEvent,
    CodeExecutionStartedEvent,
    CodeExecutionCompletedEvent,
    JudgeQueueUpdatedEvent,
)

# Domain Services
from .services import JudgeDomainService

# Repository Interfaces
from .repositories import (
    SubmissionRepository,
    CodeExecutionRepository,
    JudgeQueueRepository,
)

__all__ = [
    # Models and Value Objects
    "Submission",
    "CodeExecution",
    "JudgeQueue",
    "ExecutionResult",
    "JudgeCaseResult",
    "ExecutionStatus",
    "JudgeResult",
    "Language",
    # Events
    "SubmissionCreatedEvent",
    "SubmissionJudgedEvent",
    "CodeExecutionStartedEvent",
    "CodeExecutionCompletedEvent",
    "JudgeQueueUpdatedEvent",
    # Services
    "JudgeDomainService",
    # Repository Interfaces
    "SubmissionRepository",
    "CodeExecutionRepository",
    "JudgeQueueRepository",
]
