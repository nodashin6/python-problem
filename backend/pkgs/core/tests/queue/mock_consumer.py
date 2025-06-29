"""
Mock Queue Consumer
テスト用のモックキューコンシューマー

テスト用にメッセージキューをシミュレート
"""

from collections import deque
from typing import Any

from ppcore.queue.queue_consumer import QConsumer
from ppcore.queue.services.queue_service import QMessage


class MockQueueConsumer(QConsumer):
    """
    Mock Queue Consumer - テスト用のモックコンシューマー
    メモリ内でメッセージキューをシミュレート
    """

    def __init__(self):
        self.message_queue: deque[QMessage] = deque()
        self.is_available = True

    async def pop_message(self) -> QMessage | None:
        """Pop message from mock queue"""
        if self.message_queue:
            return self.message_queue.popleft()
        return None

    async def access_message_queue(self) -> bool:
        """Check mock queue availability"""
        return self.is_available

    # テスト用のヘルパーメソッド
    def add_message(
        self,
        message_id: str,
        message_type: str,
        payload: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Add message to mock queue for testing"""
        message = QMessage(
            message_id=message_id, message_type=message_type, payload=payload, metadata=metadata
        )
        self.message_queue.append(message)

    def clear_queue(self) -> None:
        """Clear all messages from mock queue"""
        self.message_queue.clear()

    def queue_size(self) -> int:
        """Get current queue size"""
        return len(self.message_queue)

    def set_availability(self, available: bool) -> None:
        """Set queue availability for testing"""
        self.is_available = available
