from typing import Annotated

from fastapi import Depends

from ..repositories import (
    UserAggregateReadRepository,
    UserRepository,
)
from . import _clients


def get_user_repository(
    client: Annotated[_clients.Client, Depends(_clients.get_client)],
) -> UserRepository:
    return UserRepository(client=client)


def get_user_aggregate_read_repository(
    client: Annotated[_clients.Client, Depends(_clients.get_client)],
) -> UserAggregateReadRepository:
    return UserAggregateReadRepository(client=client)


__all__ = [
    "UserRepository",
    "UserAggregateReadRepository",
    "get_user_repository",
    "get_user_aggregate_read_repository",
]
