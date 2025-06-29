"""
Queue Service
キューサービス - アーキテクチャ図のQServiceに対応

Core abstractions for queue-based services
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class QMessage:
    """Queue Message data structure"""

    message_id: str
    message_type: str
    payload: dict[str, Any]
    metadata: dict[str, Any] | None = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class QResponse:
    """Queue Response data structure"""

    success: bool
    result: Any | None = None
    error: str | None = None
    metadata: dict[str, Any] | None = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class QueueService(ABC):
    """
    Base Queue Service interface
    キューサービス基底インターフェース
    """

    @abstractmethod
    async def execute(self, message: QMessage) -> QResponse:
        """Execute service with queue message"""
        ...

    @abstractmethod
    def get_service_type(self) -> str:
        """Get service type identifier"""
        ...

    @abstractmethod
    async def validate_message(self, message: QMessage) -> bool:
        """Validate message format and content"""
        ...


class BaseQueueService(QueueService):
    """
    Base implementation of Queue Service
    キューサービス基底実装
    """

    def __init__(self, service_type: str):
        self.service_type = service_type

    def get_service_type(self) -> str:
        """Get service type identifier"""
        return self.service_type

    async def validate_message(self, message: QMessage) -> bool:
        """Basic message validation"""
        return (
            message.message_id is not None
            and message.message_type is not None
            and message.payload is not None
        )

    async def execute(self, message: QMessage) -> QResponse:
        """Base execute implementation with validation"""
        if not await self.validate_message(message):
            return QResponse(success=False, error="Invalid message format")

        return await self._execute_business_logic(message)

    @abstractmethod
    async def _execute_business_logic(self, message: QMessage) -> QResponse:
        """Execute actual business logic - to be implemented by subclasses"""
        ...
