"""
Problem Repository implementation with Supabase
問題リポジトリの Supabase 実装
"""

import uuid
from datetime import datetime
from typing import Any

from pydantic import UUID4
from supabase import Client

from src.utils import get_logger

from ....domain.entities import ProblemEntity
from ....domain.models.domain_config import DomainConfig
from ....domain.repositories.problem_repository import (
    CreateProblemSchema,
    ProblemRepositoryBase,
    ReadProblemSchema,
    UpdateProblemSchema,
)
from .shared.domain_supabase_mixin import DomainSupabaseMixin

logger = get_logger(__name__)


class ProblemRepository(DomainSupabaseMixin, ProblemRepositoryBase):
    """Problem リポジトリの Supabase 実装"""

    table_name = "problem_headers"

    def __init__(self, client: Client, config: DomainConfig):
        super().__init__(client, config)

    async def create(self, data: CreateProblemSchema) -> ProblemEntity:
        """Create a new problem in the database."""
        logger.debug(f"Creating problem with data: {data}")

        response = await self.client.table(self.table_name).insert(data.model_dump(mode="json")).execute()
        if response.error:
            logger.error(f"Error creating problem: {response.error.message}")
            raise Exception(response.error.message)
        problem_data = response.data[0]
        problem = ReadProblemSchema(**problem_data)
        return self._schema_to_entity(problem)

    async def read(self, id: UUID4) -> ProblemEntity | None:
        """Read a problem by its ID."""
        logger.debug(f"Reading problem with ID: {id}")

        # selectメソッドを活用
        problems = await self.select(limit=1, id=id)
        return problems[0] if problems else None

    async def update(self, id, schema: UpdateProblemSchema):
        """Update a problem by its ID."""
        logger.debug(f"Updating problem with ID: {id} and data: {schema}")

        response = (
            await self.client.table(self.table_name)
            .update(schema.model_dump(mode="json"))
            .eq("id", str(id))
            .execute()
        )
        if response.error:
            logger.error(f"Error updating problem: {response.error.message}")
            raise Exception(response.error.message)

        if not response.data:
            return None

        problem_data = response.data[0]
        problem = ReadProblemSchema(**problem_data)
        return self._schema_to_entity(problem)

    async def delete(self, id: UUID4) -> bool:
        """Delete a problem by its ID."""
        logger.debug(f"Deleting problem with ID: {id}")

        response = await self.client.table(self.table_name).delete().eq("id", str(id)).execute()
        if response.error:
            logger.error(f"Error deleting problem: {response.error.message}")
            raise Exception(response.error.message)

        return response.data is not None

    async def select(
        self, limit: int | None = None, offset: int | None = None, **filters: Any
    ) -> list[ProblemEntity]:
        """
        Select multiple records with optional pagination and filtering.

        Args:
            limit: Maximum number of records to return. If None, returns all matching records.
            offset: Number of records to skip before returning results.
            **filters: Additional filtering criteria.
        """
        logger.debug(f"Selecting problems with filters: {filters}, limit: {limit}, offset: {offset}")

        query = self.client.table(self.table_name).select("*")

        # フィルタリング条件を適用
        query = self._apply_filters(query, filters)

        # ページネーション
        query = self._apply_pagination(query, limit, offset)

        # 結果順序
        query = query.order("created_at", desc=True)

        response = await query.execute()
        if response.error:
            logger.error(f"Error selecting problems: {response.error.message}")
            raise Exception(response.error.message)

        problems = []
        for problem_data in response.data:
            problem = ReadProblemSchema(**problem_data)
            problems.append(self._schema_to_entity(problem))

        return problems

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
            "book_id": lambda q, v: q.eq("book_id", str(v)),
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

    async def find_by_title(self, title: str) -> ProblemEntity | None:
        """Find problem by exact title"""
        logger.debug(f"Finding problem by title: {title}")

        # selectメソッドを活用
        problems = await self.select(limit=1, title=title)
        return problems[0] if problems else None

    async def find_by_book(self, book_id: UUID4) -> list[ProblemEntity]:
        """Find problems by book ID"""
        logger.debug(f"Finding problems by book: {book_id}")

        # selectメソッドを活用
        return await self.select(book_id=book_id)

    async def find_published(self, limit: int = 50, offset: int = 0) -> list[ProblemEntity]:
        """Find published problems with pagination"""
        logger.debug(f"Finding published problems with limit: {limit}, offset: {offset}")

        # selectメソッドを活用
        return await self.select(limit=limit, offset=offset, is_published=True)

    async def search_by_title(self, title_query: str, limit: int = 20) -> list[ProblemEntity]:
        """Search problems by title (partial match)"""
        logger.debug(f"Searching problems by title: {title_query}")

        query = (
            self.client.table(self.table_name)
            .select("*")
            .ilike("title", f"%{title_query}%")
            .order("created_at", desc=True)
            .limit(limit)
        )

        response = await query.execute()
        if response.error:
            logger.error(f"Error searching problems by title: {response.error.message}")
            raise Exception(response.error.message)

        problems = []
        for problem_data in response.data:
            problem = ReadProblemSchema(**problem_data)
            problems.append(self._schema_to_entity(problem))

        return problems

    def _schema_to_entity(self, schema: ReadProblemSchema) -> ProblemEntity:
        """Convert a ReadProblemSchema to a ProblemEntity."""
        return ProblemEntity(
            id=schema.id,
            title=schema.title,
            description=schema.description,
            book_id=schema.book_id,
            tags=schema.tags,
            published_at=schema.published_at,
            archived_at=schema.archived_at,
            created_at=schema.created_at,
            updated_at=schema.updated_at,
            content_markdown=schema.content_markdown,
            content_created_at=schema.content_created_at,
            content_updated_at=schema.content_updated_at,
            language=schema.language,
        )
