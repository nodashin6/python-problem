"""
Tests for API Routers
APIルーターのテスト

Author: Judge System Team
Date: 2025-06-30
"""

from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from ppprob.app.api.models import BookResponse, ProblemDetailResponse, ProblemResponse
from ppprob.app.api.routers import router
from ppprob.domain.entities.book import BookEntity
from ppprob.domain.entities.problem import ProblemEntity


@pytest.fixture
def app():
    """テスト用のFastAPIアプリケーション"""
    test_app = FastAPI()
    test_app.include_router(router)
    return test_app


@pytest.fixture
def client(app):
    """テスト用のHTTPクライアント"""
    return TestClient(app)


@pytest.fixture
def mock_book_entity():
    """モック問題集エンティティ"""
    mock_entity = Mock(spec=BookEntity)
    mock_entity.id = uuid4()
    mock_entity.title = "テスト問題集"
    mock_entity.description = "テスト用の問題集です"
    mock_entity.author_id = uuid4()
    mock_entity.published_at = None
    mock_entity.archived_at = None
    mock_entity.created_at = None
    mock_entity.updated_at = None
    return mock_entity


@pytest.fixture
def mock_problem_entity():
    """モック問題エンティティ"""
    mock_entity = Mock(spec=ProblemEntity)
    mock_entity.id = uuid4()
    mock_entity.book_id = uuid4()
    mock_entity.title = "テスト問題"
    mock_entity.description = "テスト用の問題です"
    mock_entity.tags = ["test", "sample"]
    mock_entity.content_markdown = "# テスト問題\n\n問題の内容です。"
    mock_entity.published_at = None
    mock_entity.archived_at = None
    mock_entity.created_at = None
    mock_entity.updated_at = None
    return mock_entity


class TestBookEndpoints:
    """問題集エンドポイントのテストクラス"""

    @pytest.mark.asyncio
    async def test_get_books_success(self, client, mock_book_entity):
        """問題集一覧取得の成功テスト"""
        with pytest.MonkeyPatch.context() as mp:
            # モックの設定
            mock_usecase = AsyncMock()
            mock_result = Mock()
            mock_result.books = [mock_book_entity]
            mock_usecase.execute.return_value = mock_result

            # 依存性注入をモック
            mp.setattr("ppprob.app.api.routers.get_read_published_books_usecase", lambda: mock_usecase)

            # Act
            response = client.get("/books")

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["title"] == "テスト問題集"

    @pytest.mark.asyncio
    async def test_get_book_success(self, client, mock_book_entity):
        """問題集詳細取得の成功テスト"""
        with pytest.MonkeyPatch.context() as mp:
            # モックの設定
            mock_usecase = AsyncMock()
            mock_result = Mock()
            mock_result.book = mock_book_entity
            mock_usecase.execute.return_value = mock_result

            # 依存性注入をモック
            mp.setattr("ppprob.app.api.routers.get_read_book_by_id_usecase", lambda: mock_usecase)

            # Act
            response = client.get(f"/books/{mock_book_entity.id}")

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["title"] == "テスト問題集"

    @pytest.mark.asyncio
    async def test_get_book_not_found(self, client):
        """問題集が見つからない場合のテスト"""
        with pytest.MonkeyPatch.context() as mp:
            # モックの設定
            mock_usecase = AsyncMock()
            mock_result = Mock()
            mock_result.book = None
            mock_usecase.execute.return_value = mock_result

            # 依存性注入をモック
            mp.setattr("ppprob.app.api.routers.get_read_book_by_id_usecase", lambda: mock_usecase)

            # Act
            book_id = uuid4()
            response = client.get(f"/books/{book_id}")

            # Assert
            assert response.status_code == 404
            assert response.json()["detail"] == "Book not found"

    @pytest.mark.asyncio
    async def test_create_book_success(self, client, mock_book_entity):
        """問題集作成の成功テスト"""
        with pytest.MonkeyPatch.context() as mp:
            # モックの設定
            mock_usecase = AsyncMock()
            mock_result = Mock()
            mock_result.book_id = mock_book_entity.id
            mock_result.title = mock_book_entity.title
            mock_result.description = mock_book_entity.description
            mock_result.author_id = mock_book_entity.author_id
            mock_usecase.execute.return_value = mock_result

            # 依存性注入をモック
            mp.setattr("ppprob.app.api.routers.get_create_book_usecase", lambda: mock_usecase)

            # Act
            request_data = {
                "title": "テスト問題集",
                "description": "テスト用の問題集です",
                "author_id": str(mock_book_entity.author_id),
            }
            response = client.post("/books", json=request_data)

            # Assert
            assert response.status_code == 201
            data = response.json()
            assert data["title"] == "テスト問題集"


class TestProblemEndpoints:
    """問題エンドポイントのテストクラス"""

    @pytest.mark.asyncio
    async def test_get_problems_all_success(self, client, mock_problem_entity):
        """全問題取得の成功テスト"""
        with pytest.MonkeyPatch.context() as mp:
            # モックの設定
            mock_usecase = AsyncMock()
            mock_result = Mock()
            mock_result.problems = [mock_problem_entity]
            mock_usecase.execute.return_value = mock_result

            # 依存性注入をモック
            mp.setattr("ppprob.app.api.routers.get_read_published_problems_usecase", lambda: mock_usecase)

            # Act
            response = client.get("/problems")

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["title"] == "テスト問題"

    @pytest.mark.asyncio
    async def test_get_problems_by_book_id_success(self, client, mock_problem_entity):
        """問題集別問題取得の成功テスト"""
        with pytest.MonkeyPatch.context() as mp:
            # モックの設定
            mock_usecase = AsyncMock()
            mock_result = Mock()
            mock_result.problems = [mock_problem_entity]
            mock_usecase.execute.return_value = mock_result

            # 依存性注入をモック
            mp.setattr("ppprob.app.api.routers.get_read_problems_by_book_id_usecase", lambda: mock_usecase)

            # Act
            book_id = uuid4()
            response = client.get(f"/problems?book_id={book_id}")

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["title"] == "テスト問題"

    @pytest.mark.asyncio
    async def test_get_problem_success(self, client, mock_problem_entity):
        """問題詳細取得の成功テスト"""
        with pytest.MonkeyPatch.context() as mp:
            # モックの設定
            mock_usecase = AsyncMock()
            mock_result = Mock()
            mock_result.problem = mock_problem_entity
            mock_usecase.execute.return_value = mock_result

            # 依存性注入をモック
            mp.setattr("ppprob.app.api.routers.get_read_problem_by_id_usecase", lambda: mock_usecase)

            # Act
            response = client.get(f"/problems/{mock_problem_entity.id}")

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["title"] == "テスト問題"
            assert "content_markdown" in data

    @pytest.mark.asyncio
    async def test_get_problem_not_found(self, client):
        """問題が見つからない場合のテスト"""
        with pytest.MonkeyPatch.context() as mp:
            # モックの設定
            mock_usecase = AsyncMock()
            mock_result = Mock()
            mock_result.problem = None
            mock_usecase.execute.return_value = mock_result

            # 依存性注入をモック
            mp.setattr("ppprob.app.api.routers.get_read_problem_by_id_usecase", lambda: mock_usecase)

            # Act
            problem_id = uuid4()
            response = client.get(f"/problems/{problem_id}")

            # Assert
            assert response.status_code == 404
            assert response.json()["detail"] == "Problem not found"

    @pytest.mark.asyncio
    async def test_create_problem_success(self, client, mock_problem_entity):
        """問題作成の成功テスト"""
        with pytest.MonkeyPatch.context() as mp:
            # モックの設定
            mock_usecase = AsyncMock()
            mock_result = Mock()
            mock_result.problem_id = mock_problem_entity.id
            mock_result.book_id = mock_problem_entity.book_id
            mock_result.title = mock_problem_entity.title
            mock_result.description = mock_problem_entity.description
            mock_result.tags = mock_problem_entity.tags
            mock_usecase.execute.return_value = mock_result

            # 依存性注入をモック
            mp.setattr("ppprob.app.api.routers.get_create_problem_usecase", lambda: mock_usecase)

            # Act
            request_data = {
                "book_id": str(mock_problem_entity.book_id),
                "title": "テスト問題",
                "description": "テスト用の問題です",
                "tags": ["test", "sample"],
                "content_markdown": "# テスト問題\n\n問題の内容です。",
            }
            response = client.post("/problems", json=request_data)

            # Assert
            assert response.status_code == 201
            data = response.json()
            assert data["title"] == "テスト問題"
