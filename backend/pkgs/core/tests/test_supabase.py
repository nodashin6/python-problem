from supabase import Client

from ppcore.infrastructure.supabase.client import create_client


def test_create_client():
    """
    Supabaseクライアントが正しく作成されるかテスト
    """
    client: Client = create_client()
    assert client is not None
    assert isinstance(client, Client)
