"""
User repository interface
"""

from abc import abstractmethod
from typing import Optional, List
from uuid import UUID

from .repository_base import CoreRepositoryBase
from ..models import User
from ....const import UserRole


class UserRepository(CoreRepositoryBase[User]):
    """User repository interface"""

    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email"""
        pass

    @abstractmethod
    async def find_by_username(self, username: str) -> Optional[User]:
        """Find user by username"""
        pass

    @abstractmethod
    async def find_by_role(self, role: UserRole) -> List[User]:
        """Find users by role"""
        pass

    @abstractmethod
    async def find_active_users(self, limit: int = 100, offset: int = 0) -> List[User]:
        """Find active users with pagination"""
        pass

    @abstractmethod
    async def count_by_role(self, role: UserRole) -> int:
        """Count users by role"""
        pass

    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email"""
        pass

    @abstractmethod
    async def exists_by_username(self, username: str) -> bool:
        """Check if user exists by username"""
        pass

    @abstractmethod
    async def update_last_login(self, user_id: UUID) -> None:
        """Update user's last login timestamp"""
        pass
