from ..client import Client, create_client
from ....domain.protocols.database_protocols import DatabaseConfig


def get_client(config: DatabaseConfig) -> Client:
    """
    Get an instance of the Supabase client.

    Args:
        config: Database configuration containing URL and key

    Returns:
        Client: An instance of the Supabase client.
    """
    return create_client(config)


__all__ = [
    "get_client",
    "Client",
]
