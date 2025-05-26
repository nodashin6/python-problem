"""
Database infrastructure components
データベースインフラストラクチャ
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, TypeVar, Generic, Union
from datetime import datetime
from contextlib import asynccontextmanager
import uuid

import asyncpg
from supabase import create_client, Client
from pydantic import BaseModel

from ..env import settings
from ..const import DB_POOL_SIZE, DB_TIMEOUT

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class DatabaseConnection:
    """データベース接続の抽象化"""

    async def execute(self, query: str, *args) -> Any:
        raise NotImplementedError

    async def fetch(self, query: str, *args) -> List[Dict[str, Any]]:
        raise NotImplementedError

    async def fetchrow(self, query: str, *args) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

    async def fetchval(self, query: str, *args) -> Any:
        raise NotImplementedError


class PostgreSQLConnection(DatabaseConnection):
    """PostgreSQL接続実装"""

    def __init__(self, connection: asyncpg.Connection):
        self.connection = connection

    async def execute(self, query: str, *args) -> Any:
        return await self.connection.execute(query, *args)

    async def fetch(self, query: str, *args) -> List[Dict[str, Any]]:
        rows = await self.connection.fetch(query, *args)
        return [dict(row) for row in rows]

    async def fetchrow(self, query: str, *args) -> Optional[Dict[str, Any]]:
        row = await self.connection.fetchrow(query, *args)
        return dict(row) if row else None

    async def fetchval(self, query: str, *args) -> Any:
        return await self.connection.fetchval(query, *args)


class SupabaseConnection(DatabaseConnection):
    """Supabase接続実装"""

    def __init__(self, client: Client):
        self.client = client

    async def execute(self, query: str, *args) -> Any:
        # Supabaseでは直接SQLクエリは実行できないので
        # REST APIまたはpostgrestを使用
        raise NotImplementedError("Direct SQL execution not supported with Supabase")

    async def fetch(self, query: str, *args) -> List[Dict[str, Any]]:
        # Supabase特有の実装が必要
        raise NotImplementedError("Use Supabase client methods instead")

    async def fetchrow(self, query: str, *args) -> Optional[Dict[str, Any]]:
        raise NotImplementedError("Use Supabase client methods instead")

    async def fetchval(self, query: str, *args) -> Any:
        raise NotImplementedError("Use Supabase client methods instead")


class DatabaseManager:
    """データベース管理クラス"""

    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self._connection_string: Optional[str] = None

    async def initialize(self, connection_string: Optional[str] = None):
        """データベース接続プールを初期化"""
        if connection_string:
            self._connection_string = connection_string
        elif settings.database_url:
            self._connection_string = settings.database_url
        else:
            # Supabaseから接続文字列を構築
            self._connection_string = f"postgresql://postgres:{settings.supabase_service_key}@{settings.supabase_url.replace('https://', '').replace('http://', '')}:5432/postgres"

        try:
            self.pool = await asyncpg.create_pool(
                self._connection_string,
                min_size=1,
                max_size=DB_POOL_SIZE,
                command_timeout=DB_TIMEOUT,
            )
            logger.info("Database connection pool initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise

    async def close(self):
        """データベース接続プールを閉じる"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")

    @asynccontextmanager
    async def get_connection(self) -> DatabaseConnection:
        """データベース接続を取得"""
        if not self.pool:
            raise RuntimeError("Database not initialized")

        async with self.pool.acquire() as connection:
            yield PostgreSQLConnection(connection)

    @asynccontextmanager
    async def get_transaction(self) -> DatabaseConnection:
        """トランザクション付きデータベース接続を取得"""
        if not self.pool:
            raise RuntimeError("Database not initialized")

        async with self.pool.acquire() as connection:
            async with connection.transaction():
                yield PostgreSQLConnection(connection)


class SupabaseClient:
    """Supabase クライアント"""

    def __init__(self):
        self.client: Optional[Client] = None

    def initialize(self):
        """Supabase クライアントを初期化"""
        try:
            self.client = create_client(
                settings.supabase_url, settings.supabase_anon_key
            )
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise

    def get_client(self) -> Client:
        """Supabase クライアントを取得"""
        if not self.client:
            raise RuntimeError("Supabase client not initialized")
        return self.client

    async def insert(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """データを挿入"""
        if not self.client:
            raise RuntimeError("Supabase client not initialized")

        try:
            response = self.client.table(table).insert(data).execute()
            return response.data[0] if response.data else {}
        except Exception as e:
            logger.error(f"Failed to insert data into {table}: {e}")
            raise

    async def select(
        self, table: str, filters: Optional[Dict[str, Any]] = None, columns: str = "*"
    ) -> List[Dict[str, Any]]:
        """データを選択"""
        if not self.client:
            raise RuntimeError("Supabase client not initialized")

        try:
            query = self.client.table(table).select(columns)

            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)

            response = query.execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Failed to select data from {table}: {e}")
            raise

    async def update(
        self, table: str, data: Dict[str, Any], filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """データを更新"""
        if not self.client:
            raise RuntimeError("Supabase client not initialized")

        try:
            query = self.client.table(table).update(data)

            for key, value in filters.items():
                query = query.eq(key, value)

            response = query.execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Failed to update data in {table}: {e}")
            raise

    async def delete(self, table: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """データを削除"""
        if not self.client:
            raise RuntimeError("Supabase client not initialized")

        try:
            query = self.client.table(table)

            for key, value in filters.items():
                query = query.eq(key, value)

            response = query.delete().execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Failed to delete data from {table}: {e}")
            raise


class BaseRepository(Generic[T]):
    """リポジトリの基底クラス"""

    def __init__(
        self,
        db_manager: DatabaseManager,
        supabase_client: SupabaseClient,
        table_name: str,
        model_class: type[T],
    ):
        self.db_manager = db_manager
        self.supabase_client = supabase_client
        self.table_name = table_name
        self.model_class = model_class

    async def find_by_id(self, id: Union[str, uuid.UUID]) -> Optional[T]:
        """IDでエンティティを取得"""
        data = await self.supabase_client.select(
            self.table_name, filters={"id": str(id)}
        )

        if data:
            return self.model_class(**data[0])
        return None

    async def find_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        """全エンティティを取得"""
        data = await self.supabase_client.select(self.table_name)
        return [self.model_class(**item) for item in data[offset : offset + limit]]

    async def save(self, entity: T) -> T:
        """エンティティを保存"""
        data = entity.model_dump(mode="json")

        # IDが存在する場合は更新、そうでなければ挿入
        if hasattr(entity, "id") and entity.id:
            updated_data = await self.supabase_client.update(
                self.table_name, data, filters={"id": str(entity.id)}
            )
            return self.model_class(**updated_data[0]) if updated_data else entity
        else:
            # 新規作成の場合はIDを生成
            if not data.get("id"):
                data["id"] = str(uuid.uuid4())

            inserted_data = await self.supabase_client.insert(self.table_name, data)
            return self.model_class(**inserted_data)

    async def delete(self, id: Union[str, uuid.UUID]) -> bool:
        """エンティティを削除"""
        try:
            deleted_data = await self.supabase_client.delete(
                self.table_name, filters={"id": str(id)}
            )
            return len(deleted_data) > 0
        except Exception:
            return False


# グローバルインスタンス
db_manager = DatabaseManager()
supabase_client = SupabaseClient()


async def initialize_database():
    """データベースを初期化"""
    await db_manager.initialize()
    supabase_client.initialize()


async def close_database():
    """データベースを閉じる"""
    await db_manager.close()
