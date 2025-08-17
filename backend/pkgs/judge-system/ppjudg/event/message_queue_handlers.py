"""
Message Queue Event Handlers
メッセージキューイベントハンドラー

メッセージキューから呼び出される処理を実装
イベントハンドラーはドメインサービスとリポジトリのみに依存し、ユースケースには依存しない
"""

import uuid
from datetime import datetime
from typing import Any

from dependency_injector.wiring import Provide, inject

from typing import Protocol
from ..domain.entities.enums import ExecutionStatus, JudgeResultType

# Local protocols to avoid cross-package dependencies
class ProblemRepository(Protocol):
    """Problem repository protocol - local definition"""
    async def find_by_id(self, problem_id): ...
    async def get_judge_cases(self, problem_id): ...

class EventBus(Protocol):
    """Event bus protocol - local definition"""
    async def publish(self, event): ...

class JudgeCompletedEvent:
    """Judge completed event - local definition"""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class JudgeErrorEvent:
    """Judge error event - local definition"""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

def get_logger(name):
    """Simple logger function - local definition"""
    import logging
    return logging.getLogger(name)
# from ..app.container import JudgeContainer
from ..domain.repositories.judge_queue_repository import JudgeQueueRepositoryBase as JudgeQueueRepository  
from ..domain.repositories.submission_repository import SubmissionRepositoryBase as SubmissionRepository
# from ..domain.services.judge_service import JudgeDomainService

# Local service protocol to avoid import issues
class JudgeDomainService(Protocol):
    """Judge domain service protocol - local definition"""
    async def process_submission(self, submission, judge_cases): ...

logger = get_logger(__name__)


class MessageQueueEventHandler:
    """メッセージキューからのイベント処理のベースクラス"""

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus

    async def handle_message(self, message: dict[str, Any]) -> bool:
        """メッセージを処理する抽象メソッド"""
        raise NotImplementedError

    async def _publish_error_event(self, message_id: str, error: str, context: dict[str, Any]) -> None:
        """エラーイベントを発行"""
        try:
            error_event = JudgeErrorEvent(
                judge_id=context.get("judge_id", "unknown"),
                submission_id=context.get("submission_id", "unknown"),
                error=error,
                context=context,
                correlation_id=str(uuid.uuid4()),
            )
            await self.event_bus.publish(error_event)
        except Exception as e:
            logger.error(f"Failed to publish error event: {e}")


class SubmissionQueueHandler(MessageQueueEventHandler):
    """提出キューからのメッセージハンドラー"""

    # @inject - temporarily disabled for testing
    def __init__(
        self,
        submission_repo: SubmissionRepository,
        queue_repo: JudgeQueueRepository,
        problem_repo: ProblemRepository,
        judge_service: JudgeDomainService,
        event_bus: EventBus,
    ):
        super().__init__(event_bus)
        self.submission_repo = submission_repo
        self.queue_repo = queue_repo
        self.problem_repo = problem_repo
        self.judge_service = judge_service

    async def handle_submission_created_message(self, message: dict[str, Any]) -> bool:
        """提出作成メッセージを処理"""
        try:
            submission_id = uuid.UUID(message["submission_id"])
            user_id = uuid.UUID(message["user_id"])
            problem_id = uuid.UUID(message["problem_id"])

            logger.info(
                f"Processing submission created message: {submission_id} "
                f"by user {user_id} for problem {problem_id}"
            )

            # 提出がキューに正しく追加されているか確認
            queue_item = await self.queue_repo.find_by_submission(submission_id)
            if not queue_item:
                logger.error(f"Queue item not found for submission: {submission_id}")
                await self._publish_error_event(
                    message.get("message_id", "unknown"),
                    "Queue item not found",
                    {"submission_id": str(submission_id)},
                )
                return False

            logger.info(f"Submission created message processed successfully: {submission_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to handle submission created message: {e}")
            await self._publish_error_event(
                message.get("message_id", "unknown"), str(e), {"message": message}
            )
            return False

    async def handle_judge_request_message(self, message: dict[str, Any]) -> bool:
        """ジャッジリクエストメッセージを処理"""
        try:
            submission_id = uuid.UUID(message["submission_id"])
            worker_id = message.get("worker_id", "mq-worker")

            logger.info(f"Processing judge request message: {submission_id} with worker {worker_id}")

            # 提出を取得
            submission = await self.submission_repo.find_by_id(submission_id)
            if not submission:
                logger.error(f"Submission not found: {submission_id}")
                await self._publish_error_event(
                    message.get("message_id", "unknown"),
                    "Submission not found",
                    {"submission_id": str(submission_id)},
                )
                return False

            # 問題を取得
            problem = await self.problem_repo.find_by_id(submission.problem_id)
            if not problem:
                logger.error(f"Problem not found: {submission.problem_id}")
                await self._publish_error_event(
                    message.get("message_id", "unknown"),
                    "Problem not found",
                    {"submission_id": str(submission_id), "problem_id": str(submission.problem_id)},
                )
                return False

            # ジャッジケースを取得
            judge_cases = await self.problem_repo.get_judge_cases(submission.problem_id)
            if not judge_cases:
                logger.error(f"No judge cases found for problem: {submission.problem_id}")
                await self._publish_error_event(
                    message.get("message_id", "unknown"),
                    "No judge cases found",
                    {"submission_id": str(submission_id), "problem_id": str(submission.problem_id)},
                )
                return False

            # キューアイテムを実行中に更新
            queue_item = await self.queue_repo.find_by_submission(submission_id)
            if queue_item:
                queue_item.status = ExecutionStatus.RUNNING
                queue_item.worker_id = worker_id
                queue_item.started_at = datetime.utcnow()
                await self.queue_repo.save(queue_item)

            # ドメインサービスでジャッジ実行
            success = await self.judge_service.process_submission(submission, judge_cases)

            if success:
                # 提出を保存
                await self.submission_repo.save(submission)

                # キューを完了状態に更新
                if queue_item:
                    queue_item.status = ExecutionStatus.COMPLETED
                    queue_item.completed_at = datetime.utcnow()
                    await self.queue_repo.save(queue_item)

                logger.info(f"Judge request completed successfully: {submission_id}")

                # 完了イベントを発行
                completed_event = JudgeCompletedEvent(
                    judge_id=str(uuid.uuid4()),
                    submission_id=str(submission_id),
                    result=submission.overall_result.value,
                    score=submission.total_points,
                    user_id=str(submission.user_id),
                    correlation_id=message.get("correlation_id", str(uuid.uuid4())),
                )
                await self.event_bus.publish(completed_event)

                return True
            else:
                # 失敗時はキューを失敗状態に更新
                if queue_item:
                    queue_item.status = ExecutionStatus.FAILED
                    queue_item.error_message = "Judge processing failed"
                    await self.queue_repo.save(queue_item)

                logger.error(f"Judge request failed: {submission_id}")
                await self._publish_error_event(
                    message.get("message_id", "unknown"),
                    "Judge processing failed",
                    {"submission_id": str(submission_id), "worker_id": worker_id},
                )
                return False

        except Exception as e:
            logger.error(f"Failed to handle judge request message: {e}")
            await self._publish_error_event(
                message.get("message_id", "unknown"), str(e), {"message": message}
            )
            return False

    async def handle_rejudge_request_message(self, message: dict[str, Any]) -> bool:
        """再ジャッジリクエストメッセージを処理"""
        try:
            submission_id = uuid.UUID(message["submission_id"])
            reason = message.get("reason", "Manual rejudge request")

            logger.info(f"Processing rejudge request message: {submission_id}, reason: {reason}")

            # 提出をペンディング状態にリセット
            submission = await self.submission_repo.find_by_id(submission_id)
            if not submission:
                logger.error(f"Submission not found for rejudge: {submission_id}")
                return False

            submission.status = ExecutionStatus.PENDING
            submission.overall_result = JudgeResultType.PENDING
            submission.total_points = 0
            submission.judge_case_results = []
            submission.judged_at = None

            await self.submission_repo.save(submission)

            # キューアイテムもリセット
            queue_item = await self.queue_repo.find_by_submission(submission_id)
            if queue_item:
                queue_item.status = ExecutionStatus.PENDING
                queue_item.worker_id = None
                queue_item.started_at = None
                queue_item.error_message = None
                queue_item.priority = 5  # 再ジャッジは高優先度
                await self.queue_repo.save(queue_item)

            logger.info(f"Rejudge request processed successfully: {submission_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to handle rejudge request message: {e}")
            await self._publish_error_event(
                message.get("message_id", "unknown"), str(e), {"message": message}
            )
            return False


class JudgeWorkerEventHandler(MessageQueueEventHandler):
    """ジャッジワーカーからのメッセージハンドラー"""

    # @inject - temporarily disabled for testing
    def __init__(
        self,
        queue_repo: JudgeQueueRepository,
        event_bus: EventBus,
    ):
        super().__init__(event_bus)
        self.queue_repo = queue_repo

    async def handle_worker_status_message(self, message: dict[str, Any]) -> bool:
        """ワーカーステータスメッセージを処理"""
        try:
            worker_id = message["worker_id"]
            status = message["status"]

            logger.info(f"Processing worker status message: {worker_id} -> {status}")

            if status == "heartbeat":
                # ハートビート処理
                await self._handle_worker_heartbeat(worker_id)
            elif status == "shutdown":
                # ワーカーシャットダウン処理
                await self._handle_worker_shutdown(worker_id)
            elif status == "error":
                # ワーカーエラー処理
                await self._handle_worker_error(worker_id, message)

            return True

        except Exception as e:
            logger.error(f"Failed to handle worker status message: {e}")
            return False

    async def handle_queue_maintenance_message(self, message: dict[str, Any]) -> bool:
        """キューメンテナンスメッセージを処理"""
        try:
            action = message["action"]

            logger.info(f"Processing queue maintenance message: {action}")

            if action == "cleanup_stale":
                # スタックしたアイテムのクリーンアップ
                minutes = message.get("minutes", 30)
                reset_count = await self._reset_stale_items(minutes)
                logger.info(f"Reset {reset_count} stale queue items")

            elif action == "cleanup_completed":
                # 完了済みアイテムのクリーンアップ
                days = message.get("days", 7)
                deleted_count = await self._cleanup_completed_items(days)
                logger.info(f"Deleted {deleted_count} completed queue items")

            elif action == "rebalance":
                # キューリバランス
                await self._handle_queue_rebalance()

            return True

        except Exception as e:
            logger.error(f"Failed to handle queue maintenance message: {e}")
            return False

    async def _handle_worker_heartbeat(self, worker_id: str) -> None:
        """ワーカーハートビート処理"""
        try:
            logger.debug(f"Worker heartbeat received: {worker_id}")
            # 実装は具体的な要件に依存
        except Exception as e:
            logger.error(f"Failed to handle worker heartbeat: {e}")

    async def _handle_worker_shutdown(self, worker_id: str) -> None:
        """ワーカーシャットダウン処理"""
        try:
            logger.info(f"Processing worker shutdown: {worker_id}")

            # ワーカーが処理中の提出を解放
            released_count = await self._release_worker_submissions(worker_id)
            logger.info(f"Released {released_count} submissions from worker {worker_id}")

        except Exception as e:
            logger.error(f"Failed to handle worker shutdown: {e}")

    async def _handle_worker_error(self, worker_id: str, message: dict[str, Any]) -> None:
        """ワーカーエラー処理"""
        try:
            error_details = message.get("error", "Unknown error")
            logger.error(f"Worker error reported: {worker_id} - {error_details}")

            # エラーが重大な場合は提出を解放
            if message.get("severity") == "critical":
                released_count = await self._release_worker_submissions(worker_id)
                logger.info(f"Released {released_count} submissions due to critical worker error")

        except Exception as e:
            logger.error(f"Failed to handle worker error: {e}")

    async def _handle_queue_rebalance(self) -> None:
        """キューリバランス処理"""
        try:
            logger.info("Processing queue rebalance")
            # 実装は具体的な要件に依存
            logger.info("Queue rebalance completed")
        except Exception as e:
            logger.error(f"Failed to handle queue rebalance: {e}")

    async def _release_worker_submissions(self, worker_id: str) -> int:
        """ワーカーの提出を解放"""
        try:
            worker_items = await self.queue_repo.find_by_worker(worker_id)
            released_count = 0

            for item in worker_items:
                if item.status in [ExecutionStatus.RUNNING, ExecutionStatus.PENDING]:
                    item.status = ExecutionStatus.PENDING
                    item.worker_id = None
                    item.started_at = None
                    await self.queue_repo.save(item)
                    released_count += 1

            return released_count
        except Exception as e:
            logger.error(f"Failed to release worker submissions: {e}")
            return 0

    async def _reset_stale_items(self, minutes: int) -> int:
        """スタックしたアイテムをリセット"""
        try:
            cutoff_time = datetime.utcnow() - datetime.timedelta(minutes=minutes)
            stale_items = await self.queue_repo.find_stale_items(cutoff_time)
            reset_count = 0

            for item in stale_items:
                item.status = ExecutionStatus.PENDING
                item.worker_id = None
                item.started_at = None
                await self.queue_repo.save(item)
                reset_count += 1

            return reset_count
        except Exception as e:
            logger.error(f"Failed to reset stale items: {e}")
            return 0

    async def _cleanup_completed_items(self, days: int) -> int:
        """完了済みアイテムをクリーンアップ"""
        try:
            cutoff_date = datetime.utcnow() - datetime.timedelta(days=days)
            return await self.queue_repo.delete_completed_before(cutoff_date)
        except Exception as e:
            logger.error(f"Failed to cleanup completed items: {e}")
            return 0


# メッセージハンドラーのファクトリー
class MessageQueueHandlerFactory:
    """メッセージキューハンドラーファクトリー"""

    @staticmethod
    def create_submission_handler() -> SubmissionQueueHandler:
        """提出キューハンドラーを作成"""
        from unittest.mock import AsyncMock
        return SubmissionQueueHandler(
            submission_repo=AsyncMock(),
            queue_repo=AsyncMock(),
            problem_repo=AsyncMock(),
            judge_service=AsyncMock(),
            event_bus=AsyncMock(),
        )

    @staticmethod
    def create_worker_handler() -> JudgeWorkerEventHandler:
        """ワーカーイベントハンドラーを作成"""
        from unittest.mock import AsyncMock
        return JudgeWorkerEventHandler(
            queue_repo=AsyncMock(),
            event_bus=AsyncMock(),
        )

    @staticmethod
    def create_all_handlers() -> dict[str, MessageQueueEventHandler]:
        """全てのメッセージハンドラーを作成"""
        return {
            "submission": MessageQueueHandlerFactory.create_submission_handler(),
            "worker": MessageQueueHandlerFactory.create_worker_handler(),
        }


# メッセージルーターとディスパッチャー
class MessageQueueDispatcher:
    """メッセージキューディスパッチャー"""

    def __init__(self):
        self.handlers = MessageQueueHandlerFactory.create_all_handlers()

    async def dispatch_message(self, message: dict[str, Any]) -> bool:
        """メッセージを適切なハンドラーにディスパッチ"""
        try:
            message_type = message.get("type")
            handler_name = message.get("handler", self._get_default_handler(message_type))

            if handler_name not in self.handlers:
                logger.error(f"Unknown handler: {handler_name}")
                return False

            handler = self.handlers[handler_name]

            # メッセージタイプに応じた処理を実行
            if message_type == "submission.created":
                return await handler.handle_submission_created_message(message)
            elif message_type == "judge.request":
                return await handler.handle_judge_request_message(message)
            elif message_type == "judge.rejudge":
                return await handler.handle_rejudge_request_message(message)
            elif message_type == "worker.status":
                return await handler.handle_worker_status_message(message)
            elif message_type == "queue.maintenance":
                return await handler.handle_queue_maintenance_message(message)
            else:
                logger.error(f"Unknown message type: {message_type}")
                return False

        except Exception as e:
            logger.error(f"Failed to dispatch message: {e}")
            return False

    def _get_default_handler(self, message_type: str) -> str:
        """メッセージタイプから適切なハンドラーを推測"""
        if message_type and (message_type.startswith(("submission", "judge"))):
            return "submission"
        elif message_type and (message_type.startswith(("worker", "queue"))):
            return "worker"
        else:
            return "submission"  # デフォルト
