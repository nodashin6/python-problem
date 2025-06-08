"""
Tests for UpdateUserUseCase
"""

from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from pydddi import UseCaseExecutionError

from ppauth.domain.entities import UserEntity
from ppauth.domain.services.user_service import UserService
from ppauth.usecase.update_user_usecase import UpdateUserCommand, UpdateUserResult, UpdateUserUseCase


class TestUpdateUserUseCase:
    """Test cases for UpdateUserUseCase"""

    @pytest.mark.asyncio
    async def test_update_user_success(self, user_service: UserService, sample_user: UserEntity):
        """Test successful user update"""
        # Arrange
        user_id = sample_user.id
        command = UpdateUserCommand(
            user_id=user_id,
            username="updateduser",
            display_name="Updated User",
            email="updated@example.com",
            avatar_url="https://example.com/new-avatar.jpg",
            bio="Updated bio",
        )

        # Create updated user entity
        updated_user = UserEntity(
            id=sample_user.id,
            username=command.username,
            display_name=command.display_name,
            email=command.email,
            password_hash=sample_user.password_hash,
            avatar_url=command.avatar_url,
            bio=command.bio,
            is_active=sample_user.is_active,
            created_at=sample_user.created_at,
            updated_at=sample_user.updated_at,
        )

        # Mock repository methods
        user_service.user_repo.read = AsyncMock(return_value=sample_user)
        user_service.user_repo.update = AsyncMock(return_value=updated_user)
        user_service.is_username_available = AsyncMock(return_value=True)
        user_service.is_email_available = AsyncMock(return_value=True)

        usecase = UpdateUserUseCase(user_service)

        # Act
        result = await usecase.execute(command)

        # Assert
        assert isinstance(result, UpdateUserResult)
        assert result.user_id == user_id
        assert result.username == command.username
        assert result.display_name == command.display_name
        assert result.email == command.email
        assert result.avatar_url == command.avatar_url
        assert result.bio == command.bio

        # Verify repository calls
        user_service.user_repo.read.assert_called_once_with(user_id)
        user_service.user_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_user_partial_update(self, user_service: UserService, sample_user: UserEntity):
        """Test partial user update (only some fields)"""
        # Arrange
        user_id = sample_user.id
        command = UpdateUserCommand(user_id=user_id, display_name="Partially Updated User")

        # Create partially updated user
        updated_user = UserEntity(
            id=sample_user.id,
            username=sample_user.username,  # unchanged
            display_name=command.display_name,  # updated
            email=sample_user.email,  # unchanged
            password_hash=sample_user.password_hash,
            avatar_url=sample_user.avatar_url,
            bio=sample_user.bio,
            is_active=sample_user.is_active,
            created_at=sample_user.created_at,
            updated_at=sample_user.updated_at,
        )

        user_service.user_repo.read = AsyncMock(return_value=sample_user)
        user_service.user_repo.update = AsyncMock(return_value=updated_user)

        usecase = UpdateUserUseCase(user_service)

        # Act
        result = await usecase.execute(command)

        # Assert
        assert result.display_name == command.display_name
        assert result.username == sample_user.username  # unchanged
        assert result.email == sample_user.email  # unchanged

    @pytest.mark.asyncio
    async def test_update_user_password(self, user_service: UserService, sample_user: UserEntity):
        """Test password update"""
        # Arrange
        user_id = sample_user.id
        new_password = "newpassword123"
        command = UpdateUserCommand(user_id=user_id, password=new_password)

        new_password_hash = "new_hashed_password_60_chars_1234567890123456789012345678901"

        updated_user = UserEntity(
            id=sample_user.id,
            username=sample_user.username,
            display_name=sample_user.display_name,
            email=sample_user.email,
            password_hash=new_password_hash,
            avatar_url=sample_user.avatar_url,
            bio=sample_user.bio,
            is_active=sample_user.is_active,
            created_at=sample_user.created_at,
            updated_at=sample_user.updated_at,
        )

        user_service.user_repo.read = AsyncMock(return_value=sample_user)
        user_service.user_repo.update = AsyncMock(return_value=updated_user)
        user_service.password_manager.hash_password = Mock(return_value=new_password_hash)

        usecase = UpdateUserUseCase(user_service)

        # Act
        result = await usecase.execute(command)

        # Assert
        user_service.password_manager.hash_password.assert_called_once_with(new_password)
        user_service.user_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_user_not_found(self, user_service: UserService):
        """Test update when user is not found"""
        # Arrange
        user_id = uuid4()
        command = UpdateUserCommand(user_id=user_id, username="nonexistent")

        user_service.user_repo.read = AsyncMock(return_value=None)

        usecase = UpdateUserUseCase(user_service)

        # Act & Assert
        with pytest.raises(UseCaseExecutionError) as exc_info:
            await usecase.execute(command)

        assert f"User with ID {user_id} not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_user_username_taken(self, user_service: UserService, sample_user: UserEntity):
        """Test update when new username is already taken"""
        # Arrange
        user_id = sample_user.id
        command = UpdateUserCommand(user_id=user_id, username="takenusernameohtheruser")

        user_service.user_repo.read = AsyncMock(return_value=sample_user)
        user_service.is_username_available = AsyncMock(return_value=False)

        usecase = UpdateUserUseCase(user_service)

        # Act & Assert
        with pytest.raises(UseCaseExecutionError) as exc_info:
            await usecase.execute(command)

        assert "Username is already taken" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_user_email_taken(self, user_service: UserService, sample_user: UserEntity):
        """Test update when new email is already taken"""
        # Arrange
        user_id = sample_user.id
        command = UpdateUserCommand(user_id=user_id, email="taken@example.com")

        user_service.user_repo.read = AsyncMock(return_value=sample_user)
        user_service.is_email_available = AsyncMock(return_value=False)

        usecase = UpdateUserUseCase(user_service)

        # Act & Assert
        with pytest.raises(UseCaseExecutionError) as exc_info:
            await usecase.execute(command)

        assert "Email is already taken" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_user_same_username_allowed(
        self, user_service: UserService, sample_user: UserEntity
    ):
        """Test update with same username (should be allowed)"""
        # Arrange
        user_id = sample_user.id
        command = UpdateUserCommand(
            user_id=user_id,
            username=sample_user.username,  # same username
        )

        user_service.user_repo.read = AsyncMock(return_value=sample_user)
        user_service.user_repo.update = AsyncMock(return_value=sample_user)
        user_service.is_username_available = AsyncMock(return_value=False)  # taken by others

        usecase = UpdateUserUseCase(user_service)

        # Act
        result = await usecase.execute(command)

        # Assert - should not raise exception
        assert result.username == sample_user.username

    @pytest.mark.asyncio
    async def test_update_user_deactivate(self, user_service: UserService, sample_user: UserEntity):
        """Test user deactivation"""
        # Arrange
        user_id = sample_user.id
        command = UpdateUserCommand(user_id=user_id, is_active=False)

        deactivated_user = UserEntity(
            id=sample_user.id,
            username=sample_user.username,
            display_name=sample_user.display_name,
            email=sample_user.email,
            password_hash=sample_user.password_hash,
            avatar_url=sample_user.avatar_url,
            bio=sample_user.bio,
            is_active=False,
            created_at=sample_user.created_at,
            updated_at=sample_user.updated_at,
        )

        user_service.user_repo.read = AsyncMock(return_value=sample_user)
        user_service.user_repo.update = AsyncMock(return_value=deactivated_user)

        usecase = UpdateUserUseCase(user_service)

        # Act
        result = await usecase.execute(command)

        # Assert
        assert result.is_active is False
