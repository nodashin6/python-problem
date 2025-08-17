"""
Queue System Integration Tests
キューシステム統合テスト

QueueConsumer, QueueDispatcher, QueueServiceの統合テスト
"""

import pytest

from ppcore.queue.queue_dispatcher import QDispatcher
from ppcore.queue.services.queue_service import QMessage

from .hello_usecase import ErrorUseCase, HelloUseCase
from .mock_consumer import MockQueueConsumer
from .mock_runtime import MockQueueRuntime


class TestQueueSystemIntegration:
    """Queue System Integration Test Suite"""

    @pytest.fixture
    def consumer(self):
        """Create mock consumer"""
        return MockQueueConsumer()

    @pytest.fixture
    def runtime(self):
        """Create mock runtime"""
        return MockQueueRuntime()

    @pytest.fixture
    def dispatcher(self, consumer, runtime):
        """Create dispatcher with mocked dependencies"""
        return QDispatcher(consumer, runtime)

    @pytest.fixture
    def hello_service(self):
        """Create Hello UseCase service"""
        return HelloUseCase()

    @pytest.fixture
    def error_service(self):
        """Create Error UseCase service"""
        return ErrorUseCase()

    async def test_dispatcher_service_registration(self, dispatcher, hello_service):
        """Test dispatcher service registration"""
        # サービスを登録
        dispatcher.register_service("hello", hello_service)

        # 登録されたかチェック
        assert "hello" in dispatcher.services
        assert dispatcher.services["hello"] == hello_service

    async def test_consumer_message_handling(self, consumer):
        """Test queue consumer message operations"""
        # 初期状態はキューが空
        assert consumer.queue_size() == 0
        assert await consumer.pop_message() is None

        # メッセージ追加
        consumer.add_message("msg-1", "hello", {"name": "Alice"})
        assert consumer.queue_size() == 1

        # メッセージ取得
        message = await consumer.pop_message()
        assert message is not None
        assert message.message_id == "msg-1"
        assert message.message_type == "hello"
        assert message.payload["name"] == "Alice"

        # キューが空になった
        assert consumer.queue_size() == 0
        assert await consumer.pop_message() is None

    async def test_hello_usecase_execution(self, hello_service):
        """Test Hello UseCase execution"""
        # 正常ケース
        message = QMessage(message_id="test-1", message_type="hello", payload={"name": "Bob"})

        response = await hello_service.execute(message)
        assert response.success is True
        assert response.result["greeting"] == "Hello, Bob!"
        assert response.metadata["processed_by"] == "HelloUseCase"

        # デフォルト名ケース
        message_default = QMessage(message_id="test-2", message_type="hello", payload={})

        response_default = await hello_service.execute(message_default)
        assert response_default.success is True
        assert response_default.result["greeting"] == "Hello, World!"

    async def test_hello_usecase_validation(self, hello_service):
        """Test Hello UseCase message validation"""
        # 有効なメッセージ
        valid_message = QMessage(message_id="test-1", message_type="hello", payload={"name": "Charlie"})
        assert await hello_service.validate_message(valid_message) is True

        # 名前なしでも有効
        no_name_message = QMessage(message_id="test-2", message_type="hello", payload={})
        assert await hello_service.validate_message(no_name_message) is True

        # 無効なメッセージ(name が文字列でない)
        invalid_message = QMessage(message_id="test-3", message_type="hello", payload={"name": 123})
        assert await hello_service.validate_message(invalid_message) is False

    async def test_error_usecase_execution(self, error_service):
        """Test Error UseCase execution"""
        message = QMessage(message_id="test-error", message_type="error", payload={})

        response = await error_service.execute(message)
        assert response.success is False
        assert response.error == "Intentional error for testing"
        assert response.metadata["processed_by"] == "ErrorUseCase"

    async def test_full_integration_success(self, consumer, runtime, dispatcher, hello_service):
        """Test full queue system integration - success case"""
        # サービス登録
        dispatcher.register_service("hello", hello_service)

        # メッセージをキューに追加
        consumer.add_message("msg-1", "hello", {"name": "Dave"})

        # メッセージ処理フロー
        message = await dispatcher.get_next_message()
        assert message is not None
        assert message.message_id == "msg-1"

        response = await dispatcher.process_message(message)
        assert response.success is True
        assert response.result["greeting"] == "Hello, Dave!"

        # ランタイムが実行されたかチェック
        assert runtime.get_execution_count() == 1
        assert runtime.last_executed_service == hello_service
        assert runtime.last_executed_message == message

    async def test_full_integration_unknown_service(self, consumer, dispatcher):
        """Test full queue system integration - unknown service case"""
        # 未登録のサービスタイプ
        consumer.add_message("msg-1", "unknown", {"data": "test"})

        message = await dispatcher.get_next_message()
        response = await dispatcher.process_message(message)

        assert response.success is False
        assert "No service registered for message type: unknown" in response.error

    async def test_full_integration_runtime_failure(self, consumer, runtime, dispatcher, hello_service):
        """Test full queue system integration - runtime failure case"""
        # サービス登録
        dispatcher.register_service("hello", hello_service)

        # ランタイムを失敗モードに設定
        runtime.set_failure_mode(True)

        # メッセージをキューに追加
        consumer.add_message("msg-1", "hello", {"name": "Eve"})

        message = await dispatcher.get_next_message()
        response = await dispatcher.process_message(message)

        assert response.success is False
        assert response.error == "Mock runtime failure"

    async def test_multiple_messages_processing(
        self, consumer, runtime, dispatcher, hello_service, error_service
    ):
        """Test processing multiple messages"""
        # 複数のサービス登録
        dispatcher.register_service("hello", hello_service)
        dispatcher.register_service("error", error_service)

        # 複数のメッセージを追加
        consumer.add_message("msg-1", "hello", {"name": "Alice"})
        consumer.add_message("msg-2", "error", {})
        consumer.add_message("msg-3", "hello", {"name": "Bob"})

        results = []

        # 全メッセージを処理
        while True:
            message = await dispatcher.get_next_message()
            if message is None:
                break

            response = await dispatcher.process_message(message)
            results.append((message.message_type, response.success))

        # 結果検証
        assert len(results) == 3
        assert results[0] == ("hello", True)
        assert results[1] == ("error", False)
        assert results[2] == ("hello", True)

        # ランタイムが3回実行されたかチェック
        assert runtime.get_execution_count() == 3
