"""
DDD Hello UseCase Test
DDDパターンのHello UseCaseテスト

pydddiとQueue Systemの統合テスト
"""

import asyncio
import importlib.util
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from ppcore.queue.services.queue_service import QMessage

# Load hello_usecase module dynamically
spec = importlib.util.spec_from_file_location(
    "hello_usecase", os.path.join(os.path.dirname(__file__), "hello_usecase.py")
)
hello_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hello_module)

HelloCommand = hello_module.HelloCommand
HelloResult = hello_module.HelloResult
HelloUseCase = hello_module.HelloUseCase


async def test_ddd_hello_usecase():
    """Test DDD pattern Hello UseCase"""
    print("=== Testing DDD Hello UseCase ===")

    usecase = HelloUseCase()

    # Test 1: DDDパターンでの直接実行
    print("\n1. DDD Pattern Direct Execution:")
    command = HelloCommand(name="Alice")
    result = await usecase.execute(command)

    assert isinstance(result, HelloResult)
    assert result.greeting == "Hello, Alice!"
    assert result.processed_by == "HelloUseCase"
    print(f"✓ Command: {command}")
    print(f"✓ Result: {result}")

    # Test 2: デフォルト名での実行
    print("\n2. Default Name Execution:")
    default_command = HelloCommand()  # name="World"がデフォルト
    default_result = await usecase.execute(default_command)

    assert default_result.greeting == "Hello, World!"
    print(f"✓ Default Command: {default_command}")
    print(f"✓ Default Result: {default_result}")

    # Test 3: Queue Serviceとしての実行
    print("\n3. Queue Service Execution:")
    message = QMessage(message_id="ddd-test-1", message_type="hello", payload={"name": "Bob"})

    response = await usecase._execute_business_logic(message)

    assert response.success is True
    assert response.result["greeting"] == "Hello, Bob!"
    assert response.metadata["processed_by"] == "HelloUseCase"
    print(f"✓ QMessage: {message}")
    print(f"✓ QResponse: {response}")

    # Test 4: Queue ServiceとDDDパターンの結果が一致することを確認
    print("\n4. Consistency Check:")
    ddd_result = await usecase.execute(HelloCommand(name="Charlie"))
    queue_response = await usecase._execute_business_logic(QMessage("test", "hello", {"name": "Charlie"}))

    assert ddd_result.greeting == queue_response.result["greeting"]
    assert ddd_result.processed_by == queue_response.metadata["processed_by"]
    print("✓ DDD and Queue Service results are consistent")

    print("\n🎉 All DDD Hello UseCase Tests Passed! 🎉")


async def test_usecase_as_queue_service():
    """Test HelloUseCase as part of queue system"""
    print("\n=== Testing HelloUseCase in Queue System ===")

    # Import queue components
    from ppcore.queue.queue_consumer import QConsumer
    from ppcore.queue.queue_dispatcher import QDispatcher
    from ppcore.queue.queue_runtime import QRuntime

    # Mock Consumer
    class SimpleMockConsumer(QConsumer):
        def __init__(self):
            self.messages = []
            self.index = 0

        def add_message(self, msg_id: str, msg_type: str, payload: dict):
            message = QMessage(msg_id, msg_type, payload)
            self.messages.append(message)

        async def pop_message(self) -> QMessage | None:
            if self.index < len(self.messages):
                msg = self.messages[self.index]
                self.index += 1
                return msg
            return None

        async def access_message_queue(self) -> bool:
            return True

    # Setup queue system
    consumer = SimpleMockConsumer()
    runtime = QRuntime()
    dispatcher = QDispatcher(consumer, runtime)
    hello_usecase = HelloUseCase()

    # Register DDD UseCase as Queue Service
    dispatcher.register_service("hello", hello_usecase)
    print("✓ DDD UseCase registered as Queue Service")

    # Add test messages
    consumer.add_message("ddd-1", "hello", {"name": "DDD-Alice"})
    consumer.add_message("ddd-2", "hello", {"name": "DDD-Bob"})
    consumer.add_message("ddd-3", "hello", {})  # Default name

    # Process messages
    results = []
    while True:
        message = await dispatcher.get_next_message()
        if message is None:
            break

        response = await dispatcher.process_message(message)
        results.append((message.payload.get("name", "World"), response.result["greeting"]))
        print(f"✓ Processed: {message.payload} -> {response.result['greeting']}")

    # Verify results
    expected = [
        ("DDD-Alice", "Hello, DDD-Alice!"),
        ("DDD-Bob", "Hello, DDD-Bob!"),
        ("World", "Hello, World!"),
    ]

    assert results == expected
    print("✓ All queue messages processed correctly through DDD UseCase")

    print("\n🎉 Queue System Integration with DDD UseCase Successful! 🎉")


async def main():
    """Run all DDD tests"""
    print("Starting DDD Hello UseCase Tests...")

    try:
        await test_ddd_hello_usecase()
        await test_usecase_as_queue_service()

        print("\n" + "=" * 60)
        print("🚀 ALL DDD TESTS COMPLETED SUCCESSFULLY! 🚀")
        print("=" * 60)
        print("Key Achievements:")
        print("✅ DDDパターン(Command/Result)の実装")
        print("✅ pydddi IUseCaseインターフェースの継承")
        print("✅ Queue ServiceとDDDパターンの統合")
        print("✅ 両方の実行パスで一貫した結果")
        print("✅ Queue Systemでの完全な動作確認")

    except Exception as e:
        print(f"\n❌ DDD Test Failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
