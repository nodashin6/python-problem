"""
Tests for API routers - Complete fixed version
"""

from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from ppauth.app.api.routers import auth_router
from ppauth.app.dependencies import (
    get_auth_service,
    get_create_user_usecase,
    get_current_user,
    get_delete_user_usecase,
    get_read_active_users_usecase,
    get_read_user_by_id_usecase,
    get_read_users_by_role_usecase,
    get_update_user_usecase,
    get_user_service,
    require_admin,
)
from ppauth.domain.enums import Permission, UserRole
from ppauth.domain.models.user import User
from ppauth.usecase.create_user_usecase import CreateUserResult
from ppauth.usecase.delete_user_usecase import DeleteUserResult
from ppauth.usecase.read_users_by_role_usecase import ReadUsersByRoleResult
from ppauth.usecase.update_user_usecase import UpdateUserResult
from ppauth.usecase.user_types import UserResult


@pytest.fixture
def app():
    """Create FastAPI app for testing"""
    app = FastAPI()
    app.include_router(auth_router)
    return app


@pytest.fixture
def sample_user_model(sample_user):
    """Sample user model for testing"""
    return User(
        id=sample_user.id,
        username=sample_user.username,
        display_name=sample_user.display_name,
        email=sample_user.email,
        role=UserRole.USER,
        permissions=[Permission.USER_READ],
        is_active=sample_user.is_active,
        created_at=sample_user.created_at,
        avatar_url=sample_user.avatar_url,
        bio=sample_user.bio,
    )


@pytest.fixture
def admin_user_model(admin_user):
    """Sample admin user model for testing"""
    return User(
        id=admin_user.id,
        username=admin_user.username,
        display_name=admin_user.display_name,
        email=admin_user.email,
        role=UserRole.ADMIN,
        permissions=[Permission.SYSTEM_ADMIN],
        is_active=admin_user.is_active,
        created_at=admin_user.created_at,
        avatar_url=admin_user.avatar_url,
        bio=admin_user.bio,
    )


class TestAuthenticationEndpoints:
    """Test authentication endpoints"""

    def test_login_success(self, app, sample_user):
        """Test successful login"""
        # Setup mock services with proper async mocking
        mock_auth_service = Mock()
        mock_auth_service.authenticate_user = AsyncMock(return_value=sample_user)
        mock_auth_service.create_access_token = Mock(return_value="test_token")

        mock_user_service = Mock()

        # Override dependencies
        app.dependency_overrides[get_auth_service] = lambda: mock_auth_service
        app.dependency_overrides[get_user_service] = lambda: mock_user_service

        # Create client and execute
        with TestClient(app) as client:
            response = client.post(
                "/auth/login", json={"email": "test@example.com", "password": "password123"}
            )

        # Clear overrides
        app.dependency_overrides.clear()

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "test_token"
        assert data["token_type"] == "bearer"
        assert data["user"]["id"] == str(sample_user.id)

    def test_login_invalid_credentials(self, app):
        """Test login with invalid credentials"""
        # Setup mock services
        mock_auth_service = Mock()
        mock_auth_service.authenticate_user = AsyncMock(return_value=None)

        mock_user_service = Mock()

        # Override dependencies
        app.dependency_overrides[get_auth_service] = lambda: mock_auth_service
        app.dependency_overrides[get_user_service] = lambda: mock_user_service

        # Create client and execute
        with TestClient(app) as client:
            response = client.post(
                "/auth/login", json={"email": "test@example.com", "password": "wrong_password"}
            )

        # Clear overrides
        app.dependency_overrides.clear()

        # Assert
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

    def test_register_success(self, app):
        """Test successful user registration"""
        # Setup
        user_id = uuid4()
        mock_result = CreateUserResult(
            user_id=user_id,
            username="newuser",
            display_name="New User",
            email="new@example.com",
            avatar_url=None,
            bio=None,
            is_active=True,
        )

        mock_usecase = AsyncMock()
        mock_usecase.execute.return_value = mock_result

        # Override dependencies
        app.dependency_overrides[get_create_user_usecase] = lambda: mock_usecase

        # Create client and execute
        with TestClient(app) as client:
            response = client.post(
                "/auth/register",
                json={
                    "username": "newuser",
                    "display_name": "New User",
                    "email": "new@example.com",
                    "password": "password123",
                },
            )

        # Clear overrides
        app.dependency_overrides.clear()

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "new@example.com"


class TestUserManagementEndpoints:
    """Test user management endpoints"""

    def test_get_current_user_info_success(self, app, sample_user_model):
        """Test getting current user information"""
        # Override dependencies
        app.dependency_overrides[get_current_user] = lambda: sample_user_model

        # Create client and execute
        with TestClient(app) as client:
            response = client.get("/auth/users/me")

        # Clear overrides
        app.dependency_overrides.clear()

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(sample_user_model.id)
        assert data["username"] == sample_user_model.username

    def test_get_user_by_id_admin_access(self, app, admin_user_model, sample_user):
        """Test getting user by ID with admin access"""
        # Setup - Fix UserResult structure
        user_result = UserResult(user=sample_user)

        mock_usecase = AsyncMock()
        mock_usecase.execute.return_value = user_result

        # Override dependencies
        app.dependency_overrides[get_read_user_by_id_usecase] = lambda: mock_usecase
        app.dependency_overrides[get_current_user] = lambda: admin_user_model

        # Create client and execute
        with TestClient(app) as client:
            response = client.get(f"/auth/users/{sample_user.id}")

        # Clear overrides
        app.dependency_overrides.clear()

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(sample_user.id)

    def test_update_user_success(self, app, sample_user_model):
        """Test successful user update"""
        # Setup
        mock_result = UpdateUserResult(
            user_id=sample_user_model.id,
            username="updated_user",
            display_name="Updated User",
            email="updated@example.com",
            avatar_url=None,
            bio="Updated bio",
            is_active=True,
        )

        mock_usecase = AsyncMock()
        mock_usecase.execute.return_value = mock_result

        # Override dependencies
        app.dependency_overrides[get_update_user_usecase] = lambda: mock_usecase
        app.dependency_overrides[get_current_user] = lambda: sample_user_model

        # Create client and execute
        with TestClient(app) as client:
            response = client.put(
                f"/auth/users/{sample_user_model.id}",
                json={"username": "updated_user", "display_name": "Updated User", "bio": "Updated bio"},
            )

        # Clear overrides
        app.dependency_overrides.clear()

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "updated_user"

    def test_delete_user_admin_only(self, app, admin_user_model):
        """Test user deletion by admin"""
        # Setup
        user_id = uuid4()
        mock_result = DeleteUserResult(user_id=user_id, deleted=True, soft_deleted=True)

        mock_usecase = AsyncMock()
        mock_usecase.execute.return_value = mock_result

        # Override dependencies
        app.dependency_overrides[get_delete_user_usecase] = lambda: mock_usecase
        app.dependency_overrides[get_current_user] = lambda: admin_user_model
        app.dependency_overrides[require_admin] = lambda: admin_user_model

        # Create client and execute
        with TestClient(app) as client:
            response = client.delete(f"/auth/users/{user_id}")

        # Clear overrides
        app.dependency_overrides.clear()

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["deleted"] is True


class TestAdminEndpoints:
    """Test admin endpoints"""

    def test_create_user_admin_success(self, app, admin_user_model):
        """Test admin user creation"""
        # Setup
        user_id = uuid4()
        mock_result = CreateUserResult(
            user_id=user_id,
            username="admin_created_user",
            display_name="Admin Created User",
            email="admin_created@example.com",
            avatar_url=None,
            bio=None,
            is_active=True,
        )

        mock_usecase = AsyncMock()
        mock_usecase.execute.return_value = mock_result

        # Override dependencies
        app.dependency_overrides[get_create_user_usecase] = lambda: mock_usecase
        app.dependency_overrides[get_current_user] = lambda: admin_user_model
        app.dependency_overrides[require_admin] = lambda: admin_user_model

        # Create client and execute
        with TestClient(app) as client:
            response = client.post(
                "/auth/admin/users?role=user",  # Use lowercase enum value
                json={
                    "username": "admin_created_user",
                    "display_name": "Admin Created User",
                    "email": "admin_created@example.com",
                    "password": "password123",
                },
            )

        # Clear overrides
        app.dependency_overrides.clear()

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "admin_created_user"

    def test_get_all_users_success(self, app, admin_user_model):
        """Test getting all users list"""
        # Setup
        mock_result = ReadUsersByRoleResult(users=[], total_count=0)

        mock_usecase = AsyncMock()
        mock_usecase.execute.return_value = mock_result

        # Override dependencies
        app.dependency_overrides[get_read_users_by_role_usecase] = lambda: mock_usecase
        app.dependency_overrides[get_current_user] = lambda: admin_user_model
        app.dependency_overrides[require_admin] = lambda: admin_user_model

        # Create client and execute
        with TestClient(app) as client:
            response = client.get("/auth/users?role=user&limit=10&offset=0")

        # Clear overrides
        app.dependency_overrides.clear()

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "total_count" in data

    def test_get_active_users_success(self, app, admin_user_model):
        """Test getting active users"""
        # Setup - ReadActiveUsersUseCase returns list[User], not a result object
        mock_users = []  # Empty list of User objects

        mock_usecase = AsyncMock()
        mock_usecase.execute.return_value = mock_users

        # Override dependencies
        app.dependency_overrides[get_read_active_users_usecase] = lambda: mock_usecase
        app.dependency_overrides[get_current_user] = lambda: admin_user_model
        app.dependency_overrides[require_admin] = lambda: admin_user_model

        # Create client and execute
        with TestClient(app) as client:
            response = client.get("/auth/users/active")

        # Clear overrides
        app.dependency_overrides.clear()

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)  # Should return a list directly
