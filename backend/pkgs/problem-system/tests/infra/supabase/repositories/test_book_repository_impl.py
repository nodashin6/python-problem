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
    from ppcore.domain.protocols.database_protocols import DatabaseConfig
    import os
    
    # Load .env file if environment variables are not set
    if not os.getenv("SUPABASE_URL"):
        env_file = "/mnt/d/nodashin/python-problem/backend/.env"
        if os.path.exists(env_file):
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value
    
    config = DatabaseConfig(
        url=os.getenv("SUPABASE_URL", "http://localhost:54221"),
        key=os.getenv("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0")
    )
    return create_client(config)


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


@pytest.fixture
def created_user():
    """テスト用のユーザー（シードされたユーザーを使用）"""
    from unittest.mock import Mock
    user = Mock()
    # Use one of the seeded user IDs
    user.id = "550e8400-e29b-41d4-a716-446655440020"  # testuser from sample data
    return user


def get_sample_create_schema(author_id: UUID4 | None):
    """テスト用のCreateBookSchema"""
    return CreateBookSchema(
        title="Test Book",
        author_id=author_id,
    )


@pytest.mark.integration
def test_repository_initialization(repository):
    """リポジトリの初期化テスト"""
    assert isinstance(repository, BookRepositoryImpl)
    assert repository.table_name == "books"


@pytest.mark.integration
def test_create_book(repository, created_user):
    """書籍の作成テスト"""
    # author_idがNullの場合は外部キー制約をスキップ
    author_id = created_user.id if created_user.id is not None else None

    create_schema = get_sample_create_schema(author_id=author_id)
    book = repository.create(create_schema)
    assert isinstance(book, BookEntity)
    assert book.title == create_schema.title
    assert book.author_id == create_schema.author_id
    assert hasattr(book, 'id')
    assert book.id is not None
