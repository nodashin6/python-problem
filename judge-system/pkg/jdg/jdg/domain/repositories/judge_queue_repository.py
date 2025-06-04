"""
Judge Queue Repository interface
ジャッジキューリポジトリインターフェース
"""

import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from ..models import JudgeQueue
from ....const import ExecutionStatus


class JudgeQueueRepository(ABC):
    """ジャッジキューリポジトリのインターフェース"""

    @abstractmethod
    async def save(self, queue_item: JudgeQueue) -> bool:
        """キューアイテムを保存"""
        pass

    @abstractmethod
    async def find_by_id(self, queue_id: uuid.UUID) -> Optional[JudgeQueue]:
        """IDでキューアイテムを検索"""
        pass

    @abstractmethod
    async def find_by_submission(
        self, submission_id: uuid.UUID
    ) -> Optional[JudgeQueue]:
        """提出IDでキューアイテムを検索"""
        pass

    @abstractmethod
    async def find_pending(self, limit: int = 50) -> List[JudgeQueue]:
        """実行待ちのキューアイテムを取得"""
        pass

    @abstractmethod
    async def find_by_priority(
        self, min_priority: int = 0, limit: int = 50
    ) -> List[JudgeQueue]:
        """優先度でキューアイテムを検索"""
        pass

    @abstractmethod
    async def find_by_status(
        self, status: ExecutionStatus, limit: int = 50
    ) -> List[JudgeQueue]:
        """ステータスでキューアイテムを検索"""
        pass

    @abstractmethod
    async def find_by_worker(self, worker_id: str) -> List[JudgeQueue]:
        """ワーカーIDでキューアイテムを検索"""
        pass

    @abstractmethod
    async def find_retry_candidates(self, limit: int = 50) -> List[JudgeQueue]:
        """リトライ対象のキューアイテムを検索"""
        pass

    @abstractmethod
    async def find_stale_items(
        self, before_date: datetime, limit: int = 50
    ) -> List[JudgeQueue]:
        """古いキューアイテムを検索"""
        pass

    @abstractmethod
    async def get_next_item(self, worker_id: str) -> Optional[JudgeQueue]:
        """ワーカーの次のアイテムを取得（アトミックな操作）"""
        pass

    @abstractmethod
    async def assign_to_worker(self, queue_id: uuid.UUID, worker_id: str) -> bool:
        """ワーカーにアイテムを割り当て"""
        pass

    @abstractmethod
    async def release_worker_items(self, worker_id: str) -> int:
        """ワーカーのアイテムを解放"""
        pass

    @abstractmethod
    async def update_status(self, queue_id: uuid.UUID, status: ExecutionStatus) -> bool:
        """ステータスを更新"""
        pass

    @abstractmethod
    async def increment_retry(self, queue_id: uuid.UUID) -> bool:
        """リトライ回数を増加"""
        pass

    @abstractmethod
    async def count_by_status(self, status: ExecutionStatus) -> int:
        """ステータス別のキューアイテム数をカウント"""
        pass

    @abstractmethod
    async def count_pending(self) -> int:
        """実行待ちのアイテム数をカウント"""
        pass

    @abstractmethod
    async def get_queue_statistics(self) -> dict:
        """キューの統計情報を取得"""
        pass

    @abstractmethod
    async def delete(self, queue_id: uuid.UUID) -> bool:
        """キューアイテムを削除"""
        pass

    @abstractmethod
    async def delete_completed(self, before_date: datetime) -> int:
        """完了済みの古いアイテムを削除"""
        pass
