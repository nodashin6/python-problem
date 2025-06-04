"""
Core domain layer exports
"""

# Models
from .models import (
    Entity,
    ValueObject,
    User,
    Problem,
    Book,
    JudgeCase,
    ProblemContent,
    Editorial,
    EditorialContent,
    Tag,
    ProblemMetadata,
    UserProfile,
    # Events
    ProblemCreated,
    ProblemPublished,
    JudgeCaseAdded,
    UserRegistered,
)

# Repositories
from .repositories import (
    UserRepository,
    ProblemRepository,
    JudgeCaseRepository,
    BookRepository,
    ProblemContentRepository,
    EditorialRepository,
    EditorialContentRepository,
)

# Services
from .services import UserDomainService, ProblemDomainService, BookDomainService

__all__ = [
    # Base classes
    "Entity",
    "ValueObject",
    # Entities
    "User",
    "Problem",
    "Book",
    "JudgeCase",
    "ProblemContent",
    "Editorial",
    "EditorialContent",
    # Value Objects
    "Tag",
    "ProblemMetadata",
    "UserProfile",
    # Events
    "ProblemCreated",
    "ProblemPublished",
    "JudgeCaseAdded",
    "UserRegistered",
    # Repository interfaces
    "UserRepository",
    "ProblemRepository",
    "JudgeCaseRepository",
    "BookRepository",
    "ProblemContentRepository",
    "EditorialRepository",
    "EditorialContentRepository",
    # Domain services
    "UserDomainService",
    "ProblemDomainService",
    "BookDomainService",
]
