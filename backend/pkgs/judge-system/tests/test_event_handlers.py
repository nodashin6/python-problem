"""
Event Handlers Tests
イベントハンドラーテスト
"""

import uuid
from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest

import sys
import os
# Add judge-system package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
# Add core package to path for ppcore imports
backend_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..')
sys.path.insert(0, os.path.join(backend_dir, 'pkgs', 'core'))
sys.path.insert(0, os.path.join(backend_dir, 'pkgs', 'problem-system'))
sys.path.insert(0, backend_dir)  # for src.utils import

from ppjudg.domain.entities.enums import ExecutionStatus, JudgeResultType
from ppjudg.event.message_queue_handlers import (
    MessageQueueDispatcher,
    SubmissionQueueHandler,
    JudgeWorkerEventHandler,
)
from ppjudg.event.domain_event_handlers import (
    CoreDomainEventHandler,
    JudgeSystemEventHandler
)

# Mock the events since they come from shared
class MockEvent:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.data = kwargs

class JudgeCompletedEvent(MockEvent):
    pass

class ProblemCreatedEvent(MockEvent):
    pass


class TestSubmissionQueueHandler:
    """SubmissionQueueHandlerのテスト"""

    @pytest.fixture
    def mock_dependencies(self):
        """モック依存関係を作成"""
        return {
            'submission_repo': AsyncMock(),
            'queue_repo': AsyncMock(),
            'problem_repo': AsyncMock(),
            'judge_service': AsyncMock(),
            'event_bus': AsyncMock()
        }

    @pytest.fixture
    def handler(self, mock_dependencies):
        """ハンドラーインスタンスを作成"""
        return SubmissionQueueHandler(
            submission_repo=mock_dependencies['submission_repo'],
            queue_repo=mock_dependencies['queue_repo'],
            problem_repo=mock_dependencies['problem_repo'],
            judge_service=mock_dependencies['judge_service'],
            event_bus=mock_dependencies['event_bus']
        )

    @pytest.mark.asyncio
    async def test_handle_submission_created_message_success(self, handler, mock_dependencies):
        """提出作成メッセージの正常処理テスト"""
        # テストデータ
        submission_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        problem_id = str(uuid.uuid4())
        
        message = {
            "submission_id": submission_id,
            "user_id": user_id,
            "problem_id": problem_id,
            "message_id": "msg_001"
        }

        # キューアイテムが存在する場合
        mock_queue_item = Mock()
        mock_dependencies['queue_repo'].find_by_submission.return_value = mock_queue_item

        # テスト実行  
        result = await handler.handle_submission_created_message(message)

        # 検証
        assert result is True
        mock_dependencies['queue_repo'].find_by_submission.assert_called_once_with(uuid.UUID(submission_id))

    @pytest.mark.asyncio
    async def test_handle_submission_created_message_no_queue_item(self, handler, mock_dependencies):
        """キューアイテムが存在しない場合のテスト"""
        message = {
            "submission_id": str(uuid.uuid4()),
            "user_id": str(uuid.uuid4()), 
            "problem_id": str(uuid.uuid4()),
            "message_id": "msg_001"
        }

        # キューアイテムが存在しない
        mock_dependencies['queue_repo'].find_by_submission.return_value = None

        # テスト実行
        result = await handler.handle_submission_created_message(message)

        # 検証
        assert result is False
        mock_dependencies['event_bus'].publish.assert_called()

    @pytest.mark.asyncio
    async def test_handle_judge_request_message_success(self, handler, mock_dependencies):
        """ジャッジリクエストメッセージの正常処理テスト"""
        # テストデータ
        submission_id = str(uuid.uuid4())
        worker_id = "test-worker"
        
        message = {
            "submission_id": submission_id,
            "worker_id": worker_id,
            "correlation_id": "corr_001"
        }

        # モック設定
        mock_submission = Mock()
        mock_submission.id = uuid.UUID(submission_id)
        mock_submission.problem_id = uuid.uuid4()
        mock_submission.user_id = uuid.uuid4()
        mock_submission.overall_result = Mock()
        mock_submission.overall_result.value = "ACCEPTED"
        mock_submission.total_points = 100

        mock_problem = Mock()
        mock_judge_cases = [Mock()]
        mock_queue_item = Mock()

        mock_dependencies['submission_repo'].find_by_id.return_value = mock_submission
        mock_dependencies['problem_repo'].find_by_id.return_value = mock_problem
        mock_dependencies['problem_repo'].get_judge_cases.return_value = mock_judge_cases
        mock_dependencies['queue_repo'].find_by_submission.return_value = mock_queue_item
        mock_dependencies['judge_service'].process_submission.return_value = True

        # テスト実行
        result = await handler.handle_judge_request_message(message)

        # 検証
        assert result is True
        mock_dependencies['judge_service'].process_submission.assert_called_once_with(mock_submission, mock_judge_cases)
        mock_dependencies['submission_repo'].save.assert_called_once_with(mock_submission)
        mock_dependencies['event_bus'].publish.assert_called()

    @pytest.mark.asyncio
    async def test_handle_rejudge_request_message(self, handler, mock_dependencies):
        """再ジャッジリクエストメッセージのテスト"""
        submission_id = str(uuid.uuid4())
        message = {
            "submission_id": submission_id,
            "reason": "Manual rejudge"
        }

        # モック設定
        mock_submission = Mock()
        mock_queue_item = Mock()
        
        mock_dependencies['submission_repo'].find_by_id.return_value = mock_submission
        mock_dependencies['queue_repo'].find_by_submission.return_value = mock_queue_item

        # テスト実行
        result = await handler.handle_rejudge_request_message(message)

        # 検証
        assert result is True
        assert mock_submission.status == ExecutionStatus.PENDING
        assert mock_submission.overall_result == JudgeResultType.PENDING
        assert mock_submission.total_points == 0
        mock_dependencies['submission_repo'].save.assert_called_once_with(mock_submission)


class TestJudgeWorkerEventHandler:
    """JudgeWorkerEventHandlerのテスト"""

    @pytest.fixture
    def mock_dependencies(self):
        return {
            'queue_repo': AsyncMock(),
            'event_bus': AsyncMock()
        }

    @pytest.fixture
    def handler(self, mock_dependencies):
        return JudgeWorkerEventHandler(
            queue_repo=mock_dependencies['queue_repo'],
            event_bus=mock_dependencies['event_bus']
        )

    @pytest.mark.asyncio
    async def test_handle_worker_status_heartbeat(self, handler, mock_dependencies):
        """ワーカーハートビートメッセージのテスト"""
        message = {
            "worker_id": "worker-1",
            "status": "heartbeat"
        }

        result = await handler.handle_worker_status_message(message)
        assert result is True

    @pytest.mark.asyncio
    async def test_handle_worker_status_shutdown(self, handler, mock_dependencies):
        """ワーカーシャットダウンメッセージのテスト"""
        message = {
            "worker_id": "worker-1", 
            "status": "shutdown"
        }

        # モック設定
        mock_items = [Mock(), Mock()]
        for item in mock_items:
            item.status = ExecutionStatus.RUNNING
        
        mock_dependencies['queue_repo'].find_by_worker.return_value = mock_items

        result = await handler.handle_worker_status_message(message)
        assert result is True
        
        # 提出が解放されたことを確認
        for item in mock_items:
            assert item.status == ExecutionStatus.PENDING
            assert item.worker_id is None

    @pytest.mark.asyncio
    async def test_handle_queue_maintenance_cleanup_stale(self, handler, mock_dependencies):
        """スタックしたアイテムのクリーンアップテスト"""
        message = {
            "action": "cleanup_stale",
            "minutes": 30
        }

        # モック設定
        mock_stale_items = [Mock(), Mock()]
        mock_dependencies['queue_repo'].find_stale_items.return_value = mock_stale_items

        result = await handler.handle_queue_maintenance_message(message)
        assert result is True


class TestMessageQueueDispatcher:
    """MessageQueueDispatcherのテスト"""

    @pytest.fixture
    def dispatcher(self):
        return MessageQueueDispatcher()

    @pytest.mark.asyncio
    async def test_dispatch_submission_created(self, dispatcher):
        """提出作成メッセージのディスパッチテスト"""
        message = {
            "type": "submission.created",
            "submission_id": str(uuid.uuid4()),
            "user_id": str(uuid.uuid4()),
            "problem_id": str(uuid.uuid4())
        }

        # ハンドラーをモックに置き換え
        mock_handler = AsyncMock()
        mock_handler.handle_submission_created_message.return_value = True
        dispatcher.handlers["submission"] = mock_handler

        result = await dispatcher.dispatch_message(message)
        assert result is True
        mock_handler.handle_submission_created_message.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_dispatch_judge_request(self, dispatcher):
        """ジャッジリクエストメッセージのディスパッチテスト"""
        message = {
            "type": "judge.request",
            "submission_id": str(uuid.uuid4()),
            "worker_id": "worker-1"
        }

        mock_handler = AsyncMock()
        mock_handler.handle_judge_request_message.return_value = True
        dispatcher.handlers["submission"] = mock_handler

        result = await dispatcher.dispatch_message(message)
        assert result is True
        mock_handler.handle_judge_request_message.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_dispatch_unknown_message_type(self, dispatcher):
        """未知のメッセージタイプのテスト"""
        message = {
            "type": "unknown.message",
            "data": "test"
        }

        result = await dispatcher.dispatch_message(message)
        assert result is False

    def test_get_default_handler(self, dispatcher):
        """デフォルトハンドラー選択のテスト"""
        assert dispatcher._get_default_handler("submission.created") == "submission"
        assert dispatcher._get_default_handler("judge.request") == "submission" 
        assert dispatcher._get_default_handler("worker.status") == "worker"
        assert dispatcher._get_default_handler("queue.maintenance") == "worker"
        assert dispatcher._get_default_handler("unknown") == "submission"


class TestDomainEventHandlers:
    """ドメインイベントハンドラーのテスト"""

    @pytest.fixture
    def mock_event_bus(self):
        return AsyncMock()

    @pytest.fixture
    def mock_submission_use_case(self):
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_core_domain_handler_problem_created(self, mock_event_bus, mock_submission_use_case):
        """問題作成イベントハンドリングのテスト"""
        handler = CoreDomainEventHandler(
            submission_use_case=mock_submission_use_case,
            event_bus=mock_event_bus
        )

        event = ProblemCreatedEvent(
            problem_id=str(uuid.uuid4()),
            title="Test Problem", 
            difficulty="easy",
            correlation_id=str(uuid.uuid4())
        )
        event.data = {
            "problem_id": event.problem_id,
            "title": event.title,
            "difficulty": event.difficulty
        }

        await handler.handle_problem_created(event)
        # イベントが正常に処理されることを確認（エラーが発生しない）

    @pytest.mark.asyncio
    async def test_judge_system_handler_judge_completed(self, mock_event_bus):
        """ジャッジ完了イベントハンドリングのテスト"""
        mock_worker_use_case = AsyncMock()
        
        handler = JudgeSystemEventHandler(
            worker_use_case=mock_worker_use_case,
            event_bus=mock_event_bus
        )

        event = JudgeCompletedEvent(
            judge_id=str(uuid.uuid4()),
            submission_id=str(uuid.uuid4()),
            result="ACCEPTED",
            score=100,
            user_id=str(uuid.uuid4()),
            correlation_id=str(uuid.uuid4())
        )
        event.data = {
            "judge_id": event.judge_id,
            "submission_id": event.submission_id,
            "result": event.result,
            "score": event.score,
            "user_id": event.user_id
        }

        await handler.handle_judge_completed(event)
        # イベントが正常に処理されることを確認