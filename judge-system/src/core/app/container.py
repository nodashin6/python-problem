"""
Core Domain Dependency Injection Container
コアドメイン依存性注入コンテナ
"""

from dependency_injector import containers, providers
from dependency_injector.providers import Factory, Singleton
import logging

from supabase import create_client, AsyncClient
from ..infra.repositories.supabase_repositories import (
    SupabaseBookRepository,
    SupabaseProblemRepository,
    SupabaseJudgeCaseRepository,
    SupabaseUserProblemStatusRepository,
)
from .services import (
    BookApplicationService,
    ProblemApplicationService,
    JudgeCaseApplicationService,
    UserProblemStatusApplicationService,
)
from ...shared.config import settings

logger = logging.getLogger(__name__)


class CoreApplicationContainer(containers.DeclarativeContainer):
    """コアドメインアプリケーションコンテナ"""

    # Configure provider
    config = providers.Configuration()

    # Supabase client
    supabase_client = Singleton(
        create_client,
        supabase_url=settings.SUPABASE_URL,
        supabase_key=settings.SUPABASE_ANON_KEY,
    )

    # Repository layer
    book_repository = Factory(SupabaseBookRepository, supabase_client=supabase_client)

    problem_repository = Factory(
        SupabaseProblemRepository, supabase_client=supabase_client
    )

    judge_case_repository = Factory(
        SupabaseJudgeCaseRepository, supabase_client=supabase_client
    )

    user_problem_status_repository = Factory(
        SupabaseUserProblemStatusRepository, supabase_client=supabase_client
    )

    # Application services
    book_service = Factory(BookApplicationService, book_repository=book_repository)

    problem_service = Factory(
        ProblemApplicationService,
        problem_repository=problem_repository,
        judge_case_repository=judge_case_repository,
    )

    judge_case_service = Factory(
        JudgeCaseApplicationService, judge_case_repository=judge_case_repository
    )

    user_status_service = Factory(
        UserProblemStatusApplicationService,
        user_problem_status_repository=user_problem_status_repository,
    )

    async def init_resources(self) -> None:
        """リソースを初期化"""
        try:
            # データベース接続を検証
            client = self.supabase_client()

            # 簡単な接続テスト（非同期でない可能性があるのでtry/catchで囲む）
            try:
                response = (
                    await client.table("books").select("count").limit(1).execute()
                )
                logger.info("Core domain database connection verified")
            except:
                # 同期版を試す
                response = client.table("books").select("count").limit(1).execute()
                logger.info("Core domain database connection verified (sync)")

            logger.info("Core domain container initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize core domain container: {e}")
            raise

    async def shutdown_resources(self) -> None:
        """リソースをシャットダウン"""
        try:
            # クリーンアップ処理があればここに記述
            logger.info("Core domain container shutdown completed")

        except Exception as e:
            logger.error(f"Error during core domain container shutdown: {e}")
            raise


# Global container instance
container = CoreApplicationContainer()
