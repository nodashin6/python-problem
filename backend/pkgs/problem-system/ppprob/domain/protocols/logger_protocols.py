"""
Logger Protocol for Problem Domain
問題ドメインログプロトコル - インフラストラクチャに依存しない抽象化
"""

from abc import ABC, abstractmethod


class Logger(ABC):
    """
    Logger Protocol
    ログ出力プロトコル
    """

    @abstractmethod
    def info(self, message: str) -> None:
        """Log info message"""
        pass

    @abstractmethod
    def warning(self, message: str) -> None:
        """Log warning message"""
        pass

    @abstractmethod
    def error(self, message: str) -> None:
        """Log error message"""
        pass

    @abstractmethod
    def debug(self, message: str) -> None:
        """Log debug message"""
        pass