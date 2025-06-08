from supabase import Client
from ppcore.infra.supabase.client import create_supabase_client


def test_create_supabase_client():
    """
    Supabaseクライアントが正しく作成されるかテスト
    """
    client: Client = create_supabase_client()
    assert client is not None
    assert isinstance(client, Client)
