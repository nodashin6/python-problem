"""
Core Domain Repository Interfaces
コアドメインリポジトリインターフェース

Author: Judge System Team
Date: 2025-01-12
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID

from ..domain.models import Book, Problem, JudgeCase, UserProblemStatus


class BookRepositoryInterface(ABC):
    """Book repository interface"""

    @abstractmethod
    async def create(self, book: Book) -> Book:
        """Create a new book"""
        pass

    @abstractmethod
    async def find_by_id(self, book_id: UUID) -> Optional[Book]:
        """Find book by ID"""
        pass

    @abstractmethod
    async def find_published_books(self) -> List[Book]:
        """Find all published books"""
        pass

    @abstractmethod
    async def update(self, book: Book) -> Book:
        """Update book"""
        pass

    @abstractmethod
    async def delete(self, book_id: UUID) -> bool:
        """Delete book"""
        pass


class ProblemRepositoryInterface(ABC):
    """Problem repository interface"""

    @abstractmethod
    async def create(self, problem: Problem) -> Problem:
        """Create a new problem"""
        pass

    @abstractmethod
    async def find_by_id(self, problem_id: UUID) -> Optional[Problem]:
        """Find problem by ID"""
        pass

    @abstractmethod
    async def find_by_book_id(self, book_id: UUID) -> List[Problem]:
        """Find problems by book ID"""
        pass

    @abstractmethod
    async def find_published_problems(self) -> List[Problem]:
        """Find all published problems"""
        pass

    @abstractmethod
    async def update(self, problem: Problem) -> Problem:
        """Update problem"""
        pass

    @abstractmethod
    async def delete(self, problem_id: UUID) -> bool:
        """Delete problem"""
        pass


class JudgeCaseRepositoryInterface(ABC):
    """JudgeCase repository interface"""

    @abstractmethod
    async def create(self, judge_case: JudgeCase) -> JudgeCase:
        """Create a new judge case"""
        pass

    @abstractmethod
    async def find_by_id(self, judge_case_id: UUID) -> Optional[JudgeCase]:
        """Find judge case by ID"""
        pass

    @abstractmethod
    async def find_by_problem_id(self, problem_id: UUID) -> List[JudgeCase]:
        """Find judge cases by problem ID"""
        pass

    @abstractmethod
    async def update(self, judge_case: JudgeCase) -> JudgeCase:
        """Update judge case"""
        pass

    @abstractmethod
    async def delete(self, judge_case_id: UUID) -> bool:
        """Delete judge case"""
        pass


class UserProblemStatusRepositoryInterface(ABC):
    """UserProblemStatus repository interface"""

    @abstractmethod
    async def create(self, status: UserProblemStatus) -> UserProblemStatus:
        """Create a new user problem status"""
        pass

    @abstractmethod
    async def find_by_user_and_problem(
        self, user_id: str, problem_id: UUID
    ) -> Optional[UserProblemStatus]:
        """Find user problem status by user ID and problem ID"""
        pass

    @abstractmethod
    async def find_by_user_id(self, user_id: str) -> List[UserProblemStatus]:
        """Find all user problem statuses by user ID"""
        pass

    @abstractmethod
    async def update(self, status: UserProblemStatus) -> UserProblemStatus:
        """Update user problem status"""
        pass

    @abstractmethod
    async def delete(self, user_id: str, problem_id: UUID) -> bool:
        """Delete user problem status"""
        pass
