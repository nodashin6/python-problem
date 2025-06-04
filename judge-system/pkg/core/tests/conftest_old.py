"""
Core tests specific configuration
"""

import pytest
from unittest.mock import MagicMock, AsyncMock
from uuid import uuid4

from src.core.domain.models import User, Problem, Book, JudgeCase, UserProfile
from src.const import UserRole, DifficultyLevel, ProblemStatus, JudgeCaseType


@pytest.fixture
def sample_user():
    """テスト用ユーザーのサンプルデータ"""
    profile = UserProfile(display_name="Test User")
    return User(
        email="test@example.com",
        username="testuser",
        password_hash="hashed_password",
        profile=profile,
        role=UserRole.USER,
    )


@pytest.fixture
def sample_problem():
    """テスト用問題のサンプルデータ"""
    return Problem(
        title="Sample Problem",
        description="This is a sample problem for testing",
        author_id=uuid4(),
        difficulty=DifficultyLevel.EASY,
        status=ProblemStatus.PUBLISHED,
    )


@pytest.fixture
def sample_book():
    """テスト用問題集のサンプルデータ"""
    return Book(
        title="Sample Book",
        description="This is a sample book for testing",
        author_id=uuid4(),
        is_published=True,
    )


@pytest.fixture
def sample_judge_case():
    """テスト用ジャッジケースのサンプルデータ"""
    return JudgeCase(
        problem_id=uuid4(),
        name="Sample Input/Output",
        input_data="1 2",
        expected_output="3",
        case_type=JudgeCaseType.SAMPLE,
        points=1,
    )


@pytest.fixture
def mock_event_bus():
    """モックイベントバス"""
    return AsyncMock()


@pytest.fixture
def mock_password_manager():
    """モックパスワードマネージャー"""
    manager = MagicMock()
    manager.hash_password.return_value = "hashed_password"
    manager.verify_password.return_value = True
    return manager


@pytest.fixture
def mock_jwt_manager():
    """モックJWTマネージャー"""
    manager = MagicMock()
    manager.create_access_token.return_value = "access_token"
    manager.verify_token.return_value = {"user_id": str(uuid4())}
    return manager


# Pytest configuration for core tests
def pytest_configure(config):
    """Pytest configuration for core module tests"""
    config.addinivalue_line("markers", "core: mark test as core module test")
