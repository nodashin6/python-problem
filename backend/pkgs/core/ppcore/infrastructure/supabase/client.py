from supabase import Client
from supabase import create_client as __create_client

from ...domain.protocols.database_protocols import DatabaseConfig


def create_client(config: DatabaseConfig) -> Client:
    """
    Supabaseクライアントを作成する関数
    """
    return __create_client(config.url, config.key)
