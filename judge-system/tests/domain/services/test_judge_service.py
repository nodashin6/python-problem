import pytest
from unittest import mock
import uuid
from src.domain.services.judge_service import JudgeService
from src.infra.repositories.judge_repository import JudgeResultRepository
from src.domain import models


@pytest.fixture
def mock_repository():
    """モックリポジトリを準備"""
    repo = mock.MagicMock(spec=JudgeResultRepository)
    # saveメソッドの実装
    repo.save = mock.MagicMock()
    # getメソッドの実装
    repo.get = mock.MagicMock(return_value={
        "status": "completed",
        "problem_id": "001",
        "problem_set": "getting-started",
        "code": 'print("Hello, World!")',
        "results": [
            {
                "id": "001_01",
                "problem": {"id": "001"},
                "test_case": {
                    "id": "01",
                    "name": "sample",
                    "problem": {"id": "001"},
                    "stdin": {"id": "", "name": "sample", "content": ""},
                    "stdout": {"id": "", "name": "sample", "content": "Hello, World!"}
                },
                "status": "AC",
                "metadata": {
                    "memory_used": 1024,
                    "time_used": 100,
                    "compile_error": None,
                    "runtime_error": None,
                    "output": "Hello, World!"
                }
            }
        ]
    })
    
    return repo


def test_judge_service_start_judge(mock_repository):
    """ジャッジ開始のテスト"""
    # モックUUID
    test_uuid = "test-uuid-1234"
    with mock.patch('uuid.uuid4', return_value=test_uuid):
        service = JudgeService(repository=mock_repository)
        judge_id = service.start_judge("001", 'print("Hello, World!")', "getting-started")
        
        # UUIDが正しく返されるか
        assert judge_id == str(test_uuid)
        
        # リポジトリのsaveが正しく呼ばれたか
        mock_repository.save.assert_called_once()
        # 第1引数はUUID
        assert mock_repository.save.call_args[0][0] == str(test_uuid)
        # 第2引数は辞書で、以下のキーを持っている
        saved_data = mock_repository.save.call_args[0][1]
        assert "status" in saved_data and saved_data["status"] == "running"
        assert "problem_id" in saved_data and saved_data["problem_id"] == "001"
        assert "code" in saved_data and saved_data["code"] == 'print("Hello, World!")'


def test_judge_service_get_status(mock_repository):
    """ジャッジ状態取得のテスト"""
    service = JudgeService(repository=mock_repository)
    judge_id = "test-judge-id"
    
    # 状態取得
    status = service.get_judge_status(judge_id)
    
    # リポジトリのgetが正しく呼ばれたか
    mock_repository.get.assert_called_once_with(judge_id)
    
    # 返り値が正しいか
    assert status["status"] == "completed"
    assert status["problem_id"] == "001"
    assert status["problem_set"] == "getting-started"
    assert "results" in status and len(status["results"]) == 1


def test_judge_service_save_submission_with_valid_id(mock_repository):
    """有効なIDで提出結果を保存するテスト"""
    service = JudgeService(repository=mock_repository)
    judge_id = "test-judge-id"
    user_id = "test-user"
    
    # サービスのロガーとステータスマネージャーを直接モック化
    service.submission_logger = mock.MagicMock()
    service.submission_logger.save_submission.return_value = mock.MagicMock(id="test-submission-id")
    
    service.user_status_manager = mock.MagicMock()
    service.user_status_manager.user_id = user_id  # ユーザーIDを合わせておく
    service.user_status_manager.update_problem_status.return_value = mock.MagicMock(
        model_dump=mock.MagicMock(return_value={"solved_at": "2025-05-12T12:00:00"})
    )
    
    # 提出結果を保存
    result = service.save_submission_result(judge_id, user_id)
    
    # 結果が正しいか
    assert result["status"] == "success"
    assert result["submission_id"] == "test-submission-id"
    assert "problem_status" in result