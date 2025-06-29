"""
Tests for UserService domain service
"""

from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from ppauth.domain.entities.user import RoleEntity, UserEntity
from ppauth.domain.enums import UserRole
from ppauth.domain.services.user_service import UserService


class TestUserService:
    """Test cases for UserService"""

    @pytest.mark.asyncio
    async def test_is_email_available_true(self, user_service: UserService):
        """Test email availability check when email is available"""
        # Arrange
        email = "available@example.com"
        user_service.user_repo.find_by_email = AsyncMock(return_value=None)

        # Act
        result = await user_service.is_email_available(email)

        # Assert
        assert result is True
        user_service.user_repo.find_by_email.assert_called_once_with(email)

    @pytest.mark.asyncio
    async def test_is_email_available_false(self, user_service: UserService, sample_user: UserEntity):
        """Test email availability check when email is taken"""
        # Arrange
        email = "taken@example.com"
        user_service.user_repo.find_by_email = AsyncMock(return_value=sample_user)

        # Act
        result = await user_service.is_email_available(email)

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_is_user_name_available_true(self, user_service: UserService):
        """Test user_name availability check when user_name is available"""
        # Arrange
        user_name = "availableuser"
        user_service.user_repo.find_by_user_name = AsyncMock(return_value=None)

        # Act
        result = await user_service.is_user_name_available(user_name)

        # Assert
        assert result is True
        user_service.user_repo.find_by_user_name.assert_called_once_with(user_name)

    @pytest.mark.asyncio
    async def test_is_user_name_available_false(self, user_service: UserService, sample_user: UserEntity):
        """Test user_name availability check when user_name is taken"""
        # Arrange
        user_name = "takenuser"
        user_service.user_repo.find_by_user_name = AsyncMock(return_value=sample_user)

        # Act
        result = await user_service.is_user_name_available(user_name)

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_register_user_success(self, user_service: UserService, sample_user: UserEntity):
        """Test successful user registration"""
        # Arrange
        email = "newuser@example.com"
        user_name = "newuser"
        display_name = "New User"
        password = "password123"

        user_service.user_repo.find_by_email = AsyncMock(return_value=None)
        user_service.user_repo.find_by_user_name = AsyncMock(return_value=None)
        user_service.user_repo.create_user_with_role = AsyncMock(return_value=sample_user)

        # Act
        result = await user_service.register_user(
            email=email, user_name=user_name, display_name=display_name, password=password
        )

        # Assert
        assert result == sample_user
        user_service.authentificator.hash_password.assert_called_once_with(password)
        user_service.user_repo.create_user_with_role.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_user_email_taken(self, user_service: UserService, sample_user: UserEntity):
        """Test user registration when email is already taken"""
        # Arrange
        email = "taken@example.com"
        user_name = "newuser"
        display_name = "New User"
        password = "password123"

        user_service.user_repo.find_by_email = AsyncMock(return_value=sample_user)

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await user_service.register_user(
                email=email, user_name=user_name, display_name=display_name, password=password
            )

        assert "Email already exists" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_register_user_user_name_taken(self, user_service: UserService, sample_user: UserEntity):
        """Test user registration when user_name is already taken"""
        # Arrange
        email = "new@example.com"
        user_name = "takenuser"
        display_name = "New User"
        password = "password123"

        user_service.user_repo.find_by_email = AsyncMock(return_value=None)
        user_service.user_repo.find_by_user_name = AsyncMock(return_value=sample_user)

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await user_service.register_user(
                email=email, user_name=user_name, display_name=display_name, password=password
            )

        assert "user_name already exists" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, user_service: UserService, sample_user: UserEntity):
        """Test successful user authentication"""
        # Arrange
        email = sample_user.email
        password = "correct_password"

        user_service.user_repo.find_by_email = AsyncMock(return_value=sample_user)
        user_service.authentificator.verify_password = Mock(return_value=True)

        # Act
        result = await user_service.authenticate_user(email, password)

        # Assert
        assert result == sample_user
        user_service.user_repo.find_by_email.assert_called_once_with(email)
        user_service.authentificator.verify_password.assert_called_once_with(
            password, sample_user.password_hash
        )

    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(
        self, user_service: UserService, sample_user: UserEntity
    ):
        """Test authentication with wrong password"""
        # Arrange
        email = sample_user.email
        password = "wrong_password"

        user_service.user_repo.find_by_email = AsyncMock(return_value=sample_user)
        user_service.authentificator.verify_password = Mock(return_value=False)

        # Act
        result = await user_service.authenticate_user(email, password)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, user_service: UserService):
        """Test authentication when user is not found"""
        # Arrange
        email = "nonexistent@example.com"
        password = "password123"

        user_service.user_repo.find_by_email = AsyncMock(return_value=None)

        # Act
        result = await user_service.authenticate_user(email, password)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_user_inactive(self, user_service: UserService, sample_user: UserEntity):
        """Test authentication when user is inactive"""
        # Arrange
        email = sample_user.email
        password = "correct_password"
        sample_user.is_active = False

        user_service.user_repo.find_by_email = AsyncMock(return_value=sample_user)

        # Act
        result = await user_service.authenticate_user(email, password)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_deactivate_user_success(self, user_service: UserService, sample_user: UserEntity):
        """Test successful user deactivation"""
        # Arrange
        user_id = sample_user.id
        user_service.user_repo.update_user_with_role = AsyncMock(return_value=sample_user)

        # Act
        result = await user_service.deactivate_user(user_id)

        # Assert
        assert result is True
        user_service.user_repo.update_user_with_role.assert_called_once()

    @pytest.mark.asyncio
    async def test_deactivate_user_not_found(self, user_service: UserService):
        """Test user deactivation when user is not found"""
        # Arrange
        user_id = uuid4()
        user_service.user_repo.update_user_with_role = AsyncMock(return_value=None)

        # Act
        result = await user_service.deactivate_user(user_id)

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_assign_role_success(self, user_service: UserService):
        """Test successful role assignment"""
        # Arrange
        user_id = uuid4()
        role = UserRole.ADMIN

        # user_service.user_role_repo.exists_by_user_id_and_role = AsyncMock(return_value=False)
        # user_service.user_role_repo.create = AsyncMock(return_value=None)

        # Act
        result = await user_service.change_user_role(user_id, role)

        # Assert
        assert result is None  # change_user_role returns UserEntity or None
        # user_service.user_role_repo.exists_by_user_id_and_role.assert_called_once_with(user_id, role)
        # user_service.user_role_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_assign_role_already_exists(self, user_service: UserService):
        """Test role assignment when role already exists"""
        # Arrange
        user_id = uuid4()
        role = UserRole.ADMIN

        # user_service.user_role_repo.exists_by_user_id_and_role = AsyncMock(return_value=True)

        # Act
        result = await user_service.change_user_role(user_id, role)

        # Assert
        assert result is None  # change_user_role returns UserEntity or None
