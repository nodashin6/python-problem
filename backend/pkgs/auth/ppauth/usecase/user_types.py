from datetime import datetime
from uuid import UUID

from pydddi import IUseCaseResult

from ..domain.entities import UserEntity
from ..domain.entities.enums import UserRole
from ..domain.models import User


class UserResult(IUseCaseResult):
    """Result for user operations"""

    user: UserEntity


class UserListResult(IUseCaseResult):
    """Result for user list operations"""

    users: list[UserResult]


class ReadUserListResult(IUseCaseResult):
    """Result for reading user lists with pagination"""

    users: list[UserResult]
    total_count: int


class UserAggregateResult(IUseCaseResult):
    """Result for user aggregate operations"""

    user: User


class UserAggregateListResult(IUseCaseResult):
    """Result for user aggregate list operations"""

    users: list[UserAggregateResult]
