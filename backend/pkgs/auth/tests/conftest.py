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

from ppauth.domain.entities.user import RoleEntity, UserEntity
from ppauth.domain.enums import UserRole
from ppauth.domain.helpers.authentificator.authentificator import Authentificator
from ppauth.domain.helpers.authentificator.password_helper import PasswordManager
from ppauth.domain.helpers.authentificator.token_helper import JWTManager
from ppauth.domain.repositories.user_repository import UserRepository
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
    mock_repo.create_user_with_role = AsyncMock(return_value=None)
    mock_repo.update_user_with_role = AsyncMock(return_value=None)
    mock_repo.find_by_email = AsyncMock(return_value=None)
    mock_repo.find_by_user_name = AsyncMock(return_value=None)
    mock_repo.find_by_id_with_role = AsyncMock(return_value=None)
    mock_repo.list_active_users = AsyncMock(return_value=[])
    mock_repo.delete = AsyncMock(return_value=True)

    return mock_repo


@pytest.fixture
def mock_authentificator() -> Authentificator:
    """Mock authentificator for testing"""
    mock_auth = Mock()
    mock_auth.hash_password = Mock(return_value="$2b$12$abcdefghijklmnopqrstuvwxyz123456789012345678901234")
    mock_auth.verify_password = Mock(return_value=True)
    mock_auth.create_access_token = Mock(return_value="mock_jwt_token")
    return mock_auth


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
    mock_authentificator: Authentificator,
) -> UserService:
    """User service with mocked dependencies"""
    return UserService(
        user_repo=mock_user_repository,
        authentificator=mock_authentificator,
    )


@pytest.fixture
def sample_user() -> UserEntity:
    """Sample user entity for testing"""
    role_entity = RoleEntity(
        id=uuid4(),
        user_id=uuid4(),
        role=UserRole.USER,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    return UserEntity(
        id=uuid4(),
        user_name="testuser",
        display_name="Test User",
        email="test@example.com",
        password_hash="$2b$12$abcdefghijklmnopqrstuvwxyz123456789012345678901234",
        avatar_url="https://example.com/avatar.jpg",
        bio="Test user bio",
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        role_entity=role_entity,
    )


@pytest.fixture
def sample_role() -> RoleEntity:
    """Sample role entity for testing"""
    user_id = uuid4()
    return RoleEntity(
        id=uuid4(),
        user_id=user_id,
        role=UserRole.USER,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def admin_user() -> UserEntity:
    """Sample admin user entity for testing"""
    role_entity = RoleEntity(
        id=uuid4(),
        user_id=uuid4(),
        role=UserRole.ADMIN,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    return UserEntity(
        id=uuid4(),
        user_name="adminuser",
        display_name="Admin User",
        email="admin@example.com",
        password_hash="hashed_password_60_chars_12345678901234567890123456789012",
        avatar_url=None,
        bio=None,
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        role_entity=role_entity,
    )


@pytest.fixture
def admin_role() -> RoleEntity:
    """Sample admin role entity for testing"""
    user_id = uuid4()
    return RoleEntity(
        id=uuid4(),
        user_id=user_id,
        role=UserRole.ADMIN,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
