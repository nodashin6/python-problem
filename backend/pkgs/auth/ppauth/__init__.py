"""
PPAuth - Authentication and Authorization Package

Clean Architecture implementation for Python problem solving platform authentication.
"""

import os

# Domain exports
from .domain.entities import UserEntity, UserRoleEntity
from .domain.entities.enums import ROLE_PERMISSIONS, Permission, UserRole
from .domain.models.user import User
from .domain.repositories.user_aggreate_read_repository import UserAggregateReadRepository
from .domain.repositories.user_repository import UserRepository
from .domain.repositories.user_role_respository import UserRoleRepository
from .domain.services.auth_service import (
    AuthenticationService,
    AuthorizationService,
    JWTManager,
    PasswordManager,
)
from .domain.services.user_service import UserService
from .infrastructure.supabase.repositories.user_aggregate_read_repository_impl import (
    UserAggregateReadRepositoryImpl,
)
from .infrastructure.supabase.repositories.user_repository_impl import UserRepositoryImpl
from .infrastructure.supabase.repositories.user_role_repository_impl import UserRoleRepositoryImpl
from .usecase.create_user_usecase import CreateUserCommand, CreateUserResult, CreateUserUseCase
from .usecase.delete_user_usecase import DeleteUserCommand, DeleteUserResult, DeleteUserUseCase
from .usecase.read_user_usecase import (
    ReadUserByEmailCommand,
    ReadUserByEmailResult,
    ReadUserByEmailUseCase,
    ReadUserByIdCommand,
    ReadUserByIdResult,
    ReadUserByIdUseCase,
    ReadUsersByRoleCommand,
    ReadUsersByRoleResult,
    ReadUsersByRoleUseCase,
)
from .usecase.update_user_usecase import UpdateUserCommand, UpdateUserResult, UpdateUserUseCase

__version__ = "1.0.0"

# Base exports always available
_base_exports = [
    # Domain entities
    "UserEntity",
    "UserRoleEntity",
    "UserRole",
    "Permission",
    "ROLE_PERMISSIONS",
    # Domain models
    "User",
    # Repository interfaces
    "UserRepository",
    "UserRoleRepository",
    "UserAggregateReadRepository",
    # Services
    "UserService",
    "AuthenticationService",
    "AuthorizationService",
    "JWTManager",
    "PasswordManager",
    # Infrastructure
    "UserRepositoryImpl",
    "UserRoleRepositoryImpl",
    "UserAggregateReadRepositoryImpl",
    # Use cases
    "CreateUserUseCase",
    "CreateUserCommand",
    "CreateUserResult",
    "UpdateUserUseCase",
    "UpdateUserCommand",
    "UpdateUserResult",
    "DeleteUserUseCase",
    "DeleteUserCommand",
    "DeleteUserResult",
    "ReadUserByIdUseCase",
    "ReadUserByIdCommand",
    "ReadUserByIdResult",
    "ReadUserByEmailUseCase",
    "ReadUserByEmailCommand",
    "ReadUserByEmailResult",
    "ReadUsersByRoleUseCase",
    "ReadUsersByRoleCommand",
    "ReadUsersByRoleResult",
]

# Conditionally import app layer if not in test mode
if os.getenv("PPAUTH_TEST_MODE") != "true":
    from .app.api.routers import auth_router
    from .app.dependencies import (
        get_current_user,
        get_optional_user,
        require_admin,
        require_moderator,
        require_verified_email,
    )

    # Add app exports to globals
    globals()["auth_router"] = auth_router
    globals()["get_current_user"] = get_current_user
    globals()["get_optional_user"] = get_optional_user
    globals()["require_admin"] = require_admin
    globals()["require_moderator"] = require_moderator
    globals()["require_verified_email"] = require_verified_email

    __all__ = _base_exports + [
        "auth_router",
        "get_current_user",
        "get_optional_user",
        "require_admin",
        "require_moderator",
        "require_verified_email",
    ]
else:
    __all__ = _base_exports
