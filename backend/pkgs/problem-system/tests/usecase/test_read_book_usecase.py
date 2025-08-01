"""
Tests for Read Book UseCase
問題集読み取りユースケースのテスト

Author: Judge System Team
Date: 2025-06-30
"""

from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from pydddi import UseCaseExecutionError

from ppprob.domain.entities.book import BookEntity
from ppprob.usecase.read_book_usecase import (
    ReadBookByIdCommand,
    ReadBookByIdResult,
    ReadBookByIdUseCase,
    ReadPublishedBooksCommand,
    ReadPublishedBooksResult,
    ReadPublishedBooksUseCase,
)


class TestReadBookByIdUseCase:
    """ReadBookByIdUseCaseのテストクラス"""

    @pytest.fixture
    def mock_book_service(self):
        """モック問題集サービス"""
        from unittest.mock import AsyncMock, Mock; service = Mock(); service.get_book_by_id = AsyncMock(); service.get_published_books = AsyncMock(); return service

    @pytest.fixture
    def usecase(self, mock_book_service):
        """テスト対象のユースケース"""
        return ReadBookByIdUseCase(mock_book_service)

    @pytest.fixture
    def mock_book_entity(self):
        """モック問題集エンティティ"""
        book_id = uuid4()

        mock_entity = Mock(spec=BookEntity)
        mock_entity.id = book_id
        mock_entity.title = "テスト問題集"
        mock_entity.description = "テスト用の問題集です"
        mock_entity.author_id = uuid4()

        return mock_entity

    @pytest.mark.asyncio
    async def test_execute_success(self, usecase, mock_book_service, mock_book_entity):
        """正常な問題集取得のテスト"""
        # Arrange
        book_id = mock_book_entity.id
        command = ReadBookByIdCommand(book_id=book_id)
        mock_book_service.get_book_by_id = AsyncMock(return_value=mock_book_entity)

        # Act
        result = await usecase.execute(command)

        # Assert
        assert isinstance(result, ReadBookByIdResult)
        assert result.book == mock_book_entity

        # サービスが正しい引数で呼ばれたかを確認
        mock_book_service.get_book_by_id.assert_called_once_with(book_id)

    @pytest.mark.asyncio
    async def test_execute_book_not_found(self, usecase, mock_book_service):
        """問題集が見つからない場合のテスト"""
        # Arrange
        book_id = uuid4()
        command = ReadBookByIdCommand(book_id=book_id)
        mock_book_service.get_book_by_id = AsyncMock(return_value=None)

        # Act
        result = await usecase.execute(command)

        # Assert
        assert isinstance(result, ReadBookByIdResult)
        assert result.book is None

        # サービスが正しい引数で呼ばれたかを確認
        mock_book_service.get_book_by_id.assert_called_once_with(book_id)

    @pytest.mark.asyncio
    async def test_execute_service_exception_raises_execution_error(self, usecase, mock_book_service):
        """サービスで例外が発生した場合の実行エラーテスト"""
        # Arrange
        book_id = uuid4()
        command = ReadBookByIdCommand(book_id=book_id)
        mock_book_service.get_book_by_id = AsyncMock(side_effect=Exception("Database error"))

        # Act & Assert
        with pytest.raises(UseCaseExecutionError, match="Failed to read book: Database error"):
            await usecase.execute(command)


class TestReadPublishedBooksUseCase:
    """ReadPublishedBooksUseCaseのテストクラス"""

    @pytest.fixture
    def mock_book_service(self):
        """モック問題集サービス"""
        from unittest.mock import AsyncMock, Mock; service = Mock(); service.get_book_by_id = AsyncMock(); service.get_published_books = AsyncMock(); return service

    @pytest.fixture
    def usecase(self, mock_book_service):
        """テスト対象のユースケース"""
        return ReadPublishedBooksUseCase(mock_book_service)

    @pytest.fixture
    def mock_book_entities(self):
        """モック問題集エンティティのリスト"""
        entities = []
        for i in range(3):
            mock_entity = Mock(spec=BookEntity)
            mock_entity.id = uuid4()
            mock_entity.title = f"テスト問題集{i + 1}"
            mock_entity.description = f"テスト用の問題集{i + 1}です"
            mock_entity.author_id = uuid4()
            entities.append(mock_entity)

        return entities

    @pytest.mark.asyncio
    async def test_execute_success(self, usecase, mock_book_service, mock_book_entities):
        """正常な公開問題集取得のテスト"""
        # Arrange
        command = ReadPublishedBooksCommand()
        mock_book_service.get_published_books = AsyncMock(return_value=mock_book_entities)

        # Act
        result = await usecase.execute(command)

        # Assert
        assert isinstance(result, ReadPublishedBooksResult)
        assert result.books == mock_book_entities
        assert len(result.books) == 3

        # サービスが呼ばれたかを確認
        mock_book_service.get_published_books.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_empty_result(self, usecase, mock_book_service):
        """公開問題集が0件の場合のテスト"""
        # Arrange
        command = ReadPublishedBooksCommand()
        mock_book_service.get_published_books = AsyncMock(return_value=[])

        # Act
        result = await usecase.execute(command)

        # Assert
        assert isinstance(result, ReadPublishedBooksResult)
        assert result.books == []
        assert len(result.books) == 0

        # サービスが呼ばれたかを確認
        mock_book_service.get_published_books.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_service_exception_raises_execution_error(self, usecase, mock_book_service):
        """サービスで例外が発生した場合の実行エラーテスト"""
        # Arrange
        command = ReadPublishedBooksCommand()
        mock_book_service.get_published_books = AsyncMock(side_effect=Exception("Database error"))

        # Act & Assert
        with pytest.raises(UseCaseExecutionError, match="Failed to read published books: Database error"):
            await usecase.execute(command)
