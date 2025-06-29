"""
Queue Consumer
キューコンシューマー - メッセージキューからメッセージを取得

アーキテクチャ図のQConsumerに対応
"""

from abc import ABC, abstractmethod

from .services.queue_service import QMessage


class QConsumer(ABC):
    """
    Queue Consumer interface
    キューコンシューマーインターフェース
    """

    @abstractmethod
    async def pop_message(self) -> QMessage | None:
        """Pop message from message queue"""
        ...

    @abstractmethod
    async def access_message_queue(self) -> bool:
        """Access message queue and check availability"""
        ...


class BaseQConsumer(QConsumer):
    """
    Base Queue Consumer implementation
    基底キューコンシューマー実装
    """

    def __init__(self, queue_connection: str):
        self.queue_connection = queue_connection
        self.is_connected = False

    async def connect(self) -> None:
        """Connect to message queue"""
        # Infrastructure layerで具体的な実装を提供
        self.is_connected = True

    async def disconnect(self) -> None:
        """Disconnect from message queue"""
        self.is_connected = False

    async def access_message_queue(self) -> bool:
        """Access message queue and check availability"""
        if not self.is_connected:
            await self.connect()
        return self.is_connected
