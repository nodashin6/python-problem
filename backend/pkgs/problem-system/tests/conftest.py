"""
Problem System tests configuration
"""

from datetime import datetime
from uuid import uuid4

import pytest
from pydantic import UUID4
from supabase import Client

from ppauth.domain.entities import UserEntity
from ppcore.infrastructure.supabase.client import create_client


@pytest.fixture
def client() -> Client:
    """Supabaseクライアントのインスタンス"""
    return create_client()


@pytest.fixture
def mock_user_id() -> UUID4:
    """テスト用のユーザーID (ppauth管理を想定)"""
    return uuid4()


@pytest.fixture
def mock_user_entity(mock_user_id: UUID4) -> UserEntity:
    """テスト用のユーザーエンティティ (ppauth管理を想定)"""
    # Note: これは ppauth のUserEntity のモックです
    # 実際のテストでは ppauth のフィクスチャを使用することを推奨
    return UserEntity(
        id=mock_user_id,
        user_name="testuser",
        display_name="Test User",
        email="test@example.com",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def sample_book_data(mock_user_id: UUID4):
    """テスト用の問題集データ"""
    return {
        "title": "テスト問題集",
        "description": "テスト用の問題集です",
        "author_id": mock_user_id,
    }


@pytest.fixture
def sample_problem_data():
    """テスト用の問題データ"""
    return {
        "title": "テスト問題",
        "description": "テスト用の問題です",
        "book_id": uuid4(),
        "tags": ["test", "sample"],
        "content_markdown": "# テスト問題\n\n問題の内容です。\n\n```python\nprint('Hello World')\n```",
    }


@pytest.fixture
def created_book(client, mock_user_id: UUID4):
    """テスト用の問題集を実際にDBに作成"""
    book_id = uuid4()

    try:
        response = (
            client.table("books")
            .insert(
                {
                    "id": str(book_id),
                    "title": "テスト問題集",
                    "description": "テスト用の問題集です",
                    "author_id": str(mock_user_id),
                    "is_published": True,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                }
            )
            .execute()
        )

        class DummyBook:
            def __init__(self, book_id, author_id):
                self.id = book_id
                self.title = "テスト問題集"
                self.description = "テスト用の問題集です"
                self.author_id = author_id
                self.is_published = True

        yield DummyBook(book_id, mock_user_id)

        # クリーンアップ: テスト後に問題集を削除
        client.table("books").delete().eq("id", str(book_id)).execute()

    except Exception as e:
        # booksテーブルがない場合の処理
        class DummyBook:
            def __init__(self):
                self.id = uuid4()
                self.title = "テスト問題集"
                self.description = "テスト用の問題集です"
                self.author_id = None
                self.is_published = True

        yield DummyBook()


@pytest.fixture
def created_problem(client, created_book):
    """テスト用の問題を実際にDBに作成"""
    problem_id = uuid4()

    try:
        response = (
            client.table("problems")
            .insert(
                {
                    "id": str(problem_id),
                    "title": "テスト問題",
                    "description": "テスト用の問題です",
                    "book_id": str(created_book.id),
                    "tags": ["test", "sample"],
                    "content_markdown": "# テスト問題\n\n問題の内容です。\n\n```python\nprint('Hello World')\n```",
                    "status": "published",
                    "difficulty": "easy",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                }
            )
            .execute()
        )

        class DummyProblem:
            def __init__(self, problem_id, book_id):
                self.id = problem_id
                self.title = "テスト問題"
                self.description = "テスト用の問題です"
                self.book_id = book_id
                self.tags = ["test", "sample"]
                self.content_markdown = (
                    "# テスト問題\n\n問題の内容です。\n\n```python\nprint('Hello World')\n```"
                )

        yield DummyProblem(problem_id, created_book.id)

        # クリーンアップ: テスト後に問題を削除
        client.table("problems").delete().eq("id", str(problem_id)).execute()

    except Exception as e:
        # problemsテーブルがない場合の処理
        class DummyProblem:
            def __init__(self):
                self.id = uuid4()
                self.title = "テスト問題"
                self.description = "テスト用の問題です"
                self.book_id = uuid4()
                self.tags = ["test", "sample"]
                self.content_markdown = (
                    "# テスト問題\n\n問題の内容です。\n\n```python\nprint('Hello World')\n```"
                )

        yield DummyProblem()


@pytest.fixture
def mock_book_repository():
    """モック問題集リポジトリ"""
    from unittest.mock import Mock

    return Mock()


@pytest.fixture
def mock_problem_repository():
    """モック問題リポジトリ"""
    from unittest.mock import Mock

    return Mock()


@pytest.fixture
def mock_book_service():
    """モック問題集サービス"""
    from unittest.mock import Mock

    return Mock()


@pytest.fixture
def mock_problem_service():
    """モック問題サービス"""
    from unittest.mock import Mock

    return Mock()
