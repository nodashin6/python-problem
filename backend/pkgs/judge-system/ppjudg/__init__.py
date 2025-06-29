"""
Judge System Package
ジャッジシステムパッケージ - 提出コードの実行・評価

責任領域:
- コード実行環境の管理
- テストケースの実行
- 実行結果の判定
- パフォーマンス計測
- セキュリティ制御
"""

# Domain Models
# Domain Entities
from .domain.entities import JudgeResultEntity, SubmissionEntity
from .domain.models import ExecutionResult, JudgeResult, Submission

# Domain Services
from .domain.services import ExecutionService, JudgeDomainService

# Queue Services (Judge-specific)
from .queue import JudgeQueueService

# Use Cases
from .usecase import (
    ExecuteCodeUseCase,
    JudgeSubmissionUseCase,
    SubmitCodeUseCase,
)

__all__ = [
    # Models
    "Submission",
    "JudgeResult",
    "ExecutionResult",
    # Entities
    "SubmissionEntity",
    "JudgeResultEntity",
    # Services
    "JudgeDomainService",
    "ExecutionService",
    # Use Cases
    "SubmitCodeUseCase",
    "ExecuteCodeUseCase",
    "JudgeSubmissionUseCase",
    # Queue
    "JudgeQueueService",
]
