from typing import Annotated

from fastapi import Depends

from ..repositories import (
    UserAggregateReadRepositoryImpl,
    UserRepositoryImpl,
)
from . import _clients


def get_user_repository(
    client: Annotated[_clients.Client, Depends(_clients.get_client)],
) -> UserRepositoryImpl:
    return UserRepositoryImpl(client=client)


def get_user_aggregate_read_repository(
    client: Annotated[_clients.Client, Depends(_clients.get_client)],
) -> UserAggregateReadRepositoryImpl:
    return UserAggregateReadRepositoryImpl(client=client)


__all__ = [
    "UserRepositoryImpl",
    "UserAggregateReadRepositoryImpl",
    "get_user_repository",
    "get_user_aggregate_read_repository",
]
