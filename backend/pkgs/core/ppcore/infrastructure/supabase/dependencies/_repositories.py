from pydoc import cli
from typing import Annotated

from fastapi import Depends

from ..repositories import SupabaseRepositoryImpl
from . import _clients


def get_supabase_repository(
    client: Annotated[_clients.Client, Depends(_clients.get_client)],
) -> SupabaseRepositoryImpl:
    """
    Get an instance of the Supabase repository.

    Returns:
        SupabaseRepositoryImpl: An instance of the Supabase repository.
    """
    return SupabaseRepositoryImpl(client=client)  # Assuming the constructor does not require parameters
