from uuid import UUID

from pydddi import IDomainService

from ...domain.entities import BookEntity
from ...domain.repositories.book_repository import BookRepository


class BookService(IDomainService):
    """BookApplicationService - 問題集アプリケーションサービス"""

    def __init__(self, book_repository: BookRepository):
        self._book_repository = book_repository

    async def get_published_books(self) -> list[BookEntity]:
        """公開済み問題集一覧を取得"""
        return await self._book_repository.find_published()

    async def get_book_by_id(self, book_id: UUID) -> BookEntity | None:
        """IDで問題集を取得"""
        return await self._book_repository.read(book_id)

    async def get_books_by_author(self, author_id: UUID) -> list[BookEntity]:
        """著者IDで問題集一覧を取得"""
        return await self._book_repository.find_by_author(author_id)

    async def create_book(self, title: str, description: str, author_id: UUID) -> BookEntity:
        """問題集を作成"""
        from ..domain.repositories.book_repository import CreateBookSchema

        create_data = CreateBookSchema(title=title, description=description, author_id=author_id)
        return await self._book_repository.create(create_data)

    async def publish_book(self, book_id: UUID) -> BookEntity:
        """問題集を公開"""
        from datetime import datetime

        from ..domain.repositories.book_repository import UpdateBookSchema

        update_data = UpdateBookSchema(id=book_id, published_at=datetime.now())
        return await self._book_repository.update(book_id, update_data)

    async def archive_book(self, book_id: UUID) -> BookEntity:
        """問題集をアーカイブ"""
        from datetime import datetime

        from ..domain.repositories.book_repository import UpdateBookSchema

        update_data = UpdateBookSchema(id=book_id, archived_at=datetime.now())
        return await self._book_repository.update(book_id, update_data)
