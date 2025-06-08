"""
Tests for ReadUserUseCase
"""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from pydddi import UseCaseExecutionError

from ppauth.domain.entities import UserEntity, UserRoleEntity
from ppauth.domain.entities.enums import UserRole
from ppauth.domain.services.user_service import UserService
from ppauth.usecase.read_user_usecase import (
    ReadUserByEmailCommand,
    ReadUserByEmailUseCase,
    ReadUserByIdCommand,
    ReadUserByIdUseCase,
    ReadUserListResult,
    ReadUsersByRoleCommand,
    ReadUsersByRoleUseCase,
    UserResult,
)


class TestReadUserByIdUseCase:
    """Test cases for ReadUserByIdUseCase"""

    @pytest.mark.asyncio
    async def test_get_user_by_id_success(
        self, user_service: UserService, sample_user: UserEntity, sample_user_role: UserRoleEntity
    ):
        """Test successful user retrieval by ID"""
        # Arrange
        user_id = sample_user.id
        command = ReadUserByIdCommand(user_id=user_id)

        # Set up user role with matching user_id
        sample_user_role.user_id = user_id

        user_service.user_repo.read = AsyncMock(return_value=sample_user)
        user_service.user_role_repo.find_by_user_id = AsyncMock(return_value=[sample_user_role])

        usecase = ReadUserByIdUseCase(user_service)

        # Act
        result = await usecase.execute(command)

        # Assert
        assert isinstance(result, UserResult)
        assert result.user.id == user_id
        assert result.user.username == sample_user.username
        assert result.user.display_name == sample_user.display_name
        assert result.user.email == sample_user.email
        assert result.user.avatar_url == sample_user.avatar_url
        assert result.user.bio == sample_user.bio
        assert result.user.is_active == sample_user.is_active

        # Verify service calls
        user_service.user_repo.read.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, user_service: UserService):
        """Test user retrieval when user is not found"""
        # Arrange
        user_id = uuid4()
        command = ReadUserByIdCommand(user_id=user_id)

        user_service.user_repo.read = AsyncMock(return_value=None)

        usecase = ReadUserByIdUseCase(user_service)

        # Act & Assert
        with pytest.raises(UseCaseExecutionError) as exc_info:
            await usecase.execute(command)

        assert f"User with ID {user_id} not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_user_with_multiple_roles(self, user_service: UserService, sample_user: UserEntity):
        """Test user retrieval with user entity validation"""
        # Arrange
        user_id = sample_user.id
        command = ReadUserByIdCommand(user_id=user_id)

        user_service.user_repo.read = AsyncMock(return_value=sample_user)

        usecase = ReadUserByIdUseCase(user_service)

        # Act
        result = await usecase.execute(command)

        # Assert
        assert isinstance(result, UserResult)
        assert result.user.id == user_id
        assert result.user.username == sample_user.username
        assert result.user.display_name == sample_user.display_name
        assert result.user.email == sample_user.email
        assert result.user.avatar_url == sample_user.avatar_url
        assert result.user.bio == sample_user.bio
        assert result.user.is_active == sample_user.is_active

        # Verify service calls
        user_service.user_repo.read.assert_called_once_with(user_id)


class TestReadUserByEmailUseCase:
    """Test cases for ReadUserByEmailUseCase"""

    @pytest.mark.asyncio
    async def test_get_user_by_email_success(self, user_service: UserService, sample_user: UserEntity):
        """Test successful user retrieval by email"""
        # Arrange
        email = sample_user.email
        command = ReadUserByEmailCommand(email=email)

        user_service.user_repo.find_by_email = AsyncMock(return_value=sample_user)

        usecase = ReadUserByEmailUseCase(user_service)

        # Act
        result = await usecase.execute(command)

        # Assert
        assert isinstance(result, UserResult)
        assert result.user.email == email
        assert result.user.username == sample_user.username

        # Verify service calls
        user_service.user_repo.find_by_email.assert_called_once_with(email)

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, user_service: UserService):
        """Test user retrieval when email is not found"""
        # Arrange
        email = "nonexistent@example.com"
        command = ReadUserByEmailCommand(email=email)

        user_service.user_repo.find_by_email = AsyncMock(return_value=None)

        usecase = ReadUserByEmailUseCase(user_service)

        # Act & Assert
        with pytest.raises(UseCaseExecutionError) as exc_info:
            await usecase.execute(command)

        assert f"User with email {email} not found" in str(exc_info.value)


class TestReadUsersByRoleUseCase:
    """Test cases for ReadUsersByRoleUseCase"""

    @pytest.mark.asyncio
    async def test_get_users_by_role_success(
        self, user_service: UserService, sample_user: UserEntity, admin_user: UserEntity
    ):
        """Test successful users retrieval by role"""
        # Arrange
        role = UserRole.ADMIN
        command = ReadUsersByRoleCommand(role=role, limit=10, offset=0)

        admin_user_role = UserRoleEntity(
            id=uuid4(),
            user_id=admin_user.id,
            role=UserRole.ADMIN,
            created_at=admin_user.created_at,
            updated_at=admin_user.updated_at,
        )

        user_service.user_role_repo.find_by_role = AsyncMock(return_value=[admin_user_role])
        user_service.user_repo.read = AsyncMock(return_value=admin_user)
        user_service.user_role_repo.find_by_user_id = AsyncMock(return_value=[admin_user_role])
        user_service.user_role_repo.count_by_role = AsyncMock(return_value=1)

        usecase = ReadUsersByRoleUseCase(user_service)

        # Act
        result = await usecase.execute(command)

        # Assert
        assert isinstance(result, ReadUserListResult)
        assert len(result.users) == 1
        assert result.total_count == 1
        assert result.users[0].user.id == admin_user.id

        # Verify service calls (roles are no longer fetched in the usecase)

        # Verify service calls
        user_service.user_role_repo.find_by_role.assert_called_once_with(role, limit=10, offset=0)
        user_service.user_role_repo.count_by_role.assert_called_once_with(role)

    @pytest.mark.asyncio
    async def test_get_users_by_role_empty_result(self, user_service: UserService):
        """Test users retrieval when no users have the role"""
        # Arrange
        role = UserRole.ADMIN
        command = ReadUsersByRoleCommand(role=role)

        user_service.user_role_repo.find_by_role = AsyncMock(return_value=[])
        user_service.user_role_repo.count_by_role = AsyncMock(return_value=0)

        usecase = ReadUsersByRoleUseCase(user_service)

        # Act
        result = await usecase.execute(command)

        # Assert
        assert isinstance(result, ReadUserListResult)
        assert len(result.users) == 0
        assert result.total_count == 0

    @pytest.mark.asyncio
    async def test_get_users_by_role_with_pagination(
        self, user_service: UserService, sample_user: UserEntity
    ):
        """Test users retrieval with pagination parameters"""
        # Arrange
        role = UserRole.USER
        command = ReadUsersByRoleCommand(role=role, limit=5, offset=10)

        user_role = UserRoleEntity(
            id=uuid4(),
            user_id=sample_user.id,
            role=UserRole.USER,
            created_at=sample_user.created_at,
            updated_at=sample_user.updated_at,
        )

        user_service.user_role_repo.find_by_role = AsyncMock(return_value=[user_role])
        user_service.user_repo.read = AsyncMock(return_value=sample_user)
        user_service.user_role_repo.find_by_user_id = AsyncMock(return_value=[user_role])
        user_service.user_role_repo.count_by_role = AsyncMock(return_value=25)

        usecase = ReadUsersByRoleUseCase(user_service)

        # Act
        result = await usecase.execute(command)

        # Assert
        assert len(result.users) == 1
        assert result.total_count == 25

        # Verify pagination parameters were passed
        user_service.user_role_repo.find_by_role.assert_called_once_with(role, limit=5, offset=10)

    @pytest.mark.asyncio
    async def test_get_users_by_role_user_not_found(self, user_service: UserService):
        """Test users retrieval when user role exists but user entity is deleted"""
        # Arrange
        role = UserRole.USER
        command = ReadUsersByRoleCommand(role=role)

        from datetime import datetime

        orphaned_user_role = UserRoleEntity(
            id=uuid4(),
            user_id=uuid4(),  # Non-existent user
            role=UserRole.USER,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        user_service.user_role_repo.find_by_role = AsyncMock(return_value=[orphaned_user_role])
        user_service.user_repo.read = AsyncMock(return_value=None)  # User not found
        user_service.user_role_repo.count_by_role = AsyncMock(return_value=1)

        usecase = ReadUsersByRoleUseCase(user_service)

        # Act
        result = await usecase.execute(command)

        # Assert - Should skip users that don't exist
        assert len(result.users) == 0
        assert result.total_count == 1  # Count still includes the role
