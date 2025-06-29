"""
Advanced Queue System Tests
高度なキューシステムテスト

複数のユースケースと高度なテストシナリオ
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from ppcore.queue.queue_consumer import QConsumer
from ppcore.queue.queue_dispatcher import QDispatcher
from ppcore.queue.queue_runtime import QRuntime
from ppcore.queue.services.queue_service import BaseQueueService, QMessage, QResponse


class MathCalculatorService(BaseQueueService):
    """Math Calculator Service - 数学計算サービス"""

    def __init__(self):
        super().__init__("math")

    async def _execute_business_logic(self, message: QMessage) -> QResponse:
        operation = message.payload.get("operation")
        a = message.payload.get("a")
        b = message.payload.get("b")

        if operation == "add":
            result = a + b
        elif operation == "multiply":
            result = a * b
        elif operation == "divide":
            if b == 0:
                return QResponse(success=False, error="Division by zero")
            result = a / b
        else:
            return QResponse(success=False, error=f"Unknown operation: {operation}")

        return QResponse(success=True, result={"operation": operation, "a": a, "b": b, "result": result})

    async def validate_message(self, message: QMessage) -> bool:
        if not await super().validate_message(message):
            return False

        payload = message.payload
        required_fields = ["operation", "a", "b"]

        for field in required_fields:
            if field not in payload:
                return False

        if not isinstance(payload["a"], (int, float)):
            return False
        if not isinstance(payload["b"], (int, float)):
            return False
        if payload["operation"] not in ["add", "multiply", "divide"]:
            return False

        return True


class DataProcessingService(BaseQueueService):
    """Data Processing Service - データ処理サービス"""

    def __init__(self):
        super().__init__("data_processing")
        self.processed_count = 0

    async def _execute_business_logic(self, message: QMessage) -> QResponse:
        data_list = message.payload.get("data", [])
        operation = message.payload.get("operation", "count")

        if operation == "count":
            result = len(data_list)
        elif operation == "sum":
            result = sum(data_list) if all(isinstance(x, (int, float)) for x in data_list) else 0
        elif operation == "average":
            if len(data_list) == 0:
                result = 0
            else:
                result = (
                    sum(data_list) / len(data_list)
                    if all(isinstance(x, (int, float)) for x in data_list)
                    else 0
                )
        else:
            return QResponse(success=False, error=f"Unknown operation: {operation}")

        self.processed_count += 1

        return QResponse(
            success=True,
            result={
                "operation": operation,
                "data_count": len(data_list),
                "result": result,
                "processed_total": self.processed_count,
            },
        )


class AdvancedMockConsumer(QConsumer):
    """高度なモックコンシューマー"""

    def __init__(self):
        self.messages = []
        self.current_index = 0
        self.access_count = 0
        self.pop_count = 0

    def add_message(self, msg_id: str, msg_type: str, payload: dict, metadata: dict = None):
        message = QMessage(
            message_id=msg_id, message_type=msg_type, payload=payload, metadata=metadata or {}
        )
        self.messages.append(message)

    async def pop_message(self) -> QMessage | None:
        self.pop_count += 1
        if self.current_index < len(self.messages):
            msg = self.messages[self.current_index]
            self.current_index += 1
            return msg
        return None

    async def access_message_queue(self) -> bool:
        self.access_count += 1
        return True

    def reset_counters(self):
        self.current_index = 0
        self.access_count = 0
        self.pop_count = 0

    def get_stats(self):
        return {
            "total_messages": len(self.messages),
            "processed_messages": self.current_index,
            "remaining_messages": len(self.messages) - self.current_index,
            "access_count": self.access_count,
            "pop_count": self.pop_count,
        }


async def test_math_calculator():
    """Test Math Calculator Service"""
    print("\n=== Testing Math Calculator Service ===")

    service = MathCalculatorService()

    # Test addition
    msg = QMessage("math-1", "math", {"operation": "add", "a": 10, "b": 5})
    response = await service.execute(msg)
    assert response.success is True
    assert response.result["result"] == 15
    print("✓ Addition: 10 + 5 = 15")

    # Test multiplication
    msg = QMessage("math-2", "math", {"operation": "multiply", "a": 7, "b": 8})
    response = await service.execute(msg)
    assert response.success is True
    assert response.result["result"] == 56
    print("✓ Multiplication: 7 * 8 = 56")

    # Test division
    msg = QMessage("math-3", "math", {"operation": "divide", "a": 20, "b": 4})
    response = await service.execute(msg)
    assert response.success is True
    assert response.result["result"] == 5.0
    print("✓ Division: 20 / 4 = 5.0")

    # Test division by zero
    msg = QMessage("math-4", "math", {"operation": "divide", "a": 10, "b": 0})
    response = await service.execute(msg)
    assert response.success is False
    assert "Division by zero" in response.error
    print("✓ Division by zero handled correctly")

    # Test invalid operation (validation should catch this)
    msg = QMessage("math-5", "math", {"operation": "subtract", "a": 10, "b": 5})
    response = await service.execute(msg)
    print(f"Response: {response}")  # Debug output
    assert response.success is False
    assert "Invalid message format" in response.error  # Validation catches this
    print("✓ Invalid operation caught by validation")


async def test_data_processing():
    """Test Data Processing Service"""
    print("\n=== Testing Data Processing Service ===")

    service = DataProcessingService()

    # Test count operation
    msg = QMessage("data-1", "data_processing", {"data": [1, 2, 3, 4, 5], "operation": "count"})
    response = await service.execute(msg)
    assert response.success is True
    assert response.result["result"] == 5
    assert response.result["processed_total"] == 1
    print("✓ Count operation: [1,2,3,4,5] = 5 items")

    # Test sum operation
    msg = QMessage("data-2", "data_processing", {"data": [10, 20, 30], "operation": "sum"})
    response = await service.execute(msg)
    assert response.success is True
    assert response.result["result"] == 60
    assert response.result["processed_total"] == 2
    print("✓ Sum operation: [10,20,30] = 60")

    # Test average operation
    msg = QMessage("data-3", "data_processing", {"data": [2, 4, 6, 8], "operation": "average"})
    response = await service.execute(msg)
    assert response.success is True
    assert response.result["result"] == 5.0
    assert response.result["processed_total"] == 3
    print("✓ Average operation: [2,4,6,8] = 5.0")


async def test_full_system_integration():
    """Test full system integration with multiple services"""
    print("\n=== Testing Full System Integration ===")

    # Setup
    consumer = AdvancedMockConsumer()
    runtime = QRuntime()
    dispatcher = QDispatcher(consumer, runtime)

    # Register services
    math_service = MathCalculatorService()
    data_service = DataProcessingService()
    dispatcher.register_service("math", math_service)
    dispatcher.register_service("data_processing", data_service)

    # Add various messages
    consumer.add_message("msg-1", "math", {"operation": "add", "a": 100, "b": 200})
    consumer.add_message("msg-2", "data_processing", {"data": [1, 2, 3, 4, 5], "operation": "sum"})
    consumer.add_message("msg-3", "math", {"operation": "multiply", "a": 12, "b": 8})
    consumer.add_message("msg-4", "data_processing", {"data": [10, 20, 30, 40], "operation": "average"})
    consumer.add_message("msg-5", "unknown_service", {"test": "data"})  # This should fail

    results = []

    # Process all messages
    while True:
        message = await dispatcher.get_next_message()
        if message is None:
            break

        response = await dispatcher.process_message(message)
        results.append(
            {
                "message_id": message.message_id,
                "message_type": message.message_type,
                "success": response.success,
                "result": response.result,
                "error": response.error,
            }
        )

    # Verify results
    assert len(results) == 5

    # Check math results
    assert results[0]["success"] is True
    assert results[0]["result"]["result"] == 300  # 100 + 200
    print("✓ Math service: 100 + 200 = 300")

    # Check data processing results
    assert results[1]["success"] is True
    assert results[1]["result"]["result"] == 15  # sum([1,2,3,4,5])
    print("✓ Data service: sum([1,2,3,4,5]) = 15")

    # Check multiplication
    assert results[2]["success"] is True
    assert results[2]["result"]["result"] == 96  # 12 * 8
    print("✓ Math service: 12 * 8 = 96")

    # Check average
    assert results[3]["success"] is True
    assert results[3]["result"]["result"] == 25.0  # average([10,20,30,40])
    print("✓ Data service: average([10,20,30,40]) = 25.0")

    # Check unknown service failure
    assert results[4]["success"] is False
    assert "No service" in results[4]["error"]
    print("✓ Unknown service rejected correctly")

    # Check consumer stats
    stats = consumer.get_stats()
    assert stats["total_messages"] == 5
    assert stats["processed_messages"] == 5
    assert stats["remaining_messages"] == 0
    print(f"✓ Consumer stats: {stats}")


async def test_queue_runtime_timeout():
    """Test queue runtime timeout functionality"""
    print("\n=== Testing Queue Runtime Timeout ===")

    class SlowService(BaseQueueService):
        def __init__(self):
            super().__init__("slow")

        async def _execute_business_logic(self, message: QMessage) -> QResponse:
            # Simulate slow processing
            await asyncio.sleep(2)  # 2 seconds
            return QResponse(success=True, result={"processed": True})

    runtime = QRuntime(timeout_seconds=1)  # 1 second timeout
    service = SlowService()
    message = QMessage("slow-1", "slow", {})

    response = await runtime.execute_service(service, message)
    assert response.success is False
    assert "timeout" in response.error.lower()
    print("✓ Timeout handled correctly")


async def main():
    """Run all tests"""
    print("Starting Advanced Queue System Tests...")

    try:
        await test_math_calculator()
        await test_data_processing()
        await test_full_system_integration()
        await test_queue_runtime_timeout()

        print("\n🎉 All Advanced Tests Passed Successfully! 🎉")

    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
