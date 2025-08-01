"""
Client Protocols for Domain Layer
ドメインレイヤー用クライアントプロトコル - インフラストラクチャに依存しない抽象化
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class DBClient(ABC):
    """
    Database Client Protocol
    データベースクライアントプロトコル - RDBMSの抽象化
    """

    @abstractmethod
    async def execute_query(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Execute a query and return results"""
        pass

    @abstractmethod
    async def execute_command(
        self,
        command: str,
        params: Optional[Dict[str, Any]] = None
    ) -> int:
        """Execute a command and return affected rows count"""
        pass

    @abstractmethod
    async def begin_transaction(self) -> None:
        """Begin a database transaction"""
        pass

    @abstractmethod
    async def commit_transaction(self) -> None:
        """Commit the current transaction"""
        pass

    @abstractmethod
    async def rollback_transaction(self) -> None:
        """Rollback the current transaction"""
        pass


class S3Client(ABC):
    """
    S3 Client Protocol
    S3クライアントプロトコル - オブジェクトストレージの抽象化
    """

    @abstractmethod
    async def upload_file(
        self,
        bucket: str,
        key: str,
        data: bytes,
        content_type: Optional[str] = None
    ) -> str:
        """Upload file and return URL"""
        pass

    @abstractmethod
    async def download_file(
        self,
        bucket: str,
        key: str
    ) -> bytes:
        """Download file and return content"""
        pass

    @abstractmethod
    async def delete_file(
        self,
        bucket: str,
        key: str
    ) -> bool:
        """Delete file and return success status"""
        pass

    @abstractmethod
    async def get_presigned_url(
        self,
        bucket: str,
        key: str,
        expires_in: int = 3600
    ) -> str:
        """Generate presigned URL for file access"""
        pass

    @abstractmethod
    async def list_files(
        self,
        bucket: str,
        prefix: Optional[str] = None
    ) -> List[str]:
        """List files in bucket with optional prefix"""
        pass


class MQClient(ABC):
    """
    Message Queue Client Protocol
    メッセージキュークライアントプロトコル - 非同期メッセージングの抽象化
    """

    @abstractmethod
    async def publish_message(
        self,
        queue: str,
        message: Dict[str, Any],
        delay: Optional[int] = None
    ) -> str:
        """Publish message to queue and return message ID"""
        pass

    @abstractmethod
    async def consume_message(
        self,
        queue: str,
        timeout: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Consume message from queue"""
        pass

    @abstractmethod
    async def acknowledge_message(
        self,
        queue: str,
        message_id: str
    ) -> bool:
        """Acknowledge message processing"""
        pass

    @abstractmethod
    async def reject_message(
        self,
        queue: str,
        message_id: str,
        requeue: bool = True
    ) -> bool:
        """Reject message and optionally requeue"""
        pass

    @abstractmethod
    async def create_queue(
        self,
        queue: str,
        durable: bool = True
    ) -> bool:
        """Create a new queue"""
        pass

    @abstractmethod
    async def delete_queue(
        self,
        queue: str,
        if_empty: bool = True
    ) -> bool:
        """Delete a queue"""
        pass