"""
Problem repository interface
"""

from abc import abstractmethod
from typing import Optional, List, Dict, Any
from uuid import UUID

from .repository_base import CoreRepositoryBase
from ..models import Problem, Tag
from ....const import DifficultyLevel, ProblemStatus


class ProblemRepository(CoreRepositoryBase[Problem]):
    """Problem repository interface"""

    @abstractmethod
    async def find_by_title(self, title: str) -> Optional[Problem]:
        """Find problem by exact title"""
        pass

    @abstractmethod
    async def find_by_author(self, author_id: UUID) -> List[Problem]:
        """Find problems by author"""
        pass

    @abstractmethod
    async def find_by_book(self, book_id: UUID) -> List[Problem]:
        """Find problems by book"""
        pass

    @abstractmethod
    async def find_by_status(self, status: ProblemStatus) -> List[Problem]:
        """Find problems by status"""
        pass

    @abstractmethod
    async def find_by_difficulty(self, difficulty: DifficultyLevel) -> List[Problem]:
        """Find problems by difficulty"""
        pass

    @abstractmethod
    async def find_by_tags(self, tag_names: List[str]) -> List[Problem]:
        """Find problems by tags"""
        pass

    @abstractmethod
    async def search_by_title(self, title_query: str, limit: int = 20) -> List[Problem]:
        """Search problems by title (partial match)"""
        pass

    @abstractmethod
    async def find_published(self, limit: int = 50, offset: int = 0) -> List[Problem]:
        """Find published problems with pagination"""
        pass

    @abstractmethod
    async def count_by_status(self, status: ProblemStatus) -> int:
        """Count problems by status"""
        pass

    @abstractmethod
    async def count_by_author(self, author_id: UUID) -> int:
        """Count problems by author"""
        pass

    @abstractmethod
    async def get_statistics(self, problem_id: UUID) -> Dict[str, Any]:
        """Get problem statistics (submissions, acceptance rate, etc.)"""
        pass

    @abstractmethod
    async def update_statistics(self, problem_id: UUID, submission_count: int, accepted_count: int) -> None:
        """Update problem statistics"""
        pass

    @abstractmethod
    async def get_popular_tags(self, limit: int = 20) -> List[tuple[str, int]]:
        """Get popular tags with usage count"""
        pass
