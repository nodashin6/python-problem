"""
Book repository interface
"""

from pydddi import ICrudRepository
from abc import abstractmethod
from typing import Optional, List
from uuid import UUID


class BookRepository(ICrudRepository[Book]):
    """Book repository interface"""

    @abstractmethod
    async def find_by_title(self, title: str) -> Optional[Book]:
        """Find book by exact title"""
        pass

    @abstractmethod
    async def find_by_author(self, author_id: UUID) -> List[Book]:
        """Find books by author"""
        pass

    @abstractmethod
    async def find_published(self, limit: int = 50, offset: int = 0) -> List[Book]:
        """Find published books with pagination"""
        pass

    @abstractmethod
    async def search_by_title(self, title_query: str, limit: int = 20) -> List[Book]:
        """Search books by title (partial match)"""
        pass

    @abstractmethod
    async def count_by_author(self, author_id: UUID) -> int:
        """Count books by author"""
        pass

    @abstractmethod
    async def count_published(self) -> int:
        """Count published books"""
        pass
