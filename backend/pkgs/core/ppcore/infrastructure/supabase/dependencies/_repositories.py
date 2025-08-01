from ..repositories import SupabaseRepository
from ....domain.protocols.database_protocols import DatabaseConfig
from . import _clients


def get_supabase_repository(
    config: DatabaseConfig,
) -> SupabaseRepository:
    """
    Get an instance of the Supabase repository.
    
    Args:
        config: Database configuration for creating client

    Returns:
        SupabaseRepository: An instance of the Supabase repository.
    """
    client = _clients.get_client(config)
    return SupabaseRepository(supabase_client=client)
