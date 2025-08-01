"""
Problem Aggregate Repository implementation with Supabase
問題集約リポジトリの Supabase 実装
"""

from supabase import Client

from src.utils import get_logger

from ....domain.models import Problem
from ....domain.models.domain_config import DomainConfig
from ....domain.repositories.problem_aggregate_repository import (
    ProblemAggregateRepositoryBase,
    ProblemReadAggregateSchema,
)
from .shared.domain_supabase_mixin import DomainSupabaseMixin

logger = get_logger(__name__)


class ProblemAggregateRepository(DomainSupabaseMixin, ProblemAggregateRepositoryBase):
    """Problem 集約リポジトリの Supabase 実装"""

    def __init__(self, client: Client, config: DomainConfig):
        super().__init__(client, config)

    async def find_by_id(self, problem_id: str) -> Problem | None:
        """Find a problem aggregate by its ID with all related data."""
        logger.debug(f"Finding problem aggregate with ID: {problem_id}")

        try:
            # JOINクエリでProblem + Book + Authorを取得
            response = await self.client.rpc(
                "get_problem_aggregate", {"p_problem_id": problem_id}
            ).execute()

            if response.error:
                logger.error(f"Error finding problem aggregate: {response.error.message}")
                raise Exception(response.error.message)

            if not response.data:
                return None

            data = response.data[0]
            schema = ProblemReadAggregateSchema(**data)
            return self._schema_to_aggregate(schema)

        except Exception as e:
            logger.error(f"Failed to find problem aggregate {problem_id}: {e}")
            return None

    async def find_all(self, limit: int = 50, offset: int = 0) -> list[Problem]:
        """Find all problem aggregates with pagination."""
        logger.debug(f"Finding all problem aggregates with limit: {limit}, offset: {offset}")

        try:
            response = await self.client.rpc(
                "get_problem_aggregates", {"p_limit": limit, "p_offset": offset}
            ).execute()

            if response.error:
                logger.error(f"Error finding problem aggregates: {response.error.message}")
                raise Exception(response.error.message)

            problems = []
            for data in response.data:
                schema = ProblemReadAggregateSchema(**data)
                problem = self._schema_to_aggregate(schema)
                if problem:
                    problems.append(problem)

            return problems

        except Exception as e:
            logger.error(f"Failed to find problem aggregates: {e}")
            return []

    def _schema_to_aggregate(self, schema: ProblemReadAggregateSchema) -> Problem:
        """Convert a ProblemReadAggregateSchema to a Problem aggregate."""
        return Problem(
            id=schema.id,
            book_id=schema.book_id,
            title=schema.title,
            description=schema.description,
            tags=schema.tags,
            published_at=schema.published_at,
            archived_at=None,  # ProblemReadAggregateSchemaにはarchived_atがない
            created_at=schema.created_at or "",
            updated_at=schema.updated_at or "",
            content_markdown=schema.content_markdown,
            content_created_at=schema.content_created_at,
            content_updated_at=schema.content_updated_at,
            book_title=None,  # 必要に応じて追加
            author_name=None,  # 必要に応じて追加
        )
