"""
Problem domain service unit tests
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.core.domain.services.problem_service import ProblemDomainService
from src.core.domain.models import Problem, JudgeCase, Tag, ProblemMetadata
from src.core.domain.repositories import (
    ProblemRepository,
    JudgeCaseRepository,
    ProblemContentRepository,
)
from src.const import DifficultyLevel, ProblemStatus, JudgeCaseType
from src.shared.events import EventBus


@pytest.mark.core
class TestProblemDomainService:
    """ProblemDomainServiceのテスト"""

    @pytest.fixture
    def mock_problem_repo(self):
        """モックProblemRepositoryを作成"""
        repo = AsyncMock(spec=ProblemRepository)
        return repo

    @pytest.fixture
    def mock_judge_case_repo(self):
        """モックJudgeCaseRepositoryを作成"""
        repo = AsyncMock(spec=JudgeCaseRepository)
        return repo

    @pytest.fixture
    def mock_content_repo(self):
        """モックProblemContentRepositoryを作成"""
        repo = AsyncMock(spec=ProblemContentRepository)
        return repo

    @pytest.fixture
    def mock_event_bus(self):
        """モックEventBusを作成"""
        bus = AsyncMock(spec=EventBus)
        return bus

    @pytest.fixture
    def problem_service(
        self, mock_problem_repo, mock_judge_case_repo, mock_content_repo, mock_event_bus
    ):
        """ProblemDomainServiceのインスタンスを作成"""
        return ProblemDomainService(
            problem_repo=mock_problem_repo,
            judge_case_repo=mock_judge_case_repo,
            content_repo=mock_content_repo,
            event_bus=mock_event_bus,
        )

    @pytest.mark.asyncio
    async def test_create_problem_success(
        self, problem_service, mock_problem_repo, mock_event_bus
    ):
        """問題作成成功のテスト"""
        # モックの設定
        mock_problem_repo.find_by_title.return_value = None  # 重複なし
        mock_problem_repo.create.return_value = Problem(
            title="Test Problem", description="Test description", author_id=uuid4()
        )

        # テスト実行
        result = await problem_service.create_problem(
            title="Test Problem",
            description="Test description",
            author_id=uuid4(),
            difficulty=DifficultyLevel.MEDIUM,
            tags=["algorithms", "dynamic-programming"],
        )

        # アサート
        assert result.title == "Test Problem"
        assert result.difficulty == DifficultyLevel.MEDIUM
        assert len(result.tags) == 2
        mock_problem_repo.create.assert_called_once()
        mock_event_bus.publish.assert_called()

    @pytest.mark.asyncio
    async def test_create_problem_duplicate_title(
        self, problem_service, mock_problem_repo
    ):
        """問題作成時のタイトル重複エラーのテスト"""
        # モックの設定 - 既存の問題を返す
        existing_problem = Problem(
            title="Existing Problem",
            description="Existing description",
            author_id=uuid4(),
        )
        mock_problem_repo.find_by_title.return_value = existing_problem

        # テスト実行とアサート
        with pytest.raises(ValueError, match="Problem with this title already exists"):
            await problem_service.create_problem(
                title="Existing Problem",
                description="Test description",
                author_id=uuid4(),
            )

    @pytest.mark.asyncio
    async def test_add_sample_case_success(
        self, problem_service, mock_judge_case_repo, mock_event_bus
    ):
        """サンプルケース追加成功のテスト"""
        problem_id = uuid4()

        # モックの設定
        mock_judge_case_repo.create.return_value = JudgeCase(
            problem_id=problem_id,
            name="Sample 1",
            input_data="1 2",
            expected_output="3",
            case_type=JudgeCaseType.SAMPLE,
        )

        # テスト実行
        result = await problem_service.add_sample_case(
            problem_id=problem_id,
            name="Sample 1",
            input_data="1 2",
            expected_output="3",
        )

        # アサート
        assert result.case_type == JudgeCaseType.SAMPLE
        assert result.name == "Sample 1"
        mock_judge_case_repo.create.assert_called_once()
        mock_event_bus.publish.assert_called()

    @pytest.mark.asyncio
    async def test_add_hidden_case_success(
        self, problem_service, mock_judge_case_repo, mock_event_bus
    ):
        """隠しケース追加成功のテスト"""
        problem_id = uuid4()

        # モックの設定
        mock_judge_case_repo.create.return_value = JudgeCase(
            problem_id=problem_id,
            name="Hidden 1",
            input_data="5 10",
            expected_output="15",
            case_type=JudgeCaseType.HIDDEN,
        )

        # テスト実行
        result = await problem_service.add_hidden_case(
            problem_id=problem_id,
            name="Hidden 1",
            input_data="5 10",
            expected_output="15",
            points=5,
        )

        # アサート
        assert result.case_type == JudgeCaseType.HIDDEN
        assert result.points == 5
        mock_judge_case_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_problem_with_cases(
        self, problem_service, mock_problem_repo, mock_judge_case_repo
    ):
        """問題とケースの取得テスト"""
        problem_id = uuid4()

        # モックの設定
        problem = Problem(
            id=problem_id,
            title="Test Problem",
            description="Test description",
            author_id=uuid4(),
        )
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

        mock_problem_repo.get.return_value = problem
        mock_judge_case_repo.find_by_problem_id.return_value = judge_cases

        # テスト実行
        result_problem, result_cases = await problem_service.get_problem_with_cases(
            problem_id
        )

        # アサート
        assert result_problem.id == problem_id
        assert len(result_cases) == 2
        assert result_cases[0].case_type == JudgeCaseType.SAMPLE
        assert result_cases[1].case_type == JudgeCaseType.HIDDEN

    @pytest.mark.asyncio
    async def test_publish_problem_success(
        self, problem_service, mock_problem_repo, mock_event_bus
    ):
        """問題公開成功のテスト"""
        problem_id = uuid4()
        problem = Problem(
            id=problem_id,
            title="Test Problem",
            description="Test description",
            author_id=uuid4(),
            status=ProblemStatus.DRAFT,
        )

        # モックの設定
        mock_problem_repo.get.return_value = problem
        mock_problem_repo.update.return_value = problem

        # テスト実行
        result = await problem_service.publish_problem(problem_id)

        # アサート
        assert result.status == ProblemStatus.PUBLISHED
        mock_problem_repo.update.assert_called_once()
        mock_event_bus.publish.assert_called()

    @pytest.mark.asyncio
    async def test_publish_problem_not_found(self, problem_service, mock_problem_repo):
        """存在しない問題の公開エラーテスト"""
        problem_id = uuid4()

        # モックの設定
        mock_problem_repo.get.return_value = None

        # テスト実行とアサート
        with pytest.raises(ValueError, match="Problem not found"):
            await problem_service.publish_problem(problem_id)

    @pytest.mark.asyncio
    async def test_update_problem_tags(self, problem_service, mock_problem_repo):
        """問題タグ更新のテスト"""
        problem_id = uuid4()
        problem = Problem(
            id=problem_id,
            title="Test Problem",
            description="Test description",
            author_id=uuid4(),
        )

        # モックの設定
        mock_problem_repo.get.return_value = problem
        mock_problem_repo.update.return_value = problem

        # テスト実行
        new_tags = ["algorithms", "graph", "bfs"]
        result = await problem_service.update_problem_tags(problem_id, new_tags)

        # アサート
        assert len(result.tags) == 3
        tag_names = {tag.name for tag in result.tags}
        assert tag_names == {"algorithms", "graph", "bfs"}
        mock_problem_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_problems_by_difficulty(self, problem_service, mock_problem_repo):
        """難易度別問題取得のテスト"""
        problems = [
            Problem(
                title="Easy Problem",
                description="Easy description",
                author_id=uuid4(),
                difficulty=DifficultyLevel.EASY,
            ),
            Problem(
                title="Medium Problem",
                description="Medium description",
                author_id=uuid4(),
                difficulty=DifficultyLevel.MEDIUM,
            ),
        ]

        # モックの設定
        mock_problem_repo.find_by_difficulty.return_value = [problems[0]]

        # テスト実行
        result = await problem_service.get_problems_by_difficulty(DifficultyLevel.EASY)

        # アサート
        assert len(result) == 1
        assert result[0].difficulty == DifficultyLevel.EASY
        mock_problem_repo.find_by_difficulty.assert_called_once_with(
            DifficultyLevel.EASY
        )

    @pytest.mark.asyncio
    async def test_search_problems_by_tags(self, problem_service, mock_problem_repo):
        """タグ検索のテスト"""
        # モックの設定
        mock_problem_repo.find_by_tags.return_value = []

        # テスト実行
        result = await problem_service.search_problems_by_tags(["algorithms", "graph"])

        # アサート
        mock_problem_repo.find_by_tags.assert_called_once_with(["algorithms", "graph"])

    @pytest.mark.asyncio
    async def test_delete_problem_success(
        self, problem_service, mock_problem_repo, mock_judge_case_repo
    ):
        """問題削除成功のテスト"""
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
        await problem_service.delete_problem(problem_id)

        # アサート
        mock_judge_case_repo.delete_by_problem_id.assert_called_once_with(problem_id)
        mock_problem_repo.delete.assert_called_once_with(problem_id)

    @pytest.mark.asyncio
    async def test_delete_problem_not_found(self, problem_service, mock_problem_repo):
        """存在しない問題の削除エラーテスト"""
        problem_id = uuid4()

        # モックの設定
        mock_problem_repo.get.return_value = None

        # テスト実行とアサート
        with pytest.raises(ValueError, match="Problem not found"):
            await problem_service.delete_problem(problem_id)
