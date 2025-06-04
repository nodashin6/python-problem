"""
Test-specific seeder that handles auth.users dependency
auth.usersに依存しないテスト専用のシーダー
"""

import asyncio
from typing import Optional
from supabase import create_client, Client
from src.env import SUPABASE_URL, SUPABASE_SERVICE_KEY
from src.seed.sample_data import get_all_sample_data
import logging

logger = logging.getLogger(__name__)


class TestDatabaseSeeder:
    """テスト環境用のデータベースシーダー（auth.users依存を回避）"""

    def __init__(self):
        """Supabaseクライアントを初期化"""
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

    async def seed_test_data(self, clear_existing: bool = False) -> bool:
        """テストデータを投入（auth.users制約を回避）"""
        try:
            if clear_existing:
                await self._clear_test_data()

            # まずauth.usersにテストユーザーを作成
            await self._create_auth_users()

            sample_data = get_all_sample_data()

            # Core domainのデータを順番に投入
            await self._seed_core_domain(sample_data)

            # Judge domainのデータを投入
            await self._seed_judge_domain(sample_data)

            logger.info("✅ All test data seeded successfully!")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to seed test data: {e}")
            return False

    async def _create_auth_users(self) -> None:
        """auth.usersテーブルにテストユーザーを作成"""
        logger.info("👤 Creating auth users...")

        # Service roleで直接auth.usersに挿入
        # 注意: 実際のプロダクションでは推奨されない方法
        test_users = [
            {
                "id": "550e8400-e29b-41d4-a716-446655440020",
                "email": "test.user@example.com",
                "encrypted_password": "$2a$10$test.password.hash",  # ダミーハッシュ
                "email_confirmed_at": "2025-05-27T00:00:00.000Z",
                "created_at": "2025-05-27T00:00:00.000Z",
                "updated_at": "2025-05-27T00:00:00.000Z",
                "raw_app_meta_data": "{}",
                "raw_user_meta_data": "{}",
            },
            {
                "id": "550e8400-e29b-41d4-a716-446655440021",
                "email": "admin@example.com",
                "encrypted_password": "$2a$10$admin.password.hash",  # ダミーハッシュ
                "email_confirmed_at": "2025-05-27T00:00:00.000Z",
                "created_at": "2025-05-27T00:00:00.000Z",
                "updated_at": "2025-05-27T00:00:00.000Z",
                "raw_app_meta_data": "{}",
                "raw_user_meta_data": "{}",
            },
        ]

        for user in test_users:
            try:
                # auth schemaへの直接挿入を試行
                # これはテスト環境でのみ使用
                result = (
                    self.supabase.postgrest.schema("auth")
                    .table("users")
                    .upsert(user, on_conflict="id")
                    .execute()
                )
                logger.info(f"Created auth user: {user['email']}")
            except Exception as e:
                logger.warning(f"Failed to create auth user {user['email']}: {e}")
                # auth.usersへの直接アクセスが失敗した場合は、
                # public.usersの外部キー制約を一時的に無効化することを検討

    async def _seed_core_domain(self, sample_data: dict) -> None:
        """Core domainのデータを投入（auth.users制約考慮）"""
        logger.info("🌱 Seeding Core domain data...")

        # 1. Users (auth.usersが存在することを前提)
        if sample_data.get("users"):
            try:
                result = (
                    self.supabase.table("users")
                    .upsert(sample_data["users"], on_conflict="id")
                    .execute()
                )
                logger.info(f"Users seeded: {len(result.data)} records")
            except Exception as e:
                logger.error(f"Failed to seed users: {e}")
                # Usersの投入に失敗した場合、他のテーブルも失敗する可能性が高い
                logger.info("Attempting to seed without users table...")

        # 2. User roles
        if sample_data.get("user_roles"):
            try:
                result = (
                    self.supabase.table("user_roles")
                    .upsert(sample_data["user_roles"], on_conflict="user_id")
                    .execute()
                )
                logger.info(f"User roles seeded: {len(result.data)} records")
            except Exception as e:
                logger.warning(f"Failed to seed user roles: {e}")

        # 3. Books (ユーザーに依存しない)
        if sample_data.get("books"):
            result = (
                self.supabase.table("books")
                .upsert(sample_data["books"], on_conflict="id")
                .execute()
            )
            logger.info(f"Books seeded: {len(result.data)} records")

        # 4. Problems
        if sample_data.get("problems"):
            result = (
                self.supabase.table("problems")
                .upsert(sample_data["problems"], on_conflict="id")
                .execute()
            )
            logger.info(f"Problems seeded: {len(result.data)} records")

        # 5. Problem contents
        if sample_data.get("problem_contents"):
            for content in sample_data["problem_contents"]:
                try:
                    result = (
                        self.supabase.table("problem_contents")
                        .upsert(content, on_conflict="problem_id,language")
                        .execute()
                    )
                except Exception as e:
                    logger.warning(f"Problem content upsert failed: {e}")
            logger.info(
                f"Problem contents seeded: {len(sample_data['problem_contents'])} records"
            )

        # 6. Case files
        if sample_data.get("case_files"):
            result = (
                self.supabase.table("case_files")
                .upsert(sample_data["case_files"], on_conflict="id")
                .execute()
            )
            logger.info(f"Case files seeded: {len(result.data)} records")

        # 7. Judge cases
        if sample_data.get("judge_cases"):
            for judge_case in sample_data["judge_cases"]:
                try:
                    existing = (
                        self.supabase.table("judge_cases")
                        .select("id")
                        .eq("problem_id", judge_case["problem_id"])
                        .eq("input_id", judge_case["input_id"])
                        .eq("output_id", judge_case["output_id"])
                        .execute()
                    )

                    if not existing.data:
                        result = (
                            self.supabase.table("judge_cases")
                            .insert(judge_case)
                            .execute()
                        )
                except Exception as e:
                    logger.warning(f"Judge case insert failed: {e}")
            logger.info(
                f"Judge cases seeded: {len(sample_data['judge_cases'])} records"
            )

    async def _seed_judge_domain(self, sample_data: dict) -> None:
        """Judge domainのデータを投入"""
        logger.info("⚖️ Seeding Judge domain data...")

        # 1. Submissions
        if sample_data.get("submissions"):
            try:
                result = (
                    self.supabase.table("submissions")
                    .upsert(sample_data["submissions"], on_conflict="id")
                    .execute()
                )
                logger.info(f"Submissions seeded: {len(result.data)} records")
            except Exception as e:
                logger.warning(f"Failed to seed submissions: {e}")

    async def _clear_test_data(self) -> None:
        """テストデータをクリア"""
        logger.info("🧹 Clearing test data...")

        # Judge domainから先にクリア
        judge_tables = [
            "judge_case_result_metadata",
            "judge_case_results",
            "judge_processes",
            "submissions",
        ]

        for table in judge_tables:
            try:
                result = (
                    self.supabase.table(table)
                    .delete()
                    .gte("created_at", "1900-01-01")
                    .execute()
                )
                logger.info(
                    f"Cleared {table}: {len(result.data) if result.data else 0} records"
                )
            except Exception as e:
                logger.warning(f"Failed to clear {table}: {e}")

        # Core domainをクリア
        core_tables = [
            "user_problem_status",
            "user_stats",
            "user_roles",
            "judge_cases",
            "case_files",
            "editorial_contents",
            "editorials",
            "problem_contents",
            "problems",
            "books",
            "users",
        ]

        for table in core_tables:
            try:
                result = (
                    self.supabase.table(table)
                    .delete()
                    .gte("created_at", "1900-01-01")
                    .execute()
                )
                logger.info(
                    f"Cleared {table}: {len(result.data) if result.data else 0} records"
                )
            except Exception as e:
                logger.warning(f"Failed to clear {table}: {e}")

        # auth.usersもクリア（テスト用）
        try:
            result = (
                self.supabase.postgrest.schema("auth")
                .table("users")
                .delete()
                .gte("created_at", "1900-01-01")
                .execute()
            )
            logger.info(
                f"Cleared auth.users: {len(result.data) if result.data else 0} records"
            )
        except Exception as e:
            logger.warning(f"Failed to clear auth.users: {e}")


async def seed_test_database(clear_existing: bool = False) -> bool:
    """テスト用データベースにサンプルデータを投入"""
    seeder = TestDatabaseSeeder()
    return await seeder.seed_test_data(clear_existing=clear_existing)


if __name__ == "__main__":

    async def main():
        logging.basicConfig(level=logging.INFO)
        logger.info("🚀 Starting test database seeding...")

        success = await seed_test_database(clear_existing=True)

        if success:
            logger.info("✅ Test seeding complete!")
        else:
            logger.error("❌ Test seeding failed!")

    asyncio.run(main())
