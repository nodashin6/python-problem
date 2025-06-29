"""
Core domain models for problem management and user management.
Follows Domain-Driven Design principles with proper entity and value object separation.
"""

from .user import RoleEntity, UserEntity

__all__ = [
    "UserEntity",
    "RoleEntity",
]
