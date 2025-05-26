"""
Judge Worker Use Cases
ジャッジワーカーユースケース
"""

import uuid
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable

from ..domain.repositories.submission_repository import SubmissionRepository
from ..domain.repositories.judge_queue_repository import JudgeQueueRepository
from ..domain.repositories.code_execution_repository import CodeExecutionRepository
from ...core.domain.repositories.problem_repository import ProblemRepository
from ..domain.services.judge_service import JudgeDomainService
from .submission_use_case import SubmissionJudgeUseCase
from .code_execution_use_case import JudgeQueueUseCase
from ...const import ExecutionStatus
from ...shared.events import DomainEventBus, SubmissionJudgedEvent


logger = logging.getLogger(__name__)


class JudgeWorkerUseCase:
    """ジャッジワーカー関連のユースケース"""

    def __init__(
        self,
        submission_repo: SubmissionRepository,
        queue_repo: JudgeQueueRepository,
        execution_repo: CodeExecutionRepository,
        problem_repo: ProblemRepository,
        judge_service: JudgeDomainService,
        event_bus: DomainEventBus,
    ):
        self.submission_repo = submission_repo
        self.queue_repo = queue_repo
        self.execution_repo = execution_repo
        self.problem_repo = problem_repo
        self.judge_service = judge_service
        self.event_bus = event_bus

        # 他のユースケースを初期化
        self.submission_judge = SubmissionJudgeUseCase(
            submission_repo, queue_repo, problem_repo, judge_service, event_bus
        )
        self.queue_use_case = JudgeQueueUseCase(
            queue_repo, submission_repo, judge_service
        )

    async def start_worker(
        self,
        worker_id: str,
        polling_interval: int = 5,
        max_concurrent: int = 3,
        stop_callback: Optional[Callable[[], bool]] = None,
    ) -> None:
        """ワーカーを開始"""
        logger.info(f"Starting judge worker: {worker_id}")

        # 既存のワーカーアイテムを解放
        await self.queue_use_case.release_worker_submissions(worker_id)

        # 並行処理用のセマフォ
        semaphore = asyncio.Semaphore(max_concurrent)

        try:
            while True:
                # 停止シグナルチェック
                if stop_callback and stop_callback():
                    logger.info(f"Stop signal received for worker {worker_id}")
                    break

                try:
                    # 次の提出を取得
                    submission_id = await self.queue_use_case.get_next_submission(
                        worker_id
                    )

                    if submission_id:
                        # 並行処理で提出を処理
                        asyncio.create_task(
                            self._process_submission_with_semaphore(
                                semaphore, submission_id, worker_id
                            )
                        )
                    else:
                        # 処理する提出がない場合は少し待機
                        await asyncio.sleep(polling_interval)

                except Exception as e:
                    logger.error(f"Error in worker {worker_id} main loop: {e}")
                    await asyncio.sleep(polling_interval)

        except asyncio.CancelledError:
            logger.info(f"Worker {worker_id} was cancelled")
        except Exception as e:
            logger.error(f"Fatal error in worker {worker_id}: {e}")
        finally:
            # クリーンアップ
            await self._cleanup_worker(worker_id)

    async def _process_submission_with_semaphore(
        self, semaphore: asyncio.Semaphore, submission_id: uuid.UUID, worker_id: str
    ) -> None:
        """セマフォを使って提出を処理"""
        async with semaphore:
            await self._process_single_submission(submission_id, worker_id)

    async def _process_single_submission(
        self, submission_id: uuid.UUID, worker_id: str
    ) -> None:
        """単一の提出を処理"""
        try:
            logger.info(f"Worker {worker_id} processing submission: {submission_id}")

            # 提出を取得
            submission = await self.submission_repo.find_by_id(submission_id)
            if not submission:
                logger.error(f"Submission not found: {submission_id}")
                await self.queue_use_case.fail_submission(
                    submission_id, worker_id, "Submission not found"
                )
                return

            # 問題を取得
            problem = await self.problem_repo.find_by_id(submission.problem_id)
            if not problem:
                logger.error(f"Problem not found: {submission.problem_id}")
                await self.queue_use_case.fail_submission(
                    submission_id, worker_id, "Problem not found"
                )
                return

            # ジャッジケースを取得
            judge_cases = await self.problem_repo.get_judge_cases(submission.problem_id)
            if not judge_cases:
                logger.error(
                    f"No judge cases found for problem: {submission.problem_id}"
                )
                await self.queue_use_case.fail_submission(
                    submission_id, worker_id, "No judge cases found"
                )
                return

            # ジャッジ処理を実行
            judge_success = await self.judge_service.process_submission(
                submission, judge_cases
            )

            if judge_success:
                # 提出を保存
                await self.submission_repo.save(submission)

                # キューを完了状態に更新
                await self.queue_use_case.complete_submission(submission_id, worker_id)

                # ドメインイベントを発行
                event = SubmissionJudgedEvent(
                    submission_id=submission.id,
                    user_id=submission.user_id,
                    problem_id=submission.problem_id,
                    result=submission.overall_result.value,
                    points=submission.total_points,
                    judged_at=submission.judged_at or datetime.utcnow(),
                )
                self.event_bus.publish(event)

                logger.info(
                    f"Worker {worker_id} completed submission: {submission_id} -> {submission.overall_result}"
                )
            else:
                await self.queue_use_case.fail_submission(
                    submission_id, worker_id, "Judge processing failed"
                )

        except Exception as e:
            logger.error(
                f"Worker {worker_id} failed to process submission {submission_id}: {e}"
            )
            await self.queue_use_case.fail_submission(
                submission_id, worker_id, f"Processing error: {str(e)}"
            )

    async def _cleanup_worker(self, worker_id: str) -> None:
        """ワーカーのクリーンアップ"""
        try:
            released_count = await self.queue_use_case.release_worker_submissions(
                worker_id
            )
            logger.info(
                f"Worker {worker_id} cleanup: released {released_count} submissions"
            )
        except Exception as e:
            logger.error(f"Error during worker {worker_id} cleanup: {e}")

    async def get_worker_status(self, worker_id: str) -> Dict[str, Any]:
        """ワーカーの状態を取得"""
        try:
            # ワーカーが処理中のアイテムを取得
            worker_items = await self.queue_repo.find_by_worker(worker_id)

            # 統計情報を計算
            running_count = len(
                [
                    item
                    for item in worker_items
                    if item.status == ExecutionStatus.RUNNING
                ]
            )
            total_assigned = len(worker_items)

            return {
                "worker_id": worker_id,
                "running_submissions": running_count,
                "total_assigned": total_assigned,
                "items": [
                    {
                        "submission_id": str(item.submission_id),
                        "status": item.status.value,
                        "assigned_at": (
                            item.assigned_at.isoformat() if item.assigned_at else None
                        ),
                        "started_at": (
                            item.started_at.isoformat() if item.started_at else None
                        ),
                    }
                    for item in worker_items
                ],
            }

        except Exception as e:
            logger.error(f"Failed to get worker status for {worker_id}: {e}")
            return {"worker_id": worker_id, "error": str(e)}


class JudgeSystemMaintenanceUseCase:
    """ジャッジシステムメンテナンス関連のユースケース"""

    def __init__(
        self,
        submission_repo: SubmissionRepository,
        queue_repo: JudgeQueueRepository,
        execution_repo: CodeExecutionRepository,
    ):
        self.submission_repo = submission_repo
        self.queue_repo = queue_repo
        self.execution_repo = execution_repo
        self.queue_use_case = JudgeQueueUseCase(queue_repo, submission_repo, None)

    async def cleanup_system(
        self, cleanup_days: int = 30, execution_days: int = 7
    ) -> Dict[str, int]:
        """システムのクリーンアップ"""
        try:
            results = {}

            # 完了済みキューアイテムの削除
            deleted_queue = await self.queue_use_case.cleanup_completed_items(
                cleanup_days
            )
            results["deleted_queue_items"] = deleted_queue

            # 古いコード実行の削除
            before_date = datetime.utcnow() - timedelta(days=execution_days)
            deleted_executions = await self.execution_repo.delete_old_executions(
                before_date
            )
            results["deleted_executions"] = deleted_executions

            logger.info(f"System cleanup completed: {results}")
            return results

        except Exception as e:
            logger.error(f"Failed to cleanup system: {e}")
            return {"error": str(e)}

    async def reset_stuck_submissions(self, minutes: int = 30) -> Dict[str, int]:
        """スタックした提出をリセット"""
        try:
            # スタックしたキューアイテムをリセット
            reset_count = await self.queue_use_case.reset_stale_items(minutes)

            return {"reset_submissions": reset_count}

        except Exception as e:
            logger.error(f"Failed to reset stuck submissions: {e}")
            return {"error": str(e)}

    async def get_system_status(self) -> Dict[str, Any]:
        """システム全体の状態を取得"""
        try:
            # キューの状態
            queue_stats = await self.queue_use_case.get_queue_status()

            # 今日の統計
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow = today + timedelta(days=1)

            execution_stats = await self.execution_repo.get_execution_statistics(
                today, tomorrow
            )

            # 問題の提出数統計（サンプル）
            submission_counts = {}
            for status in ExecutionStatus:
                count = await self.submission_repo.count_by_status(status)
                submission_counts[f"submissions_{status.value}"] = count

            return {
                "timestamp": datetime.utcnow().isoformat(),
                "queue": queue_stats,
                "executions": execution_stats,
                "submissions": submission_counts,
            }

        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return {"error": str(e)}

    async def health_check(self) -> Dict[str, Any]:
        """システムのヘルスチェック"""
        try:
            health = {"status": "healthy", "checks": {}}

            # ペンディング提出の数をチェック
            pending_count = await self.queue_repo.count_pending()
            health["checks"]["pending_submissions"] = {
                "count": pending_count,
                "status": "warning" if pending_count > 100 else "ok",
            }

            # スタックした提出をチェック
            stale_items = await self.queue_use_case.get_stale_items(30, 10)
            health["checks"]["stale_submissions"] = {
                "count": len(stale_items),
                "status": "warning" if len(stale_items) > 5 else "ok",
            }

            # 全体的な健全性を判定
            warnings = [
                check
                for check in health["checks"].values()
                if check["status"] == "warning"
            ]
            if warnings:
                health["status"] = "warning"

            return health

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }
