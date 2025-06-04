"""
Integration tests configuration
統合テスト設定
"""

import pytest
import asyncio
from typing import AsyncGenerator
from supabase import create_client, Client
from src.env import SUPABASE_URL, SUPABASE_SERVICE_KEY
from src.seed.seeder import DatabaseSeeder


@pytest.fixture(scope="session")
def event_loop():
    """セッション全体で同じイベントループを使用"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def supabase_client() -> AsyncGenerator[Client, None]:
    """Supabaseクライアントのフィクスチャ"""
    client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    yield client


@pytest.fixture(scope="function")
async def clean_database(supabase_client: Client) -> AsyncGenerator[Client, None]:
    """各テスト実行前にデータベースをクリーンアップ"""
    seeder = DatabaseSeeder()

    # テスト前にクリーンアップ
    await seeder.clear_all_data()

    yield supabase_client

    # テスト後にもクリーンアップ
    await seeder.clear_all_data()


@pytest.fixture(scope="function")
async def seeded_database(clean_database: Client) -> AsyncGenerator[Client, None]:
    """テストデータがシードされたデータベース"""
    seeder = DatabaseSeeder()

    # テストデータを投入
    success = await seeder.seed_all(clear_existing=False)
    assert success, "Failed to seed test data"

    yield clean_database


class IntegrationTestBase:
    """統合テストのベースクラス"""

    @pytest.fixture(autouse=True)
    def setup(self, seeded_database: Client):
        """各テストで自動的に実行される設定"""
        self.supabase = seeded_database

    async def get_user_by_email(self, email: str):
        """メールアドレスでユーザーを取得"""
        result = self.supabase.table("users").select("*").eq("email", email).execute()
        return result.data[0] if result.data else None

    async def get_problem_by_title(self, title: str):
        """タイトルで問題を取得"""
        result = (
            self.supabase.table("problems").select("*").eq("title", title).execute()
        )
        return result.data[0] if result.data else None

    async def get_submission_by_id(self, submission_id: str):
        """IDで提出を取得"""
        result = (
            self.supabase.table("submissions")
            .select("*")
            .eq("id", submission_id)
            .execute()
        )
        return result.data[0] if result.data else None

    async def create_test_submission(
        self, problem_id: str, user_id: str, source_code: str, language: str = "python"
    ) -> str:
        """テスト用の提出を作成"""
        submission_data = {
            "problem_id": problem_id,
            "user_id": user_id,
            "language": language,
            "source_code": source_code,
            "status": "pending",
        }

        result = self.supabase.table("submissions").insert(submission_data).execute()
        return result.data[0]["id"]
