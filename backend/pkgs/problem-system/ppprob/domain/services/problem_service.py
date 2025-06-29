from uuid import UUID

from pydddi import IDomainService

from ...domain.entities import ProblemEntity
from ...domain.repositories.problem_repository import ProblemRepository


class ProblemApplicationService:
    """ProblemApplicationService - 問題アプリケーションサービス"""

    def __init__(self, problem_repository: ProblemRepository):
        self._problem_repository = problem_repository

    async def get_published_problems(self) -> list[ProblemEntity]:
        """公開済み問題一覧を取得"""
        return await self._problem_repository.find_published()

    async def get_problem_by_id(self, problem_id: UUID) -> ProblemEntity | None:
        """IDで問題を取得"""
        return await self._problem_repository.read(problem_id)

    async def get_problems_by_book_id(self, book_id: UUID) -> list[ProblemEntity]:
        """問題集IDで問題一覧を取得"""
        return await self._problem_repository.find_by_book(book_id)

    async def create_problem(
        self,
        title: str,
        description: str,
        book_id: UUID,
        tags: list[str] | None = None,
        content_markdown: str | None = None,
    ) -> ProblemEntity:
        """問題を作成"""
        from ..domain.repositories.problem_repository import CreateProblemSchema

        create_data = CreateProblemSchema(
            title=title,
            description=description,
            book_id=book_id,
            tags=tags or [],
            content_markdown=content_markdown,
        )
        return await self._problem_repository.create(create_data)

    async def publish_problem(self, problem_id: UUID) -> ProblemEntity:
        """問題を公開"""
        from datetime import datetime

        from ..domain.repositories.problem_repository import UpdateProblemSchema

        update_data = UpdateProblemSchema(id=problem_id, published_at=datetime.now())
        return await self._problem_repository.update(problem_id, update_data)

    async def archive_problem(self, problem_id: UUID) -> ProblemEntity:
        """問題をアーカイブ"""
        from datetime import datetime

        from ..domain.repositories.problem_repository import UpdateProblemSchema

        update_data = UpdateProblemSchema(id=problem_id, archived_at=datetime.now())
        return await self._problem_repository.update(problem_id, update_data)
