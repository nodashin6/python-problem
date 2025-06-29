"""
Mock pydddi implementation
pydddiのモック実装 - テスト用

DDDパターンの基本インターフェースをモック
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

# Type variables for generic interfaces
TCommand = TypeVar("TCommand", bound="IUseCaseCommand")
TResult = TypeVar("TResult", bound="IUseCaseResult")


class IUseCaseCommand:
    """UseCase Command interface"""


class IUseCaseResult:
    """UseCase Result interface"""


class IUseCase(ABC, Generic[TCommand, TResult]):
    """UseCase interface"""

    @abstractmethod
    async def execute(self, command: TCommand) -> TResult:
        """Execute use case with command"""
        ...
