"""
Book Repository implementation with Supabase
ブックリポジトリの Supabase 実装
"""

import uuid
from datetime import datetime
from typing import Any

from pydantic import UUID4
from supabase import Client

from src.utils import get_logger

from ....domain.entities import BookEntity
from ....domain.models.domain_config import DomainConfig
from ....domain.repositories.book_repository import (
    BookRepositoryBase,
    CreateBookSchema,
    ReadBookSchema,
    UpdateBookSchema,
)
from .shared.domain_supabase_mixin import DomainSupabaseMixin

logger = get_logger(__name__)


class BookRepository(DomainSupabaseMixin, BookRepositoryBase):
    """Book リポジトリの Supabase 実装"""

    table_name = "books"

    def __init__(self, client: Client, config: DomainConfig):
        super().__init__(client, config)

    def create(self, data: CreateBookSchema) -> BookEntity:
        """Create a new book in the database."""
        logger.debug(f"Creating book with data: {data}")

        response = self.client.table(self.table_name).insert(data.model_dump(mode="json")).execute()
        book_data = response.data[0]
        book = ReadBookSchema(**book_data)
        return self._schema_to_entity(book)

    def read(self, id: UUID4) -> BookEntity | None:
        """Read a book by its ID."""
        logger.debug(f"Reading book with ID: {id}")

        # selectメソッドを活用
        books = self.select(limit=1, id=id)
        return books[0] if books else None

    def read_optional(self, id):
        """Read a book by its ID, returning None if not found."""
        try:
            book = self.read(id)
            return book
        except Exception as e:
            return None

    def update(self, id, schema: UpdateBookSchema):
        """Update a book by its ID."""
        logger.debug(f"Updating book with ID: {id} and data: {schema}")

        response = (
            self.client.table(self.table_name)
            .update(schema.model_dump(mode="json"))
            .eq("id", str(id))
            .execute()
        )

        if not response.data:
            return None

        book_data = response.data[0]
        book = ReadBookSchema(**book_data)
        return self._schema_to_entity(book)

    def delete(self, id: UUID4) -> bool:
        """Delete a book by its ID."""
        logger.debug(f"Deleting book with ID: {id}")

        response = self.client.table(self.table_name).delete().eq("id", str(id)).execute()

        return response.data is not None

    def delete_all(self) -> None:
        """Delete all books in the database."""
        all_entities = self.select(limit=None)
        all_ids = [str(entity.id) for entity in all_entities]
        response = self.client.table(self.table_name).delete().in_("id", all_ids).execute()

    def select(
        self, limit: int | None = None, offset: int | None = None, **filters: Any
    ) -> list[BookEntity]:
        """
        Select multiple records with optional pagination and filtering.

        Args:
            limit: Maximum number of records to return. If None, returns all matching records.
            offset: Number of records to skip before returning results.
            **filters: Additional filtering criteria.
        """
        logger.debug(f"Selecting books with filters: {filters}, limit: {limit}, offset: {offset}")

        query = self.client.table(self.table_name).select("*")

        # フィルタリング条件を適用
        query = self._apply_filters(query, filters)

        # ページネーション
        query = self._apply_pagination(query, limit, offset)

        # 結果順序
        query = query.order("created_at", desc=True)

        response = query.execute()

        books = []
        for book_data in response.data:
            book = ReadBookSchema(**book_data)
            books.append(self._schema_to_entity(book))

        return books

    def _apply_filters(self, query, filters: dict[str, Any]):
        """Apply filtering conditions to the query."""
        for key, value in filters.items():
            if value is not None:
                query = self._apply_single_filter(query, key, value)
        return query

    def _apply_single_filter(self, query, key: str, value: Any):
        """Apply a single filter condition to the query."""
        filter_map = {
            "id": lambda q, v: q.eq("id", str(v)),
            "title": lambda q, v: q.eq("title", v),
            "author_id": lambda q, v: q.eq("author_id", str(v)),
            "published_at": lambda q, v: q.eq("published_at", v),
            "archived_at": lambda q, v: q.eq("archived_at", v),
            "is_published": self._apply_published_filter,
            "is_archived": self._apply_archived_filter,
        }

        filter_func = filter_map.get(key)
        return filter_func(query, value) if filter_func else query

    def _apply_published_filter(self, query, is_published: bool):
        """Apply published filter to the query."""
        if is_published:
            return query.not_.is_("published_at", "null")
        else:
            return query.is_("published_at", "null")

    def _apply_archived_filter(self, query, is_archived: bool):
        """Apply archived filter to the query."""
        if is_archived:
            return query.not_.is_("archived_at", "null")
        else:
            return query.is_("archived_at", "null")

    def _apply_pagination(self, query, limit: int | None, offset: int | None):
        """Apply pagination to the query."""
        if offset:
            query = query.range(offset, offset + (limit - 1) if limit else 999999)
        elif limit:
            query = query.limit(limit)
        return query

    async def find_by_title(self, title: str) -> BookEntity | None:
        """Find book by exact title"""
        logger.debug(f"Finding book by title: {title}")

        # selectメソッドを活用
        books = await self.select(limit=1, title=title)
        return books[0] if books else None

    async def find_by_author(self, author_id: UUID4) -> list[BookEntity]:
        """Find books by author"""
        logger.debug(f"Finding books by author: {author_id}")

        # selectメソッドを活用
        return await self.select(author_id=author_id)

    async def find_published(self, limit: int = 50, offset: int = 0) -> list[BookEntity]:
        """Find published books with pagination"""
        logger.debug(f"Finding published books with limit: {limit}, offset: {offset}")

        # selectメソッドを活用
        return await self.select(limit=limit, offset=offset, is_published=True)

    async def search_by_title(self, title_query: str, limit: int = 20) -> list[BookEntity]:
        """Search books by title (partial match)"""
        logger.debug(f"Searching books by title: {title_query}")

        query = (
            self.client.table(self.table_name)
            .select("*")
            .ilike("title", f"%{title_query}%")
            .order("created_at", desc=True)
            .limit(limit)
        )

        response = await query.execute()
        if response.error:
            logger.error(f"Error searching books by title: {response.error.message}")
            raise Exception(response.error.message)

        books = []
        for book_data in response.data:
            book = ReadBookSchema(**book_data)
            books.append(self._schema_to_entity(book))

        return books

    async def count_by_author(self, author_id: UUID4) -> int:
        """Count books by author"""
        logger.debug(f"Counting books by author: {author_id}")

        response = (
            await self.client.table(self.table_name)
            .select("*", count="exact")
            .eq("author_id", str(author_id))
            .execute()
        )
        if response.error:
            logger.error(f"Error counting books by author: {response.error.message}")
            raise Exception(response.error.message)

        return response.count or 0

    async def count_published(self) -> int:
        """Count published books"""
        logger.debug("Counting published books")

        response = (
            await self.client.table(self.table_name)
            .select("*", count="exact")
            .not_.is_("published_at", "null")
            .execute()
        )
        if response.error:
            logger.error(f"Error counting published books: {response.error.message}")
            raise Exception(response.error.message)

        return response.count or 0

    def _schema_to_entity(self, schema: ReadBookSchema) -> BookEntity:
        """Convert a ReadBookSchema to a BookEntity."""
        return BookEntity(
            id=schema.id,
            title=schema.title,
            author_id=schema.author_id,
            published_at=schema.published_at,
            archived_at=schema.archived_at,
            created_at=schema.created_at,
            updated_at=schema.updated_at,
        )
