from supabase import create_client, Client
from src.env import EnvSettings


def create_supabase_client() -> Client:
    """
    Supabaseクライアントを作成する関数
    """
    env = EnvSettings()
    url: str = env.supabase_url
    key: str = env.supabase_anon_key
    return create_client(url, key)
