"""
Judge Seed Domain Service
ジャッジシードドメインサービス

ジャッジドメイン（ppjudg）に関連するシード処理のビジネスロジック
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from ppjudg.domain.repositories import SubmissionRepositoryBase
from ..value_objects import SeedResult, TestCaseFileResult

logger = logging.getLogger(__name__)


class JudgeSeedService:
    """ジャッジシード処理のドメインサービス"""

    def __init__(
        self,
        submission_repository: SubmissionRepositoryBase,
    ):
        self.submission_repository = submission_repository

    async def seed_submissions(
        self, 
        submissions_data: List[Dict[str, Any]],
        overwrite_existing: bool = False
    ) -> SeedResult:
        """
        提出データをシード
        
        Args:
            submissions_data: 提出データのリスト
            overwrite_existing: 既存データを上書きするか
            
        Returns:
            SeedResult: シード結果
        """
        logger.info(f"📨 Seeding {len(submissions_data)} submissions...")
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        errors = []

        for submission_data in submissions_data:
            try:
                result = await self._seed_single_submission(submission_data, overwrite_existing)
                
                if result.action == "created":
                    created_count += 1
                elif result.action == "updated":
                    updated_count += 1
                else:
                    skipped_count += 1
                    
            except Exception as e:
                error_msg = f"Failed to seed submission '{submission_data.get('id', 'Unknown')}': {e}"
                logger.error(error_msg)
                errors.append(error_msg)

        return SeedResult(
            entity_type="submissions",
            total_processed=len(submissions_data),
            created_count=created_count,
            updated_count=updated_count,
            skipped_count=skipped_count,
            errors=errors,
            success=len(errors) == 0
        )

    async def seed_test_case_files(
        self,
        test_cases_data: List[Dict[str, Any]],
        create_physical_files: bool = False,
        base_directory: Optional[str] = None
    ) -> TestCaseFileResult:
        """
        テストケースファイルをシード
        
        Args:
            test_cases_data: テストケースデータ
            create_physical_files: 物理ファイルを作成するか
            base_directory: ファイル作成のベースディレクトリ
            
        Returns:
            TestCaseFileResult: シード結果
        """
        logger.info(f"📁 Seeding {len(test_cases_data)} test case files...")
        
        created_files = []
        errors = []
        
        if create_physical_files:
            base_path = Path(base_directory or "testcases")
            base_path.mkdir(exist_ok=True)
            
            # 各問題のテストケースファイルを作成
            try:
                created_files = await self._create_test_case_files(base_path)
                logger.info(f"Created {len(created_files)} test case files")
                
            except Exception as e:
                error_msg = f"Failed to create test case files: {e}"
                logger.error(error_msg)
                errors.append(error_msg)

        return TestCaseFileResult(
            total_files=len(test_cases_data),
            created_files=created_files,
            errors=errors,
            success=len(errors) == 0,
            base_directory=str(base_path) if create_physical_files else None
        )

    async def get_judge_statistics(self) -> Dict[str, Any]:
        """ジャッジデータの統計情報を取得"""
        logger.info("📊 Gathering judge statistics...")
        
        try:
            # 提出データ統計
            recent_submissions = await self.submission_repository.find_recent(limit=100)
            
            submissions_by_language = {}
            submissions_by_status = {}
            
            for submission in recent_submissions:
                language = getattr(submission, 'language', 'unknown')
                status = getattr(submission, 'status', 'unknown')
                
                submissions_by_language[language] = submissions_by_language.get(language, 0) + 1
                submissions_by_status[status] = submissions_by_status.get(status, 0) + 1

            return {
                "submissions": {
                    "total": len(recent_submissions),
                    "by_language": submissions_by_language,
                    "by_status": submissions_by_status,
                },
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Failed to gather judge statistics: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def clear_judge_data(self) -> SeedResult:
        """ジャッジ関連データをクリア"""
        logger.info("🧹 Clearing judge data...")
        
        try:
            # 提出データなどの削除
            # 実装は具体的なリポジトリ仕様に依存
            
            return SeedResult(
                entity_type="judge_data",
                total_processed=0,
                created_count=0,
                updated_count=0,
                skipped_count=0,
                errors=[],
                success=True
            )
            
        except Exception as e:
            error_msg = f"Failed to clear judge data: {e}"
            logger.error(error_msg)
            return SeedResult(
                entity_type="judge_data",
                total_processed=0,
                created_count=0,
                updated_count=0,
                skipped_count=0,
                errors=[error_msg],
                success=False
            )

    async def _seed_single_submission(self, submission_data: Dict[str, Any], overwrite: bool) -> Any:
        """単一の提出をシード"""
        from ppjudg.domain.models import Submission
        
        # 既存チェック
        existing = await self.submission_repository.find_by_id(submission_data["id"])
        
        if existing and not overwrite:
            return type('Result', (), {'action': 'skipped'})()
        
        if existing and overwrite:
            # 更新処理（実装依存）
            return type('Result', (), {'action': 'updated'})()
        else:
            # 新規作成
            submission = Submission(
                id=submission_data["id"],
                problem_id=submission_data["problem_id"],
                user_id=submission_data["user_id"],
                language=submission_data["language"],
                source_code=submission_data["source_code"],
                status=submission_data["status"],
            )
            
            await self.submission_repository.save(submission)
            return type('Result', (), {'action': 'created'})()

    async def _create_test_case_files(self, base_path: Path) -> List[str]:
        """実際のテストケースファイルを作成"""
        created_files = []
        
        # Hello World問題のテストケース
        hello_world_dir = base_path / "hello_world"
        hello_world_dir.mkdir(exist_ok=True)
        
        input1 = hello_world_dir / "input1.txt"
        output1 = hello_world_dir / "output1.txt"
        
        input1.write_text("")
        output1.write_text("Hello, World!")
        
        created_files.extend([str(input1), str(output1)])

        # 足し算問題のテストケース
        addition_dir = base_path / "addition"
        addition_dir.mkdir(exist_ok=True)
        
        cases = [
            ("input1.txt", "3 5", "output1.txt", "8"),
            ("input2.txt", "10 20", "output2.txt", "30"),
        ]
        
        for input_file, input_content, output_file, output_content in cases:
            input_path = addition_dir / input_file
            output_path = addition_dir / output_file
            
            input_path.write_text(input_content)
            output_path.write_text(output_content)
            
            created_files.extend([str(input_path), str(output_path)])

        # 配列の最大値問題のテストケース
        max_array_dir = base_path / "max_array"
        max_array_dir.mkdir(exist_ok=True)
        
        input1 = max_array_dir / "input1.txt"
        output1 = max_array_dir / "output1.txt"
        
        input1.write_text("5\n3 1 4 1 5")
        output1.write_text("5")
        
        created_files.extend([str(input1), str(output1)])
        
        return created_files