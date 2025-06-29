"""
Book Aggregate Repository implementation with Supabase
ブック集約リポジトリの Supabase 実装
"""

from supabase import Client

from ppauth.domain.entities import UserEntity
from ppauth.infrastructure.supabase.repositories.user_repository_impl import (
    ReadUserSchema,
    UserRepositoryImpl,
)
from src.utils import get_logger

from ....domain.models import Book
from ....domain.models.domain_config import DomainConfig
from ....domain.repositories.book_aggregate_repository import (
    BookAggregateRepository,
    BookReadAggregateSchema,
)
from .shared.domain_supabase_mixin import DomainSupabaseMixin

logger = get_logger(__name__)


class BookAggregateRepositoryImpl(DomainSupabaseMixin, BookAggregateRepository):
    """Book 集約リポジトリの Supabase 実装"""

    def __init__(self, client: Client, config: DomainConfig):
        super().__init__(client, config)

    async def find_by_id(self, book_id: str) -> Book | None:
        """Find a book aggregate by its ID with all related data."""
        logger.debug(f"Finding book aggregate with ID: {book_id}")

        try:
            # JOINクエリでBook + Author + Problem統計を取得
            response = await self.client.rpc("get_book_aggregate", {"p_book_id": book_id}).execute()

            if response.error:
                logger.error(f"Error finding book aggregate: {response.error.message}")
                raise Exception(response.error.message)

            if not response.data:
                return None

            data = response.data[0]
            schema = BookReadAggregateSchema(**data)
            return self._schema_to_aggregate(schema)

        except Exception as e:
            logger.error(f"Failed to find book aggregate {book_id}: {e}")
            return None

    async def find_all(self, limit: int = 50, offset: int = 0) -> list[Book]:
        """Find all book aggregates with pagination."""
        logger.debug(f"Finding all book aggregates with limit: {limit}, offset: {offset}")

        try:
            response = await self.client.rpc(
                "get_book_aggregates", {"p_limit": limit, "p_offset": offset}
            ).execute()

            if response.error:
                logger.error(f"Error finding book aggregates: {response.error.message}")
                raise Exception(response.error.message)

            books = []
            for data in response.data:
                schema = BookReadAggregateSchema(**data)
                book = self._schema_to_aggregate(schema)
                if book:
                    books.append(book)

            return books

        except Exception as e:
            logger.error(f"Failed to find book aggregates: {e}")
            return []

    def _schema_to_aggregate(self, schema: BookReadAggregateSchema) -> Book:
        """Convert a BookReadAggregateSchema to a Book aggregate."""
        # UserEntityを構築
        author = UserEntity(
            id=schema.author_id,
            name=schema.author_name,
            email=schema.author_email,
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
