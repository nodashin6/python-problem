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
    ProblemContent,
    EditorialContent,
    Tag,
    ProblemMetadata,
    UserProfile,
)

# Domain Events - temporarily disabled until events.py is created
# from .domain.events import (
#     UserRegisteredEvent,
#     UserProfileUpdatedEvent,
#     ProblemCreatedEvent,
#     ProblemUpdatedEvent,
#     ProblemPublishedEvent,
#     JudgeCaseAddedEvent,
#     JudgeCaseUpdatedEvent,
#     BookCreatedEvent,
#     BookUpdatedEvent,
#     BookPublishedEvent,
# )

# Domain Services
from .domain.services import UserDomainService, ProblemDomainService, BookDomainService

# Repository Interfaces
from .domain.repositories import (
    UserRepository,
    ProblemRepository,
    JudgeCaseRepository,
    BookRepository,
    ProblemContentRepository,
    EditorialRepository,
)

# Infrastructure Implementations
from .infra import (
    UserRepositoryImpl,
    ProblemRepositoryImpl,
    JudgeCaseRepositoryImpl,
    BookRepositoryImpl,
    # ContentRepositoryImpl,  # temporarily disabled
)

__all__ = [
    # Models
    "User",
    "Problem",
    "JudgeCase",
    "Book",
    "ProblemContent",
    "EditorialContent",
    "Tag",
    "ProblemMetadata",
    "UserProfile",
    # Events - temporarily disabled
    # "UserRegisteredEvent",
    # "UserProfileUpdatedEvent",
    # "ProblemCreatedEvent",
    # "ProblemUpdatedEvent",
    # "ProblemPublishedEvent",
    # "JudgeCaseAddedEvent",
    # "JudgeCaseUpdatedEvent",
    # "BookCreatedEvent",
    # "BookUpdatedEvent",
    # "BookPublishedEvent",
    # Services
    "UserDomainService",
    "ProblemDomainService",
    "BookDomainService",
    # Repository Interfaces
    "UserRepository",
    "ProblemRepository",
    "JudgeCaseRepository",
    "BookRepository",
    "ProblemContentRepository",
    "EditorialRepository",
    # Repository Implementations
    "UserRepositoryImpl",
    "ProblemRepositoryImpl",
    "JudgeCaseRepositoryImpl",
    "BookRepositoryImpl",
    # "ContentRepositoryImpl",  # temporarily disabled
]
