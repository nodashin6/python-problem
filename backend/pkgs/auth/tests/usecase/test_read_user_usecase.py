"""
Tests for ReadUserUseCase
"""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from pydddi import UseCaseExecutionError

from ppauth.domain.entities import RoleEntity, UserEntity
from ppauth.domain.enums import UserRole
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
    async def test_read_user_by_id_success(
        self, user_service: UserService, sample_user: UserEntity, sample_role: RoleEntity
    ):
        """Test successful user retrieval by ID"""
        # Arrange
        user_id = sample_user.id
        command = ReadUserByIdCommand(user_id=user_id)

        # Set up user role with matching user_id
        sample_role.user_id = user_id

        user_service.user_repo.find_by_id_with_role = AsyncMock(return_value=sample_user)
        # user_service.user_role_repo.find_by_user_id = AsyncMock(return_value=[sample_role])

        usecase = ReadUserByIdUseCase(user_service)

        # Act
        result = await usecase.execute(command)

        # Assert
        assert isinstance(result, UserResult)
        assert result.user.id == user_id
        assert result.user.user_name == sample_user.user_name
        assert result.user.display_name == sample_user.display_name
        assert result.user.email == sample_user.email
        assert result.user.avatar_url == sample_user.avatar_url
        assert result.user.bio == sample_user.bio
        assert result.user.is_active == sample_user.is_active

        # Verify service calls
        user_service.user_repo.find_by_id_with_role.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_read_user_by_id_not_found(self, user_service: UserService):
        """Test user retrieval when user is not found"""
        # Arrange
        user_id = uuid4()
        command = ReadUserByIdCommand(user_id=user_id)

        user_service.user_repo.find_by_id_with_role = AsyncMock(return_value=None)

        usecase = ReadUserByIdUseCase(user_service)

        # Act & Assert
        with pytest.raises(UseCaseExecutionError) as exc_info:
            await usecase.execute(command)

        assert f"User with ID {user_id} not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_read_user_with_multiple_roles(self, user_service: UserService, sample_user: UserEntity):
        """Test user retrieval with user entity validation"""
        # Arrange
        user_id = sample_user.id
        command = ReadUserByIdCommand(user_id=user_id)

        user_service.user_repo.find_by_id_with_role = AsyncMock(return_value=sample_user)

        usecase = ReadUserByIdUseCase(user_service)

        # Act
        result = await usecase.execute(command)

        # Assert
        assert isinstance(result, UserResult)
        assert result.user.id == user_id
        assert result.user.user_name == sample_user.user_name
        assert result.user.display_name == sample_user.display_name
        assert result.user.email == sample_user.email
        assert result.user.avatar_url == sample_user.avatar_url
        assert result.user.bio == sample_user.bio
        assert result.user.is_active == sample_user.is_active

        # Verify service calls
        user_service.user_repo.find_by_id_with_role.assert_called_once_with(user_id)


class TestReadUserByEmailUseCase:
    """Test cases for ReadUserByEmailUseCase"""

    @pytest.mark.asyncio
    async def test_read_user_by_email_success(self, user_service: UserService, sample_user: UserEntity):
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
        assert result.user.user_name == sample_user.user_name

        # Verify service calls
        user_service.user_repo.find_by_email.assert_called_once_with(email)

    @pytest.mark.asyncio
    async def test_read_user_by_email_not_found(self, user_service: UserService):
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
    async def test_read_users_by_role_success(
        self, user_service: UserService, sample_user: UserEntity, admin_user: UserEntity
    ):
        """Test successful users retrieval by role"""
        # Arrange
        role = UserRole.ADMIN
        command = ReadUsersByRoleCommand(role=role, limit=10, offset=0)

        # admin_userにroleを設定
        admin_user.role_entity = RoleEntity(
            id=uuid4(),
            user_id=admin_user.id,
            role=UserRole.ADMIN,
            created_at=admin_user.created_at,
            updated_at=admin_user.updated_at,
        )

        # 正しいメソッドをモック
        user_service.user_repo.list_users_by_role = AsyncMock(return_value=[admin_user])

        usecase = ReadUsersByRoleUseCase(user_service)

        # Act
        result = await usecase.execute(command)

        # Assert
        assert isinstance(result, ReadUserListResult)
        assert len(result.users) == 1
        assert result.total_count == 1
        assert result.users[0].user.id == admin_user.id

        # Verify service calls
        user_service.user_repo.list_users_by_role.assert_called_once_with(role=role, limit=10, offset=0)

    @pytest.mark.asyncio
    async def test_read_users_by_role_empty_result(self, user_service: UserService):
        """Test users retrieval when no users have the role"""
        # Arrange
        role = UserRole.ADMIN
        command = ReadUsersByRoleCommand(role=role)

        # リポジトリが空のリストを返すことをモック
        user_service.user_repo.list_users_by_role = AsyncMock(return_value=[])

        usecase = ReadUsersByRoleUseCase(user_service)

        # Act
        result = await usecase.execute(command)

        # Assert
        assert isinstance(result, ReadUserListResult)
        assert len(result.users) == 0
        assert result.total_count == 0

        # Verify correct method was called
        user_service.user_repo.list_users_by_role.assert_called_once_with(role=role, limit=100, offset=0)

    @pytest.mark.asyncio
    async def test_read_users_by_role_with_pagination(
        self, user_service: UserService, sample_user: UserEntity
    ):
        """Test users retrieval with pagination parameters"""
        # Arrange
        role = UserRole.USER
        command = ReadUsersByRoleCommand(role=role, limit=5, offset=10)

        # sample_userにroleを設定
        sample_user.role_entity = RoleEntity(
            id=uuid4(),
            user_id=sample_user.id,
            role=UserRole.USER,
            created_at=sample_user.created_at,
            updated_at=sample_user.updated_at,
        )

        # 正しいメソッドをモック
        user_service.user_repo.list_users_by_role = AsyncMock(return_value=[sample_user])

        usecase = ReadUsersByRoleUseCase(user_service)

        # Act
        result = await usecase.execute(command)

        # Assert
        assert len(result.users) == 1
        assert result.total_count == 1  # 実際にはリポジトリが返すユーザー数

        # Verify pagination parameters were passed
        user_service.user_repo.list_users_by_role.assert_called_once_with(role=role, limit=5, offset=10)

    @pytest.mark.asyncio
    async def test_read_users_by_role_user_not_found(self, user_service: UserService):
        """Test users retrieval when no users exist for the role"""
        # Arrange
        role = UserRole.USER
        command = ReadUsersByRoleCommand(role=role)

        # リポジトリが空のリストを返すことをモック
        user_service.user_repo.list_users_by_role = AsyncMock(return_value=[])

        usecase = ReadUsersByRoleUseCase(user_service)

        # Act
        result = await usecase.execute(command)

        # Assert - Should return empty result
        assert len(result.users) == 0
        assert result.total_count == 0

        # Verify correct method was called
        user_service.user_repo.list_users_by_role.assert_called_once_with(role=role, limit=100, offset=0)
