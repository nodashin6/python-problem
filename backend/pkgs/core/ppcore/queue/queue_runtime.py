"""
Queue Runtime
キューランタイム - サービス実行環境

アーキテクチャ図のQRuntimeに対応
"""

import asyncio
import logging
from typing import Any

from .services.queue_service import QMessage, QResponse, QueueService


class QRuntime:
    """
    Queue Runtime
    キューランタイム - サービス実行環境を管理
    """

    def __init__(self, timeout_seconds: int = 30):
        self.timeout_seconds = timeout_seconds
        self.logger = logging.getLogger(self.__class__.__name__)

    async def execute_service(self, service: QueueService, message: QMessage) -> QResponse:
        """Execute service with message in controlled runtime environment"""
        try:
            # Execute with timeout
            response = await asyncio.wait_for(service.execute(message), timeout=self.timeout_seconds)

            self.logger.info(f"Service executed successfully for message type: {message.message_type}")
            return response

        except TimeoutError:
            error_msg = f"Service execution timeout for message type: {message.message_type}"
            self.logger.error(error_msg)
            return QResponse(success=False, error=error_msg)

        except Exception as e:
            error_msg = f"Service execution failed: {e!s}"
            self.logger.error(error_msg)
            return QResponse(success=False, error=error_msg)

    def set_timeout(self, timeout_seconds: int) -> None:
        """Set execution timeout"""
        self.timeout_seconds = timeout_seconds

    def get_runtime_info(self) -> dict[str, Any]:
        """Get runtime information"""
        return {"timeout_seconds": self.timeout_seconds, "runtime_type": self.__class__.__name__}
