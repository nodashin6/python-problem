"""
Tests for Core Domain Repository Base Classes
コアドメインリポジトリ基底クラスのテスト
"""

import pytest
from typing import Type
from uuid import UUID, uuid4
from datetime import datetime

from ppcore.domain.base import BaseEntity
from ppcore.domain.repositories import DatabaseRepositoryBase
from ppcore.domain.client_protocols import DBClient
from ppcore.domain.protocols.database_protocols import DatabaseTransaction


class DummyEntity(BaseEntity):
    """Dummy entity for repository tests"""
    name: str
    email: str


class MockDBClient(DBClient):
    """Mock DB client for testing"""
    
    def __init__(self):
        self.queries = []
        self.commands = []
        self.data = {}
        self.in_transaction = False
        
    async def execute_query(self, query: str, params=None):
        self.queries.append((query, params))
        
        # Mock responses based on query patterns
        if "SELECT * FROM test_entities WHERE id =" in query:
            entity_id = params.get("id") if params else None
            if entity_id in self.data:
                return [self.data[entity_id]]
            return []
        elif "SELECT * FROM test_entities ORDER BY created_at DESC" in query:
            return list(self.data.values())
        elif "INSERT INTO test_entities" in query:
            # Simulate successful insert
            return []
        elif "UPDATE test_entities" in query:
            # Simulate successful update
            return []
        elif "DELETE FROM test_entities" in query:
            # Simulate successful delete
            return []
        elif "SELECT COUNT(*) as count FROM test_entities" in query:
            return [{"count": len(self.data)}]
        elif "SELECT 1 FROM test_entities WHERE id =" in query:
            entity_id = params.get("id") if params else None
            return [{"1": 1}] if entity_id in self.data else []
        return []
    
    async def execute_command(self, command: str, params=None) -> int:
        self.commands.append((command, params))
        return 1  # Mock affected rows
    
    async def begin_transaction(self) -> None:
        self.in_transaction = True
    
    async def commit_transaction(self) -> None:
        self.in_transaction = False
    
    async def rollback_transaction(self) -> None:
        self.in_transaction = False


class DummyRepository(DatabaseRepositoryBase):
    """Concrete repository implementation for testing"""
    
    def get_table_name(self) -> str:
        return "test_entities"
    
    def get_entity_type(self) -> Type[DummyEntity]:
        return DummyEntity


class TestDatabaseRepositoryBase:
    """Test DatabaseRepositoryBase functionality"""

    @pytest.fixture
    def mock_client(self):
        return MockDBClient()

    @pytest.fixture
    def repository(self, mock_client):
        return DummyRepository(mock_client)

    @pytest.fixture
    def test_entity(self):
        return DummyEntity(
            id=uuid4(),
            name="Test User",
            email="test@example.com",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

    async def test_find_by_id_found(self, repository, mock_client, test_entity):
        """Test finding entity by ID when it exists"""
        # Setup mock data
        mock_client.data[str(test_entity.id)] = {
            "id": str(test_entity.id),
            "name": test_entity.name,
            "email": test_entity.email,
            "created_at": test_entity.created_at.isoformat(),
            "updated_at": test_entity.updated_at.isoformat()
        }
        
        result = await repository.find_by_id(test_entity.id)
        
        assert result is not None
        assert result.id == test_entity.id
        assert result.name == test_entity.name
        assert result.email == test_entity.email

    async def test_find_by_id_not_found(self, repository, mock_client):
        """Test finding entity by ID when it doesn't exist"""
        non_existent_id = uuid4()
        
        result = await repository.find_by_id(non_existent_id)
        
        assert result is None

    async def test_find_all(self, repository, mock_client, test_entity):
        """Test finding all entities with pagination"""
        # Setup mock data
        mock_client.data[str(test_entity.id)] = {
            "id": str(test_entity.id),
            "name": test_entity.name,
            "email": test_entity.email,
            "created_at": test_entity.created_at.isoformat(),
            "updated_at": test_entity.updated_at.isoformat()
        }
        
        result = await repository.find_all(limit=10, offset=0)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].id == test_entity.id

    async def test_save_new_entity(self, repository, mock_client, test_entity):
        """Test saving a new entity (insert)"""
        # Mock that entity doesn't exist (find_by_id returns None)
        result = await repository.save(test_entity)
        
        assert result == test_entity
        # Verify insert query was executed
        insert_queries = [q for q in mock_client.queries if "INSERT INTO" in q[0]]
        assert len(insert_queries) > 0

    async def test_save_existing_entity(self, repository, mock_client, test_entity):
        """Test saving an existing entity (update)"""
        # Setup mock data to simulate existing entity
        mock_client.data[str(test_entity.id)] = {
            "id": str(test_entity.id),
            "name": "Old Name",
            "email": test_entity.email,
            "created_at": test_entity.created_at.isoformat(),
            "updated_at": test_entity.updated_at.isoformat()
        }
        
        result = await repository.save(test_entity)
        
        assert result == test_entity
        # Verify update query was executed
        update_queries = [q for q in mock_client.queries if "UPDATE" in q[0]]
        assert len(update_queries) > 0

    async def test_delete(self, repository, mock_client, test_entity):
        """Test deleting an entity"""
        result = await repository.delete(test_entity.id)
        
        assert result is True
        # Verify delete query was executed
        delete_queries = [q for q in mock_client.queries if "DELETE FROM" in q[0]]
        assert len(delete_queries) == 1

    async def test_exists_true(self, repository, mock_client, test_entity):
        """Test checking if entity exists when it does"""
        # Setup mock data
        mock_client.data[str(test_entity.id)] = {"dummy": "data"}
        
        result = await repository.exists(test_entity.id)
        
        assert result is True

    async def test_exists_false(self, repository, mock_client):
        """Test checking if entity exists when it doesn't"""
        non_existent_id = uuid4()
        
        result = await repository.exists(non_existent_id)
        
        assert result is False

    async def test_count(self, repository, mock_client, test_entity):
        """Test counting entities"""
        # Setup mock data
        mock_client.data[str(test_entity.id)] = {"dummy": "data"}
        
        result = await repository.count()
        
        assert result == 1

    def test_get_table_name(self, repository):
        """Test getting table name"""
        assert repository.get_table_name() == "test_entities"

    def test_get_entity_type(self, repository):
        """Test getting entity type"""
        assert repository.get_entity_type() == DummyEntity

    def test_map_to_entity(self, repository):
        """Test mapping database row to entity"""
        row = {
            "id": str(uuid4()),
            "name": "Test User",
            "email": "test@example.com",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        entity = repository._map_to_entity(row)
        
        assert isinstance(entity, DummyEntity)
        assert entity.name == "Test User"
        assert entity.email == "test@example.com"