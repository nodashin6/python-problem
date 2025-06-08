"""
Integration tests for user-related use cases
"""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from pydddi import UseCaseExecutionError

from ppauth.domain.entities import UserEntity, UserRoleEntity
from ppauth.domain.entities.enums import UserRole
from ppauth.domain.services.user_service import UserService
from ppauth.usecase.create_user_usecase import CreateUserCommand, CreateUserUseCase
from ppauth.usecase.delete_user_usecase import DeleteUserCommand, DeleteUserUseCase
from ppauth.usecase.read_user_usecase import (
    ReadUserByEmailCommand,
    ReadUserByEmailUseCase,
    ReadUserByIdCommand,
    ReadUserByIdUseCase,
)
from ppauth.usecase.update_user_usecase import UpdateUserCommand, UpdateUserUseCase


class TestUserUseCaseIntegration:
    """Integration tests for user use cases"""

    @pytest.mark.asyncio
    async def test_create_and_read_user_flow(
        self, user_service: UserService, sample_user: UserEntity, sample_user_role: UserRoleEntity
    ):
        """Test complete flow: create user then read it"""
        # Arrange
        create_command = CreateUserCommand(
            username="integrationuser",
            display_name="Integration User",
            email="integration@example.com",
            password="password123",
            bio="Integration test user",
        )

        # Mock user service for creation
        user_service.register_user = AsyncMock(return_value=sample_user)

        # Mock for reading
        sample_user_role.user_id = sample_user.id
        user_service.user_repo.read = AsyncMock(return_value=sample_user)
        user_service.user_role_repo.find_by_user_id = AsyncMock(return_value=[sample_user_role])

        create_usecase = CreateUserUseCase(user_service)
        read_usecase = ReadUserByIdUseCase(user_service)

        # Act - Create user
        create_result = await create_usecase.execute(create_command)

        # Act - Read user
        read_command = ReadUserByIdCommand(user_id=create_result.user_id)
        read_result = await read_usecase.execute(read_command)

        # Assert
        assert create_result.user_id == read_result.user.id
        assert create_result.username == read_result.user.username
        assert create_result.email == read_result.user.email

    @pytest.mark.asyncio
    async def test_create_update_read_user_flow(
        self, user_service: UserService, sample_user: UserEntity, sample_user_role: UserRoleEntity
    ):
        """Test complete flow: create user, update it, then read it"""
        # Arrange - Create
        create_command = CreateUserCommand(
            username="flowuser", display_name="Flow User", email="flow@example.com", password="password123"
        )

        user_service.register_user = AsyncMock(return_value=sample_user)

        # Arrange - Update
        updated_user = UserEntity(
            id=sample_user.id,
            username=sample_user.username,
            display_name="Updated Flow User",  # Changed
            email=sample_user.email,
            password_hash=sample_user.password_hash,
            avatar_url="https://example.com/new-avatar.jpg",  # Added
            bio=sample_user.bio,
            is_active=sample_user.is_active,
            created_at=sample_user.created_at,
            updated_at=sample_user.updated_at,
        )

        user_service.user_repo.read = AsyncMock(return_value=sample_user)
        user_service.user_repo.update = AsyncMock(return_value=updated_user)
        user_service.is_username_available = AsyncMock(return_value=True)
        user_service.is_email_available = AsyncMock(return_value=True)

        # Arrange - Read
        sample_user_role.user_id = sample_user.id
        user_service.user_role_repo.find_by_user_id = AsyncMock(return_value=[sample_user_role])

        create_usecase = CreateUserUseCase(user_service)
        update_usecase = UpdateUserUseCase(user_service)
        read_usecase = ReadUserByIdUseCase(user_service)

        # Act - Create
        create_result = await create_usecase.execute(create_command)

        # Act - Update
        update_command = UpdateUserCommand(
            user_id=create_result.user_id,
            display_name="Updated Flow User",
            avatar_url="https://example.com/new-avatar.jpg",
        )
        update_result = await update_usecase.execute(update_command)

        # Mock updated user for read
        user_service.user_repo.read = AsyncMock(return_value=updated_user)

        # Act - Read
        read_command = ReadUserByIdCommand(user_id=create_result.user_id)
        read_result = await read_usecase.execute(read_command)

        # Assert
        assert read_result.user.display_name == "Updated Flow User"
        assert read_result.user.avatar_url == "https://example.com/new-avatar.jpg"
        assert read_result.user.id == create_result.user_id

    @pytest.mark.asyncio
    async def test_create_soft_delete_read_user_flow(
        self, user_service: UserService, sample_user: UserEntity
    ):
        """Test complete flow: create user, soft delete it, then try to read it"""
        # Arrange - Create
        create_command = CreateUserCommand(
            username="deleteuser",
            display_name="Delete User",
            email="delete@example.com",
            password="password123",
        )

        user_service.register_user = AsyncMock(return_value=sample_user)

        # Arrange - Delete
        deactivated_user = UserEntity(
            id=sample_user.id,
            username=sample_user.username,
            display_name=sample_user.display_name,
            email=sample_user.email,
            password_hash=sample_user.password_hash,
            avatar_url=sample_user.avatar_url,
            bio=sample_user.bio,
            is_active=False,  # Deactivated
            created_at=sample_user.created_at,
            updated_at=sample_user.updated_at,
        )

        user_service.user_repo.read = AsyncMock(return_value=sample_user)
        user_service.deactivate_user = AsyncMock(return_value=True)

        create_usecase = CreateUserUseCase(user_service)
        delete_usecase = DeleteUserUseCase(user_service)
        read_usecase = ReadUserByIdUseCase(user_service)

        # Act - Create
        create_result = await create_usecase.execute(create_command)

        # Act - Soft Delete
        delete_command = DeleteUserCommand(user_id=create_result.user_id, soft_delete=True)
        delete_result = await delete_usecase.execute(delete_command)

        # Assert delete result
        assert delete_result.deleted is True
        assert delete_result.soft_deleted is True

        # Mock deactivated user for read
        user_service.user_repo.read = AsyncMock(return_value=deactivated_user)
        user_service.user_role_repo.find_by_user_id = AsyncMock(return_value=[])

        # Act - Read (should still work but user is inactive)
        read_command = ReadUserByIdCommand(user_id=create_result.user_id)
        read_result = await read_usecase.execute(read_command)

        # Assert
        assert read_result.user.is_active is False
        assert read_result.user.id == create_result.user_id

    @pytest.mark.asyncio
    async def test_find_user_by_email_integration(
        self, user_service: UserService, sample_user: UserEntity, sample_user_role: UserRoleEntity
    ):
        """Test finding user by email integration"""
        # Arrange
        email = sample_user.email
        sample_user_role.user_id = sample_user.id

        user_service.user_repo.find_by_email = AsyncMock(return_value=sample_user)
        user_service.user_role_repo.find_by_user_id = AsyncMock(return_value=[sample_user_role])

        read_usecase = ReadUserByEmailUseCase(user_service)

        # Act
        command = ReadUserByEmailCommand(email=email)
        result = await read_usecase.execute(command)

        # Assert
        assert result.user.email == email
        assert result.user.id == sample_user.id

    @pytest.mark.asyncio
    async def test_error_handling_chain(self, user_service: UserService):
        """Test error handling across multiple use case calls"""
        # Arrange
        non_existent_user_id = uuid4()

        user_service.user_repo.read = AsyncMock(return_value=None)

        update_usecase = UpdateUserUseCase(user_service)
        delete_usecase = DeleteUserUseCase(user_service)
        read_usecase = ReadUserByIdUseCase(user_service)

        # Act & Assert - Update non-existent user
        update_command = UpdateUserCommand(user_id=non_existent_user_id, username="nonexistent")
        with pytest.raises(UseCaseExecutionError):
            await update_usecase.execute(update_command)

        # Act & Assert - Delete non-existent user
        delete_command = DeleteUserCommand(user_id=non_existent_user_id)
        with pytest.raises(UseCaseExecutionError):
            await delete_usecase.execute(delete_command)

        # Act & Assert - Read non-existent user
        read_command = ReadUserByIdCommand(user_id=non_existent_user_id)
        with pytest.raises(UseCaseExecutionError):
            await read_usecase.execute(read_command)
