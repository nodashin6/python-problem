"""
Seed Use Case
シードユースケース

問題シードサービスとジャッジシードサービスを協調させてデータシードを実行
"""

import logging
from typing import Any, Dict, List, Optional

from ..domain.services import ProblemSeedService, JudgeSeedService
from ..domain.value_objects import SeedResult, SeedStatistics, TestCaseFileResult
from ..sample_data import (
    SAMPLE_BOOKS,
    SAMPLE_PROBLEMS,
    SAMPLE_SUBMISSIONS,
    SAMPLE_CASE_FILES,
    SAMPLE_JUDGE_CASES,
)

logger = logging.getLogger(__name__)


class SeedUseCase:
    """シード処理を統合管理するユースケース"""

    def __init__(
        self,
        problem_seed_service: ProblemSeedService,
        judge_seed_service: Optional[JudgeSeedService] = None,
    ):
        """
        Args:
            problem_seed_service: 問題シードサービス
            judge_seed_service: ジャッジシードサービス（オプション）
        """
        self.problem_seed_service = problem_seed_service
        self.judge_seed_service = judge_seed_service

    async def seed_complete_dataset(
        self,
        clear_existing: bool = False,
        custom_data: Optional[Dict[str, List[Dict[str, Any]]]] = None,
        create_test_files: bool = False,
        test_files_directory: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        完全なデータセットをシード
        
        Args:
            clear_existing: 既存データをクリアするか
            custom_data: カスタムデータ（省略時はサンプルデータを使用）
            create_test_files: テストケースファイルを作成するか
            test_files_directory: テストファイル作成ディレクトリ
            
        Returns:
            Dict: シード結果の詳細
        """
        logger.info("🚀 Starting complete dataset seeding...")
        
        results = {
            "success": True,
            "problem_domain": {},
            "judge_domain": {},
            "test_files": {},
            "errors": []
        }

        try:
            # 1. 既存データクリア
            if clear_existing:
                clear_result = await self._clear_all_data()
                if not clear_result["success"]:
                    results["errors"].extend(clear_result["errors"])

            # 2. カスタムデータまたはデフォルトデータを取得
            data = self._prepare_seed_data(custom_data)

            # 3. 問題ドメインのシード
            problem_results = await self._seed_problem_domain(
                books_data=data["books"],
                problems_data=data["problems"]
            )
            results["problem_domain"] = problem_results

            # 4. ジャッジドメインのシード
            if self.judge_seed_service:
                judge_results = await self._seed_judge_domain(
                    submissions_data=data["submissions"],
                    test_cases_data=data["test_cases"],
                    create_test_files=create_test_files,
                    test_files_directory=test_files_directory
                )
                results["judge_domain"] = judge_results

            # 5. 全体的な成功判定
            results["success"] = (
                problem_results["success"] and
                (not self.judge_seed_service or results["judge_domain"]["success"])
            )

            if results["success"]:
                logger.info("✅ Complete dataset seeding finished successfully!")
            else:
                logger.warning("⚠️ Dataset seeding completed with some issues")

        except Exception as e:
            error_msg = f"Complete dataset seeding failed: {e}"
            logger.error(error_msg)
            results["success"] = False
            results["errors"].append(error_msg)

        return results

    async def seed_problems_only(
        self,
        books_data: Optional[List[Dict[str, Any]]] = None,
        problems_data: Optional[List[Dict[str, Any]]] = None,
        overwrite_existing: bool = False,
    ) -> Dict[str, Any]:
        """
        問題データのみをシード
        
        Args:
            books_data: 問題集データ
            problems_data: 問題データ  
            overwrite_existing: 既存データを上書きするか
            
        Returns:
            Dict: シード結果
        """
        logger.info("📚 Starting problems-only seeding...")
        
        books = books_data or SAMPLE_BOOKS
        problems = problems_data or SAMPLE_PROBLEMS
        
        return await self._seed_problem_domain(books, problems, overwrite_existing)

    async def seed_judge_only(
        self,
        submissions_data: Optional[List[Dict[str, Any]]] = None,
        test_cases_data: Optional[List[Dict[str, Any]]] = None,
        create_test_files: bool = False,
        test_files_directory: Optional[str] = None,
        overwrite_existing: bool = False,
    ) -> Dict[str, Any]:
        """
        ジャッジデータのみをシード
        
        Args:
            submissions_data: 提出データ
            test_cases_data: テストケースデータ
            create_test_files: テストファイルを作成するか
            test_files_directory: テストファイル作成ディレクトリ
            overwrite_existing: 既存データを上書きするか
            
        Returns:
            Dict: シード結果
        """
        if not self.judge_seed_service:
            logger.warning("⚠️ Judge seed service not available")
            return {"success": False, "error": "Judge seed service not available"}

        logger.info("⚖️ Starting judge-only seeding...")
        
        submissions = submissions_data or SAMPLE_SUBMISSIONS
        test_cases = test_cases_data or SAMPLE_CASE_FILES
        
        return await self._seed_judge_domain(
            submissions, test_cases, create_test_files, 
            test_files_directory, overwrite_existing
        )

    async def get_comprehensive_statistics(self) -> Dict[str, Any]:
        """包括的な統計情報を取得"""
        logger.info("📊 Gathering comprehensive statistics...")
        
        stats = {
            "success": True,
            "problem_domain": {},
            "judge_domain": {},
            "errors": []
        }

        try:
            # 問題ドメイン統計
            problem_stats = await self.problem_seed_service.get_problem_statistics()
            stats["problem_domain"] = {
                "books_total": problem_stats.books_total,
                "books_by_difficulty": problem_stats.books_by_difficulty,
                "problems_total": problem_stats.problems_total,
                "problems_by_difficulty": problem_stats.problems_by_difficulty,
                "problems_by_status": problem_stats.problems_by_status,
            }

            # ジャッジドメイン統計
            if self.judge_seed_service:
                judge_stats = await self.judge_seed_service.get_judge_statistics()
                stats["judge_domain"] = judge_stats

        except Exception as e:
            error_msg = f"Failed to gather statistics: {e}"
            logger.error(error_msg)
            stats["success"] = False
            stats["errors"].append(error_msg)

        return stats

    async def _seed_problem_domain(
        self, 
        books_data: List[Dict[str, Any]], 
        problems_data: List[Dict[str, Any]],
        overwrite_existing: bool = False
    ) -> Dict[str, Any]:
        """問題ドメインをシード"""
        logger.info("📚 Seeding problem domain...")
        
        try:
            # Books
            books_result = await self.problem_seed_service.seed_books(
                books_data, overwrite_existing
            )
            
            # Problems
            problems_result = await self.problem_seed_service.seed_problems(
                problems_data, overwrite_existing
            )

            success = books_result.is_successful and problems_result.is_successful
            
            return {
                "success": success,
                "books": {
                    "total": books_result.total_processed,
                    "created": books_result.created_count,
                    "updated": books_result.updated_count,
                    "skipped": books_result.skipped_count,
                    "errors": books_result.errors,
                },
                "problems": {
                    "total": problems_result.total_processed,
                    "created": problems_result.created_count,
                    "updated": problems_result.updated_count,
                    "skipped": problems_result.skipped_count,
                    "errors": problems_result.errors,
                }
            }

        except Exception as e:
            error_msg = f"Problem domain seeding failed: {e}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }

    async def _seed_judge_domain(
        self,
        submissions_data: List[Dict[str, Any]],
        test_cases_data: List[Dict[str, Any]],
        create_test_files: bool = False,
        test_files_directory: Optional[str] = None,
        overwrite_existing: bool = False
    ) -> Dict[str, Any]:
        """ジャッジドメインをシード"""
        if not self.judge_seed_service:
            return {"success": False, "error": "Judge service not available"}

        logger.info("⚖️ Seeding judge domain...")
        
        try:
            # Submissions
            submissions_result = await self.judge_seed_service.seed_submissions(
                submissions_data, overwrite_existing
            )
            
            # Test Case Files
            test_files_result = await self.judge_seed_service.seed_test_case_files(
                test_cases_data, create_test_files, test_files_directory
            )

            success = submissions_result.is_successful and test_files_result.is_successful

            return {
                "success": success,
                "submissions": {
                    "total": submissions_result.total_processed,
                    "created": submissions_result.created_count,
                    "updated": submissions_result.updated_count,
                    "skipped": submissions_result.skipped_count,
                    "errors": submissions_result.errors,
                },
                "test_files": {
                    "total": test_files_result.total_files,
                    "created": test_files_result.created_count,
                    "created_files": test_files_result.created_files,
                    "base_directory": test_files_result.base_directory,
                    "errors": test_files_result.errors,
                }
            }

        except Exception as e:
            error_msg = f"Judge domain seeding failed: {e}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }

    async def _clear_all_data(self) -> Dict[str, Any]:
        """全データをクリア"""
        logger.info("🧹 Clearing all data...")
        
        results = {
            "success": True,
            "errors": []
        }

        try:
            # ジャッジデータクリア
            if self.judge_seed_service:
                judge_clear = await self.judge_seed_service.clear_judge_data()
                if not judge_clear.is_successful:
                    results["errors"].extend(judge_clear.errors)

            # 問題データクリア
            problem_clear = await self.problem_seed_service.clear_problem_data()
            if not problem_clear.is_successful:
                results["errors"].extend(problem_clear.errors)

            results["success"] = len(results["errors"]) == 0

        except Exception as e:
            error_msg = f"Failed to clear data: {e}"
            logger.error(error_msg)
            results["success"] = False
            results["errors"].append(error_msg)

        return results

    def _prepare_seed_data(self, custom_data: Optional[Dict[str, List[Dict[str, Any]]]]) -> Dict[str, List[Dict[str, Any]]]:
        """シード用データを準備"""
        if custom_data:
            return {
                "books": custom_data.get("books", SAMPLE_BOOKS),
                "problems": custom_data.get("problems", SAMPLE_PROBLEMS),
                "submissions": custom_data.get("submissions", SAMPLE_SUBMISSIONS),
                "test_cases": custom_data.get("test_cases", SAMPLE_CASE_FILES),
                "judge_cases": custom_data.get("judge_cases", SAMPLE_JUDGE_CASES),
            }
        else:
            return {
                "books": SAMPLE_BOOKS,
                "problems": SAMPLE_PROBLEMS,
                "submissions": SAMPLE_SUBMISSIONS,
                "test_cases": SAMPLE_CASE_FILES,
                "judge_cases": SAMPLE_JUDGE_CASES,
            }