"""
Tests configuration
テスト設定
"""

import asyncio
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, Mock

import pytest


@pytest.fixture(scope="session")
def event_loop():
    """セッション全体で同じイベントループを使用"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# テスト用のモックフィクスチャ
@pytest.fixture
def mock_submission_repo():
    """Mock SubmissionRepository"""
    return AsyncMock()


@pytest.fixture
def mock_queue_repo():
    """Mock JudgeQueueRepository"""
    return AsyncMock()


@pytest.fixture
def mock_problem_repo():
    """Mock ProblemRepository"""
    return AsyncMock()


@pytest.fixture
def mock_user_repo():
    """Mock UserRepository"""
    return AsyncMock()


@pytest.fixture
def mock_judge_service():
    """Mock JudgeDomainService"""
    return AsyncMock()


@pytest.fixture
def mock_event_bus():
    """Mock EventBus"""
    return AsyncMock()


@pytest.fixture
def mock_code_execution_repo():
    """Mock CodeExecutionRepository"""
    return AsyncMock()


# テスト用のエンティティモック作成ヘルパー
class MockEntityFactory:
    """テスト用エンティティのモックファクトリー"""
    
    @staticmethod
    def create_mock_submission():
        """モック提出を作成"""
        mock = Mock()
        mock.id = Mock()
        mock.problem_id = Mock()
        mock.user_id = Mock()
        mock.code = "print('test')"
        mock.language = Mock()
        mock.status = Mock()
        mock.overall_result = Mock()
        mock.total_points = 0
        mock.max_points = 100
        mock.submitted_at = Mock()
        mock.judged_at = None
        mock.judge_case_results = []
        return mock
    
    @staticmethod
    def create_mock_queue_item():
        """モックキューアイテムを作成"""
        mock = Mock()
        mock.id = Mock()
        mock.submission_id = Mock()
        mock.priority = 1
        mock.status = Mock()
        mock.worker_id = None
        mock.created_at = Mock()
        mock.started_at = None
        mock.completed_at = None
        mock.error_message = None
        return mock
    
    @staticmethod
    def create_mock_problem():
        """モック問題を作成"""
        mock = Mock()
        mock.id = Mock()
        mock.title = "Test Problem"
        mock.status = "published"
        mock.difficulty_level = "easy"
        return mock
    
    @staticmethod
    def create_mock_user():
        """モックユーザーを作成"""
        mock = Mock()
        mock.id = Mock()
        mock.email = "test@example.com"
        mock.role = "user"
        return mock
    
    @staticmethod
    def create_mock_judge_case():
        """モックジャッジケースを作成"""
        mock = Mock()
        mock.id = Mock()
        mock.input_data = "test input"
        mock.expected_output = "test output"
        mock.points = 100
        return mock


@pytest.fixture
def mock_entity_factory():
    """MockEntityFactoryのフィクスチャ"""
    return MockEntityFactory


class IntegrationTestBase:
    """統合テストのベースクラス"""
    
    @pytest.fixture(autouse=True)
    def setup_integration_test(self):
        """統合テストの共通セットアップ"""
        from ppcore.infrastructure.supabase.client import create_client
        from ppcore.domain.protocols.database_protocols import DatabaseConfig
        import os
        
        config = DatabaseConfig(
            url=os.getenv("SUPABASE_URL", "https://test.supabase.co"),
            key=os.getenv("SUPABASE_ANON_KEY", "test_key")
        )
        self.supabase = create_client(config)
    
    async def get_user_by_email(self, email: str):
        """メールアドレスでユーザーを取得"""
        result = self.supabase.table("users").select("*").eq("email", email).execute()
        return result.data[0] if result.data else None
    
    async def get_problem_by_title(self, title: str):
        """タイトルで問題を取得"""
        result = self.supabase.table("problem_headers").select("*").eq("title", title).execute()
        return result.data[0] if result.data else None
    
    async def create_test_submission(self, problem_id, user_id, source_code, language="python"):
        """テスト用の提出を作成"""
        submission_data = {
            "problem_id": problem_id,
            "user_id": user_id,
            "code": source_code,
            "language": language,
            "status": "pending"
        }
        result = self.supabase.table("submissions").insert(submission_data).execute()
        return result.data[0]["id"] if result.data else None
    
    async def get_submission_by_id(self, submission_id):
        """IDで提出を取得"""
        result = self.supabase.table("submissions").select("*").eq("id", submission_id).execute()
        return result.data[0] if result.data else None
