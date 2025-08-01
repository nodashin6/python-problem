"""
Seed Facade
シードファサード

外部からのシード機能へのシンプルなインターフェース
"""

import logging
from typing import Any, Dict, List, Optional

from ppprob.domain.repositories import BookRepositoryBase, ProblemRepositoryBase
from ppjudg.domain.repositories import SubmissionRepositoryBase

from ..domain.services import ProblemSeedService, JudgeSeedService
from ..usecase import SeedUseCase

logger = logging.getLogger(__name__)


class SeedFacade:
    """シード機能の統合ファサード"""

    def __init__(
        self,
        book_repository: BookRepositoryBase,
        problem_repository: ProblemRepositoryBase,
        submission_repository: Optional[SubmissionRepositoryBase] = None,
    ):
        """
        Args:
            book_repository: 問題集リポジトリ
            problem_repository: 問題リポジトリ
            submission_repository: 提出リポジトリ（オプション）
        """
        self.problem_seed_service = ProblemSeedService(
            book_repository=book_repository,
            problem_repository=problem_repository,
        )
        
        self.judge_seed_service = None
        if submission_repository:
            self.judge_seed_service = JudgeSeedService(
                submission_repository=submission_repository,
            )
        
        self.seed_usecase = SeedUseCase(
            problem_seed_service=self.problem_seed_service,
            judge_seed_service=self.judge_seed_service,
        )

    async def seed_all(
        self,
        clear_existing: bool = False,
        create_test_files: bool = False,
        custom_data: Optional[Dict[str, List[Dict[str, Any]]]] = None,
    ) -> Dict[str, Any]:
        """
        全データをシード（シンプルインターフェース）
        
        Args:
            clear_existing: 既存データをクリアするか
            create_test_files: テストケースファイルを作成するか
            custom_data: カスタムデータ
            
        Returns:
            Dict: シード結果
        """
        logger.info("🚀 Starting complete seeding via facade...")
        
        return await self.seed_usecase.seed_complete_dataset(
            clear_existing=clear_existing,
            custom_data=custom_data,
            create_test_files=create_test_files,
        )

    async def seed_problems_only(
        self,
        custom_books: Optional[List[Dict[str, Any]]] = None,
        custom_problems: Optional[List[Dict[str, Any]]] = None,
        overwrite_existing: bool = False,
    ) -> Dict[str, Any]:
        """
        問題データのみをシード
        
        Args:
            custom_books: カスタム問題集データ
            custom_problems: カスタム問題データ
            overwrite_existing: 既存データを上書きするか
            
        Returns:
            Dict: シード結果
        """
        logger.info("📚 Starting problems-only seeding via facade...")
        
        return await self.seed_usecase.seed_problems_only(
            books_data=custom_books,
            problems_data=custom_problems,
            overwrite_existing=overwrite_existing,
        )

    async def get_statistics(self) -> Dict[str, Any]:
        """統計情報を取得"""
        return await self.seed_usecase.get_comprehensive_statistics()

    async def verify_data(self) -> Dict[str, Any]:
        """データを検証"""
        return await self.get_statistics()


# ファクトリー関数
def create_seed_facade(
    book_repository: BookRepositoryBase,
    problem_repository: ProblemRepositoryBase,
    submission_repository: Optional[SubmissionRepositoryBase] = None,
) -> SeedFacade:
    """シードファサードを作成"""
    return SeedFacade(
        book_repository=book_repository,
        problem_repository=problem_repository,
        submission_repository=submission_repository,
    )