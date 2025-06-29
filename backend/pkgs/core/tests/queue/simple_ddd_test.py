"""
Simple DDD Test
シンプルなDDDテスト - 最小構成
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

# 直接importを試す
try:
    from tests.queue.mock_pydddi import IUseCase, IUseCaseCommand, IUseCaseResult

    print("✓ mock_pydddi imported successfully")
except Exception as e:
    print(f"✗ mock_pydddi import failed: {e}")
    exit(1)

try:
    from ppcore.queue.services.queue_service import BaseQueueService, QMessage, QResponse

    print("✓ queue_service imported successfully")
except Exception as e:
    print(f"✗ queue_service import failed: {e}")
    exit(1)

# 直接定義
from dataclasses import dataclass


@dataclass
class TestCommand(IUseCaseCommand):
    name: str = "Test"


@dataclass
class TestResult(IUseCaseResult):
    message: str


class TestUseCase(IUseCase[TestCommand, TestResult], BaseQueueService):
    def __init__(self):
        BaseQueueService.__init__(self, "test")

    async def execute(self, command: TestCommand) -> TestResult:
        return TestResult(message=f"Hello {command.name}!")

    async def _execute_business_logic(self, message: QMessage) -> QResponse:
        name = message.payload.get("name", "World")
        command = TestCommand(name=name)
        result = await self.execute(command)
        return QResponse(success=True, result={"message": result.message})


async def main():
    print("Testing DDD Integration...")

    usecase = TestUseCase()

    # Test DDD execution
    command = TestCommand(name="DDD")
    result = await usecase.execute(command)
    print(f"✓ DDD Result: {result}")

    # Test Queue execution
    message = QMessage("test-1", "test", {"name": "Queue"})
    response = await usecase._execute_business_logic(message)
    print(f"✓ Queue Response: {response}")

    print("🎉 DDD Integration Test Successful!")


if __name__ == "__main__":
    asyncio.run(main())
