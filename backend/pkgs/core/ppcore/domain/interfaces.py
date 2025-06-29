"""
Core Domain Interfaces
コアドメインインターフェース群 - 全パッケージで共通利用
"""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar
from uuid import UUID

# Type variables for generic interfaces
T = TypeVar("T")  # Entity type
C = TypeVar("C")  # Create schema type
R = TypeVar("R")  # Read schema type
U = TypeVar("U")  # Update schema type


class IRepository(ABC, Generic[T, C, R, U]):
    """
    Repository interface
    リポジトリインターフェース基底クラス
    """

    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create new entity"""
        ...

    @abstractmethod
    async def get(self, entity_id: UUID) -> T | None:
        """Get entity by ID"""
        ...

    @abstractmethod
    async def update(self, entity_id: UUID, entity: T) -> T | None:
        """Update entity"""
        ...

    @abstractmethod
    async def delete(self, entity_id: UUID) -> bool:
        """Delete entity"""
        ...

    @abstractmethod
    async def list(self, limit: int = 100, offset: int = 0) -> list[T]:
        """List entities with pagination"""
        ...


class IDomainService(ABC):
    """
    Domain Service interface
    ドメインサービスインターフェース基底クラス
    """

    def __init__(self) -> None:
        """Initialize domain service"""
        super().__init__()


class IUseCase(ABC, Generic[T, R]):
    """
    UseCase interface
    ユースケースインターフェース基底クラス
    """

    @abstractmethod
    async def execute(self, command: T) -> R:
        """Execute usecase"""
        ...
