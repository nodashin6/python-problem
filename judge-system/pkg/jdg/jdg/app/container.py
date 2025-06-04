"""
Judge Domain Dependency Injection Container
ジャッジドメインDIコンテナ
"""

import asyncio
from typing import Type, TypeVar, Optional
import logging

from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject

from supabase import create_client
from ...shared.database import SupabaseClient  # get_supabase_client を削除
from ...shared.events import EventBus, EventStore, event_bus, event_store
from ...shared.logging import get_logger
from ...env import settings  # shared.configから変更

# Domain Interfaces
from ..domain.repositories.submission_repository import SubmissionRepository
from ..domain.repositories.code_execution_repository import CodeExecutionRepository
from ..domain.repositories.judge_queue_repository import JudgeQueueRepository
from ..domain.services.judge_service import JudgeService
from ..domain.services.code_execution_service import CodeExecutionService
from ..domain.services.queue_management_service import QueueManagementService

# Infrastructure Implementations
from ..infra.repositories.submission_repository_impl import SubmissionRepositoryImpl
from ..infra.repositories.code_execution_repository_impl import (
    CodeExecutionRepositoryImpl,
)
from ..infra.repositories.judge_queue_repository_impl import JudgeQueueRepositoryImpl

# Use Cases
from ..usecase.submission_use_case import SubmissionUseCase, SubmissionJudgeUseCase
from ..usecase.code_execution_use_case import CodeExecutionUseCase, JudgeQueueUseCase
from ..usecase.judge_worker_use_case import (
    JudgeWorkerUseCase,
    JudgeSystemMaintenanceUseCase,
)

logger = get_logger(__name__)

T = TypeVar("T")


class JudgeContainer(containers.DeclarativeContainer):
    """ジャッジドメインDIコンテナ"""

    # ワイヤリング設定
    wiring_config = containers.WiringConfiguration(
        modules=[
            "..app.services",
            "..app.handlers",
            "..app.controllers",
        ]
    )

    # 外部リソース
    config = providers.Configuration()

    # Database
    supabase_client = providers.Singleton(
        create_client,
        supabase_url=settings.supabase_url,  # SUPABASE_URLから変更
        supabase_key=settings.supabase_anon_key,  # SUPABASE_ANON_KEYから変更
    )

    # Event Infrastructure
    event_bus_instance = providers.Singleton(lambda: event_bus)

    event_store_instance = providers.Singleton(lambda: event_store)

    # Repository Implementations
    submission_repository = providers.Singleton(
        SubmissionRepositoryImpl, supabase_client=supabase_client
    )

    code_execution_repository = providers.Singleton(
        CodeExecutionRepositoryImpl, supabase_client=supabase_client
    )

    judge_queue_repository = providers.Singleton(
        JudgeQueueRepositoryImpl, supabase_client=supabase_client
    )

    # Domain Services
    judge_service = providers.Singleton(JudgeService)

    code_execution_service = providers.Singleton(CodeExecutionService)

    queue_management_service = providers.Singleton(
        QueueManagementService, judge_queue_repository=judge_queue_repository
    )

    # Use Cases
    submission_use_case = providers.Singleton(
        SubmissionUseCase,
        submission_repository=submission_repository,
        event_bus=event_bus_instance,
    )

    submission_judge_use_case = providers.Singleton(
        SubmissionJudgeUseCase,
        submission_repository=submission_repository,
        judge_service=judge_service,
        event_bus=event_bus_instance,
    )

    code_execution_use_case = providers.Singleton(
        CodeExecutionUseCase,
        code_execution_repository=code_execution_repository,
        code_execution_service=code_execution_service,
        event_bus=event_bus_instance,
    )

    judge_queue_use_case = providers.Singleton(
        JudgeQueueUseCase,
        judge_queue_repository=judge_queue_repository,
        queue_management_service=queue_management_service,
        event_bus=event_bus_instance,
    )

    judge_worker_use_case = providers.Singleton(
        JudgeWorkerUseCase,
        judge_queue_repository=judge_queue_repository,
        submission_repository=submission_repository,
        submission_judge_use_case=submission_judge_use_case,
        event_bus=event_bus_instance,
    )

    judge_system_maintenance_use_case = providers.Singleton(
        JudgeSystemMaintenanceUseCase,
        submission_repository=submission_repository,
        code_execution_repository=code_execution_repository,
        judge_queue_repository=judge_queue_repository,
        event_bus=event_bus_instance,
    )


class ContainerManager:
    """コンテナマネージャー"""

    def __init__(self):
        self.container = JudgeContainer()
        self._initialized = False

    async def initialize(self, config: Optional[dict] = None):
        """コンテナを初期化"""
        if self._initialized:
            logger.warning("Container already initialized")
            return

        try:
            # 設定を適用
            if config:
                self.container.config.from_dict(config)

            # Event Busを開始
            event_bus_instance = self.container.event_bus_instance()
            await event_bus_instance.start()

            # ワイヤリングを実行
            self.container.wire(
                modules=[
                    "jdg.app.services",
                    "jdg.app.handlers",
                    "jdg.app.controllers",
                ]
            )

            self._initialized = True
            logger.info("Judge container initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize container: {e}")
            raise

    async def shutdown(self):
        """コンテナをシャットダウン"""
        if not self._initialized:
            return

        try:
            # Event Busを停止
            event_bus_instance = self.container.event_bus_instance()
            await event_bus_instance.stop()

            # リソースをクリーンアップ
            self.container.unwire()

            self._initialized = False
            logger.info("Judge container shutdown completed")

        except Exception as e:
            logger.error(f"Error during container shutdown: {e}")

    def get_container(self) -> JudgeContainer:
        """コンテナインスタンスを取得"""
        if not self._initialized:
            raise RuntimeError("Container not initialized. Call initialize() first.")
        return self.container

    def get_service(self, service_type: Type[T]) -> T:
        """サービスインスタンスを取得"""
        if not self._initialized:
            raise RuntimeError("Container not initialized. Call initialize() first.")

        # サービスタイプに基づいてプロバイダーを特定
        provider_mapping = {
            SubmissionUseCase: self.container.submission_use_case,
            SubmissionJudgeUseCase: self.container.submission_judge_use_case,
            CodeExecutionUseCase: self.container.code_execution_use_case,
            JudgeQueueUseCase: self.container.judge_queue_use_case,
            JudgeWorkerUseCase: self.container.judge_worker_use_case,
            JudgeSystemMaintenanceUseCase: self.container.judge_system_maintenance_use_case,
            SubmissionRepository: self.container.submission_repository,
            CodeExecutionRepository: self.container.code_execution_repository,
            JudgeQueueRepository: self.container.judge_queue_repository,
        }

        provider = provider_mapping.get(service_type)
        if not provider:
            raise ValueError(f"No provider found for service type: {service_type}")

        return provider()


# グローバルインスタンス
container_manager = ContainerManager()


# 便利関数
def get_container() -> JudgeContainer:
    """DIコンテナを取得"""
    return container_manager.get_container()


def get_service(service_type: Type[T]) -> T:
    """サービスインスタンスを取得"""
    return container_manager.get_service(service_type)


# イニシャライザー
async def initialize_container(config: Optional[dict] = None):
    """コンテナを初期化（便利関数）"""
    await container_manager.initialize(config)


async def shutdown_container():
    """コンテナをシャットダウン（便利関数）"""
    await container_manager.shutdown()


# デコレータ
def inject_dependencies(func):
    """依存関係注入デコレータ"""
    return inject(func)
