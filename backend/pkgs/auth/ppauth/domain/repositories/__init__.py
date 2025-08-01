"""Repository interfaces for auth domain"""

from .user_aggregate_read_repository import UserAggregateReadRepository
from .user_repository import UserRepository

__all__ = [
    "UserRepository",
    "UserAggregateReadRepository",
]
