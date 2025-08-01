"""
Message Dispatcher Unit Tests
メッセージディスパッチャーユニットテスト

依存関係を最小化したユニットテスト
"""

from unittest.mock import AsyncMock, Mock

import pytest


class TestMessageQueueDispatcherUnit:
    """メッセージキューディスパッチャーの単体テスト"""

    def test_message_type_routing(self):
        """メッセージタイプのルーティングロジックテスト"""
        # シンプルなルーティングロジックをテスト
        def get_default_handler(message_type: str) -> str:
            """メッセージタイプから適切なハンドラーを推測"""
            if message_type and (message_type.startswith(("submission", "judge"))):
                return "submission"
            elif message_type and (message_type.startswith(("worker", "queue"))):
                return "worker"
            else:
                return "submission"  # デフォルト

        # テストケース
        test_cases = [
            ("submission.created", "submission"),
            ("judge.request", "submission"),
            ("judge.rejudge", "submission"),
            ("worker.status", "worker"),
            ("queue.maintenance", "worker"),
            ("unknown.type", "submission"),
            ("", "submission"),
            (None, "submission"),
        ]

        for message_type, expected_handler in test_cases:
            result = get_default_handler(message_type)
            assert result == expected_handler, f"Message type '{message_type}' should route to '{expected_handler}'"

    def test_message_validation(self):
        """メッセージ検証ロジックのテスト"""
        def validate_message(message):
            """メッセージの基本的な検証"""
            if not isinstance(message, dict):
                return False, "Message must be a dictionary"
            
            if "type" not in message:
                return False, "Message must have a 'type' field"
            
            if not message["type"]:
                return False, "Message type cannot be empty"
            
            return True, "Valid message"

        # 有効なメッセージ
        valid_message = {"type": "submission.created", "data": "test"}
        is_valid, error = validate_message(valid_message)
        assert is_valid is True
        assert error == "Valid message"

        # 無効なメッセージ
        invalid_messages = [
            ("not a dict", False, "Message must be a dictionary"),
            ({}, False, "Message must have a 'type' field"),
            ({"type": ""}, False, "Message type cannot be empty"),
            ({"type": None}, False, "Message type cannot be empty"),
        ]

        for message, expected_valid, expected_error in invalid_messages:
            is_valid, error = validate_message(message)
            assert is_valid == expected_valid
            assert error == expected_error

    def test_handler_selection_logic(self):
        """ハンドラー選択ロジックのテスト"""
        handlers = {
            "submission": Mock(),
            "worker": Mock()
        }

        def select_handler(message_type: str, handlers: dict):
            """ハンドラーを選択"""
            if message_type.startswith(("submission", "judge")):
                return handlers.get("submission")
            elif message_type.startswith(("worker", "queue")):
                return handlers.get("worker")
            else:
                return handlers.get("submission")  # デフォルト

        # テストケース
        submission_handler = select_handler("submission.created", handlers)
        assert submission_handler == handlers["submission"]

        worker_handler = select_handler("worker.status", handlers)
        assert worker_handler == handlers["worker"]

        default_handler = select_handler("unknown.type", handlers)
        assert default_handler == handlers["submission"]

    def test_error_handling_logic(self):
        """エラーハンドリングロジックのテスト"""
        def format_error_response(error: Exception, context: dict = None):
            """エラーレスポンスをフォーマット"""
            return {
                "success": False,
                "error": str(error),
                "error_type": type(error).__name__,
                "context": context or {}
            }

        # テストケース
        test_error = ValueError("Invalid input")
        test_context = {"message_id": "123", "timestamp": "2023-01-01"}

        response = format_error_response(test_error, test_context)

        assert response["success"] is False
        assert response["error"] == "Invalid input"
        assert response["error_type"] == "ValueError"
        assert response["context"] == test_context

    def test_message_priority_logic(self):
        """メッセージ優先度ロジックのテスト"""
        def calculate_priority(message_type: str, metadata: dict = None) -> int:
            """メッセージの優先度を計算"""
            metadata = metadata or {}
            
            # ベース優先度
            base_priority = 1
            
            # メッセージタイプによる調整
            if message_type == "judge.rejudge":
                base_priority += 3  # 再ジャッジは高優先度
            elif message_type.startswith("worker"):
                base_priority += 1  # ワーカー関連はやや高優先度
            
            # メタデータによる調整
            if metadata.get("urgent"):
                base_priority += 2
            
            return base_priority

        # テストケース
        test_cases = [
            ("submission.created", {}, 1),
            ("judge.rejudge", {}, 4),
            ("worker.status", {}, 2),
            ("submission.created", {"urgent": True}, 3),
            ("judge.rejudge", {"urgent": True}, 6),
        ]

        for message_type, metadata, expected_priority in test_cases:
            priority = calculate_priority(message_type, metadata)
            assert priority == expected_priority, f"Priority for {message_type} with {metadata} should be {expected_priority}"


class TestEventHandlerLogic:
    """イベントハンドラーロジックの単体テスト"""

    def test_submission_status_update_logic(self):
        """提出ステータス更新ロジックのテスト"""
        def update_submission_status(current_status: str, new_status: str) -> bool:
            """提出ステータスの更新が有効かチェック"""
            valid_transitions = {
                "pending": ["judging", "error"],
                "judging": ["completed", "error"],
                "completed": ["pending"],  # 再ジャッジ用
                "error": ["pending"]  # リトライ用
            }
            
            return new_status in valid_transitions.get(current_status, [])

        # 有効な遷移
        valid_cases = [
            ("pending", "judging"),
            ("judging", "completed"),
            ("completed", "pending"),
            ("error", "pending")
        ]

        for current, new in valid_cases:
            assert update_submission_status(current, new) is True

        # 無効な遷移
        invalid_cases = [
            ("completed", "judging"),
            ("judging", "pending"),
            ("pending", "completed")
        ]

        for current, new in invalid_cases:
            assert update_submission_status(current, new) is False

    def test_queue_item_filtering_logic(self):
        """キューアイテムフィルタリングロジックのテスト"""
        def filter_queue_items(items: list, filter_criteria: dict) -> list:
            """キューアイテムをフィルタリング"""
            filtered = items
            
            if "status" in filter_criteria:
                filtered = [item for item in filtered if item.get("status") == filter_criteria["status"]]
            
            if "priority" in filter_criteria:
                filtered = [item for item in filtered if item.get("priority") >= filter_criteria["priority"]]
            
            if "worker_id" in filter_criteria:
                if filter_criteria["worker_id"] is None:
                    filtered = [item for item in filtered if item.get("worker_id") is None]
                else:
                    filtered = [item for item in filtered if item.get("worker_id") == filter_criteria["worker_id"]]
            
            return filtered

        # テストデータ
        test_items = [
            {"id": 1, "status": "pending", "priority": 1, "worker_id": None},
            {"id": 2, "status": "running", "priority": 2, "worker_id": "worker-1"},
            {"id": 3, "status": "pending", "priority": 3, "worker_id": None},
            {"id": 4, "status": "completed", "priority": 1, "worker_id": "worker-2"},
        ]

        # フィルターテスト
        pending_items = filter_queue_items(test_items, {"status": "pending"})
        assert len(pending_items) == 2
        assert all(item["status"] == "pending" for item in pending_items)

        high_priority_items = filter_queue_items(test_items, {"priority": 2})
        assert len(high_priority_items) == 2
        assert all(item["priority"] >= 2 for item in high_priority_items)

        unassigned_items = filter_queue_items(test_items, {"worker_id": None})
        assert len(unassigned_items) == 2
        assert all(item["worker_id"] is None for item in unassigned_items)

    def test_worker_availability_logic(self):
        """ワーカー可用性ロジックのテスト"""
        def is_worker_available(worker_status: dict, max_concurrent: int = 3) -> bool:
            """ワーカーが利用可能かチェック"""
            if worker_status.get("status") != "active":
                return False
            
            current_jobs = worker_status.get("current_jobs", 0)
            return current_jobs < max_concurrent

        # テストケース
        test_cases = [
            ({"status": "active", "current_jobs": 0}, 3, True),
            ({"status": "active", "current_jobs": 2}, 3, True),
            ({"status": "active", "current_jobs": 3}, 3, False),
            ({"status": "inactive", "current_jobs": 0}, 3, False),
            ({"status": "error", "current_jobs": 1}, 3, False),
        ]

        for worker_status, max_concurrent, expected in test_cases:
            result = is_worker_available(worker_status, max_concurrent)
            assert result == expected, f"Worker {worker_status} availability should be {expected}"