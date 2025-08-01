"""
API UseCases Tests
API ユースケーステスト
"""

import uuid
from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest

from ppjudg.const import ExecutionStatus, JudgeResultType, ProgrammingLanguage
from ppjudg.usecase.api_submission_usecase import ApiSubmissionUseCase
from ppjudg.usecase.api_system_usecase import ApiSystemUseCase


class TestApiSubmissionUseCase:
    """ApiSubmissionUseCaseのテスト"""

    @pytest.fixture
    def mock_dependencies(self):
        """モック依存関係を作成"""
        return {
            'submission_repo': AsyncMock(),
            'queue_repo': AsyncMock(),
            'problem_repo': AsyncMock(),
            'user_repo': AsyncMock(),
            'judge_service': AsyncMock(),
            'event_bus': AsyncMock()
        }

    @pytest.fixture
    def usecase(self, mock_dependencies):
        """ユースケースインスタンスを作成"""
        return ApiSubmissionUseCase(
            submission_repo=mock_dependencies['submission_repo'],
            queue_repo=mock_dependencies['queue_repo'],
            problem_repo=mock_dependencies['problem_repo'],
            user_repo=mock_dependencies['user_repo'],
            judge_service=mock_dependencies['judge_service'],
            event_bus=mock_dependencies['event_bus']
        )

    async def test_submit_solution_success(self, usecase, mock_dependencies):
        """正常な解答提出のテスト"""
        # テストデータ
        user_id = uuid.uuid4()
        problem_id = uuid.uuid4()
        code = 'print("Hello World")'
        language = ProgrammingLanguage.PYTHON

        # モック設定
        mock_user = Mock()
        mock_problem = Mock()
        mock_problem.status = "published"
        mock_judge_cases = [Mock()]
        mock_judge_cases[0].points = 100

        mock_dependencies['user_repo'].find_by_id.return_value = mock_user
        mock_dependencies['problem_repo'].find_by_id.return_value = mock_problem
        mock_dependencies['problem_repo'].get_judge_cases.return_value = mock_judge_cases
        mock_dependencies['submission_repo'].save.return_value = True
        mock_dependencies['submission_repo'].count_recent_submissions.return_value = 5
        mock_dependencies['queue_repo'].save.return_value = True

        # テスト実行
        result = await usecase.submit_solution(user_id, problem_id, code, language)

        # 検証
        assert result["success"] is True
        assert "submission" in result
        assert result["submission"]["language"] == "python"
        assert result["submission"]["status"] == "pending"
        
        # 依存関係の呼び出し確認
        mock_dependencies['submission_repo'].save.assert_called()
        mock_dependencies['queue_repo'].save.assert_called()
        mock_dependencies['event_bus'].publish.assert_called()

    async def test_submit_solution_user_not_found(self, usecase, mock_dependencies):
        """ユーザーが存在しない場合のテスト"""
        user_id = uuid.uuid4()
        problem_id = uuid.uuid4()
        code = 'print("Hello World")'
        language = ProgrammingLanguage.PYTHON

        # ユーザーが存在しない
        mock_dependencies['user_repo'].find_by_id.return_value = None

        result = await usecase.submit_solution(user_id, problem_id, code, language)

        assert result["success"] is False
        assert result["error_code"] == "USER_NOT_FOUND"

    async def test_submit_solution_problem_not_published(self, usecase, mock_dependencies):
        """問題が公開されていない場合のテスト"""
        user_id = uuid.uuid4()
        problem_id = uuid.uuid4()
        code = 'print("Hello World")'
        language = ProgrammingLanguage.PYTHON

        mock_user = Mock()
        mock_problem = Mock()
        mock_problem.status = "draft"  # 非公開

        mock_dependencies['user_repo'].find_by_id.return_value = mock_user
        mock_dependencies['problem_repo'].find_by_id.return_value = mock_problem

        result = await usecase.submit_solution(user_id, problem_id, code, language)

        assert result["success"] is False
        assert result["error_code"] == "PROBLEM_NOT_AVAILABLE"

    async def test_submit_solution_rate_limited(self, usecase, mock_dependencies):
        """レート制限のテスト"""
        user_id = uuid.uuid4()
        problem_id = uuid.uuid4()
        code = 'print("Hello World")'
        language = ProgrammingLanguage.PYTHON

        mock_user = Mock()
        mock_problem = Mock()
        mock_problem.status = "published"

        mock_dependencies['user_repo'].find_by_id.return_value = mock_user
        mock_dependencies['problem_repo'].find_by_id.return_value = mock_problem
        mock_dependencies['submission_repo'].count_recent_submissions.return_value = 15  # 制限超過

        result = await usecase.submit_solution(user_id, problem_id, code, language)

        assert result["success"] is False
        assert result["error_code"] == "RATE_LIMITED"

    async def test_submit_solution_code_too_long(self, usecase, mock_dependencies):
        """コードが長すぎる場合のテスト"""
        user_id = uuid.uuid4()
        problem_id = uuid.uuid4()
        code = "x" * 100001  # 100KB超過
        language = ProgrammingLanguage.PYTHON

        mock_user = Mock()
        mock_problem = Mock()
        mock_problem.status = "published"

        mock_dependencies['user_repo'].find_by_id.return_value = mock_user
        mock_dependencies['problem_repo'].find_by_id.return_value = mock_problem

        result = await usecase.submit_solution(user_id, problem_id, code, language)

        assert result["success"] is False
        assert result["error_code"] == "CODE_TOO_LONG"

    async def test_get_submission_status_success(self, usecase, mock_dependencies):
        """提出状況取得の正常テスト"""
        submission_id = uuid.uuid4()

        # モック設定
        mock_submission = Mock()
        mock_submission.id = submission_id
        mock_submission.status = ExecutionStatus.COMPLETED
        mock_submission.overall_result = JudgeResultType.ACCEPTED
        mock_submission.total_points = 100
        mock_submission.max_points = 100
        mock_submission.language = ProgrammingLanguage.PYTHON
        mock_submission.submitted_at = datetime.utcnow()
        mock_submission.judged_at = datetime.utcnow()
        mock_submission.judge_case_results = []

        mock_queue_item = Mock()
        mock_queue_item.status = ExecutionStatus.COMPLETED
        mock_queue_item.worker_id = "worker-1"
        mock_queue_item.started_at = datetime.utcnow()

        mock_dependencies['submission_repo'].find_by_id.return_value = mock_submission
        mock_dependencies['queue_repo'].find_by_submission.return_value = mock_queue_item

        result = await usecase.get_submission_status(submission_id)

        assert result["success"] is True
        assert result["submission"]["submission_id"] == str(submission_id)
        assert result["submission"]["status"] == "completed"
        assert result["submission"]["result"] == "accepted"
        assert result["submission"]["score"] == 100

    async def test_get_submission_status_not_found(self, usecase, mock_dependencies):
        """提出が存在しない場合のテスト"""
        submission_id = uuid.uuid4()

        mock_dependencies['submission_repo'].find_by_id.return_value = None

        result = await usecase.get_submission_status(submission_id)

        assert result["success"] is False
        assert result["error_code"] == "SUBMISSION_NOT_FOUND"

    async def test_get_user_submissions(self, usecase, mock_dependencies):
        """ユーザー提出一覧取得のテスト"""
        user_id = uuid.uuid4()
        
        # モック設定
        mock_submissions = []
        for i in range(3):
            mock_submission = Mock()
            mock_submission.id = uuid.uuid4()
            mock_submission.problem_id = uuid.uuid4()
            mock_submission.language = ProgrammingLanguage.PYTHON
            mock_submission.status = ExecutionStatus.COMPLETED
            mock_submission.overall_result = JudgeResultType.ACCEPTED
            mock_submission.total_points = 100
            mock_submission.max_points = 100
            mock_submission.submitted_at = datetime.utcnow()
            mock_submission.judged_at = datetime.utcnow()
            mock_submissions.append(mock_submission)

        mock_dependencies['submission_repo'].find_by_filters.return_value = mock_submissions
        mock_dependencies['submission_repo'].count_by_filters.return_value = 3

        result = await usecase.get_user_submissions(user_id, limit=10, offset=0)

        assert result["success"] is True
        assert len(result["submissions"]) == 3
        assert result["pagination"]["total"] == 3

    async def test_rejudge_submission_success(self, usecase, mock_dependencies):
        """再ジャッジの正常テスト"""
        submission_id = uuid.uuid4()
        requester_user_id = uuid.uuid4()

        # モック設定
        mock_submission = Mock()
        mock_submission.id = submission_id
        mock_submission.user_id = requester_user_id  # 同じユーザー

        mock_dependencies['submission_repo'].find_by_id.return_value = mock_submission
        mock_dependencies['submission_repo'].save.return_value = True
        mock_dependencies['queue_repo'].save.return_value = True

        result = await usecase.rejudge_submission(submission_id, requester_user_id, "Manual test")

        assert result["success"] is True
        assert result["submission"]["submission_id"] == str(submission_id)
        assert result["submission"]["status"] == "pending"

    async def test_rejudge_submission_permission_denied(self, usecase, mock_dependencies):
        """再ジャッジ権限なしのテスト"""
        submission_id = uuid.uuid4()
        requester_user_id = uuid.uuid4()
        other_user_id = uuid.uuid4()

        # モック設定
        mock_submission = Mock()
        mock_submission.user_id = other_user_id  # 異なるユーザー
        mock_user = Mock()
        mock_user.role = "user"  # 管理者権限なし

        mock_dependencies['submission_repo'].find_by_id.return_value = mock_submission
        mock_dependencies['user_repo'].find_by_id.return_value = mock_user

        result = await usecase.rejudge_submission(submission_id, requester_user_id)

        assert result["success"] is False
        assert result["error_code"] == "PERMISSION_DENIED"


class TestApiSystemUseCase:
    """ApiSystemUseCaseのテスト"""

    @pytest.fixture
    def mock_dependencies(self):
        return {
            'submission_repo': AsyncMock(),
            'queue_repo': AsyncMock(),
            'execution_repo': AsyncMock(),
            'worker_use_case': AsyncMock(),
            'maintenance_use_case': AsyncMock(),
            'queue_use_case': AsyncMock()
        }

    @pytest.fixture
    def usecase(self, mock_dependencies):
        return ApiSystemUseCase(
            submission_repo=mock_dependencies['submission_repo'],
            queue_repo=mock_dependencies['queue_repo'],
            execution_repo=mock_dependencies['execution_repo'],
            worker_use_case=mock_dependencies['worker_use_case'],
            maintenance_use_case=mock_dependencies['maintenance_use_case'],
            queue_use_case=mock_dependencies['queue_use_case']
        )

    async def test_get_system_status(self, usecase, mock_dependencies):
        """システム状況取得のテスト"""
        # モック設定
        mock_dependencies['queue_repo'].count_pending.return_value = 5
        mock_dependencies['queue_repo'].count_processing.return_value = 3
        mock_dependencies['submission_repo'].count_by_date_range.return_value = 100

        result = await usecase.get_system_status()

        assert result["success"] is True
        assert "status" in result
        assert result["status"]["overall_health"] in ["healthy", "warning", "error"]

    async def test_get_queue_status(self, usecase, mock_dependencies):
        """キュー状況取得のテスト"""
        # モック設定
        mock_pending_items = [Mock() for _ in range(5)]
        mock_processing_items = [Mock() for _ in range(3)]
        
        for i, item in enumerate(mock_pending_items):
            item.priority = i % 3 + 1

        mock_dependencies['queue_repo'].find_pending_items.return_value = mock_pending_items
        mock_dependencies['queue_repo'].find_processing_items.return_value = mock_processing_items

        result = await usecase.get_queue_status()

        assert result["success"] is True
        assert result["queue"]["pending_count"] == 5
        assert result["queue"]["processing_count"] == 3
        assert "priority_distribution" in result["queue"]

    async def test_get_submission_statistics(self, usecase, mock_dependencies):
        """提出統計取得のテスト"""
        # モック設定
        mock_dependencies['submission_repo'].count_by_date_range.return_value = 50
        mock_dependencies['submission_repo'].count_by_result_and_date_range.return_value = 30

        result = await usecase.get_submission_statistics(period_days=7, group_by="day")

        assert result["success"] is True
        assert result["statistics"]["total_submissions"] == 50
        assert result["statistics"]["period"]["days"] == 7
        assert "result_distribution" in result["statistics"]

    async def test_trigger_maintenance_standard(self, usecase, mock_dependencies):
        """標準メンテナンスのテスト"""
        requester_user_id = uuid.uuid4()

        # モック設定
        mock_dependencies['maintenance_use_case'].cleanup_system.return_value = {
            "deleted_queue_items": 10,
            "deleted_executions": 5
        }
        mock_dependencies['maintenance_use_case'].reset_stuck_submissions.return_value = {
            "reset_submissions": 2
        }

        result = await usecase.trigger_maintenance(
            requester_user_id, 
            maintenance_type="standard"
        )

        assert result["success"] is True
        assert result["maintenance"]["type"] == "standard"
        assert "results" in result["maintenance"]

    async def test_trigger_maintenance_invalid_type(self, usecase, mock_dependencies):
        """無効なメンテナンスタイプのテスト"""
        requester_user_id = uuid.uuid4()

        result = await usecase.trigger_maintenance(
            requester_user_id,
            maintenance_type="invalid_type"
        )

        assert result["success"] is False
        assert result["error_code"] == "INVALID_MAINTENANCE_TYPE"

    async def test_get_worker_management(self, usecase, mock_dependencies):
        """ワーカー管理情報取得のテスト"""
        # モック設定（アクティブワーカーID取得をモック）
        usecase._get_active_worker_ids = AsyncMock(return_value=["worker-1", "worker-2"])
        
        mock_worker_status = {
            "worker_id": "worker-1",
            "running_submissions": 2,
            "total_assigned": 5
        }
        mock_dependencies['worker_use_case'].get_worker_status.return_value = mock_worker_status

        result = await usecase.get_worker_management()

        assert result["success"] is True
        assert result["workers"]["total_workers"] == 2
        assert len(result["workers"]["worker_details"]) == 2