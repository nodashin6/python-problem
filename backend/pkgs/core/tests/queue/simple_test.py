"""
Simple Queue Test
シンプルなキューテスト - 最小限の依存関係
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

# 直接importで依存関係を回避
from ppcore.queue.queue_consumer import QConsumer
from ppcore.queue.queue_dispatcher import QDispatcher
from ppcore.queue.queue_runtime import QRuntime
from ppcore.queue.services.queue_service import BaseQueueService, QMessage, QResponse


class SimpleHelloService(BaseQueueService):
    """Simple Hello Service for testing"""

    def __init__(self):
        super().__init__("hello")

    async def _execute_business_logic(self, message: QMessage) -> QResponse:
        name = message.payload.get("name", "World")
        return QResponse(success=True, result={"greeting": f"Hello, {name}!"})


class MockConsumer(QConsumer):
    """Mock consumer implementation"""

    def __init__(self):
        self.messages = []
        self.current_index = 0

    def add_message(self, msg_id: str, msg_type: str, payload: dict):
        message = QMessage(message_id=msg_id, message_type=msg_type, payload=payload)
        self.messages.append(message)

    async def pop_message(self) -> QMessage | None:
        if self.current_index < len(self.messages):
            msg = self.messages[self.current_index]
            self.current_index += 1
            return msg
        return None

    async def access_message_queue(self) -> bool:
        return True


async def test_queue_system():
    """Test queue system integration"""
    print("Testing Queue System Integration...")

    # Setup components
    consumer = MockConsumer()
    runtime = QRuntime()
    dispatcher = QDispatcher(consumer, runtime)
    hello_service = SimpleHelloService()

    # Register service
    dispatcher.register_service("hello", hello_service)
    print("✓ Service registered")

    # Add test message
    consumer.add_message("test-1", "hello", {"name": "Alice"})
    print("✓ Message added to queue")

    # Process message
    message = await dispatcher.get_next_message()
    assert message is not None
    assert message.message_id == "test-1"
    print("✓ Message retrieved from queue")

    response = await dispatcher.process_message(message)
    assert response.success is True
    assert response.result["greeting"] == "Hello, Alice!"
    print("✓ Message processed successfully")

    # Test unknown service
    consumer.add_message("test-2", "unknown", {})
    message2 = await dispatcher.get_next_message()
    response2 = await dispatcher.process_message(message2)
    assert response2.success is False
    assert "No service" in response2.error
    print("✓ Unknown service handled correctly")

    print("All tests passed! ✅")


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_queue_system())
