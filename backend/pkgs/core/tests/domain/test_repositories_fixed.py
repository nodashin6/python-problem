"""
Tests for Core Domain Repository Base Classes - Fixed Version
コアドメインリポジトリ基底クラスのテスト
"""

import pytest
from typing import Type
from uuid import uuid4
from datetime import datetime

from ppcore.domain.base import BaseEntity
from ppcore.domain.repositories import DatabaseRepositoryBase
from ppcore.domain.client_protocols import DBClient


class _TestEntity(BaseEntity):
    """Test entity for repository tests (prefixed with _ to avoid pytest collection)"""
    name: str
    email: str


class _MockDBClient(DBClient):
    """Mock DB client for testing (prefixed with _ to avoid pytest collection)"""
    
    def __init__(self):
        self.queries = []
        self.commands = []
        self.data = {}
        
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
        return 1
    
    async def begin_transaction(self) -> None:
        pass
    
    async def commit_transaction(self) -> None:
        pass
    
    async def rollback_transaction(self) -> None:
        pass


class _TestRepository(DatabaseRepositoryBase):
    """Concrete repository implementation for testing (prefixed with _ to avoid pytest collection)"""
    
    def get_table_name(self) -> str:
        return "test_entities"
    
    def get_entity_type(self) -> Type[_TestEntity]:
        return _TestEntity


class TestDatabaseRepositoryBase:
    """Test DatabaseRepositoryBase functionality"""

    @pytest.fixture
    def mock_client(self):
        return _MockDBClient()

    @pytest.fixture
    def repository(self, mock_client):
        return _TestRepository(mock_client)

    @pytest.fixture
    def test_entity(self):
        return _TestEntity(
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

    async def test_find_by_id_not_found(self, repository):
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

    async def test_delete(self, repository, test_entity):
        """Test deleting an entity"""
        result = await repository.delete(test_entity.id)
        
        assert result is True

    async def test_exists_true(self, repository, mock_client, test_entity):
        """Test checking if entity exists when it does"""
        # Setup mock data
        mock_client.data[str(test_entity.id)] = {"dummy": "data"}
        
        result = await repository.exists(test_entity.id)
        
        assert result is True

    async def test_exists_false(self, repository):
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
        assert repository.get_entity_type() == _TestEntity

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
        
        assert isinstance(entity, _TestEntity)
        assert entity.name == "Test User"
        assert entity.email == "test@example.com"

    async def test_repository_error_handling(self, repository, mock_client):
        """Test repository error handling"""
        # Mock an exception in the client
        original_execute_query = mock_client.execute_query
        
        async def failing_execute_query(query: str, params=None):
            if "SELECT * FROM test_entities WHERE id =" in query:
                raise Exception("Database connection failed")
            return await original_execute_query(query, params)
        
        mock_client.execute_query = failing_execute_query
        
        # Should raise the exception (as per our current implementation)
        with pytest.raises(Exception, match="Database connection failed"):
            await repository.find_by_id(uuid4())

    async def test_insert_implementation(self, repository, test_entity):
        """Test the _insert method implementation"""
        result = await repository._insert(test_entity)
        assert result == test_entity

    async def test_update_implementation(self, repository, test_entity):
        """Test the _update method implementation"""
        result = await repository._update(test_entity)
        assert result == test_entity