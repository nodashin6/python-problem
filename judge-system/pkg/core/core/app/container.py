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
from ..infra.repositories.user_repository_impl import UserRepositoryImpl
from ..domain.services.user_service import UserDomainService
from .services import (
    BookApplicationService,
    ProblemApplicationService,
    JudgeCaseApplicationService,
    UserProblemStatusApplicationService,
    UserApplicationService,
)
from ...env import settings  # shared.configから変更
from ...shared.auth import PasswordManager, TokenManager
from ...shared.events import EventBus
from ...shared.database import DatabaseManager

logger = logging.getLogger(__name__)


class CoreApplicationContainer(containers.DeclarativeContainer):
    """コアドメインアプリケーションコンテナ"""

    # Configure provider
    config = providers.Configuration()

    # Supabase client
    supabase_client = Singleton(
        create_client,
        supabase_url=settings.supabase_url,  # SUPABASE_URLから変更
        supabase_key=settings.supabase_anon_key,  # SUPABASE_ANON_KEYから変更
    )

    # Database manager and auth components
    database_manager = Singleton(DatabaseManager, supabase_client=supabase_client)
    password_manager = Singleton(PasswordManager)
    token_manager = Singleton(TokenManager)
    event_bus = Singleton(EventBus)

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

    user_repository = Factory(UserRepositoryImpl, db_manager=database_manager)

    # Domain services
    user_domain_service = Factory(
        UserDomainService,
        user_repo=user_repository,
        password_manager=password_manager,
        token_manager=token_manager,
        event_bus=event_bus,
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

    user_service = Factory(UserApplicationService, user_service=user_domain_service)

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
