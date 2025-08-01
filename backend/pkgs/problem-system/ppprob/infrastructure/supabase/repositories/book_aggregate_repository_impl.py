"""
Book Aggregate Repository implementation with Supabase
ブック集約リポジトリの Supabase 実装
"""

from supabase import Client

from ....domain.models import Book
from ....domain.models.domain_config import DomainConfig
from ....domain.protocols.logger_protocols import Logger
from ....domain.repositories.book_aggregate_repository import (
    BookAggregateRepositoryBase,
    BookReadAggregateSchema,
)
from ....domain.value_objects.author_info import AuthorInfo
from .shared.domain_supabase_mixin import DomainSupabaseMixin


class BookAggregateRepository(DomainSupabaseMixin, BookAggregateRepositoryBase):
    """Book 集約リポジトリの Supabase 実装"""

    def __init__(self, client: Client, config: DomainConfig, logger: Logger | None = None):
        super().__init__(client, config)
        self.logger = logger

    async def find_by_id(self, book_id: str) -> Book | None:
        """Find a book aggregate by its ID with all related data."""
        if self.logger:
            self.logger.debug(f"Finding book aggregate with ID: {book_id}")

        try:
            # JOINクエリでBook + Author + Problem統計を取得
            response = await self.client.rpc("get_book_aggregate", {"p_book_id": book_id}).execute()

            if response.error:
                if self.logger:
                    self.logger.error(f"Error finding book aggregate: {response.error.message}")
                raise Exception(response.error.message)

            if not response.data:
                return None

            data = response.data[0]
            schema = BookReadAggregateSchema(**data)
            return self._schema_to_aggregate(schema)

        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to find book aggregate {book_id}: {e}")
            return None

    async def find_all(self, limit: int = 50, offset: int = 0) -> list[Book]:
        """Find all book aggregates with pagination."""
        if self.logger:
            self.logger.debug(f"Finding all book aggregates with limit: {limit}, offset: {offset}")

        try:
            response = await self.client.rpc(
                "get_book_aggregates", {"p_limit": limit, "p_offset": offset}
            ).execute()

            if response.error:
                if self.logger:
                    self.logger.error(f"Error finding book aggregates: {response.error.message}")
                raise Exception(response.error.message)

            books = []
            for data in response.data:
                schema = BookReadAggregateSchema(**data)
                book = self._schema_to_aggregate(schema)
                if book:
                    books.append(book)

            return books

        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to find book aggregates: {e}")
            return []

    def _schema_to_aggregate(self, schema: BookReadAggregateSchema) -> Book:
        """Convert a BookReadAggregateSchema to a Book aggregate."""
        # AuthorInfoを構築 - 外部依存を排除
        author = AuthorInfo(
            id=schema.author_id,
            user_name=schema.author_name,
            display_name=schema.author_name,  # スキーマにdisplay_nameがない場合はnameを使用
            email=schema.author_email,
            avatar_url=None  # スキーマにない場合はNone
        )

        # Book集約を構築
        return Book(
            id=schema.id,
            title=schema.title,
            description=schema.description,
            author_id=schema.author_id,
            published_at=schema.published_at,
            archived_at=schema.archived_at,
            created_at=schema.created_at,
            updated_at=schema.updated_at,
            author=author,
            problem_count=schema.problem_count,
            published_problem_count=schema.published_problem_count,
        )
