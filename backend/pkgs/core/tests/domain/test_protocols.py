"""
Tests for Core Domain Protocols
コアドメインプロトコルのテスト
"""

import pytest
from typing import Any, Dict, List, Optional

from ppcore.domain.client_protocols import DBClient, S3Client, MQClient
from ppcore.domain.protocols.database_protocols import DatabaseConfig, DatabaseTransaction, DatabaseHealthCheck


class TestDatabaseConfig:
    """Test DatabaseConfig value object"""

    def test_creation(self):
        """Test config creation"""
        config = DatabaseConfig(
            url="postgresql://localhost:5432/test",
            key="test_key"
        )
        
        assert config.url == "postgresql://localhost:5432/test"
        assert config.key == "test_key"
        assert config.timeout is None
        assert config.max_connections is None

    def test_creation_with_optional_fields(self):
        """Test config creation with optional fields"""
        config = DatabaseConfig(
            url="postgresql://localhost:5432/test",
            key="test_key",
            timeout=30.0,
            max_connections=10
        )
        
        assert config.timeout == 30.0
        assert config.max_connections == 10

    def test_immutability(self):
        """Test that config is immutable"""
        config = DatabaseConfig(url="test", key="key")
        
        with pytest.raises(ValueError, match=".*frozen.*"):
            config.url = "new_url"


class TestDatabaseHealthCheck:
    """Test DatabaseHealthCheck value object"""

    def test_healthy_result(self):
        """Test healthy database result"""
        health = DatabaseHealthCheck(
            is_healthy=True,
            response_time_ms=150.5
        )
        
        assert health.is_healthy is True
        assert health.response_time_ms == 150.5
        assert health.error_message is None
        assert health.connection_count is None

    def test_unhealthy_result(self):
        """Test unhealthy database result"""
        health = DatabaseHealthCheck(
            is_healthy=False,
            response_time_ms=5000.0,
            error_message="Connection timeout",
            connection_count=0
        )
        
        assert health.is_healthy is False
        assert health.error_message == "Connection timeout"
        assert health.connection_count == 0


class MockDBClient(DBClient):
    """Mock implementation of DBClient for testing"""
    
    def __init__(self):
        self.queries = []
        self.commands = []
        self.responses = {}
        self.in_transaction = False
    
    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        self.queries.append((query, params))
        return self.responses.get(query, [])
    
    async def execute_command(self, command: str, params: Optional[Dict[str, Any]] = None) -> int:
        self.commands.append((command, params))
        return 1  # Mock affected rows
    
    async def begin_transaction(self) -> None:
        self.in_transaction = True
    
    async def commit_transaction(self) -> None:
        self.in_transaction = False
    
    async def rollback_transaction(self) -> None:
        self.in_transaction = False
    
    def set_response(self, query: str, response: List[Dict[str, Any]]):
        self.responses[query] = response


class MockS3Client(S3Client):
    """Mock implementation of S3Client for testing"""
    
    def __init__(self):
        self.uploads = []
        self.downloads = []
    
    async def upload_file(self, bucket: str, key: str, file_path: str) -> bool:
        self.uploads.append((bucket, key, file_path))
        return True
    
    async def download_file(self, bucket: str, key: str, file_path: str) -> bool:
        self.downloads.append((bucket, key, file_path))
        return True
    
    async def delete_file(self, bucket: str, key: str) -> bool:
        return True
    
    async def get_presigned_url(self, bucket: str, key: str, expires_in: int = 3600) -> str:
        return f"https://mock-s3.com/{bucket}/{key}?expires={expires_in}"
    
    async def list_files(self, bucket: str, prefix: str = "") -> List[str]:
        return []


class MockMQClient(MQClient):
    """Mock implementation of MQClient for testing"""
    
    def __init__(self):
        self.published = []
        self.consumed = []
        self.acknowledged = []
        self.rejected = []
        self.queues = set()
    
    async def publish_message(self, queue: str, message: Dict[str, Any], delay: Optional[int] = None) -> str:
        msg_id = f"msg_{len(self.published)}"
        self.published.append((queue, message, delay, msg_id))
        return msg_id
    
    async def consume_message(self, queue: str, timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        self.consumed.append((queue, timeout))
        return {"id": "test_msg", "body": "test"}
    
    async def acknowledge_message(self, queue: str, message_id: str) -> bool:
        self.acknowledged.append((queue, message_id))
        return True
    
    async def reject_message(self, queue: str, message_id: str, requeue: bool = True) -> bool:
        self.rejected.append((queue, message_id, requeue))
        return True
    
    async def create_queue(self, queue: str, durable: bool = True) -> bool:
        self.queues.add(queue)
        return True
    
    async def delete_queue(self, queue: str, if_empty: bool = True) -> bool:
        self.queues.discard(queue)
        return True


class TestDBClient:
    """Test DBClient protocol functionality"""

    @pytest.fixture
    def db_client(self):
        return MockDBClient()

    async def test_execute_query_without_params(self, db_client):
        """Test query execution without parameters"""
        query = "SELECT * FROM users"
        expected_response = [{"id": 1, "name": "test"}]
        
        db_client.set_response(query, expected_response)
        result = await db_client.execute_query(query)
        
        assert result == expected_response
        assert (query, None) in db_client.queries

    async def test_execute_query_with_params(self, db_client):
        """Test query execution with parameters"""
        query = "SELECT * FROM users WHERE id = %(id)s"
        params = {"id": 123}
        expected_response = [{"id": 123, "name": "test_user"}]
        
        db_client.set_response(query, expected_response)
        result = await db_client.execute_query(query, params)
        
        assert result == expected_response
        assert (query, params) in db_client.queries


class TestS3Client:
    """Test S3Client protocol functionality"""

    @pytest.fixture
    def s3_client(self):
        return MockS3Client()

    async def test_upload_file(self, s3_client):
        """Test file upload"""
        result = await s3_client.upload_file("test-bucket", "test-key", "/path/to/file")
        
        assert result is True
        assert ("test-bucket", "test-key", "/path/to/file") in s3_client.uploads

    async def test_download_file(self, s3_client):
        """Test file download"""
        result = await s3_client.download_file("test-bucket", "test-key", "/path/to/file")
        
        assert result is True
        assert ("test-bucket", "test-key", "/path/to/file") in s3_client.downloads

    async def test_delete_file(self, s3_client):
        """Test file deletion"""
        result = await s3_client.delete_file("test-bucket", "test-key")
        assert result is True

    async def test_list_files(self, s3_client):
        """Test file listing"""
        result = await s3_client.list_files("test-bucket", "prefix/")
        assert isinstance(result, list)


class TestMQClient:
    """Test MQClient protocol functionality"""

    @pytest.fixture
    def mq_client(self):
        return MockMQClient()

    async def test_publish(self, mq_client):
        """Test message publishing"""
        queue = "test-queue"
        message = {"type": "test", "data": "hello"}
        
        result = await mq_client.publish_message(queue, message)
        
        assert isinstance(result, str)
        assert len(mq_client.published) == 1

    async def test_subscribe(self, mq_client):
        """Test message consumption"""
        queue = "test-queue"
        
        result = await mq_client.consume_message(queue)
        
        assert result is not None
        assert len(mq_client.consumed) == 1

    async def test_unsubscribe(self, mq_client):
        """Test queue management"""
        queue = "test-queue"
        
        # Create queue
        result = await mq_client.create_queue(queue)
        assert result is True
        assert queue in mq_client.queues
        
        # Delete queue
        result = await mq_client.delete_queue(queue)
        assert result is True
        assert queue not in mq_client.queues