"""
Tests for Core Domain Protocols - Fixed Version
コアドメインプロトコルのテスト
"""

import pytest
from typing import Any, Dict, List, Optional

from ppcore.domain.client_protocols import DBClient, S3Client, MQClient
from ppcore.domain.protocols.database_protocols import DatabaseConfig, DatabaseHealthCheck


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
        self.files = {}
    
    async def upload_file(self, bucket: str, key: str, data: bytes, content_type: Optional[str] = None) -> str:
        self.uploads.append((bucket, key, data, content_type))
        self.files[f"{bucket}/{key}"] = data
        return f"https://{bucket}.s3.amazonaws.com/{key}"
    
    async def download_file(self, bucket: str, key: str) -> bytes:
        self.downloads.append((bucket, key))
        return self.files.get(f"{bucket}/{key}", b"mock_data")
    
    async def delete_file(self, bucket: str, key: str) -> bool:
        if f"{bucket}/{key}" in self.files:
            del self.files[f"{bucket}/{key}"]
        return True
    
    async def get_presigned_url(self, bucket: str, key: str, expires_in: int = 3600) -> str:
        return f"https://{bucket}.s3.amazonaws.com/{key}?expires={expires_in}"
    
    async def list_files(self, bucket: str, prefix: Optional[str] = None) -> List[str]:
        prefix = prefix or ""
        return [key.split("/", 1)[1] for key in self.files.keys() 
                if key.startswith(f"{bucket}/{prefix}")]


class MockMQClient(MQClient):
    """Mock implementation of MQClient for testing"""
    
    def __init__(self):
        self.published = []
        self.queues = {}
        self.messages = {}
        self.message_counter = 0
    
    async def publish_message(self, queue: str, message: Dict[str, Any], delay: Optional[int] = None) -> str:
        message_id = f"msg_{self.message_counter}"
        self.message_counter += 1
        self.published.append((queue, message, delay))
        
        if queue not in self.messages:
            self.messages[queue] = []
        self.messages[queue].append({"id": message_id, "data": message})
        return message_id
    
    async def consume_message(self, queue: str, timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        if queue in self.messages and self.messages[queue]:
            return self.messages[queue].pop(0)
        return None
    
    async def acknowledge_message(self, queue: str, message_id: str) -> bool:
        return True
    
    async def reject_message(self, queue: str, message_id: str, requeue: bool = True) -> bool:
        return True
    
    async def create_queue(self, queue: str, durable: bool = True) -> bool:
        self.queues[queue] = {"durable": durable}
        return True
    
    async def delete_queue(self, queue: str, if_empty: bool = True) -> bool:
        if queue in self.queues:
            del self.queues[queue]
        if queue in self.messages:
            del self.messages[queue]
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

    async def test_execute_command(self, db_client):
        """Test command execution"""
        command = "INSERT INTO users (name) VALUES (%(name)s)"
        params = {"name": "test_user"}
        
        result = await db_client.execute_command(command, params)
        
        assert result == 1
        assert (command, params) in db_client.commands

    async def test_transaction_management(self, db_client):
        """Test transaction operations"""
        assert not db_client.in_transaction
        
        await db_client.begin_transaction()
        assert db_client.in_transaction
        
        await db_client.commit_transaction()
        assert not db_client.in_transaction
        
        await db_client.begin_transaction()
        await db_client.rollback_transaction()
        assert not db_client.in_transaction


class TestS3Client:
    """Test S3Client protocol functionality"""

    @pytest.fixture
    def s3_client(self):
        return MockS3Client()

    async def test_upload_file(self, s3_client):
        """Test file upload"""
        data = b"test content"
        result = await s3_client.upload_file("test-bucket", "test-key", data, "text/plain")
        
        assert result == "https://test-bucket.s3.amazonaws.com/test-key"
        assert ("test-bucket", "test-key", data, "text/plain") in s3_client.uploads

    async def test_download_file(self, s3_client):
        """Test file download"""
        # First upload a file
        data = b"test content"
        await s3_client.upload_file("test-bucket", "test-key", data)
        
        # Then download it
        result = await s3_client.download_file("test-bucket", "test-key")
        
        assert result == data
        assert ("test-bucket", "test-key") in s3_client.downloads

    async def test_delete_file(self, s3_client):
        """Test file deletion"""
        # Upload then delete
        await s3_client.upload_file("test-bucket", "test-key", b"data")
        result = await s3_client.delete_file("test-bucket", "test-key")
        
        assert result is True
        assert "test-bucket/test-key" not in s3_client.files

    async def test_get_presigned_url(self, s3_client):
        """Test presigned URL generation"""
        result = await s3_client.get_presigned_url("test-bucket", "test-key", 7200)
        
        assert result == "https://test-bucket.s3.amazonaws.com/test-key?expires=7200"

    async def test_list_files(self, s3_client):
        """Test file listing"""
        # Upload some files
        await s3_client.upload_file("test-bucket", "prefix/file1.txt", b"data1")
        await s3_client.upload_file("test-bucket", "prefix/file2.txt", b"data2")
        await s3_client.upload_file("test-bucket", "other/file3.txt", b"data3")
        
        # List with prefix
        result = await s3_client.list_files("test-bucket", "prefix/")
        
        assert "prefix/file1.txt" in result
        assert "prefix/file2.txt" in result
        assert len([f for f in result if f.startswith("prefix/")]) == 2


class TestMQClient:
    """Test MQClient protocol functionality"""

    @pytest.fixture
    def mq_client(self):
        return MockMQClient()

    async def test_create_and_delete_queue(self, mq_client):
        """Test queue creation and deletion"""
        result = await mq_client.create_queue("test-queue", durable=True)
        assert result is True
        assert "test-queue" in mq_client.queues
        
        result = await mq_client.delete_queue("test-queue")
        assert result is True
        assert "test-queue" not in mq_client.queues

    async def test_publish_and_consume_message(self, mq_client):
        """Test message publishing and consumption"""
        message = {"type": "test", "data": "hello"}
        
        # Publish message
        message_id = await mq_client.publish_message("test-queue", message)
        assert message_id.startswith("msg_")
        assert ("test-queue", message, None) in mq_client.published
        
        # Consume message
        consumed = await mq_client.consume_message("test-queue")
        assert consumed is not None
        assert consumed["data"] == message

    async def test_acknowledge_message(self, mq_client):
        """Test message acknowledgment"""
        result = await mq_client.acknowledge_message("test-queue", "msg_123")
        assert result is True

    async def test_reject_message(self, mq_client):
        """Test message rejection"""
        result = await mq_client.reject_message("test-queue", "msg_123", requeue=True)
        assert result is True

    async def test_publish_with_delay(self, mq_client):
        """Test publishing message with delay"""
        message = {"type": "delayed", "data": "hello"}
        
        message_id = await mq_client.publish_message("test-queue", message, delay=60)
        
        assert message_id.startswith("msg_")
        assert ("test-queue", message, 60) in mq_client.published