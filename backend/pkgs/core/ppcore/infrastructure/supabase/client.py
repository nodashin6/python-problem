from supabase import Client
from supabase import create_client as __create_client

from src.env import EnvSettings


def create_client() -> Client:
    """
    Supabaseクライアントを作成する関数
    """
    env = EnvSettings()
    url: str = env.supabase_url
    key: str = env.supabase_anon_key
    return __create_client(url, key)
