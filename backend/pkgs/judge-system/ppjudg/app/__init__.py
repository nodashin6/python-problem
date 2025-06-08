"""
Judge Domain Application Layer
ジャッジドメインアプリケーション層

このモジュールはジャッジドメインのアプリケーション層を提供します。
以下のコンポーネントが含まれています：

- container: DIコンテナとサービスファクトリー
- services: アプリケーションサービス
- handlers: イベントハンドラー
- controllers: APIコントローラー
"""

from .container import (
    JudgeContainer,
    ContainerManager,
    container_manager,
    get_container,
    get_service,
    initialize_container,
    shutdown_container,
    inject_dependencies,
)

from .services import (
    SubmissionApplicationService,
    CodeExecutionApplicationService,
    JudgeSystemApplicationService,
)

from .handlers import (
    CoreDomainEventHandler,
    JudgeSystemEventHandler,
    EventHandlerFactory,
    setup_event_handlers,
)

from .controllers import (
    SubmissionController,
    CodeExecutionController,
    JudgeSystemController,
    ControllerFactory,
    get_controllers,
    # Request/Response Models
    SubmitSolutionRequest,
    ExecuteCodeRequest,
    RejudgeRequest,
    StartWorkerRequest,
    SubmissionResponse,
    ExecutionResponse,
    SystemStatusResponse,
)

__all__ = [
    # Container
    "JudgeContainer",
    "ContainerManager",
    "container_manager",
    "get_container",
    "get_service",
    "initialize_container",
    "shutdown_container",
    "inject_dependencies",
    # Services
    "SubmissionApplicationService",
    "CodeExecutionApplicationService",
    "JudgeSystemApplicationService",
    # Handlers
    "CoreDomainEventHandler",
    "JudgeSystemEventHandler",
    "EventHandlerFactory",
    "setup_event_handlers",
    # Controllers
    "SubmissionController",
    "CodeExecutionController",
    "JudgeSystemController",
    "ControllerFactory",
    "get_controllers",
    # Request/Response Models
    "SubmitSolutionRequest",
    "ExecuteCodeRequest",
    "RejudgeRequest",
    "StartWorkerRequest",
    "SubmissionResponse",
    "ExecutionResponse",
    "SystemStatusResponse",
]
