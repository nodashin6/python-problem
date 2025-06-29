"""
Auth Package
認証パッケージ - ユーザー管理・認証・認可

責任領域:
- ユーザー登録・認証
- 権限管理・ロール制御
- JWT トークン管理
- パスワード管理
- セッション管理
"""

# Domain Models (User Aggregate)
# API Controllers
from .app.api.controllers import AuthController, UserController

# Domain Entities
from .domain.entities import UserEntity, UserRoleEntity

# Domain Enums
from .domain.enums import Permission, UserRole
from .domain.models import User

# Domain Services
from .domain.services import AuthDomainService, UserDomainService

# Use Cases
from .usecase import (
    AuthenticateUserUseCase,
    CreateUserUseCase,
    DeleteUserUseCase,
    UpdateUserUseCase,
)

__all__ = [
    # Models
    "User",
    # Entities
    "UserEntity",
    "UserRoleEntity",
    # Enums
    "UserRole",
    "Permission",
    # Services
    "UserDomainService",
    "AuthDomainService",
    # Use Cases
    "CreateUserUseCase",
    "AuthenticateUserUseCase",
    "UpdateUserUseCase",
    "DeleteUserUseCase",
    # Controllers
    "AuthController",
    "UserController",
]
