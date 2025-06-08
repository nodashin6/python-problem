"""
Pytest configuration and fixtures for ppauth tests
"""

import asyncio
import os
from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Any, Dict
from unittest.mock import AsyncMock, Mock
from uuid import UUID, uuid4

import pytest
from pydantic import UUID4

# Set test mode before importing ppauth
os.environ["PPAUTH_TEST_MODE"] = "true"

# Import only domain entities and interfaces directly, avoiding app layer
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ppauth.domain.entities.entities import UserEntity, UserRoleEntity
from ppauth.domain.entities.enums import UserRole
from ppauth.domain.repositories.user_repository import UserRepository
from ppauth.domain.repositories.user_role_respository import UserRoleRepository
from ppauth.domain.services.auth_service import JWTManager, PasswordManager
from ppauth.domain.services.user_service import UserService


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_user_repository() -> UserRepository:
    """Mock user repository for testing"""
    mock_repo = AsyncMock()

    # Manually configure all repository methods
    mock_repo.read = AsyncMock(return_value=None)
    mock_repo.create = AsyncMock(return_value=None)
    mock_repo.update = AsyncMock(return_value=None)
    mock_repo.delete = AsyncMock(return_value=None)
    mock_repo.find_by_email = AsyncMock(return_value=None)
    mock_repo.find_by_username = AsyncMock(return_value=None)
    mock_repo.exists_by_email = AsyncMock(return_value=False)
    mock_repo.exists_by_username = AsyncMock(return_value=False)

    return mock_repo


@pytest.fixture
def mock_user_role_repository() -> UserRoleRepository:
    """Mock user role repository for testing"""
    mock_repo = AsyncMock()

    # Manually configure all repository methods
    mock_repo.read = AsyncMock(return_value=None)
    mock_repo.create = AsyncMock(return_value=None)
    mock_repo.update = AsyncMock(return_value=None)
    mock_repo.delete = AsyncMock(return_value=None)
    mock_repo.find_by_user_id = AsyncMock(return_value=[])
    mock_repo.find_by_role = AsyncMock(return_value=[])
    mock_repo.count_by_role = AsyncMock(return_value=0)
    mock_repo.exists_by_user_id_and_role = AsyncMock(return_value=False)
    mock_repo.delete_user_role = AsyncMock(return_value=True)
    mock_repo.delete_by_user_id = AsyncMock(return_value=True)

    return mock_repo


@pytest.fixture
def mock_password_manager() -> PasswordManager:
    """Mock password manager for testing"""
    mock_manager = Mock()
    mock_manager.hash_password = Mock(
        return_value="$2b$12$abcdefghijklmnopqrstuvwxyz123456789012345678901234"
    )
    mock_manager.verify_password = Mock(return_value=True)
    return mock_manager


@pytest.fixture
def mock_jwt_manager() -> JWTManager:
    """Mock JWT manager for testing"""
    mock_manager = Mock()
    mock_manager.create_token = Mock(return_value="mock_jwt_token")
    mock_manager.verify_token = Mock(
        return_value={
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "type": "access",
        }
    )
    return mock_manager


@pytest.fixture
def user_service(
    mock_user_repository: UserRepository,
    mock_user_role_repository: UserRoleRepository,
    mock_password_manager: PasswordManager,
    mock_jwt_manager: JWTManager,
) -> UserService:
    """User service with mocked dependencies"""
    return UserService(
        user_repo=mock_user_repository,
        user_role_repo=mock_user_role_repository,
        password_manager=mock_password_manager,
        token_manager=mock_jwt_manager,
    )


@pytest.fixture
def sample_user() -> UserEntity:
    """Sample user entity for testing"""
    return UserEntity(
        id=uuid4(),
        username="testuser",
        display_name="Test User",
        email="test@example.com",
        password_hash="$2b$12$abcdefghijklmnopqrstuvwxyz123456789012345678901234",
        avatar_url="https://example.com/avatar.jpg",
        bio="Test user bio",
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def sample_user_role() -> UserRoleEntity:
    """Sample user role entity for testing"""
    user_id = uuid4()
    return UserRoleEntity(
        id=uuid4(),
        user_id=user_id,
        role=UserRole.USER,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def admin_user() -> UserEntity:
    """Sample admin user entity for testing"""
    return UserEntity(
        id=uuid4(),
        username="adminuser",
        display_name="Admin User",
        email="admin@example.com",
        password_hash="hashed_password_60_chars_12345678901234567890123456789012",
        avatar_url=None,
        bio=None,
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def admin_user_role() -> UserRoleEntity:
    """Sample admin user role entity for testing"""
    user_id = uuid4()
    return UserRoleEntity(
        id=uuid4(),
        user_id=user_id,
        role=UserRole.ADMIN,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
