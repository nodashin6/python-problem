"""
Auth Domain Package
認証ドメインパッケージ - DDDアーキテクチャ準拠
"""

# Models (Aggregate Roots)
# Entities (Persistence Objects)
from .entities import RoleEntity, UserEntity

# Enums
from .enums import Permission, UserRole
from .models import User

# Repositories
from .repositories import UserAggregateReadRepository, UserRepository

# Schemas
from .schemas import (
    CreateUserSchema,
    ReadUserSchema,
    UpdateUserSchema,
)

# Domain Services
from .services import UserService

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
    "UserService",
    # Repositories
    "UserRepository",
    "UserAggregateReadRepository",
    # Schemas
    "CreateUserSchema",
    "UpdateUserSchema",
    "ReadUserSchema",
]
