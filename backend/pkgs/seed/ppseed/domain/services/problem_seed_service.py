"""
Problem Seed Domain Service
問題シードドメインサービス

問題ドメイン（ppprob）に関連するシード処理のビジネスロジック
"""

import logging
from typing import Any, Dict, List

from ppprob.domain.repositories import BookRepositoryBase, ProblemRepositoryBase
from ..value_objects import SeedResult, SeedStatistics

logger = logging.getLogger(__name__)


class ProblemSeedService:
    """問題シード処理のドメインサービス"""

    def __init__(
        self,
        book_repository: BookRepositoryBase,
        problem_repository: ProblemRepositoryBase,
    ):
        self.book_repository = book_repository
        self.problem_repository = problem_repository

    async def seed_books(
        self, 
        books_data: List[Dict[str, Any]],
        overwrite_existing: bool = False
    ) -> SeedResult:
        """
        問題集データをシード
        
        Args:
            books_data: 問題集データのリスト
            overwrite_existing: 既存データを上書きするか
            
        Returns:
            SeedResult: シード結果
        """
        logger.info(f"📚 Seeding {len(books_data)} books...")
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        errors = []

        for book_data in books_data:
            try:
                result = await self._seed_single_book(book_data, overwrite_existing)
                
                if result.action == "created":
                    created_count += 1
                elif result.action == "updated":
                    updated_count += 1
                else:
                    skipped_count += 1
                    
            except Exception as e:
                error_msg = f"Failed to seed book '{book_data.get('title', 'Unknown')}': {e}"
                logger.error(error_msg)
                errors.append(error_msg)

        return SeedResult(
            entity_type="books",
            total_processed=len(books_data),
            created_count=created_count,
            updated_count=updated_count,
            skipped_count=skipped_count,
            errors=errors,
            success=len(errors) == 0
        )

    async def seed_problems(
        self, 
        problems_data: List[Dict[str, Any]],
        overwrite_existing: bool = False
    ) -> SeedResult:
        """
        問題データをシード
        
        Args:
            problems_data: 問題データのリスト
            overwrite_existing: 既存データを上書きするか
            
        Returns:
            SeedResult: シード結果
        """
        logger.info(f"📋 Seeding {len(problems_data)} problems...")
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        errors = []

        for problem_data in problems_data:
            try:
                result = await self._seed_single_problem(problem_data, overwrite_existing)
                
                if result.action == "created":
                    created_count += 1
                elif result.action == "updated":
                    updated_count += 1
                else:
                    skipped_count += 1
                    
            except Exception as e:
                error_msg = f"Failed to seed problem '{problem_data.get('title', 'Unknown')}': {e}"
                logger.error(error_msg)
                errors.append(error_msg)

        return SeedResult(
            entity_type="problems",
            total_processed=len(problems_data),
            created_count=created_count,
            updated_count=updated_count,
            skipped_count=skipped_count,
            errors=errors,
            success=len(errors) == 0
        )

    async def get_problem_statistics(self) -> SeedStatistics:
        """問題データの統計情報を取得"""
        logger.info("📊 Gathering problem statistics...")
        
        try:
            # Books統計
            published_books = await self.book_repository.find_published()
            total_books = await self.book_repository.count_published()
            
            # Problems統計  
            published_problems = await self.problem_repository.find_published()
            
            books_by_difficulty = {}
            for book in published_books:
                level = getattr(book, 'difficulty_level', 'unknown')
                books_by_difficulty[level] = books_by_difficulty.get(level, 0) + 1

            problems_by_difficulty = {}
            problems_by_status = {}
            for problem in published_problems:
                level = getattr(problem, 'difficulty_level', 'unknown')
                status = getattr(problem, 'status', 'unknown')
                problems_by_difficulty[level] = problems_by_difficulty.get(level, 0) + 1
                problems_by_status[status] = problems_by_status.get(status, 0) + 1

            return SeedStatistics(
                books_total=total_books,
                books_by_difficulty=books_by_difficulty,
                problems_total=len(published_problems),
                problems_by_difficulty=problems_by_difficulty,
                problems_by_status=problems_by_status,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Failed to gather statistics: {e}")
            return SeedStatistics(
                books_total=0,
                books_by_difficulty={},
                problems_total=0,
                problems_by_difficulty={},
                problems_by_status={},
                success=False,
                error=str(e)
            )

    async def clear_problem_data(self) -> SeedResult:
        """問題関連データをクリア"""
        logger.info("🧹 Clearing problem data...")
        
        try:
            # 依存関係順でクリア（問題 → 問題集）
            # await self.problem_repository.delete_all()  # 実装されている場合
            await self.book_repository.delete_all()

            return SeedResult(
                entity_type="problem_data",
                total_processed=0,
                created_count=0,
                updated_count=0,
                skipped_count=0,
                errors=[],
                success=True
            )
            
        except Exception as e:
            error_msg = f"Failed to clear problem data: {e}"
            logger.error(error_msg)
            return SeedResult(
                entity_type="problem_data",
                total_processed=0,
                created_count=0,
                updated_count=0,
                skipped_count=0,
                errors=[error_msg],
                success=False
            )

    async def _seed_single_book(self, book_data: Dict[str, Any], overwrite: bool) -> Any:
        """単一の問題集をシード"""
        from ppprob.domain.repositories.book_repository import CreateBookSchema
        
        # 既存チェック
        existing = await self.book_repository.find_by_title(book_data["title"])
        
        if existing and not overwrite:
            return type('Result', (), {'action': 'skipped'})()
        
        if existing and overwrite:
            # 更新処理（実装依存）
            return type('Result', (), {'action': 'updated'})()
        else:
            # 新規作成
            create_schema = CreateBookSchema(
                title=book_data["title"],
                author_id=book_data.get("author_id"),
                published_at=book_data.get("published_at"),
                archived_at=book_data.get("archived_at"),
            )
            await self.book_repository.create(create_schema)
            return type('Result', (), {'action': 'created'})()

    async def _seed_single_problem(self, problem_data: Dict[str, Any], overwrite: bool) -> Any:
        """単一の問題をシード"""
        from ppprob.domain.repositories.problem_repository import CreateProblemSchema
        from ppprob.domain.enums import Language
        
        # 既存チェック
        existing = await self.problem_repository.find_by_title(problem_data["title"])
        
        if existing and not overwrite:
            return type('Result', (), {'action': 'skipped'})()
        
        if existing and overwrite:
            # 更新処理（実装依存）
            return type('Result', (), {'action': 'updated'})()
        else:
            # 新規作成
            create_schema = CreateProblemSchema(
                book_id=problem_data["book_id"],
                title=problem_data["title"],
                description=problem_data["description"],
                tags=problem_data.get("tags", []),
                published_at=problem_data.get("published_at"),
                content_markdown=problem_data.get("content_markdown"),
                language=Language.JAPANESE,
            )
            await self.problem_repository.create(create_schema)
            return type('Result', (), {'action': 'created'})()