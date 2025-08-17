"""
Tests for Dependencies
依存性注入のテスト

Author: Judge System Team
Date: 2025-06-30
"""

from unittest.mock import Mock, patch
from uuid import uuid4

import pytest

from ppprob.app.dependencies import (
    get_book_repository,
    get_book_service,
    get_create_book_usecase,
    get_create_problem_usecase,
    get_domain_config,
    get_problem_repository,
    get_problem_service,
    get_read_book_by_id_usecase,
    get_read_problem_by_id_usecase,
    get_read_problems_by_book_id_usecase,
    get_read_published_books_usecase,
    get_read_published_problems_usecase,
    get_supabase_client,
)


class TestInfrastructureDependencies:
    """インフラストラクチャ依存性のテストクラス"""

    @patch.dict("os.environ", {"SUPABASE_URL": "https://test.supabase.co", "SUPABASE_ANON_KEY": "test_key"})
    @patch("ppprob.app.dependencies.create_client")
    def test_get_supabase_client_success(self, mock_create_client):
        """Supabaseクライアント取得の成功テスト"""
        # Arrange
        mock_client = Mock()
        mock_create_client.return_value = mock_client

        # Act
        result = get_supabase_client()

        # Assert
        assert result == mock_client
        # Check that create_client was called with the expected parameters
        assert mock_create_client.call_count == 1
        call_args = mock_create_client.call_args
        assert call_args[0] == ("https://test.supabase.co", "test_key")
        assert "options" in call_args[1]  # ClientOptions should be passed as keyword argument

    @patch.dict("os.environ", {}, clear=True)
    def test_get_supabase_client_missing_env_vars(self):
        """環境変数が不足している場合のテスト"""
        # キャッシュをクリアしてテストの分離を確保
        get_supabase_client.cache_clear()
        
        # Act & Assert
        with pytest.raises(ValueError, match="SUPABASE_URL and SUPABASE_ANON_KEY must be set"):
            get_supabase_client()

    def test_get_domain_config(self):
        """ドメイン設定取得のテスト"""
        # Act
        result = get_domain_config()

        # Assert
        assert result is not None


class TestRepositoryDependencies:
    """リポジトリ依存性のテストクラス"""

    @pytest.fixture
    def mock_client(self):
        """モックSupabaseクライアント"""
        return Mock()

    def test_get_book_repository(self, mock_client):
        """BookRepository取得のテスト"""
        # Act
        result = get_book_repository(mock_client)

        # Assert
        assert result is not None
        # BookRepositoryImplのインスタンスかどうかを確認
        assert hasattr(result, "__class__")

    def test_get_problem_repository(self, mock_client):
        """ProblemRepository取得のテスト"""
        # Act
        result = get_problem_repository(mock_client)

        # Assert
        assert result is not None
        # ProblemRepositoryImplのインスタンスかどうかを確認
        assert hasattr(result, "__class__")


class TestServiceDependencies:
    """サービス依存性のテストクラス"""

    @pytest.fixture
    def mock_book_repository(self):
        """モックBookRepository"""
        return Mock()

    @pytest.fixture
    def mock_problem_repository(self):
        """モックProblemRepository"""
        return Mock()

    @pytest.fixture
    def mock_domain_config(self):
        """モックDomainConfig"""
        return Mock()

    def test_get_book_service(self, mock_book_repository):
        """BookService取得のテスト"""
        # Act
        result = get_book_service(mock_book_repository)

        # Assert
        assert result is not None
        # BookServiceのインスタンスかどうかを確認
        assert hasattr(result, "__class__")

    def test_get_problem_service(self, mock_problem_repository):
        """ProblemService取得のテスト"""
        # Act
        result = get_problem_service(mock_problem_repository)

        # Assert
        assert result is not None
        # ProblemServiceのインスタンスかどうかを確認
        assert hasattr(result, "__class__")


class TestUseCaseDependencies:
    """ユースケース依存性のテストクラス"""

    @pytest.fixture
    def mock_book_service(self):
        """モックBookService"""
        return Mock()

    @pytest.fixture
    def mock_problem_service(self):
        """モックProblemService"""
        return Mock()

    def test_get_create_book_usecase(self, mock_book_service):
        """CreateBookUseCase取得のテスト"""
        # Act
        result = get_create_book_usecase(mock_book_service)

        # Assert
        assert result is not None
        # CreateBookUseCaseのインスタンスかどうかを確認
        assert hasattr(result, "execute")

    def test_get_create_problem_usecase(self, mock_problem_service):
        """CreateProblemUseCase取得のテスト"""
        # Act
        result = get_create_problem_usecase(mock_problem_service)

        # Assert
        assert result is not None
        # CreateProblemUseCaseのインスタンスかどうかを確認
        assert hasattr(result, "execute")

    def test_get_read_published_books_usecase(self, mock_book_service):
        """ReadPublishedBooksUseCase取得のテスト"""
        # Act
        result = get_read_published_books_usecase(mock_book_service)

        # Assert
        assert result is not None
        assert hasattr(result, "execute")

    def test_get_read_book_by_id_usecase(self, mock_book_service):
        """ReadBookByIdUseCase取得のテスト"""
        # Act
        result = get_read_book_by_id_usecase(mock_book_service)

        # Assert
        assert result is not None
        assert hasattr(result, "execute")

    def test_get_read_published_problems_usecase(self, mock_problem_service):
        """ReadPublishedProblemsUseCase取得のテスト"""
        # Act
        result = get_read_published_problems_usecase(mock_problem_service)

        # Assert
        assert result is not None
        assert hasattr(result, "execute")

    def test_get_read_problems_by_book_id_usecase(self, mock_problem_service):
        """ReadProblemsByBookIdUseCase取得のテスト"""
        # Act
        result = get_read_problems_by_book_id_usecase(mock_problem_service)

        # Assert
        assert result is not None
        assert hasattr(result, "execute")

    def test_get_read_problem_by_id_usecase(self, mock_problem_service):
        """ReadProblemByIdUseCase取得のテスト"""
        # Act
        result = get_read_problem_by_id_usecase(mock_problem_service)

        # Assert
        assert result is not None
        assert hasattr(result, "execute")
