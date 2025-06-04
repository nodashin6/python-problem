"""
Core tests specific configuration (Simplified)
"""

import pytest
from unittest.mock import MagicMock, AsyncMock
from uuid import uuid4


@pytest.fixture
def mock_user_repository():
    """モックUserRepositoryを作成"""
    return AsyncMock()


@pytest.fixture
def mock_problem_repository():
    """モックProblemRepositoryを作成"""
    return AsyncMock()


@pytest.fixture
def mock_book_repository():
    """モックBookRepositoryを作成"""
    return AsyncMock()


@pytest.fixture
def mock_judge_case_repository():
    """モックJudgeCaseRepositoryを作成"""
    return AsyncMock()


@pytest.fixture
def mock_event_bus():
    """モックEventBusを作成"""
    return AsyncMock()


@pytest.fixture
def mock_password_manager():
    """モックPasswordManagerを作成"""
    return MagicMock()


@pytest.fixture
def mock_jwt_manager():
    """モックJWTManagerを作成"""
    return MagicMock()


# Pytestマーカーの定義
def pytest_configure(config):
    """テストマーカーを登録"""
    config.addinivalue_line("markers", "core: mark test as core domain test")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "unit: mark test as unit test")
