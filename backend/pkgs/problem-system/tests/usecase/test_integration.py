"""
Integration Tests for Problem System
問題システムの統合テスト

Author: Judge System Team
Date: 2025-06-30
"""

from uuid import uuid4

import pytest

from ppprob.usecase.create_book_usecase import CreateBookCommand, CreateBookUseCase
from ppprob.usecase.create_problem_usecase import CreateProblemCommand, CreateProblemUseCase
from ppprob.usecase.read_book_usecase import ReadBookByIdCommand, ReadBookByIdUseCase
from ppprob.usecase.read_problem_usecase import ReadProblemByIdCommand, ReadProblemByIdUseCase


class TestProblemSystemIntegration:
    """問題システム統合テストクラス"""

    @pytest.mark.asyncio
    async def test_book_creation_and_retrieval_flow(self, mock_book_service):
        """問題集作成から取得までの一連のフロー"""
        # Arrange
        author_id = uuid4()
        title = "統合テスト問題集"
        description = "統合テスト用の問題集です"

        # 実際のエンティティの作成
        from unittest.mock import AsyncMock
        from ppprob.domain.entities.book import BookEntity
        from datetime import datetime

        entity_id = uuid4()
        mock_entity = BookEntity(
            id=entity_id,
            title=title,
            description=description,
            author_id=author_id,
            published_at=None,
            archived_at=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # サービスのモック設定 (AsyncMockを使用)
        mock_book_service.create_book = AsyncMock(return_value=mock_entity)
        mock_book_service.get_book_by_id = AsyncMock(return_value=mock_entity)

        # Act 1: 問題集作成
        create_usecase = CreateBookUseCase(mock_book_service)
        create_command = CreateBookCommand(
            title=title,
            description=description,
            author_id=author_id,
        )
        create_result = await create_usecase.execute(create_command)

        # Assert 1: 作成結果の検証
        assert create_result.book_id == mock_entity.id
        assert create_result.title == title
        assert create_result.description == description

        # Act 2: 問題集取得
        read_usecase = ReadBookByIdUseCase(mock_book_service)
        read_command = ReadBookByIdCommand(book_id=create_result.book_id)
        read_result = await read_usecase.execute(read_command)

        # Assert 2: 取得結果の検証
        assert read_result.book is not None
        assert read_result.book.id == create_result.book_id
        assert read_result.book.title == title

    @pytest.mark.asyncio
    async def test_problem_creation_and_retrieval_flow(self, mock_problem_service):
        """問題作成から取得までの一連のフロー"""
        # Arrange
        from unittest.mock import AsyncMock, Mock

        book_id = uuid4()
        title = "統合テスト問題"
        description = "統合テスト用の問題です"
        tags = ["integration", "test"]
        content_markdown = "# 統合テスト問題\n\n統合テストの内容です。\n\n```python\nprint('test')\n```"

        # 実際のエンティティの作成
        from ppprob.domain.entities.problem import ProblemEntity
        from ppprob.domain.enums import DifficultyLevel
        from datetime import datetime

        entity_id = uuid4()
        mock_entity = ProblemEntity(
            id=entity_id,
            book_id=book_id,
            title=title,
            description=description,
            tags=tags,
            content_markdown=content_markdown,
            difficulty=DifficultyLevel.BEGINNER,
            author_id=uuid4(),
            published_at=None,
            archived_at=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            content_created_at=datetime.now(),
            content_updated_at=datetime.now(),
            language="ja"
        )

        # サービスのモック設定 (AsyncMockを使用)
        mock_problem_service.create_problem = AsyncMock(return_value=mock_entity)
        mock_problem_service.get_problem_by_id = AsyncMock(return_value=mock_entity)

        # Act 1: 問題作成
        create_usecase = CreateProblemUseCase(mock_problem_service)
        create_command = CreateProblemCommand(
            book_id=book_id,
            title=title,
            description=description,
            tags=tags,
            content_markdown=content_markdown,
        )
        create_result = await create_usecase.execute(create_command)

        # Assert 1: 作成結果の検証
        assert create_result.problem_id == mock_entity.id
        assert create_result.book_id == book_id
        assert create_result.title == title
        assert create_result.tags == tags

        # Act 2: 問題取得
        read_usecase = ReadProblemByIdUseCase(mock_problem_service)
        read_command = ReadProblemByIdCommand(problem_id=create_result.problem_id)
        read_result = await read_usecase.execute(read_command)

        # Assert 2: 取得結果の検証
        assert read_result.problem is not None
        assert read_result.problem.id == create_result.problem_id
        assert read_result.problem.title == title
        assert read_result.problem.tags == tags

    @pytest.mark.asyncio
    async def test_complete_workflow_book_to_problems(self, mock_book_service, mock_problem_service):
        """問題集作成から問題作成までの完全なワークフロー"""
        # Arrange
        from unittest.mock import AsyncMock, Mock

        author_id = uuid4()
        book_title = "ワークフロー問題集"
        problem_count = 3

        # 問題集実際のエンティティ
        from ppprob.domain.entities.book import BookEntity
        from datetime import datetime

        book_id = uuid4()
        mock_book = BookEntity(
            id=book_id,
            title=book_title,
            description="ワークフロー用の問題集",
            author_id=author_id,
            published_at=None,
            archived_at=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # 問題実際のエンティティのリスト
        from ppprob.domain.entities.problem import ProblemEntity
        from ppprob.domain.enums import DifficultyLevel
        
        mock_problems = []
        for i in range(problem_count):
            problem_id = uuid4()
            mock_problem = ProblemEntity(
                id=problem_id,
                book_id=mock_book.id,
                title=f"ワークフロー問題{i + 1}",
                description=f"ワークフロー用の問題{i + 1}",
                tags=["workflow", f"problem{i + 1}"],
                content_markdown=f"# ワークフロー問題{i + 1}\n\n内容",
                difficulty=DifficultyLevel.BEGINNER,
                author_id=author_id,
                published_at=None,
                archived_at=None,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                content_created_at=datetime.now(),
                content_updated_at=datetime.now(),
                language="ja"
            )
            mock_problems.append(mock_problem)

        # サービスのモック設定 (AsyncMockを使用)
        mock_book_service.create_book = AsyncMock(return_value=mock_book)
        mock_book_service.get_book_by_id = AsyncMock(return_value=mock_book)

        # Act 1: 問題集作成
        book_create_usecase = CreateBookUseCase(mock_book_service)
        book_create_command = CreateBookCommand(
            title=book_title,
            description="ワークフロー用の問題集",
            author_id=author_id,
        )
        book_result = await book_create_usecase.execute(book_create_command)

        # Assert 1: 問題集作成の検証
        assert book_result.book_id == mock_book.id
        assert book_result.title == book_title

        # Act 2: 複数の問題作成
        problem_create_usecase = CreateProblemUseCase(mock_problem_service)
        created_problems = []

        for i, mock_problem in enumerate(mock_problems):
            # 各問題作成時のモック設定 (AsyncMockを使用)
            mock_problem_service.create_problem = AsyncMock(return_value=mock_problem)

            problem_command = CreateProblemCommand(
                book_id=book_result.book_id,
                title=f"ワークフロー問題{i + 1}",
                description=f"ワークフロー用の問題{i + 1}",
                tags=["workflow", f"problem{i + 1}"],
                content_markdown=f"# ワークフロー問題{i + 1}\n\n内容\n\n```python\nprint('problem{i + 1}')\n```",
            )
            problem_result = await problem_create_usecase.execute(problem_command)
            created_problems.append(problem_result)

        # Assert 2: 全問題作成の検証
        assert len(created_problems) == problem_count
        for i, problem_result in enumerate(created_problems):
            assert problem_result.book_id == book_result.book_id
            assert problem_result.title == f"ワークフロー問題{i + 1}"

    @pytest.mark.asyncio
    async def test_error_handling_workflow(self, mock_book_service):
        """エラーハンドリングのワークフロー"""
        # Arrange
        from unittest.mock import AsyncMock

        from pydddi import UseCaseCommandError

        # サービスで例外が発生するように設定
        mock_book_service.create_book = AsyncMock(side_effect=Exception("Database connection failed"))

        # Act & Assert
        create_usecase = CreateBookUseCase(mock_book_service)
        invalid_command = CreateBookCommand(
            title="",  # 無効なタイトル
            description="説明",
            author_id=uuid4(),
        )

        # 無効なコマンドでのエラー
        with pytest.raises(UseCaseCommandError):
            await create_usecase.execute(invalid_command)

        # 有効なコマンドだがサービスエラー
        valid_command = CreateBookCommand(
            title="有効なタイトル",
            description="説明",
            author_id=uuid4(),
        )

        from pydddi import UseCaseExecutionError

        with pytest.raises(UseCaseExecutionError):
            await create_usecase.execute(valid_command)
