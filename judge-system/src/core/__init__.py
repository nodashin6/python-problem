"""
Core Domain module
コアドメインモジュール
"""

# Domain Models
from .domain.models import (
    User,
    Problem,
    JudgeCase,
    Book,
    Content,
    Tag,
    ProblemMetadata,
    UserProfile,
)

# Domain Events
from .domain.events import (
    UserRegisteredEvent,
    UserProfileUpdatedEvent,
    ProblemCreatedEvent,
    ProblemUpdatedEvent,
    ProblemPublishedEvent,
    JudgeCaseAddedEvent,
    JudgeCaseUpdatedEvent,
    BookCreatedEvent,
    BookUpdatedEvent,
    BookPublishedEvent,
)

# Domain Services
from .domain.services import UserDomainService, ProblemDomainService, BookDomainService

# Repository Interfaces
from .domain.repositories import (
    UserRepository,
    ProblemRepository,
    JudgeCaseRepository,
    BookRepository,
    ContentRepository,
)

# Infrastructure Implementations
from .infra import (
    UserRepositoryImpl,
    ProblemRepositoryImpl,
    JudgeCaseRepositoryImpl,
    BookRepositoryImpl,
    ContentRepositoryImpl,
)

__all__ = [
    # Models
    "User",
    "Problem",
    "JudgeCase",
    "Book",
    "Content",
    "Tag",
    "ProblemMetadata",
    "UserProfile",
    # Events
    "UserRegisteredEvent",
    "UserProfileUpdatedEvent",
    "ProblemCreatedEvent",
    "ProblemUpdatedEvent",
    "ProblemPublishedEvent",
    "JudgeCaseAddedEvent",
    "JudgeCaseUpdatedEvent",
    "BookCreatedEvent",
    "BookUpdatedEvent",
    "BookPublishedEvent",
    # Services
    "UserDomainService",
    "ProblemDomainService",
    "BookDomainService",
    # Repository Interfaces
    "UserRepository",
    "ProblemRepository",
    "JudgeCaseRepository",
    "BookRepository",
    "ContentRepository",
    # Repository Implementations
    "UserRepositoryImpl",
    "ProblemRepositoryImpl",
    "JudgeCaseRepositoryImpl",
    "BookRepositoryImpl",
    "ContentRepositoryImpl",
]
