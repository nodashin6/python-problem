"""
Core Domain Application Layer
コアドメインアプリケーション層

Author: Judge System Team
Date: 2025-01-12
"""

from .container import CoreApplicationContainer
from .services import (
    BookApplicationService,
    ProblemApplicationService,
    JudgeCaseApplicationService,
    UserProblemStatusApplicationService,
)
from .controllers import (
    BookController,
    ProblemController,
    JudgeCaseController,
    UserStatusController,
)

# グローバルコンテナインスタンス
_container: CoreApplicationContainer = None


async def initialize_core_container() -> None:
    """Core domainコンテナを初期化"""
    global _container
    _container = CoreApplicationContainer()
    await _container.init_resources()


async def shutdown_core_container() -> None:
    """Core domainコンテナを終了"""
    global _container
    if _container:
        await _container.shutdown_resources()
        _container = None


def get_core_container() -> CoreApplicationContainer:
    """Core domainコンテナを取得"""
    if _container is None:
        raise RuntimeError("Core container not initialized")
    return _container


__all__ = [
    "CoreApplicationContainer",
    "BookApplicationService",
    "ProblemApplicationService",
    "JudgeCaseApplicationService",
    "UserProblemStatusApplicationService",
    "BookController",
    "ProblemController",
    "JudgeCaseController",
    "UserStatusController",
    "initialize_core_container",
    "shutdown_core_container",
    "get_core_container",
]
