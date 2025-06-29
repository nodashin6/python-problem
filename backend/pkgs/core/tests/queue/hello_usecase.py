"""
Hello UseCase
テスト用のシンプルなHello UseCase実装

DDDパターンとQueue Serviceの統合実装例
"""

from dataclasses import dataclass

from ppcore.queue.services.queue_service import BaseQueueService, QMessage, QResponse

# Mock pydddi implementation for testing
from .mock_pydddi import (
    IUseCase,
    IUseCaseCommand,
    IUseCaseResult,
)


@dataclass
class HelloCommand(IUseCaseCommand):
    """Hello Command - DDDのCommandパターン"""

    name: str = "World"


@dataclass
class HelloResult(IUseCaseResult):
    """Hello Result - DDDのResultパターン"""

    greeting: str
    processed_by: str


class HelloUseCase(IUseCase[HelloCommand, HelloResult], BaseQueueService):
    """
    Hello UseCase - DDDパターンとQueue Serviceの統合実装
    pydddiのIUseCaseインターフェースとQueue Serviceを両方継承
    """

    def __init__(self):
        BaseQueueService.__init__(self, "hello")

    async def execute(self, command: HelloCommand) -> HelloResult:
        """DDDパターンのUseCase実行"""
        greeting = f"Hello, {command.name}!"

        return HelloResult(greeting=greeting, processed_by="HelloUseCase")

    async def _execute_business_logic(self, message: QMessage) -> QResponse:
        """Queue Service用のビジネスロジック実行"""
        # QMessageからCommandを構築
        name = message.payload.get("name", "World")
        command = HelloCommand(name=name)

        # DDDのexecuteメソッドを呼び出し
        result = await self.execute(command)

        # ResultをQResponseに変換
        return QResponse(
            success=True,
            result={"greeting": result.greeting},
            metadata={"processed_by": result.processed_by},
        )

    async def validate_message(self, message: QMessage) -> bool:
        """Validate Hello message format"""
        if not await super().validate_message(message):
            return False

        # Hello messageは"name"フィールドを持つべき(任意)
        return isinstance(message.payload.get("name"), str) or message.payload.get("name") is None


class ErrorUseCase(BaseQueueService):
    """
    Error UseCase - エラーケーステスト用
    常にエラーを返すユースケース
    """

    def __init__(self):
        super().__init__("error")

    async def _execute_business_logic(self, message: QMessage) -> QResponse:
        """Error business logic - always fails"""
        _ = message  # Suppress unused warning
        return QResponse(
            success=False, error="Intentional error for testing", metadata={"processed_by": "ErrorUseCase"}
        )
