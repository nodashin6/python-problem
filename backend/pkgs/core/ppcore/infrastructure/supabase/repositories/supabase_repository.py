from typing import Any, Dict, List, Optional
from supabase import Client

from ....domain.client_protocols import DBClient
from ....domain.repositories import DatabaseRepositoryBase


class SupabaseDBClientImpl(DBClient):
    """Supabase implementation of DBClient protocol"""
    
    def __init__(self, supabase_client: Client):
        self.client = supabase_client
    
    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute SQL query with parameters"""
        try:
            # Note: This is a simplified implementation
            # Real implementation would handle Supabase's query methods
            # and properly execute parameterized queries
            result = self.client.rpc('execute_sql', {'query': query, 'params': params or {}})
            return result.data if result.data else []
        except Exception as e:
            raise Exception(f"Database query failed: {e}")
    
    async def fetch_one(self, table: str, filters: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Fetch single record from table"""
        try:
            query = self.client.table(table).select("*")
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            result = query.limit(1).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            raise Exception(f"Database fetch failed: {e}")
    
    async def fetch_many(self, table: str, filters: Optional[Dict[str, Any]] = None, 
                        limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Fetch multiple records from table"""
        try:
            query = self.client.table(table).select("*")
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            result = query.range(offset, offset + limit - 1).execute()
            return result.data if result.data else []
        except Exception as e:
            raise Exception(f"Database fetch failed: {e}")
    
    async def insert(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert record into table"""
        try:
            result = self.client.table(table).insert(data).execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            raise Exception(f"Database insert failed: {e}")
    
    async def update(self, table: str, data: Dict[str, Any], filters: Dict[str, Any]) -> Dict[str, Any]:
        """Update records in table"""
        try:
            query = self.client.table(table).update(data)
            for key, value in filters.items():
                query = query.eq(key, value)
            result = query.execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            raise Exception(f"Database update failed: {e}")
    
    async def delete(self, table: str, filters: Dict[str, Any]) -> bool:
        """Delete records from table"""
        try:
            query = self.client.table(table).delete()
            for key, value in filters.items():
                query = query.eq(key, value)
            query.execute()
            return True
        except Exception as e:
            raise Exception(f"Database delete failed: {e}")


class SupabaseRepository(DatabaseRepositoryBase):
    """
    Supabaseリポジトリの基底クラス
    Supabaseのクライアントを使用してDatabaseRepositoryBaseを実装
    """
    
    def __init__(self, supabase_client: Client):
        db_client = SupabaseDBClientImpl(supabase_client)
        super().__init__(db_client)
        self.supabase_client = supabase_client


__all__ = [
    "SupabaseRepository",
    "SupabaseDBClientImpl",
]
