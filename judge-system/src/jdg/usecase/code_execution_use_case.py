"""
Code Execution Use Cases
コード実行ユースケース
"""

import uuid
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from ..domain.models import CodeExecution, ExecutionResult
from ..domain.repositories.code_execution_repository import CodeExecutionRepository
from ..domain.services.judge_service import JudgeDomainService
from ...const import ProgrammingLanguage as Language, ExecutionStatus


logger = logging.getLogger(__name__)


class CodeExecutionUseCase:
    """コード実行関連のユースケース"""

    def __init__(
        self, execution_repo: CodeExecutionRepository, judge_service: JudgeDomainService
    ):
        self.execution_repo = execution_repo
        self.judge_service = judge_service

    async def execute_code(
        self,
        code: str,
        language: Language,
        input_data: str = "",
        timeout_seconds: int = 30,
        memory_limit_mb: int = 256,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[CodeExecution]:
        """コードを実行"""
        try:
            # コード実行オブジェクトを作成
            execution = CodeExecution(
                id=uuid.uuid4(),
                code=code,
                language=language,
                input_data=input_data,
                status=ExecutionStatus.PENDING,
                created_at=datetime.utcnow(),
                timeout_seconds=timeout_seconds,
                memory_limit_mb=memory_limit_mb,
                metadata=metadata or {},
            )

            # 実行を保存
            success = await self.execution_repo.save(execution)
            if not success:
                logger.error(f"Failed to save code execution: {execution.id}")
                return None

            # ドメインサービスでコード実行
            execution_success = await self.judge_service.execute_code(execution)

            if execution_success:
                # 実行結果を保存
                await self.execution_repo.save(execution)
                logger.info(f"Code executed successfully: {execution.id}")
                return execution
            else:
                logger.error(f"Failed to execute code: {execution.id}")
                return execution  # エラー情報も含めて返す

        except Exception as e:
            logger.error(f"Failed to execute code: {e}")
            return None

    async def get_execution(self, execution_id: uuid.UUID) -> Optional[CodeExecution]:
        """コード実行を取得"""
        return await self.execution_repo.find_by_id(execution_id)

    async def get_executions_by_status(
        self, status: ExecutionStatus, limit: int = 50
    ) -> List[CodeExecution]:
        """ステータス別のコード実行一覧を取得"""
        return await self.execution_repo.find_by_status(status, limit)

    async def get_executions_by_language(
        self, language: Language, limit: int = 50
    ) -> List[CodeExecution]:
        """言語別のコード実行一覧を取得"""
        return await self.execution_repo.find_by_language(language, limit)

    async def get_recent_executions(self, limit: int = 50) -> List[CodeExecution]:
        """最近のコード実行一覧を取得"""
        return await self.execution_repo.find_recent(limit)

    async def get_pending_executions(self, limit: int = 50) -> List[CodeExecution]:
        """実行待ちのコード実行一覧を取得"""
        return await self.execution_repo.find_pending(limit)

    async def get_execution_statistics(
        self, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """実行統計を取得"""
        return await self.execution_repo.get_execution_statistics(start_date, end_date)

    async def cleanup_old_executions(self, days: int = 7) -> int:
        """古いコード実行を削除"""
        try:
            before_date = datetime.utcnow() - timedelta(days=days)
            deleted_count = await self.execution_repo.delete_old_executions(before_date)

            logger.info(f"Cleaned up {deleted_count} old code executions")
            return deleted_count

        except Exception as e:
            logger.error(f"Failed to cleanup old executions: {e}")
            return 0


class JudgeQueueUseCase:
    """ジャッジキュー関連のユースケース"""

    def __init__(self, queue_repo, submission_repo, judge_service):
        from ..domain.repositories.judge_queue_repository import JudgeQueueRepository
        from ..domain.repositories.submission_repository import SubmissionRepository

        self.queue_repo: JudgeQueueRepository = queue_repo
        self.submission_repo: SubmissionRepository = submission_repo
        self.judge_service: JudgeDomainService = judge_service

    async def get_next_submission(self, worker_id: str) -> Optional[uuid.UUID]:
        """ワーカーが処理する次の提出を取得"""
        try:
            queue_item = await self.queue_repo.get_next_item(worker_id)
            if queue_item:
                logger.info(
                    f"Assigned submission {queue_item.submission_id} to worker {worker_id}"
                )
                return queue_item.submission_id

            return None

        except Exception as e:
            logger.error(f"Failed to get next submission for worker {worker_id}: {e}")
            return None

    async def complete_submission(
        self, submission_id: uuid.UUID, worker_id: str
    ) -> bool:
        """提出の処理完了をマーク"""
        try:
            queue_item = await self.queue_repo.find_by_submission(submission_id)
            if not queue_item:
                logger.warning(f"Queue item not found for submission: {submission_id}")
                return False

            if queue_item.worker_id != worker_id:
                logger.warning(
                    f"Worker {worker_id} is not assigned to submission {submission_id}"
                )
                return False

            success = await self.queue_repo.update_status(
                queue_item.id, ExecutionStatus.COMPLETED
            )

            if success:
                logger.info(
                    f"Submission {submission_id} completed by worker {worker_id}"
                )

            return success

        except Exception as e:
            logger.error(f"Failed to complete submission {submission_id}: {e}")
            return False

    async def fail_submission(
        self, submission_id: uuid.UUID, worker_id: str, error_message: str
    ) -> bool:
        """提出の処理失敗をマーク"""
        try:
            queue_item = await self.queue_repo.find_by_submission(submission_id)
            if not queue_item:
                logger.warning(f"Queue item not found for submission: {submission_id}")
                return False

            if queue_item.worker_id != worker_id:
                logger.warning(
                    f"Worker {worker_id} is not assigned to submission {submission_id}"
                )
                return False

            # エラーメッセージを設定
            queue_item.error_message = error_message

            # まずアイテムを保存してエラーメッセージを記録
            await self.queue_repo.save(queue_item)

            # リトライ可能かチェック
            if queue_item.retry_count < queue_item.max_retries:
                # リトライ
                success = await self.queue_repo.increment_retry(queue_item.id)
                if success:
                    logger.info(
                        f"Submission {submission_id} queued for retry (attempt {queue_item.retry_count + 1})"
                    )
            else:
                # リトライ上限に達した場合は失敗として処理
                success = await self.queue_repo.update_status(
                    queue_item.id, ExecutionStatus.FAILED
                )
                if success:
                    logger.warning(
                        f"Submission {submission_id} failed permanently after {queue_item.retry_count} retries"
                    )

            return success

        except Exception as e:
            logger.error(f"Failed to fail submission {submission_id}: {e}")
            return False

    async def release_worker_submissions(self, worker_id: str) -> int:
        """ワーカーの提出を解放"""
        try:
            released_count = await self.queue_repo.release_worker_items(worker_id)
            logger.info(f"Released {released_count} submissions for worker {worker_id}")
            return released_count

        except Exception as e:
            logger.error(f"Failed to release worker submissions for {worker_id}: {e}")
            return 0

    async def get_queue_status(self) -> Dict[str, Any]:
        """キューの状態を取得"""
        try:
            stats = await self.queue_repo.get_queue_statistics()

            # 追加の状態情報
            pending_count = await self.queue_repo.count_pending()
            stats["pending_count"] = pending_count

            return stats

        except Exception as e:
            logger.error(f"Failed to get queue status: {e}")
            return {}

    async def get_retry_candidates(self, limit: int = 50) -> List:
        """リトライ対象のアイテムを取得"""
        return await self.queue_repo.find_retry_candidates(limit)

    async def get_stale_items(self, minutes: int = 30, limit: int = 50) -> List:
        """スタックしたアイテムを取得"""
        before_date = datetime.utcnow() - timedelta(minutes=minutes)
        return await self.queue_repo.find_stale_items(before_date, limit)

    async def cleanup_completed_items(self, days: int = 30) -> int:
        """完了済みの古いアイテムを削除"""
        try:
            before_date = datetime.utcnow() - timedelta(days=days)
            deleted_count = await self.queue_repo.delete_completed(before_date)

            logger.info(f"Cleaned up {deleted_count} completed queue items")
            return deleted_count

        except Exception as e:
            logger.error(f"Failed to cleanup completed items: {e}")
            return 0

    async def reset_stale_items(self, minutes: int = 30) -> int:
        """スタックしたアイテムをリセット"""
        try:
            stale_items = await self.get_stale_items(minutes)
            reset_count = 0

            for item in stale_items:
                # ワーカーから解放してペンディングに戻す
                success = await self.queue_repo.update_status(
                    item.id, ExecutionStatus.PENDING
                )
                if success:
                    # ワーカー情報をクリア
                    item.worker_id = None
                    item.assigned_at = None
                    item.started_at = None
                    await self.queue_repo.save(item)
                    reset_count += 1

            logger.info(f"Reset {reset_count} stale items")
            return reset_count

        except Exception as e:
            logger.error(f"Failed to reset stale items: {e}")
            return 0
