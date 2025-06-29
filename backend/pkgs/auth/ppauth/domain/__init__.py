"""
Auth Domain Package
認証ドメインパッケージ - DDDアーキテクチャ準拠
"""

# Models (Aggregate Roots)
# Entities (Persistence Objects)
from .entities import UserEntity, UserRoleEntity

# Enums
from .enums import Permission, UserRole
from .models import User

# Repositories
from .repositories import UserAggregateReadRepository, UserRepository, UserRoleRepository

# Domain Services
from .services import AuthDomainService, UserDomainService

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
    # Repositories
    "UserRepository",
    "UserRoleRepository",
    "UserAggregateReadRepository",
]
