"""
Content Repository implementation with Supabase
コンテンツリポジトリの Supabase 実装
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from ...domain.models import Content
from ...domain.repositories.content_repository import ContentRepository
from ....shared.database import DatabaseManager, BaseRepository
from ....shared.logging import get_logger
from ....const import ContentType

logger = get_logger(__name__)


class ContentRepositoryImpl(ContentRepository):
    """Content リポジトリの Supabase 実装"""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.table_name = "contents"

    async def save(self, content: Content) -> bool:
        """コンテンツを保存"""
        try:
            content_data = {
                "id": str(content.id),
                "title": content.title,
                "body": content.body,
                "content_type": content.content_type.value,
                "author_id": str(content.author_id),
                "parent_id": str(content.parent_id) if content.parent_id else None,
                "order_index": content.order_index,
                "is_published": content.is_published,
                "metadata": content.metadata,
                "created_at": content.created_at.isoformat(),
                "updated_at": content.updated_at.isoformat(),
            }

            # 既存のコンテンツをチェック
            existing = await self._find_by_id(str(content.id))

            if existing:
                # 更新
                await self._update({"id": str(content.id)}, content_data)
                logger.info(f"Content updated: {content.id}")
            else:
                # 新規作成
                await self._create(content_data)
                logger.info(f"Content created: {content.id}")

            return True

        except Exception as e:
            logger.error(f"Failed to save content {content.id}: {e}")
            return False

    async def find_by_id(self, content_id: uuid.UUID) -> Optional[Content]:
        """IDでコンテンツを検索"""
        try:
            data = await self._find_by_id(str(content_id))
            if not data:
                return None

            return self._map_to_domain(data)

        except Exception as e:
            logger.error(f"Failed to find content {content_id}: {e}")
            return None

    async def find_by_author(self, author_id: uuid.UUID) -> List[Content]:
        """作成者IDでコンテンツを検索"""
        try:
            conditions = {"author_id": str(author_id)}
            data_list = await self._find_by_conditions(conditions, order_by="created_at DESC")

            contents = []
            for data in data_list:
                content = self._map_to_domain(data)
                if content:
                    contents.append(content)

            return contents

        except Exception as e:
            logger.error(f"Failed to find contents by author {author_id}: {e}")
            return []

    async def find_by_parent(self, parent_id: uuid.UUID) -> List[Content]:
        """親IDでコンテンツを検索"""
        try:
            conditions = {"parent_id": str(parent_id)}
            data_list = await self._find_by_conditions(conditions, order_by="order_index")

            contents = []
            for data in data_list:
                content = self._map_to_domain(data)
                if content:
                    contents.append(content)

            return contents

        except Exception as e:
            logger.error(f"Failed to find contents by parent {parent_id}: {e}")
            return []

    async def find_by_type(self, content_type: ContentType) -> List[Content]:
        """タイプでコンテンツを検索"""
        try:
            conditions = {"content_type": content_type.value}
            data_list = await self._find_by_conditions(conditions, order_by="created_at DESC")

            contents = []
            for data in data_list:
                content = self._map_to_domain(data)
                if content:
                    contents.append(content)

            return contents

        except Exception as e:
            logger.error(f"Failed to find contents by type {content_type}: {e}")
            return []

    async def find_published(
        self,
        content_type: Optional[ContentType] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Content]:
        """公開コンテンツを検索"""
        try:
            conditions = {"is_published": True}
            if content_type:
                conditions["content_type"] = content_type.value

            data_list = await self._find_by_conditions(
                conditions, order_by="created_at DESC", limit=limit, offset=offset
            )

            contents = []
            for data in data_list:
                content = self._map_to_domain(data)
                if content:
                    contents.append(content)

            return contents

        except Exception as e:
            logger.error(f"Failed to find published contents: {e}")
            return []

    async def search(
        self,
        title: Optional[str] = None,
        content_type: Optional[ContentType] = None,
        author_id: Optional[uuid.UUID] = None,
        parent_id: Optional[uuid.UUID] = None,
        is_published: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Content]:
        """複合条件でコンテンツを検索"""
        try:
            query_parts = ["SELECT * FROM contents"]
            conditions = []
            params = []

            # 条件の構築
            if title:
                conditions.append("title ILIKE %s")
                params.append(f"%{title}%")

            if content_type:
                conditions.append("content_type = %s")
                params.append(content_type.value)

            if author_id:
                conditions.append("author_id = %s")
                params.append(str(author_id))

            if parent_id:
                conditions.append("parent_id = %s")
                params.append(str(parent_id))

            if is_published is not None:
                conditions.append("is_published = %s")
                params.append(is_published)

            # WHERE句の構築
            if conditions:
                query_parts.append("WHERE " + " AND ".join(conditions))

            # ソートとページング
            query_parts.append("ORDER BY created_at DESC")
            query_parts.append("LIMIT %s OFFSET %s")
            params.extend([limit, offset])

            query = " ".join(query_parts)

            db = await self.db_manager.get_connection()
            results = await db.fetch(query, params)

            contents = []
            for data in results:
                content = self._map_to_domain(dict(data))
                if content:
                    contents.append(content)

            return contents

        except Exception as e:
            logger.error(f"Failed to search contents: {e}")
            return []

    async def get_max_order_index(self, parent_id: Optional[uuid.UUID] = None) -> int:
        """最大順序インデックスを取得"""
        try:
            if parent_id:
                query = "SELECT COALESCE(MAX(order_index), -1) FROM contents WHERE parent_id = %s"
                params = [str(parent_id)]
            else:
                query = "SELECT COALESCE(MAX(order_index), -1) FROM contents WHERE parent_id IS NULL"
                params = []

            db = await self.db_manager.get_connection()
            result = await db.fetchval(query, params)
            return result if result is not None else -1

        except Exception as e:
            logger.error(f"Failed to get max order index for parent {parent_id}: {e}")
            return -1

    async def reorder_contents(
        self, parent_id: Optional[uuid.UUID], content_orders: List[Dict[str, Any]]
    ) -> bool:
        """コンテンツの順序を変更"""
        try:
            db = await self.db_manager.get_connection()

            async with db.transaction():
                for order_info in content_orders:
                    content_id = order_info["content_id"]
                    new_order = order_info["order_index"]

                    if parent_id:
                        query = """
                        UPDATE contents 
                        SET order_index = %s, updated_at = %s 
                        WHERE id = %s AND parent_id = %s
                        """
                        params = [
                            new_order,
                            datetime.utcnow().isoformat(),
                            str(content_id),
                            str(parent_id),
                        ]
                    else:
                        query = """
                        UPDATE contents 
                        SET order_index = %s, updated_at = %s 
                        WHERE id = %s AND parent_id IS NULL
                        """
                        params = [
                            new_order,
                            datetime.utcnow().isoformat(),
                            str(content_id),
                        ]

                    await db.execute(query, params)

            logger.info(f"Reordered contents for parent {parent_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to reorder contents for parent {parent_id}: {e}")
            return False

    async def delete(self, content_id: uuid.UUID) -> bool:
        """コンテンツを削除"""
        try:
            success = await self._delete({"id": str(content_id)})

            if success:
                logger.info(f"Content deleted: {content_id}")

            return success

        except Exception as e:
            logger.error(f"Failed to delete content {content_id}: {e}")
            return False

    async def delete_by_parent(self, parent_id: uuid.UUID) -> bool:
        """親コンテンツの子コンテンツをすべて削除"""
        try:
            count = await self._count({"parent_id": str(parent_id)})
            success = await self._delete({"parent_id": str(parent_id)})

            if success:
                logger.info(f"Deleted {count} child contents for parent {parent_id}")

            return success

        except Exception as e:
            logger.error(f"Failed to delete child contents for parent {parent_id}: {e}")
            return False

    async def count_by_author(self, author_id: uuid.UUID) -> int:
        """作成者のコンテンツ数をカウント"""
        try:
            return await self._count({"author_id": str(author_id)})
        except Exception as e:
            logger.error(f"Failed to count contents by author {author_id}: {e}")
            return 0

    async def count_by_type(self, content_type: ContentType) -> int:
        """タイプ別のコンテンツ数をカウント"""
        try:
            return await self._count({"content_type": content_type.value})
        except Exception as e:
            logger.error(f"Failed to count contents by type {content_type}: {e}")
            return 0

    async def count_published(self) -> int:
        """公開コンテンツ数をカウント"""
        try:
            return await self._count({"is_published": True})
        except Exception as e:
            logger.error(f"Failed to count published contents: {e}")
            return 0

    def _map_to_domain(self, data: Dict[str, Any]) -> Optional[Content]:
        """データベースレコードをドメインオブジェクトにマップ"""
        try:
            content = Content(
                id=uuid.UUID(data["id"]),
                title=data["title"],
                body=data["body"],
                content_type=ContentType(data["content_type"]),
                author_id=uuid.UUID(data["author_id"]),
                parent_id=uuid.UUID(data["parent_id"]) if data["parent_id"] else None,
                order_index=data["order_index"],
                is_published=data["is_published"],
                metadata=data.get("metadata", {}),
                created_at=datetime.fromisoformat(data["created_at"]),
                updated_at=datetime.fromisoformat(data["updated_at"]),
            )

            return content

        except Exception as e:
            logger.error(f"Failed to map data to Content domain: {e}")
            return None
