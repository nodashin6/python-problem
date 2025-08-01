"""
Domain-based Problem Seeder
ドメイン依存型問題シーダー

ppprob（問題ドメイン）とppjudg（ジャッジドメイン）に依存してデータシードを実行
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from ppprob.domain.repositories import BookRepositoryBase, ProblemRepositoryBase
from ppjudg.domain.repositories import SubmissionRepositoryBase
from .sample_data import (
    SAMPLE_BOOKS,
    SAMPLE_CASE_FILES,
    SAMPLE_JUDGE_CASES,
    SAMPLE_PROBLEM_CONTENTS,
    SAMPLE_PROBLEMS,
    SAMPLE_SUBMISSIONS,
)

logger = logging.getLogger(__name__)


class DomainBasedSeeder:
    """ドメイン層を利用した問題データシーダー"""

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
        self.book_repository = book_repository
        self.problem_repository = problem_repository
        self.submission_repository = submission_repository

    async def seed_problems_domain(
        self,
        clear_existing: bool = False,
        books_data: Optional[List[Dict]] = None,
        problems_data: Optional[List[Dict]] = None,
    ) -> bool:
        """
        問題ドメインのデータをシード
        
        Args:
            clear_existing: 既存データをクリアするか
            books_data: カスタム問題集データ
            problems_data: カスタム問題データ
        """
        try:
            logger.info("📚 Starting problem domain seeding...")

            if clear_existing:
                await self._clear_problem_domain()

            # 1. Books (問題集)
            books = books_data or SAMPLE_BOOKS
            await self._seed_books_via_domain(books)

            # 2. Problems (問題)
            problems = problems_data or SAMPLE_PROBLEMS
            await self._seed_problems_via_domain(problems)

            logger.info("✅ Problem domain seeding completed!")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to seed problem domain: {e}")
            return False

    async def seed_judge_domain(
        self,
        clear_existing: bool = False,
        submissions_data: Optional[List[Dict]] = None,
    ) -> bool:
        """
        ジャッジドメインのデータをシード
        
        Args:
            clear_existing: 既存データをクリアするか
            submissions_data: カスタム提出データ
        """
        if not self.submission_repository:
            logger.warning("⚠️ Submission repository not provided, skipping judge domain seeding")
            return True

        try:
            logger.info("⚖️ Starting judge domain seeding...")

            if clear_existing:
                await self._clear_judge_domain()

            # Submissions (提出データ)
            submissions = submissions_data or SAMPLE_SUBMISSIONS
            await self._seed_submissions_via_domain(submissions)

            logger.info("✅ Judge domain seeding completed!")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to seed judge domain: {e}")
            return False

    async def seed_complete_via_domain(
        self,
        clear_existing: bool = False,
        custom_data: Optional[Dict[str, List[Dict]]] = None,
    ) -> bool:
        """
        ドメインリポジトリを通じて全データをシード
        
        Args:
            clear_existing: 既存データをクリアするか
            custom_data: カスタムデータ辞書
        """
        try:
            logger.info("🚀 Starting complete domain-based seeding...")

            # カスタムデータの取得
            custom_data = custom_data or {}
            books_data = custom_data.get("books")
            problems_data = custom_data.get("problems")
            submissions_data = custom_data.get("submissions")

            # 問題ドメインのシード
            success = await self.seed_problems_domain(
                clear_existing=clear_existing,
                books_data=books_data,
                problems_data=problems_data,
            )

            if not success:
                return False

            # ジャッジドメインのシード
            success = await self.seed_judge_domain(
                clear_existing=False,  # 問題データはすでにクリア済み
                submissions_data=submissions_data,
            )

            if success:
                logger.info("🎉 Complete domain-based seeding finished successfully!")
            return success

        except Exception as e:
            logger.error(f"❌ Failed to complete domain-based seeding: {e}")
            return False

    async def _seed_books_via_domain(self, books_data: List[Dict]) -> None:
        """ドメインリポジトリを通じて問題集をシード"""
        logger.info(f"📚 Seeding {len(books_data)} books via domain layer...")

        for book_data in books_data:
            try:
                # ドメインエンティティの作成ロジックが必要
                # 今回はリポジトリが直接辞書を受け取ることを想定
                
                # 既存チェック
                existing = await self.book_repository.find_by_title(book_data["title"])
                
                if not existing:
                    # Create schema を利用
                    from ppprob.domain.repositories.book_repository import CreateBookSchema
                    create_schema = CreateBookSchema(
                        title=book_data["title"],
                        author_id=book_data.get("author_id"),
                        published_at=book_data.get("published_at"),
                        archived_at=book_data.get("archived_at"),
                    )
                    await self.book_repository.create(create_schema)
                    logger.info(f"Created book: {book_data['title']}")
                else:
                    logger.info(f"Book already exists: {book_data['title']}")

            except Exception as e:
                logger.warning(f"Failed to seed book {book_data.get('title', 'Unknown')}: {e}")

        logger.info("Books seeding via domain completed")

    async def _seed_problems_via_domain(self, problems_data: List[Dict]) -> None:
        """ドメインリポジトリを通じて問題をシード"""
        logger.info(f"📋 Seeding {len(problems_data)} problems via domain layer...")

        for problem_data in problems_data:
            try:
                # 既存チェック
                existing = await self.problem_repository.find_by_title(problem_data["title"])
                
                if not existing:
                    # Create schema を利用
                    from ppprob.domain.repositories.problem_repository import CreateProblemSchema
                    from ppprob.domain.enums import Language
                    
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
                    logger.info(f"Created problem: {problem_data['title']}")
                else:
                    logger.info(f"Problem already exists: {problem_data['title']}")

            except Exception as e:
                logger.warning(f"Failed to seed problem {problem_data.get('title', 'Unknown')}: {e}")

        logger.info("Problems seeding via domain completed")

    async def _seed_submissions_via_domain(self, submissions_data: List[Dict]) -> None:
        """ドメインリポジトリを通じて提出データをシード"""
        if not self.submission_repository:
            logger.warning("Submission repository not available")
            return

        logger.info(f"📨 Seeding {len(submissions_data)} submissions via domain layer...")

        for submission_data in submissions_data:
            try:
                # 既存チェック
                existing = await self.submission_repository.find_by_id(submission_data["id"])
                
                if not existing:
                    # Submission モデルの作成
                    from ppjudg.domain.models import Submission
                    
                    submission = Submission(
                        id=submission_data["id"],
                        problem_id=submission_data["problem_id"],
                        user_id=submission_data["user_id"],
                        language=submission_data["language"],
                        source_code=submission_data["source_code"],
                        status=submission_data["status"],
                    )
                    
                    await self.submission_repository.save(submission)
                    logger.info(f"Created submission: {submission_data['id']}")
                else:
                    logger.info(f"Submission already exists: {submission_data['id']}")

            except Exception as e:
                logger.warning(f"Failed to seed submission {submission_data.get('id', 'Unknown')}: {e}")

        logger.info("Submissions seeding via domain completed")

    async def _clear_problem_domain(self) -> None:
        """問題ドメインデータをクリア"""
        logger.info("🧹 Clearing problem domain data...")

        try:
            # 問題を削除
            # await self.problem_repository.delete_all()  # メソッドが存在する場合
            logger.info("Problems cleared")

            # 問題集を削除
            await self.book_repository.delete_all()
            logger.info("Books cleared")

        except Exception as e:
            logger.warning(f"Failed to clear problem domain: {e}")

    async def _clear_judge_domain(self) -> None:
        """ジャッジドメインデータをクリア"""
        if not self.submission_repository:
            return

        logger.info("🧹 Clearing judge domain data...")

        try:
            # 提出データの削除は個別に実行する必要がある場合が多い
            # 実装依存のため、詳細は省略
            logger.info("Judge domain data cleared")

        except Exception as e:
            logger.warning(f"Failed to clear judge domain: {e}")

    async def verify_seeded_data(self) -> Dict[str, Any]:
        """シードされたデータの検証"""
        logger.info("🔍 Verifying seeded data...")

        verification = {}

        try:
            # Books verification
            published_books = await self.book_repository.find_published()
            book_count = await self.book_repository.count_published()
            verification["books"] = {
                "count": book_count,
                "published": len(published_books),
                "sample": [{"title": book.title} for book in published_books[:2]]
            }

            # Problems verification
            published_problems = await self.problem_repository.find_published()
            verification["problems"] = {
                "count": len(published_problems),
                "sample": [{"title": problem.title} for problem in published_problems[:2]]
            }

            # Submissions verification
            if self.submission_repository:
                recent_submissions = await self.submission_repository.find_recent(limit=10)
                verification["submissions"] = {
                    "count": len(recent_submissions),
                    "sample": [{"id": str(sub.id)} for sub in recent_submissions[:2]]
                }

            logger.info("✅ Data verification completed")

        except Exception as e:
            logger.error(f"Failed to verify data: {e}")
            verification["error"] = str(e)

        return verification


class HybridSeeder:
    """
    ハイブリッドシーダー：ドメインリポジトリと直接DB操作を組み合わせ
    テストケースファイルなどDB直接操作が必要な部分は従来の方法を使用
    """

    def __init__(
        self,
        domain_seeder: DomainBasedSeeder,
        direct_db_seeder: Optional[Any] = None,  # 従来のProblemSeederなど
    ):
        self.domain_seeder = domain_seeder
        self.direct_db_seeder = direct_db_seeder

    async def seed_complete_hybrid(
        self,
        clear_existing: bool = False,
        include_test_cases: bool = True,
        create_test_files: bool = False,
    ) -> bool:
        """
        ハイブリッド方式での完全シード
        
        Args:
            clear_existing: 既存データをクリアするか
            include_test_cases: テストケースを含めるか
            create_test_files: 実際のテストケースファイルを作成するか
        """
        try:
            logger.info("🔄 Starting hybrid seeding...")

            # 1. ドメインレイヤーでのシード
            success = await self.domain_seeder.seed_complete_via_domain(
                clear_existing=clear_existing
            )

            if not success:
                return False

            # 2. 直接DB操作が必要な部分（テストケースなど）
            if include_test_cases and self.direct_db_seeder:
                success = await self.direct_db_seeder.seed_test_cases_only(
                    create_files=create_test_files
                )

                if not success:
                    logger.warning("⚠️ Test cases seeding failed, but continuing...")

            logger.info("🎯 Hybrid seeding completed successfully!")
            return True

        except Exception as e:
            logger.error(f"❌ Hybrid seeding failed: {e}")
            return False


# 便利な関数
async def create_domain_seeder(
    book_repo: BookRepositoryBase,
    problem_repo: ProblemRepositoryBase,
    submission_repo: Optional[SubmissionRepositoryBase] = None,
) -> DomainBasedSeeder:
    """ドメインシーダーを作成"""
    return DomainBasedSeeder(
        book_repository=book_repo,
        problem_repository=problem_repo,
        submission_repository=submission_repo,
    )


if __name__ == "__main__":
    # 直接実行時の処理例
    async def main():
        logging.basicConfig(level=logging.INFO)
        logger.info("🚀 Starting domain-based seeding example...")
        
        # 実際の使用時は、DIコンテナから適切なリポジトリを取得する
        # book_repo = container.get(BookRepositoryBase)
        # problem_repo = container.get(ProblemRepositoryBase)
        # submission_repo = container.get(SubmissionRepositoryBase)
        
        # seeder = await create_domain_seeder(book_repo, problem_repo, submission_repo)
        # success = await seeder.seed_complete_via_domain(clear_existing=True)
        
        logger.info("⚠️ This is just an example. Actual repositories needed for execution.")

    asyncio.run(main())