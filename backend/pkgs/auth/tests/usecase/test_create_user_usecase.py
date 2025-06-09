"""
Tests for CreateUserUseCase
"""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from pydddi import UseCaseExecutionError

from ppauth.domain.entities import UserEntity
from ppauth.domain.entities.enums import UserRole
from ppauth.domain.services.user_service import UserService
from ppauth.usecase.create_user_usecase import CreateUserCommand, CreateUserResult, CreateUserUseCase


class TestCreateUserUseCase:
    """Test cases for CreateUserUseCase"""

    @pytest.mark.asyncio
    async def test_create_user_success(self, user_service: UserService, sample_user: UserEntity):
        """Test successful user creation"""
        # Arrange
        command = CreateUserCommand(
            username="newuser",
            display_name="New User",
            email="newuser@example.com",
            password="password123",
            avatar_url="https://example.com/avatar.jpg",
            bio="New user bio",
            role=UserRole.USER,
        )

        # Mock the user service to return a user
        user_service.register_user = AsyncMock(return_value=sample_user)

        usecase = CreateUserUseCase(user_service)

        # Act
        result = await usecase.execute(command)

        # Assert
        assert isinstance(result, CreateUserResult)
        assert result.user_id == sample_user.id
        assert result.username == sample_user.username
        assert result.display_name == sample_user.display_name
        assert result.email == sample_user.email
        assert result.avatar_url == sample_user.avatar_url
        assert result.bio == sample_user.bio
        assert result.is_active == sample_user.is_active

        # Verify service was called correctly
        user_service.register_user.assert_called_once_with(
            email=command.email,
            username=command.username,
            display_name=command.display_name,
            password=command.password,
            avatar_url=command.avatar_url,
            bio=command.bio,
            role=command.role,
        )

    @pytest.mark.asyncio
    async def test_create_user_with_minimal_data(self, user_service: UserService, sample_user: UserEntity):
        """Test user creation with minimal required data"""
        # Arrange
        command = CreateUserCommand(
            username="minimaluser",
            display_name="Minimal User",
            email="minimal@example.com",
            password="password123",
        )

        minimal_user = UserEntity(
            id=sample_user.id,
            username=command.username,
            display_name=command.display_name,
            email=command.email,
            password_hash=sample_user.password_hash,
            avatar_url=None,
            bio=None,
            is_active=True,
            created_at=sample_user.created_at,
            updated_at=sample_user.updated_at,
        )

        user_service.register_user = AsyncMock(return_value=minimal_user)

        usecase = CreateUserUseCase(user_service)

        # Act
        result = await usecase.execute(command)

        # Assert
        assert isinstance(result, CreateUserResult)
        assert result.user_id == minimal_user.id
        assert result.username == minimal_user.username
        assert result.display_name == minimal_user.display_name
        assert result.email == minimal_user.email
        assert result.avatar_url is None
        assert result.bio is None
        assert result.is_active == minimal_user.is_active

    @pytest.mark.asyncio
    async def test_create_user_service_failure(self, user_service: UserService):
        """Test user creation when service fails"""
        # Arrange
        command = CreateUserCommand(
            username="failuser", display_name="Fail User", email="fail@example.com", password="password123"
        )

        # Mock service to raise an exception
        user_service.register_user = AsyncMock(side_effect=Exception("Email already exists"))

        usecase = CreateUserUseCase(user_service)

        # Act & Assert
        with pytest.raises(UseCaseExecutionError) as exc_info:
            await usecase.execute(command)

        assert "Failed to create user: Email already exists" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_admin_user(self, user_service: UserService, admin_user: UserEntity):
        """Test admin user creation"""
        # Arrange
        command = CreateUserCommand(
            username="adminuser",
            display_name="Admin User",
            email="admin@example.com",
            password="adminpassword123",
            role=UserRole.ADMIN,
        )

        user_service.register_user = AsyncMock(return_value=admin_user)

        usecase = CreateUserUseCase(user_service)

        # Act
        result = await usecase.execute(command)

        # Assert
        assert isinstance(result, CreateUserResult)
        assert result.user_id == admin_user.id

        # Verify service was called with admin role
        user_service.register_user.assert_called_once_with(
            email=command.email,
            username=command.username,
            display_name=command.display_name,
            password=command.password,
            avatar_url=command.avatar_url,
            bio=command.bio,
            role=UserRole.ADMIN,
        )
