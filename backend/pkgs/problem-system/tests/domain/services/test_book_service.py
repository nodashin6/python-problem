"""
Book domain service unit tests
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.core.domain.services.book_service import BookDomainService
from src.core.domain.models import Book, Problem
from src.core.domain.repositories import BookRepository, ProblemRepository
from src.shared.events import EventBus


@pytest.mark.core
class TestBookDomainService:
    """BookDomainServiceのテスト"""

    @pytest.fixture
    def mock_book_repo(self):
        """モックBookRepositoryを作成"""
        repo = AsyncMock(spec=BookRepository)
        return repo

    @pytest.fixture
    def mock_problem_repo(self):
        """モックProblemRepositoryを作成"""
        repo = AsyncMock(spec=ProblemRepository)
        return repo

    @pytest.fixture
    def mock_event_bus(self):
        """モックEventBusを作成"""
        bus = AsyncMock(spec=EventBus)
        return bus

    @pytest.fixture
    def book_service(self, mock_book_repo, mock_problem_repo, mock_event_bus):
        """BookDomainServiceのインスタンスを作成"""
        return BookDomainService(
            book_repo=mock_book_repo,
            problem_repo=mock_problem_repo,
            event_bus=mock_event_bus,
        )

    @pytest.mark.asyncio
    async def test_create_book_success(self, book_service, mock_book_repo):
        """問題集作成成功のテスト"""
        author_id = uuid4()

        # モックの設定
        mock_book_repo.find_by_title.return_value = None  # 重複なし
        mock_book_repo.create.return_value = Book(
            title="Test Book", description="Test description", author_id=author_id
        )

        # テスト実行
        result = await book_service.create_book(
            title="Test Book", description="Test description", author_id=author_id
        )

        # アサート
        assert result.title == "Test Book"
        assert result.description == "Test description"
        assert result.author_id == author_id
        assert result.is_published is False
        mock_book_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_book_duplicate_title(self, book_service, mock_book_repo):
        """問題集作成時のタイトル重複エラーのテスト"""
        author_id = uuid4()

        # モックの設定 - 既存の問題集を返す
        existing_book = Book(
            title="Existing Book",
            description="Existing description",
            author_id=author_id,
        )
        mock_book_repo.find_by_title.return_value = existing_book

        # テスト実行とアサート
        with pytest.raises(ValueError, match="Book with this title already exists"):
            await book_service.create_book(
                title="Existing Book",
                description="Test description",
                author_id=author_id,
            )

    @pytest.mark.asyncio
    async def test_publish_book_success(self, book_service, mock_book_repo):
        """問題集公開成功のテスト"""
        book_id = uuid4()
        book = Book(
            id=book_id,
            title="Test Book",
            description="Test description",
            author_id=uuid4(),
            is_published=False,
        )

        # モックの設定
        mock_book_repo.get.return_value = book
        mock_book_repo.update.return_value = book

        # テスト実行
        result = await book_service.publish_book(book_id)

        # アサート
        assert result.is_published is True
        mock_book_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_book_not_found(self, book_service, mock_book_repo):
        """存在しない問題集の公開エラーテスト"""
        book_id = uuid4()

        # モックの設定
        mock_book_repo.get.return_value = None

        # テスト実行とアサート
        with pytest.raises(ValueError, match="Book not found"):
            await book_service.publish_book(book_id)

    @pytest.mark.asyncio
    async def test_add_problem_to_book_success(self, book_service, mock_book_repo, mock_problem_repo):
        """問題集への問題追加成功のテスト"""
        book_id = uuid4()
        problem_id = uuid4()

        book = Book(id=book_id, title="Test Book", author_id=uuid4())

        problem = Problem(
            id=problem_id,
            title="Test Problem",
            description="Test description",
            author_id=uuid4(),
        )

        # モックの設定
        mock_book_repo.get.return_value = book
        mock_problem_repo.get.return_value = problem
        mock_problem_repo.update.return_value = problem

        # テスト実行
        result = await book_service.add_problem_to_book(book_id, problem_id)

        # アサート
        assert result.book_id == book_id
        mock_problem_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_problem_to_book_book_not_found(self, book_service, mock_book_repo):
        """存在しない問題集への問題追加エラーテスト"""
        book_id = uuid4()
        problem_id = uuid4()

        # モックの設定
        mock_book_repo.get.return_value = None

        # テスト実行とアサート
        with pytest.raises(ValueError, match="Book not found"):
            await book_service.add_problem_to_book(book_id, problem_id)

    @pytest.mark.asyncio
    async def test_add_problem_to_book_problem_not_found(
        self, book_service, mock_book_repo, mock_problem_repo
    ):
        """存在しない問題の問題集追加エラーテスト"""
        book_id = uuid4()
        problem_id = uuid4()

        book = Book(id=book_id, title="Test Book", author_id=uuid4())

        # モックの設定
        mock_book_repo.get.return_value = book
        mock_problem_repo.get.return_value = None

        # テスト実行とアサート
        with pytest.raises(ValueError, match="Problem not found"):
            await book_service.add_problem_to_book(book_id, problem_id)

    @pytest.mark.asyncio
    async def test_remove_problem_from_book_success(self, book_service, mock_problem_repo):
        """問題集からの問題削除成功のテスト"""
        problem_id = uuid4()
        book_id = uuid4()

        problem = Problem(
            id=problem_id,
            title="Test Problem",
            description="Test description",
            author_id=uuid4(),
            book_id=book_id,
        )

        # モックの設定
        mock_problem_repo.get.return_value = problem
        mock_problem_repo.update.return_value = problem

        # テスト実行
        result = await book_service.remove_problem_from_book(problem_id)

        # アサート
        assert result.book_id is None
        mock_problem_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_book_with_problems(self, book_service, mock_book_repo, mock_problem_repo):
        """問題集と問題の取得テスト"""
        book_id = uuid4()

        book = Book(
            id=book_id,
            title="Test Book",
            description="Test description",
            author_id=uuid4(),
        )

        problems = [
            Problem(
                title="Problem 1",
                description="Description 1",
                author_id=uuid4(),
                book_id=book_id,
            ),
            Problem(
                title="Problem 2",
                description="Description 2",
                author_id=uuid4(),
                book_id=book_id,
            ),
        ]

        # モックの設定
        mock_book_repo.get.return_value = book
        mock_problem_repo.find_by_book_id.return_value = problems

        # テスト実行
        result_book, result_problems = await book_service.get_book_with_problems(book_id)

        # アサート
        assert result_book.id == book_id
        assert len(result_problems) == 2
        assert result_problems[0].title == "Problem 1"
        assert result_problems[1].title == "Problem 2"

    @pytest.mark.asyncio
    async def test_get_published_books(self, book_service, mock_book_repo):
        """公開済み問題集取得のテスト"""
        books = [
            Book(title="Published Book 1", author_id=uuid4(), is_published=True),
            Book(title="Published Book 2", author_id=uuid4(), is_published=True),
        ]

        # モックの設定
        mock_book_repo.find_published.return_value = books

        # テスト実行
        result = await book_service.get_published_books()

        # アサート
        assert len(result) == 2
        assert all(book.is_published for book in result)
        mock_book_repo.find_published.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_books_by_author(self, book_service, mock_book_repo):
        """作者別問題集取得のテスト"""
        author_id = uuid4()
        books = [
            Book(title="Author Book 1", author_id=author_id),
            Book(title="Author Book 2", author_id=author_id),
        ]

        # モックの設定
        mock_book_repo.find_by_author_id.return_value = books

        # テスト実行
        result = await book_service.get_books_by_author(author_id)

        # アサート
        assert len(result) == 2
        assert all(book.author_id == author_id for book in result)
        mock_book_repo.find_by_author_id.assert_called_once_with(author_id)

    @pytest.mark.asyncio
    async def test_update_book_info(self, book_service, mock_book_repo):
        """問題集情報更新のテスト"""
        book_id = uuid4()
        book = Book(
            id=book_id,
            title="Old Title",
            description="Old description",
            author_id=uuid4(),
        )

        # モックの設定
        mock_book_repo.get.return_value = book
        mock_book_repo.update.return_value = book

        # テスト実行
        result = await book_service.update_book_info(
            book_id=book_id,
            title="New Title",
            description="New description",
            cover_image_url="https://example.com/cover.jpg",
        )

        # アサート
        assert result.title == "New Title"
        assert result.description == "New description"
        assert result.cover_image_url == "https://example.com/cover.jpg"
        mock_book_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_book_success(self, book_service, mock_book_repo, mock_problem_repo):
        """問題集削除成功のテスト"""
        book_id = uuid4()
        book = Book(id=book_id, title="Test Book", author_id=uuid4())

        # モックの設定
        mock_book_repo.get.return_value = book
        mock_problem_repo.find_by_book_id.return_value = []  # 関連する問題なし

        # テスト実行
        await book_service.delete_book(book_id)

        # アサート
        mock_book_repo.delete.assert_called_once_with(book_id)

    @pytest.mark.asyncio
    async def test_delete_book_with_problems_error(self, book_service, mock_book_repo, mock_problem_repo):
        """問題が含まれる問題集の削除エラーテスト"""
        book_id = uuid4()
        book = Book(id=book_id, title="Test Book", author_id=uuid4())

        problems = [
            Problem(
                title="Problem 1",
                description="Description 1",
                author_id=uuid4(),
                book_id=book_id,
            )
        ]

        # モックの設定
        mock_book_repo.get.return_value = book
        mock_problem_repo.find_by_book_id.return_value = problems

        # テスト実行とアサート
        with pytest.raises(ValueError, match="Cannot delete book with problems"):
            await book_service.delete_book(book_id)
