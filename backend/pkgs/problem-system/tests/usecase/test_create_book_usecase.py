"""
Tests for Create Book UseCase
問題集作成ユースケースのテスト

Author: Judge System Team
Date: 2025-06-30
"""

from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from pydddi import UseCaseCommandError, UseCaseExecutionError

from ppprob.domain.entities.book import BookEntity
from ppprob.usecase.create_book_usecase import (
    CreateBookCommand,
    CreateBookResult,
    CreateBookUseCase,
)


class TestCreateBookUseCase:
    """CreateBookUseCaseのテストクラス"""

    @pytest.fixture
    def mock_book_service(self):
        """モック問題集サービス"""
        from unittest.mock import AsyncMock, Mock

        service = Mock()
        service.create_book = AsyncMock()
        return service

    @pytest.fixture
    def usecase(self, mock_book_service):
        """テスト対象のユースケース"""
        return CreateBookUseCase(mock_book_service)

    @pytest.fixture
    def valid_command(self):
        """有効なコマンド"""
        return CreateBookCommand(
            title="テスト問題集",
            description="テスト用の問題集です",
            author_id=uuid4(),
        )

    @pytest.fixture
    def mock_book_entity(self):
        """モック問題集エンティティ"""
        book_id = uuid4()
        author_id = uuid4()

        mock_entity = Mock(spec=BookEntity)
        mock_entity.id = book_id
        mock_entity.title = "テスト問題集"
        mock_entity.description = "テスト用の問題集です"
        mock_entity.author_id = author_id

        return mock_entity

    @pytest.mark.asyncio
    async def test_execute_success(self, usecase, valid_command, mock_book_service, mock_book_entity):
        """正常な問題集作成のテスト"""
        # Arrange
        mock_book_service.create_book = AsyncMock(return_value=mock_book_entity)

        # Act
        result = await usecase.execute(valid_command)

        # Assert
        assert isinstance(result, CreateBookResult)
        assert result.book_id == mock_book_entity.id
        assert result.title == mock_book_entity.title
        assert result.description == mock_book_entity.description
        assert result.author_id == mock_book_entity.author_id

        # サービスが正しい引数で呼ばれたかを確認
        mock_book_service.create_book.assert_called_once_with(
            title=valid_command.title,
            description=valid_command.description,
            author_id=valid_command.author_id,
        )

    @pytest.mark.asyncio
    async def test_execute_with_empty_title_raises_command_error(self, usecase, mock_book_service):
        """空のタイトルでコマンドエラーが発生するテスト"""
        # Arrange
        invalid_command = CreateBookCommand(
            title="",
            description="説明",
            author_id=uuid4(),
        )

        # Act & Assert
        with pytest.raises(UseCaseCommandError, match="Book title cannot be empty"):
            await usecase.execute(invalid_command)

        # サービスが呼ばれていないことを確認
        mock_book_service.create_book.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_with_whitespace_title_raises_command_error(self, usecase, mock_book_service):
        """空白のみのタイトルでコマンドエラーが発生するテスト"""
        # Arrange
        invalid_command = CreateBookCommand(
            title="   ",
            description="説明",
            author_id=uuid4(),
        )

        # Act & Assert
        with pytest.raises(UseCaseCommandError, match="Book title cannot be empty"):
            await usecase.execute(invalid_command)

        # サービスが呼ばれていないことを確認
        mock_book_service.create_book.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_service_exception_raises_execution_error(
        self, usecase, valid_command, mock_book_service
    ):
        """サービスで例外が発生した場合の実行エラーテスト"""
        # Arrange
        mock_book_service.create_book = AsyncMock(side_effect=Exception("Database error"))

        # Act & Assert
        with pytest.raises(UseCaseExecutionError, match="Failed to create book: Database error"):
            await usecase.execute(valid_command)

    @pytest.mark.asyncio
    async def test_execute_with_minimal_data(self, usecase, mock_book_service, mock_book_entity):
        """最小限のデータでの問題集作成テスト"""
        # Arrange
        minimal_command = CreateBookCommand(
            title="最小限問題集",
            author_id=uuid4(),
        )

        mock_book_entity.title = "最小限問題集"
        mock_book_entity.description = ""
        mock_book_service.create_book = AsyncMock(return_value=mock_book_entity)

        # Act
        result = await usecase.execute(minimal_command)

        # Assert
        assert isinstance(result, CreateBookResult)
        assert result.title == "最小限問題集"
        assert result.description == ""

        # サービスが正しい引数で呼ばれたかを確認
        mock_book_service.create_book.assert_called_once_with(
            title=minimal_command.title,
            description=minimal_command.description,
            author_id=minimal_command.author_id,
        )

    @pytest.mark.asyncio
    async def test_execute_with_long_description(self, usecase, mock_book_service, mock_book_entity):
        """長い説明での問題集作成テスト"""
        # Arrange
        long_description = "説明" * 100  # 長い説明
        command = CreateBookCommand(
            title="長い説明の問題集",
            description=long_description,
            author_id=uuid4(),
        )

        mock_book_entity.description = long_description
        mock_book_service.create_book = AsyncMock(return_value=mock_book_entity)

        # Act
        result = await usecase.execute(command)

        # Assert
        assert isinstance(result, CreateBookResult)
        assert result.description == long_description
