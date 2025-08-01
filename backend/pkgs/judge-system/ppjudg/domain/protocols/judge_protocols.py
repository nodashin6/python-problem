"""
Judge Domain Protocols
ジャッジドメインプロトコル - インフラストラクチャに依存しない抽象化
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class EventBus(ABC):
    """
    Event Bus Protocol
    イベントバスプロトコル
    """

    @abstractmethod
    async def publish_event(self, event_name: str, data: Dict[str, Any]) -> None:
        """Publish an event"""
        pass

    @abstractmethod
    async def subscribe_to_event(self, event_name: str, handler) -> None:
        """Subscribe to an event"""
        pass


class DomainEvent(ABC):
    """
    Domain Event Protocol
    ドメインイベントプロトコル
    """

    @abstractmethod
    def get_event_name(self) -> str:
        """Get event name"""
        pass

    @abstractmethod
    def get_event_data(self) -> Dict[str, Any]:
        """Get event data"""
        pass


class Logger(ABC):
    """
    Logger Protocol
    ログ出力プロトコル
    """

    @abstractmethod
    def info(self, message: str) -> None:
        """Log info message"""
        pass

    @abstractmethod
    def warning(self, message: str) -> None:
        """Log warning message"""
        pass

    @abstractmethod
    def error(self, message: str) -> None:
        """Log error message"""
        pass

    @abstractmethod
    def debug(self, message: str) -> None:
        """Log debug message"""
        pass