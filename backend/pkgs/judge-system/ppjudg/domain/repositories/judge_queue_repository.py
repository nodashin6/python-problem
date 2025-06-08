"""
Judge Queue Repository interface
ジャッジキューリポジトリインターフェース
"""

import uuid
from abc import ABC, abstractmethod
from datetime import datetime

from ....const import ExecutionStatus
from ..models import JudgeQueue


class JudgeQueueRepository(ABC):
    """ジャッジキューリポジトリのインターフェース"""

    @abstractmethod
    async def save(self, queue_item: JudgeQueue) -> bool:
        """キューアイテムを保存"""

    @abstractmethod
    async def find_by_id(self, queue_id: uuid.UUID) -> JudgeQueue | None:
        """IDでキューアイテムを検索"""

    @abstractmethod
    async def find_by_submission(self, submission_id: uuid.UUID) -> JudgeQueue | None:
        """提出IDでキューアイテムを検索"""

    @abstractmethod
    async def find_pending(self, limit: int = 50) -> list[JudgeQueue]:
        """実行待ちのキューアイテムを取得"""

    @abstractmethod
    async def find_by_priority(
        self, min_priority: int = 0, limit: int = 50
    ) -> list[JudgeQueue]:
        """優先度でキューアイテムを検索"""

    @abstractmethod
    async def find_by_status(
        self, status: ExecutionStatus, limit: int = 50
    ) -> list[JudgeQueue]:
        """ステータスでキューアイテムを検索"""

    @abstractmethod
    async def find_by_worker(self, worker_id: str) -> list[JudgeQueue]:
        """ワーカーIDでキューアイテムを検索"""

    @abstractmethod
    async def find_retry_candidates(self, limit: int = 50) -> list[JudgeQueue]:
        """リトライ対象のキューアイテムを検索"""

    @abstractmethod
    async def find_stale_items(
        self, before_date: datetime, limit: int = 50
    ) -> list[JudgeQueue]:
        """古いキューアイテムを検索"""

    @abstractmethod
    async def get_next_item(self, worker_id: str) -> JudgeQueue | None:
        """ワーカーの次のアイテムを取得 (アトミックな操作)"""

    @abstractmethod
    async def assign_to_worker(self, queue_id: uuid.UUID, worker_id: str) -> bool:
        """ワーカーにアイテムを割り当て"""

    @abstractmethod
    async def release_worker_items(self, worker_id: str) -> int:
        """ワーカーのアイテムを解放"""

    @abstractmethod
    async def update_status(self, queue_id: uuid.UUID, status: ExecutionStatus) -> bool:
        """ステータスを更新"""

    @abstractmethod
    async def increment_retry(self, queue_id: uuid.UUID) -> bool:
        """リトライ回数を増加"""

    @abstractmethod
    async def count_by_status(self, status: ExecutionStatus) -> int:
        """ステータス別のキューアイテム数をカウント"""

    @abstractmethod
    async def count_pending(self) -> int:
        """実行待ちのアイテム数をカウント"""

    @abstractmethod
    async def get_queue_statistics(self) -> dict:
        """キューの統計情報を取得"""

    @abstractmethod
    async def delete(self, queue_id: uuid.UUID) -> bool:
        """キューアイテムを削除"""

    @abstractmethod
    async def delete_completed(self, before_date: datetime) -> int:
        """完了済みの古いアイテムを削除"""
