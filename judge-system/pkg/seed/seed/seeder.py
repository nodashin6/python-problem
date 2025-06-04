"""
Database seeder for test data
テストデータ用のデータベースシーダー
"""

import asyncio
from typing import Optional
from supabase import create_client, Client
from src.env import SUPABASE_URL, SUPABASE_SERVICE_KEY
from src.seed.sample_data import get_all_sample_data
import logging

logger = logging.getLogger(__name__)


class DatabaseSeeder:
    """データベースにテストデータを投入するクラス"""

    def __init__(self):
        """Supabaseクライアントを初期化"""
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

    async def seed_all(self, clear_existing: bool = False) -> bool:
        """すべてのテストデータを投入"""
        try:
            if clear_existing:
                await self.clear_all_data()

            sample_data = get_all_sample_data()

            # Core domainのデータを順番に投入
            await self._seed_core_domain(sample_data)

            # Judge domainのデータを投入
            await self._seed_judge_domain(sample_data)

            logger.info("✅ All sample data seeded successfully!")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to seed data: {e}")
            return False

    async def _seed_core_domain(self, sample_data: dict) -> None:
        """Core domainのデータを投入"""
        logger.info("🌱 Seeding Core domain data...")

        # 1. Users (必須: 他のテーブルの参照先)
        if sample_data.get("users"):
            result = (
                self.supabase.table("users")
                .upsert(sample_data["users"], on_conflict="id")
                .execute()
            )
            logger.info(f"Users seeded: {len(result.data)} records")

        # 2. User roles
        if sample_data.get("user_roles"):
            result = (
                self.supabase.table("user_roles")
                .upsert(sample_data["user_roles"], on_conflict="user_id")
                .execute()
            )
            logger.info(f"User roles seeded: {len(result.data)} records")

        # 3. Books
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
            # problem_contentsテーブルはprimary keyがproblem_id + languageなので、
            # より細かい制御が必要
            for content in sample_data["problem_contents"]:
                try:
                    result = (
                        self.supabase.table("problem_contents")
                        .upsert(content, on_conflict="problem_id,language")
                        .execute()
                    )
                except Exception as e:
                    logger.warning(f"Problem content upsert failed, trying insert: {e}")
                    # upsertが失敗した場合はinsertを試行
                    result = (
                        self.supabase.table("problem_contents")
                        .insert(content)
                        .execute()
                    )
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
            # judge_casesはauto incrementのidがあるので、既存データをチェック
            for judge_case in sample_data["judge_cases"]:
                try:
                    # 同じproblem_id, input_id, output_idの組み合わせがあるかチェック
                    existing = (
                        self.supabase.table("judge_cases")
                        .select("id")
                        .eq("problem_id", judge_case["problem_id"])
                        .eq("input_id", judge_case["input_id"])
                        .eq("output_id", judge_case["output_id"])
                        .execute()
                    )

                    if not existing.data:
                        # 存在しない場合のみinsert
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
            result = (
                self.supabase.table("submissions")
                .upsert(sample_data["submissions"], on_conflict="id")
                .execute()
            )
            logger.info(f"Submissions seeded: {len(result.data)} records")

    async def clear_all_data(self) -> None:
        """すべてのテストデータをクリア"""
        logger.info("🧹 Clearing existing data...")

        # Judge domainから先にクリア（外部キー制約のため）
        judge_tables = [
            "judge_case_result_metadata",
            "judge_case_results",
            "judge_processes",
            "submissions",
        ]

        for table in judge_tables:
            try:
                # より安全なクリア方法：全件削除
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

    async def verify_data(self) -> dict:
        """データ投入後の検証"""
        logger.info("🔍 Verifying seeded data...")

        verification = {}
        tables = [
            "users",
            "user_roles",
            "books",
            "problems",
            "problem_contents",
            "case_files",
            "judge_cases",
            "submissions",
        ]

        for table in tables:
            try:
                result = self.supabase.table(table).select("*", count="exact").execute()
                verification[table] = {
                    "count": result.count,
                    "sample": (
                        result.data[:2] if result.data else []
                    ),  # 最初の2件を確認用に取得
                }
                logger.info(f"{table}: {result.count} records")
            except Exception as e:
                logger.error(f"Failed to verify {table}: {e}")
                verification[table] = {"error": str(e)}

        return verification


async def seed_database(clear_existing: bool = False) -> bool:
    """データベースにサンプルデータを投入"""
    seeder = DatabaseSeeder()
    return await seeder.seed_all(clear_existing=clear_existing)


async def verify_database() -> dict:
    """データベースのデータを検証"""
    seeder = DatabaseSeeder()
    return await seeder.verify_data()


if __name__ == "__main__":
    # 直接実行時の処理
    async def main():
        logging.basicConfig(level=logging.INFO)
        logger.info("🚀 Starting database seeding...")

        # 既存データをクリアしてシード
        success = await seed_database(clear_existing=True)

        if success:
            # データ検証
            verification = await verify_database()
            logger.info("📊 Verification complete!")
            for table, info in verification.items():
                if "error" in info:
                    logger.error(f"{table}: {info['error']}")
                else:
                    logger.info(f"{table}: {info['count']} records")
        else:
            logger.error("❌ Seeding failed!")

    asyncio.run(main())
