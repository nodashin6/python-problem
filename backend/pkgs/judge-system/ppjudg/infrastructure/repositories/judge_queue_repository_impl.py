"""
Judge Queue Repository implementation using Supabase
ジャッジキューリポジトリのSupabase実装
"""

import logging
import uuid
from datetime import datetime
from typing import Any

from supabase import Client

from ....const import ExecutionStatus
from ...domain.models import JudgeQueue
from ...domain.repositories.judge_queue_repository import JudgeQueueRepository

logger = logging.getLogger(__name__)


class JudgeQueueRepositoryImpl(JudgeQueueRepository):
    """Supabaseを使ったジャッジキューリポジトリの実装"""

    def __init__(self, supabase_client: Client):
        self.client = supabase_client

    async def save(self, queue_item: JudgeQueue) -> bool:
        """キューアイテムを保存"""
        try:
            data = {
                "id": str(queue_item.id),
                "submission_id": str(queue_item.submission_id),
                "priority": queue_item.priority,
                "status": queue_item.status.value,
                "worker_id": queue_item.worker_id,
                "retry_count": queue_item.retry_count,
                "max_retries": queue_item.max_retries,
                "created_at": queue_item.created_at.isoformat(),
                "assigned_at": (
                    queue_item.assigned_at.isoformat()
                    if queue_item.assigned_at
                    else None
                ),
                "started_at": (
                    queue_item.started_at.isoformat() if queue_item.started_at else None
                ),
                "completed_at": (
                    queue_item.completed_at.isoformat()
                    if queue_item.completed_at
                    else None
                ),
                "error_message": queue_item.error_message,
                "metadata": queue_item.metadata,
            }

            # 既存レコードがあるかチェック
            existing = (
                self.client.table("judge_queue")
                .select("id")
                .eq("id", str(queue_item.id))
                .execute()
            )

            if existing.data:
                # 更新
                result = (
                    self.client.table("judge_queue")
                    .update(data)
                    .eq("id", str(queue_item.id))
                    .execute()
                )
            else:
                # 新規作成
                result = self.client.table("judge_queue").insert(data).execute()

            logger.info(f"Judge queue item saved successfully: {queue_item.id}")
            return True

        except Exception as e:
            logger.error(f"Failed to save judge queue item {queue_item.id}: {e}")
            return False

    async def find_by_id(self, queue_id: uuid.UUID) -> JudgeQueue | None:
        """IDでキューアイテムを検索"""
        try:
            result = (
                self.client.table("judge_queue")
                .select("*")
                .eq("id", str(queue_id))
                .execute()
            )

            if not result.data:
                return None

            return self._map_to_judge_queue(result.data[0])

        except Exception as e:
            logger.error(f"Failed to find judge queue item by id {queue_id}: {e}")
            return None

    async def find_by_submission(self, submission_id: uuid.UUID) -> JudgeQueue | None:
        """提出IDでキューアイテムを検索"""
        try:
            result = (
                self.client.table("judge_queue")
                .select("*")
                .eq("submission_id", str(submission_id))
                .execute()
            )

            if not result.data:
                return None

            return self._map_to_judge_queue(result.data[0])

        except Exception as e:
            logger.error(
                f"Failed to find judge queue item by submission {submission_id}: {e}"
            )
            return None

    async def find_pending(self, limit: int = 50) -> list[JudgeQueue]:
        """実行待ちのキューアイテムを取得"""
        try:
            result = (
                self.client.table("judge_queue")
                .select("*")
                .eq("status", ExecutionStatus.PENDING.value)
                .order("priority", desc=True)  # 高優先度から
                .order("created_at")  # 古いものから
                .limit(limit)
                .execute()
            )

            queue_items = []
            for data in result.data:
                queue_item = self._map_to_judge_queue(data)
                queue_items.append(queue_item)

            return queue_items

        except Exception as e:
            logger.error(f"Failed to find pending judge queue items: {e}")
            return []

    async def find_by_priority(
        self, min_priority: int = 0, limit: int = 50
    ) -> list[JudgeQueue]:
        """優先度でキューアイテムを検索"""
        try:
            result = (
                self.client.table("judge_queue")
                .select("*")
                .gte("priority", min_priority)
                .order("priority", desc=True)
                .order("created_at")
                .limit(limit)
                .execute()
            )

            queue_items = []
            for data in result.data:
                queue_item = self._map_to_judge_queue(data)
                queue_items.append(queue_item)

            return queue_items

        except Exception as e:
            logger.error(
                f"Failed to find judge queue items by priority {min_priority}: {e}"
            )
            return []

    async def find_by_status(
        self, status: ExecutionStatus, limit: int = 50
    ) -> list[JudgeQueue]:
        """ステータスでキューアイテムを検索"""
        try:
            result = (
                self.client.table("judge_queue")
                .select("*")
                .eq("status", status.value)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )

            queue_items = []
            for data in result.data:
                queue_item = self._map_to_judge_queue(data)
                queue_items.append(queue_item)

            return queue_items

        except Exception as e:
            logger.error(f"Failed to find judge queue items by status {status}: {e}")
            return []

    async def find_by_worker(self, worker_id: str) -> list[JudgeQueue]:
        """ワーカーIDでキューアイテムを検索"""
        try:
            result = (
                self.client.table("judge_queue")
                .select("*")
                .eq("worker_id", worker_id)
                .order("assigned_at", desc=True)
                .execute()
            )

            queue_items = []
            for data in result.data:
                queue_item = self._map_to_judge_queue(data)
                queue_items.append(queue_item)

            return queue_items

        except Exception as e:
            logger.error(f"Failed to find judge queue items by worker {worker_id}: {e}")
            return []

    async def find_retry_candidates(self, limit: int = 50) -> list[JudgeQueue]:
        """リトライ対象のキューアイテムを検索"""
        try:
            # ステータスがFAILEDで、リトライ回数が上限未満のもの
            result = (
                self.client.table("judge_queue")
                .select("*")
                .eq("status", ExecutionStatus.FAILED.value)
                .filter("retry_count", "lt", "max_retries")
                .order("created_at")
                .limit(limit)
                .execute()
            )

            queue_items = []
            for data in result.data:
                queue_item = self._map_to_judge_queue(data)
                queue_items.append(queue_item)

            return queue_items

        except Exception as e:
            logger.error(f"Failed to find retry candidates: {e}")
            return []

    async def find_stale_items(
        self, before_date: datetime, limit: int = 50
    ) -> list[JudgeQueue]:
        """古いキューアイテムを検索"""
        try:
            # RUNNINGステータスで指定時間より古いもの (スタックしている可能性)
            result = (
                self.client.table("judge_queue")
                .select("*")
                .eq("status", ExecutionStatus.RUNNING.value)
                .lt("started_at", before_date.isoformat())
                .order("started_at")
                .limit(limit)
                .execute()
            )

            queue_items = []
            for data in result.data:
                queue_item = self._map_to_judge_queue(data)
                queue_items.append(queue_item)

            return queue_items

        except Exception as e:
            logger.error(f"Failed to find stale items: {e}")
            return []

    async def get_next_item(self, worker_id: str) -> JudgeQueue | None:
        """ワーカーの次のアイテムを取得 (アトミックな操作)"""
        try:
            # まずペンディングアイテムを取得
            pending_items = await self.find_pending(limit=1)

            if not pending_items:
                return None

            queue_item = pending_items[0]

            # ワーカーに割り当て
            success = await self.assign_to_worker(queue_item.id, worker_id)

            if success:
                # 更新されたアイテムを取得
                return await self.find_by_id(queue_item.id)

            return None

        except Exception as e:
            logger.error(f"Failed to get next item for worker {worker_id}: {e}")
            return None

    async def assign_to_worker(self, queue_id: uuid.UUID, worker_id: str) -> bool:
        """ワーカーにアイテムを割り当て"""
        try:
            data = {
                "worker_id": worker_id,
                "status": ExecutionStatus.RUNNING.value,
                "assigned_at": datetime.utcnow().isoformat(),
                "started_at": datetime.utcnow().isoformat(),
            }

            # ペンディング状態のアイテムのみ更新
            result = (
                self.client.table("judge_queue")
                .update(data)
                .eq("id", str(queue_id))
                .eq("status", ExecutionStatus.PENDING.value)
                .execute()
            )

            return len(result.data) > 0

        except Exception as e:
            logger.error(
                f"Failed to assign queue item {queue_id} to worker {worker_id}: {e}"
            )
            return False

    async def release_worker_items(self, worker_id: str) -> int:
        """ワーカーのアイテムを解放"""
        try:
            # 実行中のアイテムをペンディングに戻す
            data = {
                "worker_id": None,
                "status": ExecutionStatus.PENDING.value,
                "assigned_at": None,
                "started_at": None,
            }

            result = (
                self.client.table("judge_queue")
                .update(data)
                .eq("worker_id", worker_id)
                .eq("status", ExecutionStatus.RUNNING.value)
                .execute()
            )

            released_count = len(result.data)
            logger.info(f"Released {released_count} items for worker {worker_id}")
            return released_count

        except Exception as e:
            logger.error(f"Failed to release worker items for {worker_id}: {e}")
            return 0

    async def update_status(self, queue_id: uuid.UUID, status: ExecutionStatus) -> bool:
        """ステータスを更新"""
        try:
            data = {"status": status.value}

            # 完了系ステータスの場合は完了時刻を設定
            if status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED]:
                data["completed_at"] = datetime.utcnow().isoformat()

            result = (
                self.client.table("judge_queue")
                .update(data)
                .eq("id", str(queue_id))
                .execute()
            )

            return len(result.data) > 0

        except Exception as e:
            logger.error(f"Failed to update status for queue item {queue_id}: {e}")
            return False

    async def increment_retry(self, queue_id: uuid.UUID) -> bool:
        """リトライ回数を増加"""
        try:
            # 現在のリトライ回数を取得
            current = await self.find_by_id(queue_id)
            if not current:
                return False

            new_retry_count = current.retry_count + 1

            data = {
                "retry_count": new_retry_count,
                "status": ExecutionStatus.PENDING.value,
                "worker_id": None,
                "assigned_at": None,
                "started_at": None,
                "error_message": None,
            }

            result = (
                self.client.table("judge_queue")
                .update(data)
                .eq("id", str(queue_id))
                .execute()
            )

            return len(result.data) > 0

        except Exception as e:
            logger.error(f"Failed to increment retry for queue item {queue_id}: {e}")
            return False

    async def count_by_status(self, status: ExecutionStatus) -> int:
        """ステータス別のキューアイテム数をカウント"""
        try:
            result = (
                self.client.table("judge_queue")
                .select("id", count="exact")
                .eq("status", status.value)
                .execute()
            )

            return result.count or 0

        except Exception as e:
            logger.error(f"Failed to count queue items by status {status}: {e}")
            return 0

    async def count_pending(self) -> int:
        """実行待ちのアイテム数をカウント"""
        return await self.count_by_status(ExecutionStatus.PENDING)

    async def get_queue_statistics(self) -> dict:
        """キューの統計情報を取得"""
        try:
            stats = {}

            # ステータス別カウント
            for status in ExecutionStatus:
                count = await self.count_by_status(status)
                stats[f"{status.value}_count"] = count

            # 総アイテム数
            total_result = (
                self.client.table("judge_queue").select("id", count="exact").execute()
            )
            stats["total_items"] = total_result.count or 0

            # 平均処理時間 (完了したアイテムのみ)
            completed_result = (
                self.client.table("judge_queue")
                .select("started_at, completed_at")
                .eq("status", ExecutionStatus.COMPLETED.value)
                .not_.is_("started_at", "null")
                .not_.is_("completed_at", "null")
                .execute()
            )

            if completed_result.data:
                processing_times = []
                for data in completed_result.data:
                    started = datetime.fromisoformat(data["started_at"])
                    completed = datetime.fromisoformat(data["completed_at"])
                    processing_time = (completed - started).total_seconds()
                    processing_times.append(processing_time)

                if processing_times:
                    stats["avg_processing_time"] = sum(processing_times) / len(
                        processing_times
                    )
                    stats["max_processing_time"] = max(processing_times)
                    stats["min_processing_time"] = min(processing_times)

            # リトライ統計
            retry_result = (
                self.client.table("judge_queue")
                .select("retry_count")
                .gt("retry_count", 0)
                .execute()
            )

            stats["items_with_retries"] = len(retry_result.data)
            if retry_result.data:
                retry_counts = [data["retry_count"] for data in retry_result.data]
                stats["avg_retry_count"] = sum(retry_counts) / len(retry_counts)

            return stats

        except Exception as e:
            logger.error(f"Failed to get queue statistics: {e}")
            return {}

    async def delete(self, queue_id: uuid.UUID) -> bool:
        """キューアイテムを削除"""
        try:
            result = (
                self.client.table("judge_queue")
                .delete()
                .eq("id", str(queue_id))
                .execute()
            )

            logger.info(f"Judge queue item deleted successfully: {queue_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete judge queue item {queue_id}: {e}")
            return False

    async def delete_completed(self, before_date: datetime) -> int:
        """完了済みの古いアイテムを削除"""
        try:
            # まず削除対象のレコード数を取得
            count_result = (
                self.client.table("judge_queue")
                .select("id", count="exact")
                .eq("status", ExecutionStatus.COMPLETED.value)
                .lt("completed_at", before_date.isoformat())
                .execute()
            )

            delete_count = count_result.count or 0

            if delete_count > 0:
                # 実際に削除
                self.client.table("judge_queue").delete().eq(
                    "status", ExecutionStatus.COMPLETED.value
                ).lt("completed_at", before_date.isoformat()).execute()

                logger.info(
                    f"Deleted {delete_count} completed queue items before {before_date}"
                )

            return delete_count

        except Exception as e:
            logger.error(f"Failed to delete completed queue items: {e}")
            return 0

    def _map_to_judge_queue(self, data: dict[str, Any]) -> JudgeQueue:
        """データベースレコードをJudgeQueueオブジェクトにマップ"""
        return JudgeQueue(
            id=uuid.UUID(data["id"]),
            submission_id=uuid.UUID(data["submission_id"]),
            priority=data.get("priority", 0),
            status=ExecutionStatus(data["status"]),
            worker_id=data.get("worker_id"),
            retry_count=data.get("retry_count", 0),
            max_retries=data.get("max_retries", 3),
            created_at=datetime.fromisoformat(data["created_at"]),
            assigned_at=(
                datetime.fromisoformat(data["assigned_at"])
                if data.get("assigned_at")
                else None
            ),
            started_at=(
                datetime.fromisoformat(data["started_at"])
                if data.get("started_at")
                else None
            ),
            completed_at=(
                datetime.fromisoformat(data["completed_at"])
                if data.get("completed_at")
                else None
            ),
            error_message=data.get("error_message"),
            metadata=data.get("metadata", {}),
        )
