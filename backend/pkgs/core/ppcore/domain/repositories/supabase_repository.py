"""
Database Repository Base
データベースリポジトリ基底クラス - DDD Repository Pattern
"""

from abc import ABC, abstractmethod
from typing import Any, List, Optional, Type, TypeVar
from uuid import UUID

from ..base import BaseEntity
from ..client_protocols import DBClient
from ..protocols.database_protocols import DatabaseTransaction

T = TypeVar('T', bound=BaseEntity)


class DatabaseRepositoryBase(ABC):
    """
    Database repository base class
    データベースリポジトリの基底クラス - 共通操作を提供
    """

    def __init__(self, client: DBClient):
        self.client = client

    @abstractmethod
    def get_table_name(self) -> str:
        """Get table name for this repository"""
        pass

    @abstractmethod
    def get_entity_type(self) -> Type[T]:
        """Get entity type for this repository"""
        pass

    async def find_by_id(self, entity_id: UUID) -> Optional[T]:
        """Find entity by ID"""
        try:
            result = await self.client.execute_query(
                f"SELECT * FROM {self.get_table_name()} WHERE id = %(id)s",
                {"id": str(entity_id)}
            )
            if not result:
                return None
            return self._map_to_entity(result[0])
        except Exception as e:
            self._handle_database_error(e)
            return None

    async def find_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        """Find all entities with pagination"""
        try:
            result = await self.client.execute_query(
                f"SELECT * FROM {self.get_table_name()} ORDER BY created_at DESC LIMIT %(limit)s OFFSET %(offset)s",
                {"limit": limit, "offset": offset}
            )
            return [self._map_to_entity(row) for row in result]
        except Exception as e:
            self._handle_database_error(e)
            return []

    async def save(self, entity: T) -> T:
        """Save entity (insert or update)"""
        try:
            # Check if entity exists
            existing = await self.find_by_id(entity.id)
            if existing:
                return await self._update(entity)
            else:
                return await self._insert(entity)
        except Exception as e:
            self._handle_database_error(e)
            raise

    async def delete(self, entity_id: UUID) -> bool:
        """Delete entity by ID"""
        try:
            await self.client.execute_query(
                f"DELETE FROM {self.get_table_name()} WHERE id = %(id)s",
                {"id": str(entity_id)}
            )
            return True
        except Exception as e:
            self._handle_database_error(e)
            return False

    async def exists(self, entity_id: UUID) -> bool:
        """Check if entity exists"""
        try:
            result = await self.client.execute_query(
                f"SELECT 1 FROM {self.get_table_name()} WHERE id = %(id)s",
                {"id": str(entity_id)}
            )
            return len(result) > 0
        except Exception as e:
            self._handle_database_error(e)
            return False

    async def count(self) -> int:
        """Count total entities"""
        try:
            result = await self.client.execute_query(
                f"SELECT COUNT(*) as count FROM {self.get_table_name()}"
            )
            return result[0]["count"] if result else 0
        except Exception as e:
            self._handle_database_error(e)
            return 0

    def _map_to_entity(self, row: dict) -> T:
        """Map database row to entity"""
        entity_type = self.get_entity_type()
        return entity_type.model_validate(row)

    async def _insert(self, entity: T) -> T:
        """Insert new entity"""
        data = entity.model_dump(exclude_unset=True)
        columns = ", ".join(data.keys())
        placeholders = ", ".join(f"%({key})s" for key in data.keys())
        
        await self.client.execute_query(
            f"INSERT INTO {self.get_table_name()} ({columns}) VALUES ({placeholders})",
            data
        )
        return entity

    async def _update(self, entity: T) -> T:
        """Update existing entity"""
        data = entity.model_dump(exclude_unset=True, exclude={"id", "created_at"})
        set_clause = ", ".join(f"{key} = %({key})s" for key in data.keys())
        data["id"] = str(entity.id)
        
        await self.client.execute_query(
            f"UPDATE {self.get_table_name()} SET {set_clause} WHERE id = %(id)s",
            data
        )
        return entity

    def _handle_database_error(self, error: Exception) -> None:
        """Handle database errors"""
        # TODO: ログ出力やエラーハンドリングの共通処理
        raise error

    def _validate_response(self, response: Any) -> Any:
        """Validate database response"""
        if not response:
            return None
        return response


class TransactionalRepositoryMixin:
    """Repository with transaction support"""
    
    def __init__(self, client: DBClient, transaction: Optional[DatabaseTransaction] = None):
        super().__init__(client)
        self.transaction = transaction
    
    async def begin_transaction(self) -> DatabaseTransaction:
        """Begin a new transaction"""
        # This would be implemented by concrete infrastructure layer
        raise NotImplementedError("Transaction support must be implemented by infrastructure layer")
    
    async def with_transaction(self, transaction: DatabaseTransaction) -> 'TransactionalRepositoryMixin':
        """Create repository instance with transaction"""
        return self.__class__(self.client, transaction)
