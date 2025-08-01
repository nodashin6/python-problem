"""
Database Domain Protocols
データベースドメインプロトコル - インフラストラクチャに依存しない抽象化
"""

from abc import ABC, abstractmethod
from typing import Optional

from ..base import BaseValueObject


class DatabaseConfig(BaseValueObject):
    """データベース接続設定"""
    
    url: str
    key: str
    timeout: Optional[float] = None
    max_connections: Optional[int] = None


class DatabaseTransaction(ABC):
    """データベース トランザクション プロトコル"""
    
    @abstractmethod
    async def commit(self) -> None:
        """トランザクションをコミット"""
        pass
    
    @abstractmethod
    async def rollback(self) -> None:
        """トランザクションをロールバック"""
        pass
    
    @abstractmethod
    async def __aenter__(self):
        """非同期コンテキストマネージャーの開始"""
        return self
    
    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """非同期コンテキストマネージャーの終了"""
        pass


class DatabaseHealthCheck(BaseValueObject):
    """データベース ヘルスチェック結果"""
    
    is_healthy: bool
    response_time_ms: float
    error_message: Optional[str] = None
    connection_count: Optional[int] = None