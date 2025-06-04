"""
Book Repository implementation with Supabase
ブックリポジトリの Supabase 実装
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from ...domain.models import Book, Tag
from ...domain.repositories.book_repository import BookRepository
from ....shared.database import DatabaseManager, BaseRepository
from ....shared.logging import get_logger

# from ....const import BookStatus  # TODO: BookStatus未定義のため一時コメントアウト

logger = get_logger(__name__)


class BookRepositoryImpl(BookRepository):
    """Book リポジトリの Supabase 実装"""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.table_name = "books"

    async def save(self, book: Book) -> bool:
        """ブックを保存"""
        try:
            book_data = {
                "id": str(book.id),
                "title": book.title,
                "description": book.description,
                "status": book.status.value,
                "author_id": str(book.author_id),
                "is_public": book.is_public,
                "created_at": book.created_at.isoformat(),
                "updated_at": book.updated_at.isoformat(),
            }

            # 既存のブックをチェック
            existing = await self._find_by_id(str(book.id))

            if existing:
                # 更新
                await self._update({"id": str(book.id)}, book_data)
                logger.info(f"Book updated: {book.id}")
            else:
                # 新規作成
                await self._create(book_data)
                logger.info(f"Book created: {book.id}")

            # タグの保存
            await self._save_book_tags(book.id, book.tags)

            return True

        except Exception as e:
            logger.error(f"Failed to save book {book.id}: {e}")
            return False

    async def find_by_id(self, book_id: uuid.UUID) -> Optional[Book]:
        """IDでブックを検索"""
        try:
            data = await self._find_by_id(str(book_id))
            if not data:
                return None

            return await self._map_to_domain(data)

        except Exception as e:
            logger.error(f"Failed to find book {book_id}: {e}")
            return None

    async def find_by_title(self, title: str) -> Optional[Book]:
        """タイトルでブックを検索"""
        try:
            conditions = {"title": title}
            data = await self._find_by_conditions(conditions)

            if not data:
                return None

            return await self._map_to_domain(data[0])

        except Exception as e:
            logger.error(f"Failed to find book by title {title}: {e}")
            return None

    async def find_by_author(self, author_id: uuid.UUID) -> List[Book]:
        """作成者IDでブックを検索"""
        try:
            conditions = {"author_id": str(author_id)}
            data_list = await self._find_by_conditions(
                conditions, order_by="created_at DESC"
            )

            books = []
            for data in data_list:
                book = await self._map_to_domain(data)
                if book:
                    books.append(book)

            return books

        except Exception as e:
            logger.error(f"Failed to find books by author {author_id}: {e}")
            return []

    async def find_public_books(self, limit: int = 50, offset: int = 0) -> List[Book]:
        """公開ブックを検索"""
        try:
            conditions = {"is_public": True}
            data_list = await self._find_by_conditions(
                conditions, order_by="created_at DESC", limit=limit, offset=offset
            )

            books = []
            for data in data_list:
                book = await self._map_to_domain(data)
                if book:
                    books.append(book)

            return books

        except Exception as e:
            logger.error(f"Failed to find public books: {e}")
            return []

    async def find_by_status(
        self, status: str
    ) -> List[Book]:  # TODO: BookStatus -> str に一時変更
        """ステータスでブックを検索"""
        try:
            conditions = {"status": status.value}
            data_list = await self._find_by_conditions(conditions)

            books = []
            for data in data_list:
                book = await self._map_to_domain(data)
                if book:
                    books.append(book)

            return books

        except Exception as e:
            logger.error(f"Failed to find books by status {status}: {e}")
            return []

    async def find_by_tags(self, tags: List[str]) -> List[Book]:
        """タグでブックを検索"""
        try:
            # タグテーブルを結合してクエリ
            query = """
            SELECT DISTINCT b.* FROM books b
            JOIN book_tags bt ON b.id = bt.book_id
            WHERE bt.tag_name = ANY(%s)
            """

            db = await self.db_manager.get_connection()
            results = await db.fetch(query, [tags])

            books = []
            for data in results:
                book = await self._map_to_domain(dict(data))
                if book:
                    books.append(book)

            return books

        except Exception as e:
            logger.error(f"Failed to find books by tags {tags}: {e}")
            return []

    async def search(
        self,
        title: Optional[str] = None,
        tags: Optional[List[str]] = None,
        author_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,  # TODO: BookStatus -> str に一時変更
        is_public: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Book]:
        """複合条件でブックを検索"""
        try:
            query_parts = ["SELECT DISTINCT b.* FROM books b"]
            conditions = []
            params = []

            # タグ条件がある場合は結合
            if tags:
                query_parts.append("JOIN book_tags bt ON b.id = bt.book_id")
                conditions.append("bt.tag_name = ANY(%s)")
                params.append(tags)

            # その他の条件
            if title:
                conditions.append("b.title ILIKE %s")
                params.append(f"%{title}%")

            if author_id:
                conditions.append("b.author_id = %s")
                params.append(str(author_id))

            if status:
                conditions.append("b.status = %s")
                params.append(status.value)

            if is_public is not None:
                conditions.append("b.is_public = %s")
                params.append(is_public)

            # WHERE句の構築
            if conditions:
                query_parts.append("WHERE " + " AND ".join(conditions))

            # ソートとページング
            query_parts.append("ORDER BY b.created_at DESC")
            query_parts.append("LIMIT %s OFFSET %s")
            params.extend([limit, offset])

            query = " ".join(query_parts)

            db = await self.db_manager.get_connection()
            results = await db.fetch(query, params)

            books = []
            for data in results:
                book = await self._map_to_domain(dict(data))
                if book:
                    books.append(book)

            return books

        except Exception as e:
            logger.error(f"Failed to search books: {e}")
            return []

    async def delete(self, book_id: uuid.UUID) -> bool:
        """ブックを削除"""
        try:
            # 関連するタグも削除
            await self._delete_book_tags(book_id)

            # ブックを削除
            success = await self._delete({"id": str(book_id)})

            if success:
                logger.info(f"Book deleted: {book_id}")

            return success

        except Exception as e:
            logger.error(f"Failed to delete book {book_id}: {e}")
            return False

    async def count_by_author(self, author_id: uuid.UUID) -> int:
        """作成者のブック数をカウント"""
        try:
            return await self._count({"author_id": str(author_id)})
        except Exception as e:
            logger.error(f"Failed to count books by author {author_id}: {e}")
            return 0

    async def count_public_books(self) -> int:
        """公開ブック数をカウント"""
        try:
            return await self._count({"is_public": True})
        except Exception as e:
            logger.error(f"Failed to count public books: {e}")
            return 0

    async def exists_title(
        self, title: str, exclude_id: Optional[uuid.UUID] = None
    ) -> bool:
        """タイトルの重複チェック"""
        try:
            conditions = {"title": title}
            if exclude_id:
                # 指定されたIDは除外
                query = "SELECT COUNT(*) FROM books WHERE title = %s AND id != %s"
                db = await self.db_manager.get_connection()
                result = await db.fetchval(query, [title, str(exclude_id)])
                return result > 0
            else:
                count = await self._count(conditions)
                return count > 0

        except Exception as e:
            logger.error(f"Failed to check title existence {title}: {e}")
            return False

    async def get_book_stats(self, book_id: uuid.UUID) -> Dict[str, Any]:
        """ブックの統計情報を取得"""
        try:
            query = """
            SELECT 
                COUNT(p.id) as problem_count,
                COUNT(CASE WHEN p.status = 'published' THEN 1 END) as published_problem_count,
                COUNT(tc.id) as total_judge_cases
            FROM books b
            LEFT JOIN problems p ON b.id = p.book_id
            LEFT JOIN judge_cases tc ON p.id = tc.problem_id
            WHERE b.id = %s
            GROUP BY b.id
            """

            db = await self.db_manager.get_connection()
            result = await db.fetchrow(query, [str(book_id)])

            if result:
                return {
                    "problem_count": result["problem_count"] or 0,
                    "published_problem_count": result["published_problem_count"] or 0,
                    "total_judge_cases": result["total_judge_cases"] or 0,
                }
            else:
                return {
                    "problem_count": 0,
                    "published_problem_count": 0,
                    "total_judge_cases": 0,
                }

        except Exception as e:
            logger.error(f"Failed to get book stats for {book_id}: {e}")
            return {
                "problem_count": 0,
                "published_problem_count": 0,
                "total_judge_cases": 0,
            }

    async def _map_to_domain(self, data: Dict[str, Any]) -> Optional[Book]:
        """データベースレコードをドメインオブジェクトにマップ"""
        try:
            # タグの取得
            tags = await self._load_book_tags(uuid.UUID(data["id"]))

            book = Book(
                id=uuid.UUID(data["id"]),
                title=data["title"],
                description=data.get("description", ""),
                status=data[
                    "status"
                ],  # TODO: BookStatus(data["status"]) -> data["status"] に一時変更
                author_id=uuid.UUID(data["author_id"]),
                is_public=data["is_public"],
                tags=tags,
                created_at=datetime.fromisoformat(data["created_at"]),
                updated_at=datetime.fromisoformat(data["updated_at"]),
            )

            return book

        except Exception as e:
            logger.error(f"Failed to map data to Book domain: {e}")
            return None

    async def _save_book_tags(self, book_id: uuid.UUID, tags: List[Tag]) -> None:
        """ブックのタグを保存"""
        try:
            # 既存のタグを削除
            await self._delete_book_tags(book_id)

            # 新しいタグを挿入
            if tags:
                tag_data = [
                    {
                        "book_id": str(book_id),
                        "tag_name": tag.name,
                        "tag_color": tag.color,
                    }
                    for tag in tags
                ]

                db = await self.db_manager.get_connection()
                query = """
                INSERT INTO book_tags (book_id, tag_name, tag_color)
                VALUES (%s, %s, %s)
                """

                for tag in tag_data:
                    await db.execute(
                        query, [tag["book_id"], tag["tag_name"], tag["tag_color"]]
                    )

        except Exception as e:
            logger.error(f"Failed to save book tags for {book_id}: {e}")

    async def _load_book_tags(self, book_id: uuid.UUID) -> List[Tag]:
        """ブックのタグを読み込み"""
        try:
            query = "SELECT tag_name, tag_color FROM book_tags WHERE book_id = %s"
            db = await self.db_manager.get_connection()
            results = await db.fetch(query, [str(book_id)])

            return [
                Tag(name=row["tag_name"], color=row["tag_color"]) for row in results
            ]

        except Exception as e:
            logger.error(f"Failed to load book tags for {book_id}: {e}")
            return []

    async def _delete_book_tags(self, book_id: uuid.UUID) -> None:
        """ブックのタグを削除"""
        try:
            query = "DELETE FROM book_tags WHERE book_id = %s"
            db = await self.db_manager.get_connection()
            await db.execute(query, [str(book_id)])

        except Exception as e:
            logger.error(f"Failed to delete book tags for {book_id}: {e}")
