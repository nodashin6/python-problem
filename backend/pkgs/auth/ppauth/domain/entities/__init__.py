"""
Core domain models for problem management and user management.
Follows Domain-Driven Design principles with proper entity and value object separation.
"""

from .entities import UserEntity, UserRoleEntity
from .enums import Permission, UserRole
