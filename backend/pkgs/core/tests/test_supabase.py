from supabase import Client

from ppcore.infrastructure.supabase.client import create_client


def test_create_client():
    """
    Supabaseクライアントが正しく作成されるかテスト
    """
    from ppcore.domain.protocols.database_protocols import DatabaseConfig
    
    config = DatabaseConfig(
        url="https://test.supabase.co",
        key="test_key",
        timeout=30,
        max_connections=10
    )
    client: Client = create_client(config)
    assert client is not None
    assert isinstance(client, Client)
