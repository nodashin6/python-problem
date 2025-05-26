"""
Judge Domain Application Services
ジャッジドメインアプリケーションサービス
"""

import asyncio
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from dataclasses import asdict

from dependency_injector.wiring import Provide, inject

from ...const import JudgeResultType, ExecutionStatus, ProgrammingLanguage
from ...shared.logging import get_logger
from ...shared.events import (
    EventBus,
    SubmissionCreatedEvent,
    JudgeStartedEvent,
    JudgeCompletedEvent,
    JudgeErrorEvent,
)

from ..domain.models.submission import Submission, SubmissionStatus
from ..domain.models.code_execution import CodeExecution
from ..domain.models.judge_queue import JudgeQueueItem
from ..domain.value_objects.judge_result import JudgeResult
from ..domain.value_objects.code_metrics import CodeMetrics

from ..usecase.submission_use_case import SubmissionUseCase, SubmissionJudgeUseCase
from ..usecase.code_execution_use_case import CodeExecutionUseCase, JudgeQueueUseCase
from ..usecase.judge_worker_use_case import (
    JudgeWorkerUseCase,
    JudgeSystemMaintenanceUseCase,
)

from .container import JudgeContainer

logger = get_logger(__name__)


class SubmissionApplicationService:
    """提出管理アプリケーションサービス"""

    @inject
    def __init__(
        self,
        submission_use_case: SubmissionUseCase = Provide[
            JudgeContainer.submission_use_case
        ],
        submission_judge_use_case: SubmissionJudgeUseCase = Provide[
            JudgeContainer.submission_judge_use_case
        ],
        judge_queue_use_case: JudgeQueueUseCase = Provide[
            JudgeContainer.judge_queue_use_case
        ],
        event_bus: EventBus = Provide[JudgeContainer.event_bus_instance],
    ):
        self.submission_use_case = submission_use_case
        self.submission_judge_use_case = submission_judge_use_case
        self.judge_queue_use_case = judge_queue_use_case
        self.event_bus = event_bus

    async def submit_solution(
        self,
        user_id: str,
        problem_id: str,
        code: str,
        language: ProgrammingLanguage,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """解答を提出"""
        try:
            # 提出を作成
            submission = await self.submission_use_case.create_submission(
                user_id=user_id,
                problem_id=problem_id,
                code=code,
                language=language.value,
                metadata=metadata or {},
            )

            # ジャッジキューに追加
            await self.judge_queue_use_case.enqueue_submission(
                submission_id=submission.submission_id, priority=1  # デフォルト優先度
            )

            # イベント発行
            event = SubmissionCreatedEvent(
                submission_id=submission.submission_id,
                user_id=user_id,
                problem_id=problem_id,
                language=language.value,
                correlation_id=str(uuid.uuid4()),
            )
            await self.event_bus.publish(event)

            logger.info(f"Submission created: {submission.submission_id}")

            return {
                "submission_id": submission.submission_id,
                "status": submission.status.value,
                "created_at": submission.created_at.isoformat(),
                "language": submission.language,
                "queue_position": await self._get_queue_position(
                    submission.submission_id
                ),
            }

        except Exception as e:
            logger.error(f"Failed to submit solution: {e}")
            raise

    async def get_submission(self, submission_id: str) -> Optional[Dict[str, Any]]:
        """提出を取得"""
        submission = await self.submission_use_case.get_submission(submission_id)
        if not submission:
            return None

        return await self._serialize_submission(submission)

    async def get_user_submissions(
        self,
        user_id: str,
        problem_id: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """ユーザーの提出一覧を取得"""
        submissions = await self.submission_use_case.get_user_submissions(
            user_id=user_id, problem_id=problem_id, limit=limit, offset=offset
        )

        serialized_submissions = []
        for submission in submissions:
            serialized_submissions.append(await self._serialize_submission(submission))

        # 統計情報も取得
        stats = await self.submission_use_case.get_user_submission_statistics(user_id)

        return {
            "submissions": serialized_submissions,
            "total_count": len(submissions),
            "statistics": stats,
        }

    async def get_problem_submissions(
        self,
        problem_id: str,
        status: Optional[SubmissionStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """問題の提出一覧を取得"""
        submissions = await self.submission_use_case.get_problem_submissions(
            problem_id=problem_id, status=status, limit=limit, offset=offset
        )

        serialized_submissions = []
        for submission in submissions:
            serialized_submissions.append(await self._serialize_submission(submission))

        return {"submissions": serialized_submissions, "total_count": len(submissions)}

    async def rejudge_submission(
        self, submission_id: str, reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """提出を再ジャッジ"""
        try:
            # 再ジャッジを実行
            submission = await self.submission_use_case.rejudge_submission(
                submission_id, reason
            )

            # キューに再追加
            await self.judge_queue_use_case.enqueue_submission(
                submission_id=submission_id, priority=2  # 再ジャッジは優先度を上げる
            )

            logger.info(f"Submission rejudge queued: {submission_id}")

            return {
                "submission_id": submission_id,
                "status": submission.status.value,
                "queue_position": await self._get_queue_position(submission_id),
                "rejudge_reason": reason,
            }

        except Exception as e:
            logger.error(f"Failed to rejudge submission: {e}")
            raise

    async def _serialize_submission(self, submission: Submission) -> Dict[str, Any]:
        """提出をシリアライズ"""
        return {
            "submission_id": submission.submission_id,
            "user_id": submission.user_id,
            "problem_id": submission.problem_id,
            "code": submission.code,
            "language": submission.language,
            "status": submission.status.value,
            "result": submission.result.value if submission.result else None,
            "score": submission.score,
            "execution_time_ms": submission.execution_time_ms,
            "memory_usage_mb": submission.memory_usage_mb,
            "created_at": submission.created_at.isoformat(),
            "judged_at": (
                submission.judged_at.isoformat() if submission.judged_at else None
            ),
            "metadata": submission.metadata,
            "judge_case_results": submission.judge_case_results,
        }

    async def _get_queue_position(self, submission_id: str) -> Optional[int]:
        """キュー内の位置を取得"""
        try:
            queue_items = await self.judge_queue_use_case.get_queue_items(limit=1000)
            for i, item in enumerate(queue_items):
                if item.submission_id == submission_id:
                    return i + 1
            return None
        except Exception:
            return None


class CodeExecutionApplicationService:
    """コード実行アプリケーションサービス"""

    @inject
    def __init__(
        self,
        code_execution_use_case: CodeExecutionUseCase = Provide[
            JudgeContainer.code_execution_use_case
        ],
        event_bus: EventBus = Provide[JudgeContainer.event_bus_instance],
    ):
        self.code_execution_use_case = code_execution_use_case
        self.event_bus = event_bus

    async def execute_code(
        self,
        code: str,
        language: ProgrammingLanguage,
        input_data: str = "",
        time_limit_ms: int = 5000,
        memory_limit_mb: int = 256,
    ) -> Dict[str, Any]:
        """コードを実行"""
        try:
            execution = await self.code_execution_use_case.execute_code(
                code=code,
                language=language.value,
                input_data=input_data,
                time_limit_ms=time_limit_ms,
                memory_limit_mb=memory_limit_mb,
            )

            return {
                "execution_id": execution.execution_id,
                "status": execution.status.value,
                "output": execution.output,
                "error": execution.error,
                "exit_code": execution.exit_code,
                "execution_time_ms": execution.execution_time_ms,
                "memory_usage_mb": execution.memory_usage_mb,
                "created_at": execution.created_at.isoformat(),
                "completed_at": (
                    execution.completed_at.isoformat()
                    if execution.completed_at
                    else None
                ),
            }

        except Exception as e:
            logger.error(f"Failed to execute code: {e}")
            raise

    async def get_execution_result(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """実行結果を取得"""
        execution = await self.code_execution_use_case.get_execution_result(
            execution_id
        )
        if not execution:
            return None

        return {
            "execution_id": execution.execution_id,
            "status": execution.status.value,
            "output": execution.output,
            "error": execution.error,
            "exit_code": execution.exit_code,
            "execution_time_ms": execution.execution_time_ms,
            "memory_usage_mb": execution.memory_usage_mb,
            "created_at": execution.created_at.isoformat(),
            "completed_at": (
                execution.completed_at.isoformat() if execution.completed_at else None
            ),
        }

    async def cleanup_old_executions(self, days: int = 7) -> Dict[str, Any]:
        """古い実行結果をクリーンアップ"""
        try:
            count = await self.code_execution_use_case.cleanup_old_executions(days)
            logger.info(f"Cleaned up {count} old executions")

            return {"cleaned_count": count, "retention_days": days}

        except Exception as e:
            logger.error(f"Failed to cleanup executions: {e}")
            raise


class JudgeSystemApplicationService:
    """ジャッジシステム管理アプリケーションサービス"""

    @inject
    def __init__(
        self,
        judge_worker_use_case: JudgeWorkerUseCase = Provide[
            JudgeContainer.judge_worker_use_case
        ],
        maintenance_use_case: JudgeSystemMaintenanceUseCase = Provide[
            JudgeContainer.judge_system_maintenance_use_case
        ],
        judge_queue_use_case: JudgeQueueUseCase = Provide[
            JudgeContainer.judge_queue_use_case
        ],
        event_bus: EventBus = Provide[JudgeContainer.event_bus_instance],
    ):
        self.judge_worker_use_case = judge_worker_use_case
        self.maintenance_use_case = maintenance_use_case
        self.judge_queue_use_case = judge_queue_use_case
        self.event_bus = event_bus
        self._workers: Dict[str, asyncio.Task] = {}

    async def start_judge_worker(
        self, worker_id: Optional[str] = None, max_concurrent_jobs: int = 3
    ) -> Dict[str, Any]:
        """ジャッジワーカーを開始"""
        try:
            if not worker_id:
                worker_id = f"worker-{uuid.uuid4().hex[:8]}"

            if worker_id in self._workers:
                raise ValueError(f"Worker {worker_id} is already running")

            # ワーカータスクを開始
            task = asyncio.create_task(
                self.judge_worker_use_case.start_worker(worker_id, max_concurrent_jobs)
            )
            self._workers[worker_id] = task

            logger.info(f"Judge worker started: {worker_id}")

            return {
                "worker_id": worker_id,
                "max_concurrent_jobs": max_concurrent_jobs,
                "status": "started",
            }

        except Exception as e:
            logger.error(f"Failed to start judge worker: {e}")
            raise

    async def stop_judge_worker(self, worker_id: str) -> Dict[str, Any]:
        """ジャッジワーカーを停止"""
        try:
            if worker_id not in self._workers:
                raise ValueError(f"Worker {worker_id} is not running")

            task = self._workers[worker_id]
            task.cancel()

            try:
                await task
            except asyncio.CancelledError:
                pass

            del self._workers[worker_id]

            await self.judge_worker_use_case.stop_worker(worker_id)

            logger.info(f"Judge worker stopped: {worker_id}")

            return {"worker_id": worker_id, "status": "stopped"}

        except Exception as e:
            logger.error(f"Failed to stop judge worker: {e}")
            raise

    async def get_system_status(self) -> Dict[str, Any]:
        """システム状態を取得"""
        try:
            # キュー状態
            queue_items = await self.judge_queue_use_case.get_queue_items(limit=1000)
            pending_count = len([item for item in queue_items if not item.worker_id])
            processing_count = len([item for item in queue_items if item.worker_id])

            # ワーカー状態
            worker_stats = await self.judge_worker_use_case.get_worker_statistics()

            # システム統計
            system_stats = await self.maintenance_use_case.get_system_statistics()

            return {
                "queue": {
                    "pending": pending_count,
                    "processing": processing_count,
                    "total": len(queue_items),
                },
                "workers": {"active": len(self._workers), "statistics": worker_stats},
                "system": system_stats,
                "event_bus": self.event_bus.get_stats(),
            }

        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            raise

    async def run_maintenance(self) -> Dict[str, Any]:
        """メンテナンス作業を実行"""
        try:
            results = await self.maintenance_use_case.run_maintenance()

            logger.info("System maintenance completed")

            return {
                "maintenance_completed": True,
                "results": results,
                "completed_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to run maintenance: {e}")
            raise

    async def get_health_check(self) -> Dict[str, Any]:
        """ヘルスチェック"""
        try:
            health = await self.maintenance_use_case.health_check()

            return {
                "healthy": health.get("overall_status") == "healthy",
                "details": health,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def shutdown(self):
        """システムをシャットダウン"""
        try:
            # 全ワーカーを停止
            for worker_id in list(self._workers.keys()):
                await self.stop_judge_worker(worker_id)

            logger.info("Judge system shutdown completed")

        except Exception as e:
            logger.error(f"Error during system shutdown: {e}")
            raise
