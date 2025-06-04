"""
Core controllers unit tests
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from fastapi import HTTPException

from src.core.app.controllers import (
    BookController,
    ProblemController,
    JudgeCaseController,
    UserProblemStatusController,
)
from src.core.app.services import (
    BookApplicationService,
    ProblemApplicationService,
    JudgeCaseApplicationService,
    UserProblemStatusApplicationService,
)
from src.core.domain.models import Book, Problem, JudgeCase, UserProblemStatus
from src.const import DifficultyLevel, ProblemStatus, JudgeCaseType


@pytest.mark.core
class TestBookController:
    """BookControllerのテスト"""

    @pytest.fixture
    def mock_book_service(self):
        """モックBookApplicationServiceを作成"""
        service = AsyncMock(spec=BookApplicationService)
        return service

    @pytest.fixture
    def book_controller(self, mock_book_service):
        """BookControllerのインスタンスを作成"""
        return BookController(book_service=mock_book_service)

    @pytest.mark.asyncio
    async def test_get_published_books_success(
        self, book_controller, mock_book_service
    ):
        """公開済み問題集取得成功のテスト"""
        # モックの設定
        books = [
            Book(title="Book 1", author_id=uuid4(), is_published=True),
            Book(title="Book 2", author_id=uuid4(), is_published=True),
        ]
        mock_book_service.get_published_books.return_value = books

        # テスト実行
        result = await book_controller.get_published_books()

        # アサート
        assert len(result) == 2
        assert all(book.is_published for book in result)
        mock_book_service.get_published_books.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_published_books_empty(self, book_controller, mock_book_service):
        """公開済み問題集なしのテスト"""
        # モックの設定
        mock_book_service.get_published_books.return_value = []

        # テスト実行
        result = await book_controller.get_published_books()

        # アサート
        assert len(result) == 0
        mock_book_service.get_published_books.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_book_by_id_success(self, book_controller, mock_book_service):
        """ID指定問題集取得成功のテスト"""
        book_id = uuid4()
        book = Book(id=book_id, title="Test Book", author_id=uuid4())

        # モックの設定
        mock_book_service.get_book_by_id.return_value = book

        # テスト実行
        result = await book_controller.get_book_by_id(book_id)

        # アサート
        assert result.id == book_id
        assert result.title == "Test Book"
        mock_book_service.get_book_by_id.assert_called_once_with(book_id)

    @pytest.mark.asyncio
    async def test_get_book_by_id_not_found(self, book_controller, mock_book_service):
        """ID指定問題集取得（存在しない）のテスト"""
        book_id = uuid4()

        # モックの設定
        mock_book_service.get_book_by_id.return_value = None

        # テスト実行とアサート
        with pytest.raises(HTTPException) as exc_info:
            await book_controller.get_book_by_id(book_id)

        assert exc_info.value.status_code == 404
        assert "Book not found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_book_by_id_service_error(
        self, book_controller, mock_book_service
    ):
        """ID指定問題集取得サービスエラーのテスト"""
        book_id = uuid4()

        # モックの設定
        mock_book_service.get_book_by_id.side_effect = Exception("Database error")

        # テスト実行とアサート
        with pytest.raises(HTTPException) as exc_info:
            await book_controller.get_book_by_id(book_id)

        assert exc_info.value.status_code == 500


@pytest.mark.core
class TestProblemController:
    """ProblemControllerのテスト"""

    @pytest.fixture
    def mock_problem_service(self):
        """モックProblemApplicationServiceを作成"""
        service = AsyncMock(spec=ProblemApplicationService)
        return service

    @pytest.fixture
    def problem_controller(self, mock_problem_service):
        """ProblemControllerのインスタンスを作成"""
        return ProblemController(problem_service=mock_problem_service)

    @pytest.mark.asyncio
    async def test_get_published_problems_success(
        self, problem_controller, mock_problem_service
    ):
        """公開済み問題取得成功のテスト"""
        # モックの設定
        problems = [
            Problem(
                title="Problem 1",
                description="Description 1",
                author_id=uuid4(),
                status=ProblemStatus.PUBLISHED,
            ),
            Problem(
                title="Problem 2",
                description="Description 2",
                author_id=uuid4(),
                status=ProblemStatus.PUBLISHED,
            ),
        ]
        mock_problem_service.get_published_problems.return_value = problems

        # テスト実行
        result = await problem_controller.get_published_problems()

        # アサート
        assert len(result) == 2
        assert all(problem.status == ProblemStatus.PUBLISHED for problem in result)
        mock_problem_service.get_published_problems.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_problem_by_id_success(
        self, problem_controller, mock_problem_service
    ):
        """ID指定問題取得成功のテスト"""
        problem_id = uuid4()
        problem = Problem(
            id=problem_id,
            title="Test Problem",
            description="Test description",
            author_id=uuid4(),
        )

        # モックの設定
        mock_problem_service.get_problem_by_id.return_value = problem

        # テスト実行
        result = await problem_controller.get_problem_by_id(problem_id)

        # アサート
        assert result.id == problem_id
        assert result.title == "Test Problem"
        mock_problem_service.get_problem_by_id.assert_called_once_with(problem_id)

    @pytest.mark.asyncio
    async def test_get_problem_by_id_not_found(
        self, problem_controller, mock_problem_service
    ):
        """ID指定問題取得（存在しない）のテスト"""
        problem_id = uuid4()

        # モックの設定
        mock_problem_service.get_problem_by_id.return_value = None

        # テスト実行とアサート
        with pytest.raises(HTTPException) as exc_info:
            await problem_controller.get_problem_by_id(problem_id)

        assert exc_info.value.status_code == 404
        assert "Problem not found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_problems_by_book_id_success(
        self, problem_controller, mock_problem_service
    ):
        """問題集ID指定問題取得成功のテスト"""
        book_id = uuid4()
        problems = [
            Problem(
                title="Problem 1",
                description="Description 1",
                author_id=uuid4(),
                book_id=book_id,
            ),
            Problem(
                title="Problem 2",
                description="Description 2",
                author_id=uuid4(),
                book_id=book_id,
            ),
        ]

        # モックの設定
        mock_problem_service.get_problems_by_book_id.return_value = problems

        # テスト実行
        result = await problem_controller.get_problems_by_book_id(book_id)

        # アサート
        assert len(result) == 2
        assert all(problem.book_id == book_id for problem in result)
        mock_problem_service.get_problems_by_book_id.assert_called_once_with(book_id)

    @pytest.mark.asyncio
    async def test_get_problems_by_difficulty_success(
        self, problem_controller, mock_problem_service
    ):
        """難易度指定問題取得成功のテスト"""
        problems = [
            Problem(
                title="Easy Problem",
                description="Easy description",
                author_id=uuid4(),
                difficulty=DifficultyLevel.EASY,
            )
        ]

        # モックの設定
        mock_problem_service.get_problems_by_difficulty.return_value = problems

        # テスト実行
        result = await problem_controller.get_problems_by_difficulty("easy")

        # アサート
        assert len(result) == 1
        assert result[0].difficulty == DifficultyLevel.EASY
        mock_problem_service.get_problems_by_difficulty.assert_called_once_with(
            DifficultyLevel.EASY
        )

    @pytest.mark.asyncio
    async def test_get_problems_by_difficulty_invalid(
        self, problem_controller, mock_problem_service
    ):
        """無効な難易度指定のテスト"""
        # テスト実行とアサート
        with pytest.raises(HTTPException) as exc_info:
            await problem_controller.get_problems_by_difficulty("invalid")

        assert exc_info.value.status_code == 400
        assert "Invalid difficulty" in str(exc_info.value.detail)


@pytest.mark.core
class TestJudgeCaseController:
    """JudgeCaseControllerのテスト"""

    @pytest.fixture
    def mock_judge_case_service(self):
        """モックJudgeCaseApplicationServiceを作成"""
        service = AsyncMock(spec=JudgeCaseApplicationService)
        return service

    @pytest.fixture
    def judge_case_controller(self, mock_judge_case_service):
        """JudgeCaseControllerのインスタンスを作成"""
        return JudgeCaseController(judge_case_service=mock_judge_case_service)

    @pytest.mark.asyncio
    async def test_get_judge_cases_by_problem_id_success(
        self, judge_case_controller, mock_judge_case_service
    ):
        """問題ID指定ジャッジケース取得成功のテスト"""
        problem_id = uuid4()
        judge_cases = [
            JudgeCase(
                problem_id=problem_id,
                name="Sample 1",
                input_data="1 2",
                expected_output="3",
                case_type=JudgeCaseType.SAMPLE,
            ),
            JudgeCase(
                problem_id=problem_id,
                name="Hidden 1",
                input_data="5 10",
                expected_output="15",
                case_type=JudgeCaseType.HIDDEN,
            ),
        ]

        # モックの設定
        mock_judge_case_service.get_judge_cases_by_problem_id.return_value = judge_cases

        # テスト実行
        result = await judge_case_controller.get_judge_cases_by_problem_id(problem_id)

        # アサート
        assert len(result) == 2
        assert all(case.problem_id == problem_id for case in result)
        mock_judge_case_service.get_judge_cases_by_problem_id.assert_called_once_with(
            problem_id
        )

    @pytest.mark.asyncio
    async def test_get_sample_cases_only_success(
        self, judge_case_controller, mock_judge_case_service
    ):
        """サンプルケースのみ取得成功のテスト"""
        problem_id = uuid4()
        sample_cases = [
            JudgeCase(
                problem_id=problem_id,
                name="Sample 1",
                input_data="1 2",
                expected_output="3",
                case_type=JudgeCaseType.SAMPLE,
            )
        ]

        # モックの設定
        mock_judge_case_service.get_sample_cases_by_problem_id.return_value = (
            sample_cases
        )

        # テスト実行
        result = await judge_case_controller.get_sample_cases_by_problem_id(problem_id)

        # アサート
        assert len(result) == 1
        assert result[0].case_type == JudgeCaseType.SAMPLE
        mock_judge_case_service.get_sample_cases_by_problem_id.assert_called_once_with(
            problem_id
        )

    @pytest.mark.asyncio
    async def test_get_judge_case_by_id_success(
        self, judge_case_controller, mock_judge_case_service
    ):
        """ID指定ジャッジケース取得成功のテスト"""
        case_id = uuid4()
        judge_case = JudgeCase(
            id=case_id,
            problem_id=uuid4(),
            name="Test Case",
            input_data="test input",
            expected_output="test output",
        )

        # モックの設定
        mock_judge_case_service.get_judge_case_by_id.return_value = judge_case

        # テスト実行
        result = await judge_case_controller.get_judge_case_by_id(case_id)

        # アサート
        assert result.id == case_id
        assert result.name == "Test Case"
        mock_judge_case_service.get_judge_case_by_id.assert_called_once_with(case_id)

    @pytest.mark.asyncio
    async def test_get_judge_case_by_id_not_found(
        self, judge_case_controller, mock_judge_case_service
    ):
        """ID指定ジャッジケース取得（存在しない）のテスト"""
        case_id = uuid4()

        # モックの設定
        mock_judge_case_service.get_judge_case_by_id.return_value = None

        # テスト実行とアサート
        with pytest.raises(HTTPException) as exc_info:
            await judge_case_controller.get_judge_case_by_id(case_id)

        assert exc_info.value.status_code == 404
        assert "Judge case not found" in str(exc_info.value.detail)


@pytest.mark.core
class TestUserProblemStatusController:
    """UserProblemStatusControllerのテスト"""

    @pytest.fixture
    def mock_status_service(self):
        """モックUserProblemStatusApplicationServiceを作成"""
        service = AsyncMock(spec=UserProblemStatusApplicationService)
        return service

    @pytest.fixture
    def status_controller(self, mock_status_service):
        """UserProblemStatusControllerのインスタンスを作成"""
        return UserProblemStatusController(status_service=mock_status_service)

    @pytest.mark.asyncio
    async def test_get_user_problem_status_success(
        self, status_controller, mock_status_service
    ):
        """ユーザー問題状態取得成功のテスト"""
        user_id = uuid4()
        problem_id = uuid4()
        status = UserProblemStatus(
            user_id=user_id,
            problem_id=problem_id,
            is_solved=True,
            best_submission_time=1000,
        )

        # モックの設定
        mock_status_service.get_user_problem_status.return_value = status

        # テスト実行
        result = await status_controller.get_user_problem_status(user_id, problem_id)

        # アサート
        assert result.user_id == user_id
        assert result.problem_id == problem_id
        assert result.is_solved is True
        mock_status_service.get_user_problem_status.assert_called_once_with(
            user_id, problem_id
        )

    @pytest.mark.asyncio
    async def test_get_user_problem_status_not_found(
        self, status_controller, mock_status_service
    ):
        """ユーザー問題状態取得（存在しない）のテスト"""
        user_id = uuid4()
        problem_id = uuid4()

        # モックの設定
        mock_status_service.get_user_problem_status.return_value = None

        # テスト実行とアサート
        with pytest.raises(HTTPException) as exc_info:
            await status_controller.get_user_problem_status(user_id, problem_id)

        assert exc_info.value.status_code == 404
        assert "User problem status not found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_user_solved_problems_success(
        self, status_controller, mock_status_service
    ):
        """ユーザー解決済み問題取得成功のテスト"""
        user_id = uuid4()
        solved_statuses = [
            UserProblemStatus(
                user_id=user_id,
                problem_id=uuid4(),
                is_solved=True,
                best_submission_time=1000,
            ),
            UserProblemStatus(
                user_id=user_id,
                problem_id=uuid4(),
                is_solved=True,
                best_submission_time=1500,
            ),
        ]

        # モックの設定
        mock_status_service.get_user_solved_problems.return_value = solved_statuses

        # テスト実行
        result = await status_controller.get_user_solved_problems(user_id)

        # アサート
        assert len(result) == 2
        assert all(status.is_solved for status in result)
        assert all(status.user_id == user_id for status in result)
        mock_status_service.get_user_solved_problems.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_get_user_progress_stats_success(
        self, status_controller, mock_status_service
    ):
        """ユーザー進捗統計取得成功のテスト"""
        user_id = uuid4()
        stats = {
            "total_attempted": 10,
            "total_solved": 7,
            "easy_solved": 3,
            "medium_solved": 3,
            "hard_solved": 1,
        }

        # モックの設定
        mock_status_service.get_user_progress_stats.return_value = stats

        # テスト実行
        result = await status_controller.get_user_progress_stats(user_id)

        # アサート
        assert result["total_attempted"] == 10
        assert result["total_solved"] == 7
        assert result["easy_solved"] == 3
        mock_status_service.get_user_progress_stats.assert_called_once_with(user_id)
