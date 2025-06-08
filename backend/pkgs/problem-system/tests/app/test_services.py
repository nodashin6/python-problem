"""
Application services unit tests
"""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.const import DifficultyLevel, JudgeCaseType, ProblemStatus
from src.core.app.services import (
    BookApplicationService,
    JudgeCaseApplicationService,
    ProblemApplicationService,
    UserProblemStatusApplicationService,
)
from src.core.domain.models import Book, JudgeCase, Problem, UserProblemStatus
from src.core.infra.repositories.interfaces import (
    BookRepositoryInterface,
    JudgeCaseRepositoryInterface,
    ProblemRepositoryInterface,
    UserProblemStatusRepositoryInterface,
)


@pytest.mark.core
class TestBookApplicationService:
    """BookApplicationServiceのテスト"""

    @pytest.fixture
    def mock_book_repo(self):
        """モックBookRepositoryInterfaceを作成"""
        repo = AsyncMock(spec=BookRepositoryInterface)
        return repo

    @pytest.fixture
    def book_app_service(self, mock_book_repo):
        """BookApplicationServiceのインスタンスを作成"""
        return BookApplicationService(book_repository=mock_book_repo)

    @pytest.mark.asyncio
    async def test_get_published_books_success(self, book_app_service, mock_book_repo):
        """公開済み問題集取得成功のテスト"""
        # モックの設定
        books = [
            Book(title="Book 1", author_id=uuid4(), is_published=True),
            Book(title="Book 2", author_id=uuid4(), is_published=True),
        ]
        mock_book_repo.find_published_books.return_value = books

        # テスト実行
        result = await book_app_service.get_published_books()

        # アサート
        assert len(result) == 2
        assert all(book.is_published for book in result)
        mock_book_repo.find_published_books.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_published_books_empty(self, book_app_service, mock_book_repo):
        """公開済み問題集なしのテスト"""
        # モックの設定
        mock_book_repo.find_published_books.return_value = []

        # テスト実行
        result = await book_app_service.get_published_books()

        # アサート
        assert len(result) == 0
        mock_book_repo.find_published_books.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_book_by_id_success(self, book_app_service, mock_book_repo):
        """ID指定問題集取得成功のテスト"""
        book_id = uuid4()
        book = Book(id=book_id, title="Test Book", author_id=uuid4())

        # モックの設定
        mock_book_repo.get.return_value = book

        # テスト実行
        result = await book_app_service.get_book_by_id(book_id)

        # アサート
        assert result.id == book_id
        assert result.title == "Test Book"
        mock_book_repo.get.assert_called_once_with(book_id)

    @pytest.mark.asyncio
    async def test_get_book_by_id_not_found(self, book_app_service, mock_book_repo):
        """ID指定問題集取得 (存在しない) のテスト"""
        book_id = uuid4()

        # モックの設定
        mock_book_repo.get.return_value = None

        # テスト実行
        result = await book_app_service.get_book_by_id(book_id)

        # アサート
        assert result is None
        mock_book_repo.get.assert_called_once_with(book_id)


@pytest.mark.core
class TestProblemApplicationService:
    """ProblemApplicationServiceのテスト"""

    @pytest.fixture
    def mock_problem_repo(self):
        """モックProblemRepositoryInterfaceを作成"""
        repo = AsyncMock(spec=ProblemRepositoryInterface)
        return repo

    @pytest.fixture
    def problem_app_service(self, mock_problem_repo):
        """ProblemApplicationServiceのインスタンスを作成"""
        return ProblemApplicationService(problem_repository=mock_problem_repo)

    @pytest.mark.asyncio
    async def test_get_published_problems_success(self, problem_app_service, mock_problem_repo):
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
        mock_problem_repo.find_published_problems.return_value = problems

        # テスト実行
        result = await problem_app_service.get_published_problems()

        # アサート
        assert len(result) == 2
        assert all(problem.status == ProblemStatus.PUBLISHED for problem in result)
        mock_problem_repo.find_published_problems.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_problem_by_id_success(self, problem_app_service, mock_problem_repo):
        """ID指定問題取得成功のテスト"""
        problem_id = uuid4()
        problem = Problem(
            id=problem_id,
            title="Test Problem",
            description="Test description",
            author_id=uuid4(),
        )

        # モックの設定
        mock_problem_repo.get.return_value = problem

        # テスト実行
        result = await problem_app_service.get_problem_by_id(problem_id)

        # アサート
        assert result.id == problem_id
        assert result.title == "Test Problem"
        mock_problem_repo.get.assert_called_once_with(problem_id)

    @pytest.mark.asyncio
    async def test_get_problems_by_book_id(self, problem_app_service, mock_problem_repo):
        """問題集ID指定問題取得のテスト"""
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
        mock_problem_repo.find_by_book_id.return_value = problems

        # テスト実行
        result = await problem_app_service.get_problems_by_book_id(book_id)

        # アサート
        assert len(result) == 2
        assert all(problem.book_id == book_id for problem in result)
        mock_problem_repo.find_by_book_id.assert_called_once_with(book_id)

    @pytest.mark.asyncio
    async def test_get_problems_by_difficulty(self, problem_app_service, mock_problem_repo):
        """難易度指定問題取得のテスト"""
        problems = [
            Problem(
                title="Easy Problem",
                description="Easy description",
                author_id=uuid4(),
                difficulty=DifficultyLevel.EASY,
            )
        ]

        # モックの設定
        mock_problem_repo.find_by_difficulty.return_value = problems

        # テスト実行
        result = await problem_app_service.get_problems_by_difficulty(DifficultyLevel.EASY)

        # アサート
        assert len(result) == 1
        assert result[0].difficulty == DifficultyLevel.EASY
        mock_problem_repo.find_by_difficulty.assert_called_once_with(DifficultyLevel.EASY)


@pytest.mark.core
class TestJudgeCaseApplicationService:
    """JudgeCaseApplicationServiceのテスト"""

    @pytest.fixture
    def mock_judge_case_repo(self):
        """モックJudgeCaseRepositoryInterfaceを作成"""
        repo = AsyncMock(spec=JudgeCaseRepositoryInterface)
        return repo

    @pytest.fixture
    def judge_case_app_service(self, mock_judge_case_repo):
        """JudgeCaseApplicationServiceのインスタンスを作成"""
        return JudgeCaseApplicationService(judge_case_repository=mock_judge_case_repo)

    @pytest.mark.asyncio
    async def test_get_judge_cases_by_problem_id(self, judge_case_app_service, mock_judge_case_repo):
        """問題ID指定ジャッジケース取得のテスト"""
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
        mock_judge_case_repo.find_by_problem_id.return_value = judge_cases

        # テスト実行
        result = await judge_case_app_service.get_judge_cases_by_problem_id(problem_id)

        # アサート
        assert len(result) == 2
        assert all(case.problem_id == problem_id for case in result)
        mock_judge_case_repo.find_by_problem_id.assert_called_once_with(problem_id)

    @pytest.mark.asyncio
    async def test_get_sample_cases_only(self, judge_case_app_service, mock_judge_case_repo):
        """サンプルケースのみ取得のテスト"""
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
        mock_judge_case_repo.find_sample_cases_by_problem_id.return_value = sample_cases

        # テスト実行
        result = await judge_case_app_service.get_sample_cases_by_problem_id(problem_id)

        # アサート
        assert len(result) == 1
        assert result[0].case_type == JudgeCaseType.SAMPLE
        mock_judge_case_repo.find_sample_cases_by_problem_id.assert_called_once_with(problem_id)

    @pytest.mark.asyncio
    async def test_get_judge_case_by_id(self, judge_case_app_service, mock_judge_case_repo):
        """ID指定ジャッジケース取得のテスト"""
        case_id = uuid4()
        judge_case = JudgeCase(
            id=case_id,
            problem_id=uuid4(),
            name="Test Case",
            input_data="test input",
            expected_output="test output",
        )

        # モックの設定
        mock_judge_case_repo.get.return_value = judge_case

        # テスト実行
        result = await judge_case_app_service.get_judge_case_by_id(case_id)

        # アサート
        assert result.id == case_id
        assert result.name == "Test Case"
        mock_judge_case_repo.get.assert_called_once_with(case_id)


@pytest.mark.core
class TestUserProblemStatusApplicationService:
    """UserProblemStatusApplicationServiceのテスト"""

    @pytest.fixture
    def mock_status_repo(self):
        """モックUserProblemStatusRepositoryInterfaceを作成"""
        repo = AsyncMock(spec=UserProblemStatusRepositoryInterface)
        return repo

    @pytest.fixture
    def status_app_service(self, mock_status_repo):
        """UserProblemStatusApplicationServiceのインスタンスを作成"""
        return UserProblemStatusApplicationService(status_repository=mock_status_repo)

    @pytest.mark.asyncio
    async def test_get_user_problem_status(self, status_app_service, mock_status_repo):
        """ユーザー問題状態取得のテスト"""
        user_id = uuid4()
        problem_id = uuid4()
        status = UserProblemStatus(
            user_id=user_id,
            problem_id=problem_id,
            is_solved=True,
            best_submission_time=1000,
        )

        # モックの設定
        mock_status_repo.find_by_user_and_problem.return_value = status

        # テスト実行
        result = await status_app_service.get_user_problem_status(user_id, problem_id)

        # アサート
        assert result.user_id == user_id
        assert result.problem_id == problem_id
        assert result.is_solved is True
        mock_status_repo.find_by_user_and_problem.assert_called_once_with(user_id, problem_id)

    @pytest.mark.asyncio
    async def test_get_user_solved_problems(self, status_app_service, mock_status_repo):
        """ユーザー解決済み問題取得のテスト"""
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
        mock_status_repo.find_solved_by_user.return_value = solved_statuses

        # テスト実行
        result = await status_app_service.get_user_solved_problems(user_id)

        # アサート
        assert len(result) == 2
        assert all(status.is_solved for status in result)
        assert all(status.user_id == user_id for status in result)
        mock_status_repo.find_solved_by_user.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_update_user_problem_status_success(self, status_app_service, mock_status_repo):
        """ユーザー問題状態更新成功のテスト"""
        user_id = uuid4()
        problem_id = uuid4()
        updated_status = UserProblemStatus(
            user_id=user_id,
            problem_id=problem_id,
            is_solved=True,
            best_submission_time=800,
        )

        # モックの設定
        mock_status_repo.update_status.return_value = updated_status

        # テスト実行
        result = await status_app_service.update_user_problem_status(
            user_id=user_id, problem_id=problem_id, is_solved=True, submission_time=800
        )

        # アサート
        assert result.is_solved is True
        assert result.best_submission_time == 800
        mock_status_repo.update_status.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_progress_stats(self, status_app_service, mock_status_repo):
        """ユーザー進捗統計取得のテスト"""
        user_id = uuid4()
        stats = {
            "total_attempted": 10,
            "total_solved": 7,
            "easy_solved": 3,
            "medium_solved": 3,
            "hard_solved": 1,
        }

        # モックの設定
        mock_status_repo.get_user_progress_stats.return_value = stats

        # テスト実行
        result = await status_app_service.get_user_progress_stats(user_id)

        # アサート
        assert result["total_attempted"] == 10
        assert result["total_solved"] == 7
        assert result["easy_solved"] == 3
        mock_status_repo.get_user_progress_stats.assert_called_once_with(user_id)
