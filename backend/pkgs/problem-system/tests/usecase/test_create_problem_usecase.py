"""
Tests for Create Problem UseCase
問題作成ユースケースのテスト

Author: Judge System Team
Date: 2025-06-30
"""

from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from pydddi import UseCaseCommandError, UseCaseExecutionError

from ppprob.domain.entities.problem import ProblemEntity
from ppprob.usecase.create_problem_usecase import (
    CreateProblemCommand,
    CreateProblemResult,
    CreateProblemUseCase,
)


class TestCreateProblemUseCase:
    """CreateProblemUseCaseのテストクラス"""

    @pytest.fixture
    def mock_problem_service(self):
        """モック問題サービス"""
        from unittest.mock import AsyncMock, Mock

        service = Mock()
        service.create_problem = AsyncMock()
        return service

    @pytest.fixture
    def usecase(self, mock_problem_service):
        """テスト対象のユースケース"""
        return CreateProblemUseCase(mock_problem_service)

    @pytest.fixture
    def valid_command(self):
        """有効なコマンド"""
        return CreateProblemCommand(
            book_id=uuid4(),
            title="テスト問題",
            description="テスト用の問題です",
            tags=["test", "sample"],
            content_markdown="# テスト問題\n\n問題の内容です。\n\n```python\nprint('Hello World')\n```",
        )

    @pytest.fixture
    def mock_problem_entity(self):
        """モック問題エンティティ"""
        problem_id = uuid4()
        book_id = uuid4()

        mock_entity = Mock(spec=ProblemEntity)
        mock_entity.id = problem_id
        mock_entity.book_id = book_id
        mock_entity.title = "テスト問題"
        mock_entity.description = "テスト用の問題です"
        mock_entity.tags = ["test", "sample"]

        return mock_entity

    @pytest.mark.asyncio
    async def test_execute_success(self, usecase, valid_command, mock_problem_service, mock_problem_entity):
        """正常な問題作成のテスト"""
        # Arrange
        mock_problem_service.create_problem = AsyncMock(return_value=mock_problem_entity)

        # Act
        result = await usecase.execute(valid_command)

        # Assert
        assert isinstance(result, CreateProblemResult)
        assert result.problem_id == mock_problem_entity.id
        assert result.book_id == mock_problem_entity.book_id
        assert result.title == mock_problem_entity.title
        assert result.description == mock_problem_entity.description
        assert result.tags == mock_problem_entity.tags

        # サービスが正しい引数で呼ばれたかを確認
        mock_problem_service.create_problem.assert_called_once_with(
            book_id=valid_command.book_id,
            title=valid_command.title,
            description=valid_command.description,
            tags=valid_command.tags,
            content_markdown=valid_command.content_markdown,
        )

    @pytest.mark.asyncio
    async def test_execute_with_empty_title_raises_command_error(self, usecase, mock_problem_service):
        """空のタイトルでコマンドエラーが発生するテスト"""
        # Arrange
        invalid_command = CreateProblemCommand(
            book_id=uuid4(),
            title="",
            description="説明",
            tags=["test"],
            content_markdown="内容",
        )

        # Act & Assert
        with pytest.raises(UseCaseCommandError, match="Problem title cannot be empty"):
            await usecase.execute(invalid_command)

        # サービスが呼ばれていないことを確認
        mock_problem_service.create_problem.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_with_whitespace_title_raises_command_error(self, usecase, mock_problem_service):
        """空白のみのタイトルでコマンドエラーが発生するテスト"""
        # Arrange
        invalid_command = CreateProblemCommand(
            book_id=uuid4(),
            title="   ",
            description="説明",
            tags=["test"],
            content_markdown="内容",
        )

        # Act & Assert
        with pytest.raises(UseCaseCommandError, match="Problem title cannot be empty"):
            await usecase.execute(invalid_command)

        # サービスが呼ばれていないことを確認
        mock_problem_service.create_problem.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_service_exception_raises_execution_error(
        self, usecase, valid_command, mock_problem_service
    ):
        """サービスで例外が発生した場合の実行エラーテスト"""
        # Arrange
        mock_problem_service.create_problem = AsyncMock(side_effect=Exception("Database error"))

        # Act & Assert
        with pytest.raises(UseCaseExecutionError, match="Failed to create problem: Database error"):
            await usecase.execute(valid_command)

    @pytest.mark.asyncio
    async def test_execute_with_empty_tags(self, usecase, mock_problem_service, mock_problem_entity):
        """タグが空の場合の問題作成テスト"""
        # Arrange
        command = CreateProblemCommand(
            book_id=uuid4(),
            title="タグなし問題",
            description="タグがない問題です",
            tags=[],
            content_markdown="内容",
        )

        mock_problem_entity.tags = []
        mock_problem_service.create_problem = AsyncMock(return_value=mock_problem_entity)

        # Act
        result = await usecase.execute(command)

        # Assert
        assert isinstance(result, CreateProblemResult)
        assert result.tags == []

    @pytest.mark.asyncio
    async def test_execute_with_many_tags(self, usecase, mock_problem_service, mock_problem_entity):
        """多数のタグがある場合の問題作成テスト"""
        # Arrange
        many_tags = [f"tag{i}" for i in range(10)]
        command = CreateProblemCommand(
            book_id=uuid4(),
            title="多数タグ問題",
            description="多数のタグがある問題です",
            tags=many_tags,
            content_markdown="内容",
        )

        mock_problem_entity.tags = many_tags
        mock_problem_service.create_problem = AsyncMock(return_value=mock_problem_entity)

        # Act
        result = await usecase.execute(command)

        # Assert
        assert isinstance(result, CreateProblemResult)
        assert result.tags == many_tags
        assert len(result.tags) == 10

    @pytest.mark.asyncio
    async def test_execute_with_long_content(self, usecase, mock_problem_service, mock_problem_entity):
        """長いコンテンツでの問題作成テスト"""
        # Arrange
        long_content = "# 長い問題\n\n" + "内容" * 1000 + "\n\n```python\nprint('test')\n```"
        command = CreateProblemCommand(
            book_id=uuid4(),
            title="長いコンテンツ問題",
            description="長いコンテンツの問題です",
            tags=["long", "content"],
            content_markdown=long_content,
        )

        mock_problem_service.create_problem = AsyncMock(return_value=mock_problem_entity)

        # Act
        result = await usecase.execute(command)

        # Assert
        assert isinstance(result, CreateProblemResult)

        # サービスが正しい引数で呼ばれたかを確認
        mock_problem_service.create_problem.assert_called_once_with(
            book_id=command.book_id,
            title=command.title,
            description=command.description,
            tags=command.tags,
            content_markdown=long_content,
        )
