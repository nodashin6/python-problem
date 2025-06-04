"""
Judge case repository interface
"""

from abc import abstractmethod
from typing import Optional, List
from uuid import UUID

from .repository_base import CoreRepositoryBase
from ..models import JudgeCase
from ....const import JudgeCaseType


class JudgeCaseRepository(CoreRepositoryBase[JudgeCase]):
    """Judge case repository interface"""

    @abstractmethod
    async def find_by_problem(self, problem_id: UUID) -> List[JudgeCase]:
        """Find all judge cases for a problem"""
        pass

    @abstractmethod
    async def find_sample_cases(self, problem_id: UUID) -> List[JudgeCase]:
        """Find sample judge cases for a problem"""
        pass

    @abstractmethod
    async def find_hidden_cases(self, problem_id: UUID) -> List[JudgeCase]:
        """Find hidden judge cases for a problem"""
        pass

    @abstractmethod
    async def find_by_type(
        self, problem_id: UUID, case_type: JudgeCaseType
    ) -> List[JudgeCase]:
        """Find judge cases by type for a problem"""
        pass

    @abstractmethod
    async def count_by_problem(self, problem_id: UUID) -> int:
        """Count judge cases for a problem"""
        pass

    @abstractmethod
    async def count_by_type(self, problem_id: UUID, case_type: JudgeCaseType) -> int:
        """Count judge cases by type for a problem"""
        pass

    @abstractmethod
    async def reorder_cases(
        self, problem_id: UUID, case_orders: List[tuple[UUID, int]]
    ) -> None:
        """Reorder judge cases for a problem"""
        pass

    @abstractmethod
    async def delete_by_problem(self, problem_id: UUID) -> int:
        """Delete all judge cases for a problem"""
        pass
