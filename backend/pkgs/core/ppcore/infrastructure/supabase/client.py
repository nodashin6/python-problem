import os
import pathlib

from dotenv import load_dotenv
from supabase import Client, create_client as __create_client

from ...domain.protocols.database_protocols import DatabaseConfig


def create_client(config: DatabaseConfig = None) -> Client:
    """
    Supabaseクライアントを作成する関数
    configが指定されない場合は.envファイルから読み込む
    """
    if config is None:
        # .envファイルを読み込み (backend/ディレクトリから)
        backend_dir = pathlib.Path(__file__).parent.parent.parent.parent.parent
        env_path = backend_dir / ".env"
        load_dotenv(env_path)

        # 環境変数からConfigを作成 (テスト時はSERVICE_KEYを使用)
        service_key = os.getenv(
            "SUPABASE_SERVICE_KEY",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU",
        )
        anon_key = os.getenv(
            "SUPABASE_ANON_KEY",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0",
        )

        # テスト環境ではSERVICE_KEYを優先
        config = DatabaseConfig(
            url=os.getenv("SUPABASE_URL", "http://127.0.0.1:54221"),
            key=service_key if service_key else anon_key,
        )

    # Supabaseクライアントを最新のAPIで作成
    return __create_client(
        supabase_url=config.url,
        supabase_key=config.key,
    )
