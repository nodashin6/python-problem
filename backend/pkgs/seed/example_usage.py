"""
Example Usage of ppseed with DDD Structure
ppseedのDDD構造での使用例
"""

import asyncio
import logging
from typing import Optional

# DIコンテナ（実際の実装では適切なDIライブラリを使用）
from ppprob.infrastructure.supabase.repositories import (
    BookRepositoryImpl,
    ProblemRepositoryImpl,
)
from ppjudg.infrastructure.repositories import SubmissionRepositoryImpl

# ppseed DDD components
from ppseed import (
    SeedFacade,
    SeedUseCase,
    ProblemSeedService,
    JudgeSeedService,
    create_seed_facade,
)

logger = logging.getLogger(__name__)


async def example_facade_usage():
    """ファサードを使用したシンプルな例"""
    logger.info("🎯 Example: Using SeedFacade...")
    
    # リポジトリインスタンス作成（実際はDIコンテナから取得）
    book_repo = BookRepositoryImpl()
    problem_repo = ProblemRepositoryImpl()
    submission_repo = SubmissionRepositoryImpl()
    
    # ファサード作成
    facade = create_seed_facade(
        book_repository=book_repo,
        problem_repository=problem_repo,
        submission_repository=submission_repo,
    )
    
    # 全データをシード
    result = await facade.seed_all(
        clear_existing=True,
        create_test_files=True,
    )
    
    if result["success"]:
        logger.info("✅ Facade seeding completed successfully!")
        
        # 統計情報取得
        stats = await facade.get_statistics()
        logger.info(f"📊 Books: {stats['problem_domain']['books_total']}")
        logger.info(f"📊 Problems: {stats['problem_domain']['problems_total']}")
    else:
        logger.error("❌ Facade seeding failed!")
        logger.error(f"Errors: {result.get('errors', [])}")


async def example_usecase_usage():
    """ユースケースを直接使用する例"""
    logger.info("🎯 Example: Using SeedUseCase directly...")
    
    # リポジトリインスタンス作成
    book_repo = BookRepositoryImpl()
    problem_repo = ProblemRepositoryImpl()
    submission_repo = SubmissionRepositoryImpl()
    
    # ドメインサービス作成
    problem_service = ProblemSeedService(
        book_repository=book_repo,
        problem_repository=problem_repo,
    )
    
    judge_service = JudgeSeedService(
        submission_repository=submission_repo,
    )
    
    # ユースケース作成
    usecase = SeedUseCase(
        problem_seed_service=problem_service,
        judge_seed_service=judge_service,
    )
    
    # カスタムデータでシード
    custom_data = {
        "books": [
            {
                "id": "custom-book-1",
                "title": "カスタム問題集",
                "description": "独自の問題集",
                "difficulty_level": "intermediate",
                "author_id": None,
            }
        ],
        "problems": [
            {
                "id": "custom-problem-1", 
                "book_id": "custom-book-1",
                "title": "カスタム問題",
                "description": "独自問題",
                "difficulty_level": "intermediate",
                "tags": ["custom", "example"],
            }
        ]
    }
    
    result = await usecase.seed_complete_dataset(
        clear_existing=True,
        custom_data=custom_data,
        create_test_files=False,
    )
    
    if result["success"]:
        logger.info("✅ UseCase seeding completed successfully!")
        
        # 詳細結果表示
        if "problem_domain" in result:
            books_info = result["problem_domain"]["books"]
            logger.info(f"📚 Books - Created: {books_info['created']}, Total: {books_info['total']}")
            
            problems_info = result["problem_domain"]["problems"]
            logger.info(f"📋 Problems - Created: {problems_info['created']}, Total: {problems_info['total']}")


async def example_service_usage():
    """ドメインサービスを直接使用する例"""
    logger.info("🎯 Example: Using Domain Services directly...")
    
    # リポジトリインスタンス作成
    book_repo = BookRepositoryImpl()
    problem_repo = ProblemRepositoryImpl()
    
    # 問題シードサービス作成
    service = ProblemSeedService(
        book_repository=book_repo,
        problem_repository=problem_repo,
    )
    
    # 問題集のみシード
    books_data = [
        {
            "title": "サービス直接使用例",
            "description": "ドメインサービスを直接使用",
            "difficulty_level": "beginner",
            "author_id": None,
        }
    ]
    
    result = await service.seed_books(books_data, overwrite_existing=False)
    
    if result.is_successful:
        logger.info(f"✅ Service seeding - Created: {result.created_count}, Skipped: {result.skipped_count}")
        
        # 統計情報取得
        stats = await service.get_problem_statistics()
        if stats.is_valid:
            logger.info(f"📊 Total books: {stats.books_total}")
            logger.info(f"📊 Books by difficulty: {stats.books_by_difficulty}")
    else:
        logger.error(f"❌ Service seeding failed: {result.errors}")


async def example_problems_only():
    """問題データのみをシードする例"""
    logger.info("🎯 Example: Problems-only seeding...")
    
    # リポジトリ作成
    book_repo = BookRepositoryImpl()
    problem_repo = ProblemRepositoryImpl()
    
    # ファサード作成（ジャッジサービスなし）
    facade = SeedFacade(
        book_repository=book_repo,
        problem_repository=problem_repo,
        submission_repository=None,  # ジャッジデータは不要
    )
    
    # 問題データのみシード
    result = await facade.seed_problems_only(overwrite_existing=True)
    
    if result["success"]:
        logger.info("✅ Problems-only seeding completed!")
        logger.info(f"📚 {result['books']['created']} books created")
        logger.info(f"📋 {result['problems']['created']} problems created")


async def main():
    """メイン実行例"""
    logging.basicConfig(level=logging.INFO)
    
    logger.info("🚀 Starting ppseed DDD structure examples...")
    
    try:
        # 1. ファサード使用例（推奨）
        await example_facade_usage()
        
        # 2. ユースケース直接使用例
        await example_usecase_usage()
        
        # 3. ドメインサービス直接使用例
        await example_service_usage()
        
        # 4. 問題データのみの例
        await example_problems_only()
        
        logger.info("🎉 All examples completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Example execution failed: {e}")


if __name__ == "__main__":
    print("⚠️ This is just an example file.")
    print("Actual repositories would need to be properly configured.")
    print("Run with: python -c 'import asyncio; from example_usage import main; asyncio.run(main())'")
    
    # Uncomment to run examples (requires proper repository setup)
    # asyncio.run(main())