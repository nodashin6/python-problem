"""
BookRepositoryImpl integration tests
実際のSupabaseデータベースを使った統合テスト
"""

from datetime import datetime
from uuid import uuid4

import pytest
from pydantic import UUID4
from supabase import Client

from ppcore.infrastructure.supabase.client import create_client
from ppprob.domain.entities import BookEntity
from ppprob.domain.enums import Language
from ppprob.domain.models.domain_config import DomainConfig
from ppprob.domain.repositories.book_repository import CreateBookSchema, ReadBookSchema, UpdateBookSchema
from ppprob.infrastructure.supabase.repositories.book_repository_impl import BookRepositoryImpl


@pytest.fixture
def client() -> Client:
    """実際のSupabaseクライアント"""
    return create_client()


@pytest.fixture
def config() -> DomainConfig:
    """ドメイン設定"""
    return DomainConfig(language=Language.JAPANESE)


@pytest.fixture
def repository(client, config):
    """リポジトリインスタンス"""
    return BookRepositoryImpl(client, config)


@pytest.fixture(scope="function", autouse=True)
def cleanup_books(repository):
    """テスト後にbooksテーブルをクリーンアップ"""
    repository.delete_all()
    yield
    repository.delete_all()


@pytest.fixture
def sample_book_id():
    """テスト用のBook ID"""
    return uuid4()


@pytest.fixture
def sample_author_id():
    """テスト用のAuthor ID"""
    return uuid4()


def get_sample_create_schema(author_id: UUID4 | None):
    """テスト用のCreateBookSchema"""
    return CreateBookSchema(
        title="Test Book",
        author_id=author_id,
        published_at="2025-01-01T00:00:00Z",
        archived_at=None,
    )


def test_repository_initialization(repository):
    """リポジトリの初期化テスト"""
    assert isinstance(repository, BookRepositoryImpl)
    assert repository.table_name == "books"


def test_create_book(repository, created_user):
    """書籍の作成テスト"""
    # author_idがNullの場合は外部キー制約をスキップ
    author_id = created_user.id if created_user.id is not None else None

    create_schema = get_sample_create_schema(author_id=author_id)
    book = repository.create(create_schema)
    assert isinstance(book, BookEntity)
    assert book.title == create_schema.title
    assert book.author_id == create_schema.author_id
    assert book.published_at == datetime.fromisoformat(create_schema.published_at.replace("Z", "+00:00"))
    assert book.archived_at is None
    assert book.created_at is not None
    assert book.updated_at is not None
