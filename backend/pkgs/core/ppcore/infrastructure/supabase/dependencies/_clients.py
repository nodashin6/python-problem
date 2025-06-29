from ..client import Client, create_client


def get_client() -> Client:
    """
    Get an instance of the Supabase client.

    Returns:
        Client: An instance of the Supabase client.
    """
    return create_client()


__all__ = [
    "get_client",
    "Client",
]
