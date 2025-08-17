from typing import Any

from supabase import Client

from ....domain.client_protocols import DBClient
from ....domain.repositories import DatabaseRepositoryBase


class SupabaseDBClientImpl(DBClient):
    """Supabase implementation of DBClient protocol"""

    def __init__(self, supabase_client: Client):
        self.client = supabase_client

    async def execute_query(self, query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Execute SQL query with parameters"""
        try:
            # Note: This is a simplified implementation
            # Real implementation would handle Supabase's query methods
            # and properly execute parameterized queries
            result = self.client.rpc("execute_sql", {"query": query, "params": params or {}})
            return result.data if result.data else []
        except Exception as e:
            raise e

    async def fetch_one(self, table: str, filters: dict[str, Any] | None = None) -> dict[str, Any] | None:
        """Fetch single record from table"""
        try:
            query = self.client.table(table).select("*")
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            result = query.limit(1).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            raise e

    async def fetch_many(
        self, table: str, filters: dict[str, Any] | None = None, limit: int = 100, offset: int = 0
    ) -> list[dict[str, Any]]:
        """Fetch multiple records from table"""
        try:
            query = self.client.table(table).select("*")
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            result = query.range(offset, offset + limit - 1).execute()
            return result.data if result.data else []
        except Exception as e:
            raise e

    async def insert(self, table: str, data: dict[str, Any]) -> dict[str, Any]:
        """Insert record into table"""
        try:
            result = self.client.table(table).insert(data).execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            raise e

    async def update(self, table: str, data: dict[str, Any], filters: dict[str, Any]) -> dict[str, Any]:
        """Update records in table"""
        try:
            query = self.client.table(table).update(data)
            for key, value in filters.items():
                query = query.eq(key, value)
            result = query.execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            raise e

    async def delete(self, table: str, filters: dict[str, Any]) -> bool:
        """Delete records from table"""
        try:
            query = self.client.table(table).delete()
            for key, value in filters.items():
                query = query.eq(key, value)
            query.execute()
            return True
        except Exception as e:
            raise e

    async def execute_command(self, command: str, params: dict[str, Any] | None = None) -> int:
        """Execute a command and return affected rows count"""
        try:
            # For Supabase, this would typically be handled through RPC calls
            # This is a simplified implementation
            result = self.client.rpc("execute_command", {"command": command, "params": params or {}})
            return result.data.get("affected_rows", 0) if result.data else 0
        except Exception as e:
            raise e

    async def begin_transaction(self) -> None:
        """Begin a database transaction"""
        # Supabase doesn't support transactions in the same way as traditional databases
        # This is a placeholder implementation

    async def commit_transaction(self) -> None:
        """Commit the current transaction"""
        # Supabase doesn't support transactions in the same way as traditional databases
        # This is a placeholder implementation

    async def rollback_transaction(self) -> None:
        """Rollback the current transaction"""
        # Supabase doesn't support transactions in the same way as traditional databases
        # This is a placeholder implementation


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
