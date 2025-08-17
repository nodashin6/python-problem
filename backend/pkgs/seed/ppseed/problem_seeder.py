"""
Problems Data Seeder
問題データ専用シーダー

問題データの投入に特化したシーダー機能を提供します。
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from supabase import Client, create_client

from src.env import SUPABASE_SERVICE_KEY, SUPABASE_URL
from .sample_data import (
    SAMPLE_BOOKS,
    SAMPLE_CASE_FILES,
    SAMPLE_JUDGE_CASES,
    SAMPLE_PROBLEM_CONTENTS,
    SAMPLE_PROBLEMS,
)

logger = logging.getLogger(__name__)


class ProblemSeeder:
    """問題データ専用のシーダークラス"""

    def __init__(self):
        """Supabaseクライアントを初期化"""
        from supabase import ClientOptions
        options = ClientOptions()
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY, options=options)

    async def seed_problems_complete(
        self,
        clear_existing: bool = False,
        include_case_files: bool = True,
        create_test_case_files: bool = False,
    ) -> bool:
        """
        問題データの完全なシードを実行
        
        Args:
            clear_existing: 既存データをクリアするか
            include_case_files: ケースファイルも含めるか
            create_test_case_files: 実際のテストケースファイルを作成するか
        """
        try:
            logger.info("🎯 Starting complete problem seeding...")

            if clear_existing:
                await self.clear_problem_data()

            # 1. Books (問題集)
            await self._seed_books()

            # 2. Problem Headers (問題メタデータ)
            await self._seed_problem_headers()

            # 3. Problem Contents (問題内容)
            await self._seed_problem_contents()

            if include_case_files:
                # 4. Case Files (テストケースファイル)
                await self._seed_case_files()

                # 5. Judge Cases (ジャッジケース)
                await self._seed_judge_cases()

            if create_test_case_files:
                # 6. 実際のテストケースファイルを作成
                await self._create_test_case_files()

            logger.info("✅ Complete problem seeding finished successfully!")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to seed problems: {e}")
            return False

    async def seed_books_only(self, books_data: Optional[List[Dict]] = None) -> bool:
        """問題集のみをシード"""
        try:
            books = books_data or SAMPLE_BOOKS
            await self._seed_books(books)
            logger.info("✅ Books seeded successfully!")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to seed books: {e}")
            return False

    async def seed_problems_only(
        self, problems_data: Optional[List[Dict]] = None, contents_data: Optional[List[Dict]] = None
    ) -> bool:
        """問題データのみをシード（問題集は除く）"""
        try:
            problems = problems_data or SAMPLE_PROBLEMS
            contents = contents_data or SAMPLE_PROBLEM_CONTENTS

            await self._seed_problem_headers(problems)
            await self._seed_problem_contents(contents)

            logger.info("✅ Problems seeded successfully!")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to seed problems: {e}")
            return False

    async def seed_test_cases_only(
        self,
        case_files_data: Optional[List[Dict]] = None,
        judge_cases_data: Optional[List[Dict]] = None,
        create_files: bool = False,
    ) -> bool:
        """テストケースのみをシード"""
        try:
            case_files = case_files_data or SAMPLE_CASE_FILES
            judge_cases = judge_cases_data or SAMPLE_JUDGE_CASES

            await self._seed_case_files(case_files)
            await self._seed_judge_cases(judge_cases)

            if create_files:
                await self._create_test_case_files()

            logger.info("✅ Test cases seeded successfully!")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to seed test cases: {e}")
            return False

    async def _seed_books(self, books_data: Optional[List[Dict]] = None) -> None:
        """問題集データを投入"""
        books = books_data or SAMPLE_BOOKS
        logger.info(f"📚 Seeding {len(books)} books...")

        result = self.supabase.table("books").upsert(books, on_conflict="id").execute()
        logger.info(f"Books seeded: {len(result.data)} records")

    async def _seed_problem_headers(self, problems_data: Optional[List[Dict]] = None) -> None:
        """問題ヘッダーデータを投入"""
        problems = problems_data or SAMPLE_PROBLEMS
        logger.info(f"📋 Seeding {len(problems)} problem headers...")

        result = self.supabase.table("problem_headers").upsert(problems, on_conflict="id").execute()
        logger.info(f"Problem headers seeded: {len(result.data)} records")

    async def _seed_problem_contents(self, contents_data: Optional[List[Dict]] = None) -> None:
        """問題内容データを投入"""
        contents = contents_data or SAMPLE_PROBLEM_CONTENTS
        logger.info(f"📝 Seeding {len(contents)} problem contents...")

        for content in contents:
            try:
                result = (
                    self.supabase.table("problem_contents")
                    .upsert(content, on_conflict="problem_id,language")
                    .execute()
                )
            except Exception as e:
                logger.warning(f"Problem content upsert failed, trying insert: {e}")
                result = self.supabase.table("problem_contents").insert(content).execute()

        logger.info(f"Problem contents seeded: {len(contents)} records")

    async def _seed_case_files(self, case_files_data: Optional[List[Dict]] = None) -> None:
        """ケースファイルデータを投入"""
        case_files = case_files_data or SAMPLE_CASE_FILES
        logger.info(f"📁 Seeding {len(case_files)} case files...")

        result = self.supabase.table("case_files").upsert(case_files, on_conflict="id").execute()
        logger.info(f"Case files seeded: {len(result.data)} records")

    async def _seed_judge_cases(self, judge_cases_data: Optional[List[Dict]] = None) -> None:
        """ジャッジケースデータを投入"""
        judge_cases = judge_cases_data or SAMPLE_JUDGE_CASES
        logger.info(f"⚖️ Seeding {len(judge_cases)} judge cases...")

        for judge_case in judge_cases:
            try:
                # 同じ組み合わせがあるかチェック
                existing = (
                    self.supabase.table("judge_cases")
                    .select("id")
                    .eq("problem_id", judge_case["problem_id"])
                    .eq("input_id", judge_case["input_id"])
                    .eq("output_id", judge_case["output_id"])
                    .execute()
                )

                if not existing.data:
                    result = self.supabase.table("judge_cases").insert(judge_case).execute()
            except Exception as e:
                logger.warning(f"Judge case insert failed: {e}")

        logger.info(f"Judge cases seeded: {len(judge_cases)} records")

    async def _create_test_case_files(self) -> None:
        """実際のテストケースファイルを作成"""
        logger.info("🗂️ Creating actual test case files...")

        testcases_dir = Path("testcases")
        testcases_dir.mkdir(exist_ok=True)

        # Hello World問題のテストケース
        hello_world_dir = testcases_dir / "hello_world"
        hello_world_dir.mkdir(exist_ok=True)

        (hello_world_dir / "input1.txt").write_text("")
        (hello_world_dir / "output1.txt").write_text("Hello, World!")

        # 足し算問題のテストケース
        addition_dir = testcases_dir / "addition"
        addition_dir.mkdir(exist_ok=True)

        (addition_dir / "input1.txt").write_text("3 5")
        (addition_dir / "output1.txt").write_text("8")
        (addition_dir / "input2.txt").write_text("10 20")
        (addition_dir / "output2.txt").write_text("30")

        # 配列の最大値問題のテストケース
        max_array_dir = testcases_dir / "max_array"
        max_array_dir.mkdir(exist_ok=True)

        (max_array_dir / "input1.txt").write_text("5\n3 1 4 1 5")
        (max_array_dir / "output1.txt").write_text("5")

        logger.info("Test case files created successfully!")

    async def clear_problem_data(self) -> None:
        """問題関連データのみをクリア"""
        logger.info("🧹 Clearing problem-related data...")

        # 依存関係順でクリア
        tables_to_clear = [
            "judge_cases",
            "case_files",
            "problem_contents",
            "problem_headers",
            "books",
        ]

        for table in tables_to_clear:
            try:
                result = self.supabase.table(table).delete().gte("created_at", "1900-01-01").execute()
                logger.info(f"Cleared {table}: {len(result.data) if result.data else 0} records")
            except Exception as e:
                logger.warning(f"Failed to clear {table}: {e}")

    async def verify_problem_data(self) -> Dict[str, Any]:
        """問題データの検証"""
        logger.info("🔍 Verifying problem data...")

        verification = {}
        tables = ["books", "problem_headers", "problem_contents", "case_files", "judge_cases"]

        for table in tables:
            try:
                result = self.supabase.table(table).select("*", count="exact").execute()
                verification[table] = {
                    "count": result.count,
                    "sample": result.data[:2] if result.data else [],
                }
                logger.info(f"{table}: {result.count} records")
            except Exception as e:
                logger.error(f"Failed to verify {table}: {e}")
                verification[table] = {"error": str(e)}

        return verification

    async def get_problem_statistics(self) -> Dict[str, Any]:
        """問題データの統計情報を取得"""
        logger.info("📊 Gathering problem statistics...")

        stats = {}

        try:
            # 問題集統計
            books_result = self.supabase.table("books").select("difficulty_level", count="exact").execute()
            books_by_difficulty = {}
            for book in books_result.data:
                level = book.get("difficulty_level", "unknown")
                books_by_difficulty[level] = books_by_difficulty.get(level, 0) + 1

            stats["books"] = {"total": books_result.count, "by_difficulty": books_by_difficulty}

            # 問題統計
            problems_result = (
                self.supabase.table("problem_headers").select("difficulty_level,status", count="exact").execute()
            )
            problems_by_difficulty = {}
            problems_by_status = {}

            for problem in problems_result.data:
                level = problem.get("difficulty_level", "unknown")
                status = problem.get("status", "unknown")
                problems_by_difficulty[level] = problems_by_difficulty.get(level, 0) + 1
                problems_by_status[status] = problems_by_status.get(status, 0) + 1

            stats["problems"] = {
                "total": problems_result.count,
                "by_difficulty": problems_by_difficulty,
                "by_status": problems_by_status,
            }

            # テストケース統計
            judge_cases_result = (
                self.supabase.table("judge_cases").select("is_sample,judge_case_type", count="exact").execute()
            )
            cases_by_type = {}
            sample_cases = 0

            for case in judge_cases_result.data:
                case_type = case.get("judge_case_type", "unknown")
                cases_by_type[case_type] = cases_by_type.get(case_type, 0) + 1
                if case.get("is_sample"):
                    sample_cases += 1

            stats["judge_cases"] = {
                "total": judge_cases_result.count,
                "sample_cases": sample_cases,
                "by_type": cases_by_type,
            }

            logger.info("📈 Statistics gathered successfully!")

        except Exception as e:
            logger.error(f"Failed to gather statistics: {e}")
            stats["error"] = str(e)

        return stats


# 便利な関数のエクスポート
async def seed_problems_complete(clear_existing: bool = False) -> bool:
    """問題データの完全なシードを実行"""
    seeder = ProblemSeeder()
    return await seeder.seed_problems_complete(clear_existing=clear_existing)


async def seed_problems_only() -> bool:
    """問題データのみをシード"""
    seeder = ProblemSeeder()
    return await seeder.seed_problems_only()


async def verify_problems() -> Dict[str, Any]:
    """問題データの検証"""
    seeder = ProblemSeeder()
    return await seeder.verify_problem_data()


async def get_problems_stats() -> Dict[str, Any]:
    """問題データの統計情報を取得"""
    seeder = ProblemSeeder()
    return await seeder.get_problem_statistics()


if __name__ == "__main__":
    # 直接実行時の処理
    async def main():
        logging.basicConfig(level=logging.INFO)
        logger.info("🚀 Starting problem seeding...")

        seeder = ProblemSeeder()

        # 完全なシード実行
        success = await seeder.seed_problems_complete(clear_existing=True, create_test_case_files=True)

        if success:
            # データ検証
            verification = await seeder.verify_problem_data()
            logger.info("📊 Verification complete!")

            # 統計情報表示
            stats = await seeder.get_problem_statistics()
            logger.info("📈 Statistics:")
            for category, info in stats.items():
                if isinstance(info, dict) and "total" in info:
                    logger.info(f"  {category}: {info['total']} records")
        else:
            logger.error("❌ Problem seeding failed!")

    asyncio.run(main())