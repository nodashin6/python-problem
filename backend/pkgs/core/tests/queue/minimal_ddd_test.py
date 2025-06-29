"""
最小DDDテスト
"""

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar


# Mock pydddi
class IUseCaseCommand:
    pass


class IUseCaseResult:
    pass


TCommand = TypeVar("TCommand", bound=IUseCaseCommand)
TResult = TypeVar("TResult", bound=IUseCaseResult)


class IUseCase(ABC, Generic[TCommand, TResult]):
    @abstractmethod
    async def execute(self, command: TCommand) -> TResult:
        pass


# Test implementation
@dataclass
class HelloCommand(IUseCaseCommand):
    name: str = "World"


@dataclass
class HelloResult(IUseCaseResult):
    greeting: str


class HelloUseCase(IUseCase[HelloCommand, HelloResult]):
    async def execute(self, command: HelloCommand) -> HelloResult:
        return HelloResult(greeting=f"Hello, {command.name}!")


async def main():
    print("Testing DDD Pattern...")

    usecase = HelloUseCase()
    command = HelloCommand(name="DDDテスト")
    result = await usecase.execute(command)

    print(f"Command: {command}")
    print(f"Result: {result}")
    print("✅ DDD Pattern works!")


if __name__ == "__main__":
    asyncio.run(main())
