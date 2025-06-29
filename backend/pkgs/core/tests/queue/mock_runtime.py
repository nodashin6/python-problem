"""
Mock Queue Runtime
テスト用のモックキューランタイム

テスト用のシンプルなランタイム環境
"""

from ppcore.queue.queue_runtime import QRuntime
from ppcore.queue.services.queue_service import QMessage, QResponse, QueueService


class MockQueueRuntime(QRuntime):
    """
    Mock Queue Runtime - テスト用のモックランタイム
    シンプルなサービス実行環境をシミュレート
    """

    def __init__(self):
        self.execution_count = 0
        self.last_executed_service: QueueService | None = None
        self.last_executed_message: QMessage | None = None
        self.should_fail = False

    async def execute_service(self, service: QueueService, message: QMessage) -> QResponse:
        """Execute service in mock runtime"""
        self.execution_count += 1
        self.last_executed_service = service
        self.last_executed_message = message

        if self.should_fail:
            return QResponse(success=False, error="Mock runtime failure")

        return await service.execute(message)

    # テスト用のヘルパーメソッド
    def reset_counters(self) -> None:
        """Reset execution counters"""
        self.execution_count = 0
        self.last_executed_service = None
        self.last_executed_message = None

    def set_failure_mode(self, should_fail: bool) -> None:
        """Set runtime to fail for testing"""
        self.should_fail = should_fail

    def get_execution_count(self) -> int:
        """Get number of services executed"""
        return self.execution_count
