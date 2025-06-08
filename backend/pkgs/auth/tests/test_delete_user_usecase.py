"""
Tests for DeleteUserUseCase
"""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from pydddi import UseCaseExecutionError

from ppauth.domain.entities import UserEntity
from ppauth.domain.services.user_service import UserService
from ppauth.usecase.delete_user_usecase import DeleteUserCommand, DeleteUserResult, DeleteUserUseCase


class TestDeleteUserUseCase:
    """Test cases for DeleteUserUseCase"""

    @pytest.mark.asyncio
    async def test_soft_delete_user_success(self, user_service: UserService, sample_user: UserEntity):
        """Test successful soft delete (deactivation)"""
        # Arrange
        user_id = sample_user.id
        command = DeleteUserCommand(user_id=user_id, soft_delete=True)

        user_service.user_repo.read = AsyncMock(return_value=sample_user)
        user_service.deactivate_user = AsyncMock(return_value=True)

        usecase = DeleteUserUseCase(user_service)

        # Act
        result = await usecase.execute(command)

        # Assert
        assert isinstance(result, DeleteUserResult)
        assert result.user_id == user_id
        assert result.deleted is True
        assert result.soft_deleted is True

        # Verify service calls
        user_service.user_repo.read.assert_called_once_with(user_id)
        user_service.deactivate_user.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_hard_delete_user_success(self, user_service: UserService, sample_user: UserEntity):
        """Test successful hard delete"""
        # Arrange
        user_id = sample_user.id
        command = DeleteUserCommand(user_id=user_id, soft_delete=False)

        user_service.user_repo.read = AsyncMock(return_value=sample_user)
        user_service.user_repo.delete = AsyncMock(return_value=None)
        user_service.user_role_repo.delete_by_user_id = AsyncMock(return_value=True)

        usecase = DeleteUserUseCase(user_service)

        # Act
        result = await usecase.execute(command)

        # Assert
        assert isinstance(result, DeleteUserResult)
        assert result.user_id == user_id
        assert result.deleted is True
        assert result.soft_deleted is False

        # Verify service calls
        user_service.user_repo.read.assert_called_once_with(user_id)
        user_service.user_repo.delete.assert_called_once_with(user_id)
        user_service.user_role_repo.delete_by_user_id.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, user_service: UserService):
        """Test delete when user is not found"""
        # Arrange
        user_id = uuid4()
        command = DeleteUserCommand(user_id=user_id, soft_delete=True)

        user_service.user_repo.read = AsyncMock(return_value=None)

        usecase = DeleteUserUseCase(user_service)

        # Act & Assert
        with pytest.raises(UseCaseExecutionError) as exc_info:
            await usecase.execute(command)

        assert f"User with ID {user_id} not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_soft_delete_user_deactivation_failure(
        self, user_service: UserService, sample_user: UserEntity
    ):
        """Test soft delete when deactivation fails"""
        # Arrange
        user_id = sample_user.id
        command = DeleteUserCommand(user_id=user_id, soft_delete=True)

        user_service.user_repo.read = AsyncMock(return_value=sample_user)
        user_service.deactivate_user = AsyncMock(return_value=False)

        usecase = DeleteUserUseCase(user_service)

        # Act
        result = await usecase.execute(command)

        # Assert
        assert result.deleted is False
        assert result.soft_deleted is True

    @pytest.mark.asyncio
    async def test_default_soft_delete(self, user_service: UserService, sample_user: UserEntity):
        """Test that soft delete is the default behavior"""
        # Arrange
        user_id = sample_user.id
        command = DeleteUserCommand(user_id=user_id)  # No soft_delete specified

        user_service.user_repo.read = AsyncMock(return_value=sample_user)
        user_service.deactivate_user = AsyncMock(return_value=True)

        usecase = DeleteUserUseCase(user_service)

        # Act
        result = await usecase.execute(command)

        # Assert
        assert result.soft_deleted is True
        user_service.deactivate_user.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_hard_delete_repository_exception(
        self, user_service: UserService, sample_user: UserEntity
    ):
        """Test hard delete when repository raises exception"""
        # Arrange
        user_id = sample_user.id
        command = DeleteUserCommand(user_id=user_id, soft_delete=False)

        user_service.user_repo.read = AsyncMock(return_value=sample_user)
        user_service.user_repo.delete = AsyncMock(side_effect=Exception("Database error"))

        usecase = DeleteUserUseCase(user_service)

        # Act & Assert
        with pytest.raises(UseCaseExecutionError) as exc_info:
            await usecase.execute(command)

        assert "Failed to delete user: Database error" in str(exc_info.value)
