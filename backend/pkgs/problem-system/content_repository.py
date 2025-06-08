"""
Content repository interfaces for problem content, editorial, etc.
"""

from abc import abstractmethod
from typing import Optional, List
from uuid import UUID

from .repository_base import CoreRepositoryBase
from ..models import ProblemContent, Editorial, EditorialContent


class ProblemContentRepository(CoreRepositoryBase[ProblemContent]):
    """Problem content repository interface"""

    @abstractmethod
    async def find_by_problem_and_language(
        self, problem_id: UUID, language: str
    ) -> Optional[ProblemContent]:
        """Find problem content by problem ID and language"""
        pass

    @abstractmethod
    async def find_by_problem(self, problem_id: UUID) -> List[ProblemContent]:
        """Find all content for a problem"""
        pass

    @abstractmethod
    async def find_available_languages(self, problem_id: UUID) -> List[str]:
        """Find available languages for a problem"""
        pass

    @abstractmethod
    async def delete_by_problem(self, problem_id: UUID) -> int:
        """Delete all content for a problem"""
        pass


class EditorialRepository(CoreRepositoryBase[Editorial]):
    """Editorial repository interface"""

    @abstractmethod
    async def find_by_problem(self, problem_id: UUID) -> Optional[Editorial]:
        """Find editorial for a problem"""
        pass

    @abstractmethod
    async def find_by_author(self, author_id: UUID) -> List[Editorial]:
        """Find editorials by author"""
        pass

    @abstractmethod
    async def find_published(self, limit: int = 50, offset: int = 0) -> List[Editorial]:
        """Find published editorials"""
        pass

    @abstractmethod
    async def count_by_author(self, author_id: UUID) -> int:
        """Count editorials by author"""
        pass


class EditorialContentRepository(CoreRepositoryBase[EditorialContent]):
    """Editorial content repository interface"""

    @abstractmethod
    async def find_by_editorial_and_language(
        self, editorial_id: UUID, language: str
    ) -> Optional[EditorialContent]:
        """Find editorial content by editorial ID and language"""
        pass

    @abstractmethod
    async def find_by_editorial(self, editorial_id: UUID) -> List[EditorialContent]:
        """Find all content for an editorial"""
        pass

    @abstractmethod
    async def find_available_languages(self, editorial_id: UUID) -> List[str]:
        """Find available languages for an editorial"""
        pass

    @abstractmethod
    async def delete_by_editorial(self, editorial_id: UUID) -> int:
        """Delete all content for an editorial"""
        pass
