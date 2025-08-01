"""
Tests for Read Problem UseCase
問題読み取りユースケースのテスト

Author: Judge System Team
Date: 2025-06-30
"""

from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from pydddi import UseCaseExecutionError

from ppprob.domain.entities.problem import ProblemEntity
from ppprob.usecase.read_problem_usecase import (
    ReadProblemByIdCommand,
    ReadProblemByIdResult,
    ReadProblemByIdUseCase,
    ReadProblemsByBookIdCommand,
    ReadProblemsByBookIdResult,
    ReadProblemsByBookIdUseCase,
    ReadPublishedProblemsCommand,
    ReadPublishedProblemsResult,
    ReadPublishedProblemsUseCase,
)


class TestReadProblemByIdUseCase:
    """ReadProblemByIdUseCaseのテストクラス"""

    @pytest.fixture
    def mock_problem_service(self):
        """モック問題サービス"""
        return Mock()

    @pytest.fixture
    def usecase(self, mock_problem_service):
        """テスト対象のユースケース"""
        return ReadProblemByIdUseCase(mock_problem_service)

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
        mock_entity.content_markdown = "# テスト問題\n\n問題の内容です。"

        return mock_entity

    @pytest.mark.asyncio
    async def test_execute_success(self, usecase, mock_problem_service, mock_problem_entity):
        """正常な問題取得のテスト"""
        # Arrange
        problem_id = mock_problem_entity.id
        command = ReadProblemByIdCommand(problem_id=problem_id)
        mock_problem_service.get_problem_by_id = AsyncMock(return_value=mock_problem_entity)

        # Act
        result = await usecase.execute(command)

        # Assert
        assert isinstance(result, ReadProblemByIdResult)
        assert result.problem == mock_problem_entity

        # サービスが正しい引数で呼ばれたかを確認
        mock_problem_service.get_problem_by_id.assert_called_once_with(problem_id)

    @pytest.mark.asyncio
    async def test_execute_problem_not_found(self, usecase, mock_problem_service):
        """問題が見つからない場合のテスト"""
        # Arrange
        problem_id = uuid4()
        command = ReadProblemByIdCommand(problem_id=problem_id)
        mock_problem_service.get_problem_by_id = AsyncMock(return_value=None)

        # Act
        result = await usecase.execute(command)

        # Assert
        assert isinstance(result, ReadProblemByIdResult)
        assert result.problem is None

        # サービスが正しい引数で呼ばれたかを確認
        mock_problem_service.get_problem_by_id.assert_called_once_with(problem_id)

    @pytest.mark.asyncio
    async def test_execute_service_exception_raises_execution_error(self, usecase, mock_problem_service):
        """サービスで例外が発生した場合の実行エラーテスト"""
        # Arrange
        problem_id = uuid4()
        command = ReadProblemByIdCommand(problem_id=problem_id)
        mock_problem_service.get_problem_by_id = AsyncMock(side_effect=Exception("Database error"))

        # Act & Assert
        with pytest.raises(UseCaseExecutionError, match="Failed to read problem: Database error"):
            await usecase.execute(command)


class TestReadProblemsByBookIdUseCase:
    """ReadProblemsByBookIdUseCaseのテストクラス"""

    @pytest.fixture
    def mock_problem_service(self):
        """モック問題サービス"""
        return Mock()

    @pytest.fixture
    def usecase(self, mock_problem_service):
        """テスト対象のユースケース"""
        return ReadProblemsByBookIdUseCase(mock_problem_service)

    @pytest.fixture
    def mock_problem_entities(self):
        """モック問題エンティティのリスト"""
        entities = []
        book_id = uuid4()
        for i in range(3):
            mock_entity = Mock(spec=ProblemEntity)
            mock_entity.id = uuid4()
            mock_entity.book_id = book_id
            mock_entity.title = f"テスト問題{i + 1}"
            mock_entity.description = f"テスト用の問題{i + 1}です"
            mock_entity.tags = [f"tag{i + 1}"]
            entities.append(mock_entity)

        return entities

    @pytest.mark.asyncio
    async def test_execute_success(self, usecase, mock_problem_service, mock_problem_entities):
        """正常な問題集別問題取得のテスト"""
        # Arrange
        book_id = mock_problem_entities[0].book_id
        command = ReadProblemsByBookIdCommand(book_id=book_id)
        mock_problem_service.get_problems_by_book_id = AsyncMock(return_value=mock_problem_entities)

        # Act
        result = await usecase.execute(command)

        # Assert
        assert isinstance(result, ReadProblemsByBookIdResult)
        assert result.problems == mock_problem_entities
        assert len(result.problems) == 3

        # サービスが正しい引数で呼ばれたかを確認
        mock_problem_service.get_problems_by_book_id.assert_called_once_with(book_id)

    @pytest.mark.asyncio
    async def test_execute_empty_result(self, usecase, mock_problem_service):
        """問題集に問題が0件の場合のテスト"""
        # Arrange
        book_id = uuid4()
        command = ReadProblemsByBookIdCommand(book_id=book_id)
        mock_problem_service.get_problems_by_book_id = AsyncMock(return_value=[])

        # Act
        result = await usecase.execute(command)

        # Assert
        assert isinstance(result, ReadProblemsByBookIdResult)
        assert result.problems == []
        assert len(result.problems) == 0

        # サービスが正しい引数で呼ばれたかを確認
        mock_problem_service.get_problems_by_book_id.assert_called_once_with(book_id)

    @pytest.mark.asyncio
    async def test_execute_service_exception_raises_execution_error(self, usecase, mock_problem_service):
        """サービスで例外が発生した場合の実行エラーテスト"""
        # Arrange
        book_id = uuid4()
        command = ReadProblemsByBookIdCommand(book_id=book_id)
        mock_problem_service.get_problems_by_book_id = AsyncMock(side_effect=Exception("Database error"))

        # Act & Assert
        with pytest.raises(
            UseCaseExecutionError, match="Failed to read problems by book ID: Database error"
        ):
            await usecase.execute(command)


class TestReadPublishedProblemsUseCase:
    """ReadPublishedProblemsUseCaseのテストクラス"""

    @pytest.fixture
    def mock_problem_service(self):
        """モック問題サービス"""
        return Mock()

    @pytest.fixture
    def usecase(self, mock_problem_service):
        """テスト対象のユースケース"""
        return ReadPublishedProblemsUseCase(mock_problem_service)

    @pytest.fixture
    def mock_problem_entities(self):
        """モック問題エンティティのリスト"""
        entities = []
        for i in range(5):
            mock_entity = Mock(spec=ProblemEntity)
            mock_entity.id = uuid4()
            mock_entity.book_id = uuid4()
            mock_entity.title = f"公開問題{i + 1}"
            mock_entity.description = f"公開された問題{i + 1}です"
            mock_entity.tags = ["published", f"tag{i + 1}"]
            entities.append(mock_entity)

        return entities

    @pytest.mark.asyncio
    async def test_execute_success(self, usecase, mock_problem_service, mock_problem_entities):
        """正常な公開問題取得のテスト"""
        # Arrange
        command = ReadPublishedProblemsCommand()
        mock_problem_service.get_published_problems = AsyncMock(return_value=mock_problem_entities)

        # Act
        result = await usecase.execute(command)

        # Assert
        assert isinstance(result, ReadPublishedProblemsResult)
        assert result.problems == mock_problem_entities
        assert len(result.problems) == 5

        # サービスが呼ばれたかを確認
        mock_problem_service.get_published_problems.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_empty_result(self, usecase, mock_problem_service):
        """公開問題が0件の場合のテスト"""
        # Arrange
        command = ReadPublishedProblemsCommand()
        mock_problem_service.get_published_problems = AsyncMock(return_value=[])

        # Act
        result = await usecase.execute(command)

        # Assert
        assert isinstance(result, ReadPublishedProblemsResult)
        assert result.problems == []
        assert len(result.problems) == 0

        # サービスが呼ばれたかを確認
        mock_problem_service.get_published_problems.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_service_exception_raises_execution_error(self, usecase, mock_problem_service):
        """サービスで例外が発生した場合の実行エラーテスト"""
        # Arrange
        command = ReadPublishedProblemsCommand()
        mock_problem_service.get_published_problems = AsyncMock(side_effect=Exception("Database error"))

        # Act & Assert
        with pytest.raises(
            UseCaseExecutionError, match="Failed to read published problems: Database error"
        ):
            await usecase.execute(command)
