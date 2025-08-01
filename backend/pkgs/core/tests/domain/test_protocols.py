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
        self.responses = {}
    
    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        self.queries.append((query, params))
        return self.responses.get(query, [])
    
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
    
    async def list_files(self, bucket: str, prefix: str = "") -> List[str]:
        return []


class MockMQClient(MQClient):
    """Mock implementation of MQClient for testing"""
    
    def __init__(self):
        self.published = []
        self.subscriptions = {}
    
    async def publish(self, topic: str, message: Dict[str, Any]) -> bool:
        self.published.append((topic, message))
        return True
    
    async def subscribe(self, topic: str, handler) -> bool:
        self.subscriptions[topic] = handler
        return True
    
    async def unsubscribe(self, topic: str) -> bool:
        if topic in self.subscriptions:
            del self.subscriptions[topic]
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
        topic = "test-topic"
        message = {"type": "test", "data": "hello"}
        
        result = await mq_client.publish(topic, message)
        
        assert result is True
        assert (topic, message) in mq_client.published

    async def test_subscribe(self, mq_client):
        """Test topic subscription"""
        topic = "test-topic"
        handler = lambda msg: None
        
        result = await mq_client.subscribe(topic, handler)
        
        assert result is True
        assert mq_client.subscriptions[topic] == handler

    async def test_unsubscribe(self, mq_client):
        """Test topic unsubscription"""
        topic = "test-topic"
        handler = lambda msg: None
        
        await mq_client.subscribe(topic, handler)
        result = await mq_client.unsubscribe(topic)
        
        assert result is True
        assert topic not in mq_client.subscriptions