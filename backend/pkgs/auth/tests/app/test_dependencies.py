"""
Tests for app dependencies
"""

from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from ppauth.app.dependencies import (
    get_current_user,
    require_admin,
    require_moderator_or_admin,
)
from ppauth.domain.enums import Permission, UserRole
from ppauth.domain.models.user import User
from backend.pkgs.auth.ppauth.domain.helpers.authentificator.authentificator import AuthenticationService
from ppauth.domain.services.user_service import UserService
from ppauth.usecase.create_user_usecase import CreateUserUseCase
from ppauth.usecase.delete_user_usecase import DeleteUserUseCase
from ppauth.usecase.read_user_aggregate_usecase import ReadActiveUsersUseCase
from ppauth.usecase.read_user_by_email_usecase import ReadUserByEmailUseCase
from ppauth.usecase.read_user_by_id_usecase import ReadUserByIdUseCase
from ppauth.usecase.read_users_by_role_usecase import ReadUsersByRoleUseCase
from ppauth.usecase.update_user_usecase import UpdateUserUseCase


class TestAuthenticationDependencies:
    """Test authentication dependencies"""

    @pytest.mark.asyncio
    async def test_get_current_user_valid_token(self, sample_user):
        """Test get_current_user with valid token"""
        # Setup
        mock_auth_service = Mock(spec=AuthenticationService)
        mock_auth_service.get_user_from_token = AsyncMock(return_value=sample_user)

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token")

        # Execute
        result = await get_current_user(credentials, mock_auth_service)

        # Assert
        assert result == sample_user

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self):
        """Test get_current_user with invalid token"""
        # Setup
        mock_auth_service = Mock(spec=AuthenticationService)
        mock_auth_service.get_user_from_token = AsyncMock(return_value=None)

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid_token")

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, mock_auth_service)

        assert exc_info.value.status_code == 401


class TestRoleBasedDependencies:
    """Test role-based access dependencies"""

    @pytest.mark.asyncio
    async def test_require_admin_with_admin_user(self):
        """Test require_admin with admin user"""
        from uuid import uuid4

        # Setup - create user with admin role
        user = User(
            id=uuid4(),
            user_name="adminuser",
            display_name="Admin User",
            email="admin@example.com",
            role=UserRole.ADMIN,
            permissions=[Permission.SYSTEM_ADMIN],
            is_active=True,
        )

        # Execute
        result = await require_admin(user)

        # Assert
        assert result == user

    @pytest.mark.asyncio
    async def test_require_admin_with_regular_user(self):
        """Test require_admin with regular user"""
        from uuid import uuid4

        # Setup - create user with regular role
        user = User(
            id=uuid4(),
            user_name="regularuser",
            display_name="Regular User",
            email="user@example.com",
            role=UserRole.USER,
            permissions=[Permission.USER_READ],
            is_active=True,
        )

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await require_admin(user)

        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_require_moderator_or_admin_with_admin_user(self):
        """Test require_moderator_or_admin with admin user"""
        from uuid import uuid4

        # Setup - create user with admin role
        user = User(
            id=uuid4(),
            user_name="adminuser",
            display_name="Admin User",
            email="admin@example.com",
            role=UserRole.ADMIN,
            permissions=[Permission.SYSTEM_ADMIN],
            is_active=True,
        )

        # Execute
        result = await require_moderator_or_admin(user)

        # Assert
        assert result == user

    @pytest.mark.asyncio
    async def test_require_moderator_or_admin_with_moderator_user(self):
        """Test require_moderator_or_admin with moderator user"""
        from uuid import uuid4

        # Setup - create user with moderator role
        user = User(
            id=uuid4(),
            user_name="moderatoruser",
            display_name="Moderator User",
            email="moderator@example.com",
            role=UserRole.MODERATOR,
            permissions=[Permission.USER_CREATE, Permission.USER_READ, Permission.USER_UPDATE],
            is_active=True,
        )

        # Execute
        result = await require_moderator_or_admin(user)

        # Assert
        assert result == user

    @pytest.mark.asyncio
    async def test_require_moderator_or_admin_with_regular_user(self):
        """Test require_moderator_or_admin with regular user"""
        from uuid import uuid4

        # Setup - create user with regular role
        user = User(
            id=uuid4(),
            user_name="regularuser",
            display_name="Regular User",
            email="user@example.com",
            role=UserRole.USER,
            permissions=[Permission.USER_READ],
            is_active=True,
        )

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await require_moderator_or_admin(user)

        assert exc_info.value.status_code == 403


class TestUserAccountStatus:
    """Test user account status checks"""

    @pytest.mark.asyncio
    async def test_get_current_user_inactive_user(self):
        """Test get_current_user with inactive user"""
        from uuid import uuid4

        # Setup
        inactive_user = User(
            id=uuid4(),
            user_name="inactiveuser",
            display_name="Inactive User",
            email="inactive@example.com",
            role=UserRole.USER,
            permissions=[Permission.USER_READ],
            is_active=False,  # Inactive user
        )

        mock_auth_service = Mock(spec=AuthenticationService)
        mock_auth_service.get_user_from_token = AsyncMock(return_value=inactive_user)

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token")

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, mock_auth_service)

        assert exc_info.value.status_code == 403
        assert "User account is deactivated" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_current_user_service_exception(self):
        """Test get_current_user when auth service raises exception"""
        # Setup
        mock_auth_service = Mock(spec=AuthenticationService)
        mock_auth_service.get_user_from_token = AsyncMock(side_effect=Exception("Database error"))

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token")

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, mock_auth_service)

        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in exc_info.value.detail


class TestDependencyInjection:
    """Test dependency injection functions"""

    @pytest.mark.asyncio
    async def test_get_create_user_usecase(self):
        """Test get_create_user_usecase dependency"""
        from ppauth.app.dependencies import get_create_user_usecase

        mock_user_service = Mock(spec=UserService)

        # Execute
        usecase = await get_create_user_usecase(mock_user_service)

        # Assert
        assert isinstance(usecase, CreateUserUseCase)
        assert usecase.user_service == mock_user_service

    @pytest.mark.asyncio
    async def test_get_update_user_usecase(self):
        """Test get_update_user_usecase dependency"""
        from ppauth.app.dependencies import get_update_user_usecase

        mock_user_service = Mock(spec=UserService)

        # Execute
        usecase = await get_update_user_usecase(mock_user_service)

        # Assert
        assert isinstance(usecase, UpdateUserUseCase)
        assert usecase.user_service == mock_user_service

    @pytest.mark.asyncio
    async def test_get_delete_user_usecase(self):
        """Test get_delete_user_usecase dependency"""
        from ppauth.app.dependencies import get_delete_user_usecase

        mock_user_service = Mock(spec=UserService)

        # Execute
        usecase = await get_delete_user_usecase(mock_user_service)

        # Assert
        assert isinstance(usecase, DeleteUserUseCase)
        assert usecase.user_service == mock_user_service

    @pytest.mark.asyncio
    async def test_get_read_user_by_id_usecase(self):
        """Test get_read_user_by_id_usecase dependency"""
        from ppauth.app.dependencies import get_read_user_by_id_usecase

        mock_user_service = Mock(spec=UserService)

        # Execute
        usecase = await get_read_user_by_id_usecase(mock_user_service)

        # Assert
        assert isinstance(usecase, ReadUserByIdUseCase)
        assert usecase.user_service == mock_user_service

    @pytest.mark.asyncio
    async def test_get_read_user_by_email_usecase(self):
        """Test get_read_user_by_email_usecase dependency"""
        from ppauth.app.dependencies import get_read_user_by_email_usecase

        mock_user_service = Mock(spec=UserService)

        # Execute
        usecase = await get_read_user_by_email_usecase(mock_user_service)

        # Assert
        assert isinstance(usecase, ReadUserByEmailUseCase)
        assert usecase.user_service == mock_user_service

    @pytest.mark.asyncio
    async def test_get_read_users_by_role_usecase(self):
        """Test get_read_users_by_role_usecase dependency"""
        from ppauth.app.dependencies import get_read_users_by_role_usecase

        mock_user_service = Mock(spec=UserService)

        # Execute
        usecase = await get_read_users_by_role_usecase(mock_user_service)

        # Assert
        assert isinstance(usecase, ReadUsersByRoleUseCase)
        assert usecase.user_service == mock_user_service

    @pytest.mark.asyncio
    async def test_get_read_active_users_usecase(self):
        """Test get_read_active_users_usecase dependency - currently returns None due to missing implementation"""
        from ppauth.app.dependencies import get_read_active_users_usecase

        # Execute
        usecase = await get_read_active_users_usecase()

        # Assert - Currently returns None due to TODO implementation
        # TODO: Update this test when the dependency is properly implemented
        assert usecase is None  # This is expected until UserAggregateReadRepository dependency is injected
