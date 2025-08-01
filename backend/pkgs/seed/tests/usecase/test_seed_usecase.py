"""
Tests for SeedUseCase
"""

import pytest
from unittest.mock import AsyncMock, patch

from ppseed.usecase import SeedUseCase
from ppseed.domain.services import ProblemSeedService, JudgeSeedService


class TestSeedUseCase:
    """Tests for SeedUseCase"""

    @pytest.fixture
    def mock_problem_seed_service(self, seed_result_success, seed_statistics):
        """Mock ProblemSeedService"""
        mock = AsyncMock(spec=ProblemSeedService)
        mock.seed_books.return_value = seed_result_success
        mock.seed_problems.return_value = seed_result_success
        mock.get_problem_statistics.return_value = seed_statistics
        mock.clear_problem_data.return_value = seed_result_success
        return mock

    @pytest.fixture
    def mock_judge_seed_service(self, seed_result_success, test_case_file_result):
        """Mock JudgeSeedService"""
        mock = AsyncMock(spec=JudgeSeedService)
        mock.seed_submissions.return_value = seed_result_success
        mock.seed_test_case_files.return_value = test_case_file_result
        mock.get_judge_statistics.return_value = {"success": True, "submissions": {"total": 0}}
        mock.clear_judge_data.return_value = seed_result_success
        return mock

    @pytest.fixture
    def usecase_with_judge(self, mock_problem_seed_service, mock_judge_seed_service):
        """Create SeedUseCase with both services"""
        return SeedUseCase(
            problem_seed_service=mock_problem_seed_service,
            judge_seed_service=mock_judge_seed_service
        )

    @pytest.fixture
    def usecase_without_judge(self, mock_problem_seed_service):
        """Create SeedUseCase without judge service"""
        return SeedUseCase(
            problem_seed_service=mock_problem_seed_service,
            judge_seed_service=None
        )

    @pytest.mark.asyncio
    async def test_seed_complete_dataset_success(self, usecase_with_judge, mock_problem_seed_service, mock_judge_seed_service):
        """Test successful complete dataset seeding"""
        with patch('ppseed.usecase.seed_usecase.SAMPLE_BOOKS', []):
            with patch('ppseed.usecase.seed_usecase.SAMPLE_PROBLEMS', []):
                with patch('ppseed.usecase.seed_usecase.SAMPLE_SUBMISSIONS', []):
                    with patch('ppseed.usecase.seed_usecase.SAMPLE_CASE_FILES', []):
                        result = await usecase_with_judge.seed_complete_dataset()
        
        assert result["success"] is True
        assert "problem_domain" in result
        assert "judge_domain" in result
        assert result["problem_domain"]["success"] is True
        assert result["judge_domain"]["success"] is True
        
        mock_problem_seed_service.seed_books.assert_called_once()
        mock_problem_seed_service.seed_problems.assert_called_once()
        mock_judge_seed_service.seed_submissions.assert_called_once()
        mock_judge_seed_service.seed_test_case_files.assert_called_once()

    @pytest.mark.asyncio
    async def test_seed_complete_dataset_with_clear(self, usecase_with_judge, mock_problem_seed_service, mock_judge_seed_service):
        """Test complete dataset seeding with clearing existing data"""
        with patch('ppseed.usecase.seed_usecase.SAMPLE_BOOKS', []):
            with patch('ppseed.usecase.seed_usecase.SAMPLE_PROBLEMS', []):
                with patch('ppseed.usecase.seed_usecase.SAMPLE_SUBMISSIONS', []):
                    with patch('ppseed.usecase.seed_usecase.SAMPLE_CASE_FILES', []):
                        result = await usecase_with_judge.seed_complete_dataset(clear_existing=True)
        
        assert result["success"] is True
        mock_judge_seed_service.clear_judge_data.assert_called_once()
        mock_problem_seed_service.clear_problem_data.assert_called_once()

    @pytest.mark.asyncio
    async def test_seed_complete_dataset_without_judge_service(self, usecase_without_judge, mock_problem_seed_service):
        """Test complete dataset seeding without judge service"""
        with patch('ppseed.usecase.seed_usecase.SAMPLE_BOOKS', []):
            with patch('ppseed.usecase.seed_usecase.SAMPLE_PROBLEMS', []):
                result = await usecase_without_judge.seed_complete_dataset()
        
        assert result["success"] is True
        assert "problem_domain" in result
        assert "judge_domain" in result
        assert result["problem_domain"]["success"] is True
        
        mock_problem_seed_service.seed_books.assert_called_once()
        mock_problem_seed_service.seed_problems.assert_called_once()

    @pytest.mark.asyncio
    async def test_seed_complete_dataset_with_custom_data(self, usecase_with_judge):
        """Test complete dataset seeding with custom data"""
        custom_data = {
            "books": [{"title": "Custom Book"}],
            "problems": [{"title": "Custom Problem"}],
            "submissions": [{"id": "custom-sub"}],
            "test_cases": [{"id": "custom-case"}]
        }
        
        result = await usecase_with_judge.seed_complete_dataset(custom_data=custom_data)
        
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_seed_complete_dataset_with_error(self, usecase_with_judge, mock_problem_seed_service, seed_result_with_errors):
        """Test complete dataset seeding with errors"""
        mock_problem_seed_service.seed_books.return_value = seed_result_with_errors
        
        with patch('ppseed.usecase.seed_usecase.SAMPLE_BOOKS', []):
            with patch('ppseed.usecase.seed_usecase.SAMPLE_PROBLEMS', []):
                with patch('ppseed.usecase.seed_usecase.SAMPLE_SUBMISSIONS', []):
                    with patch('ppseed.usecase.seed_usecase.SAMPLE_CASE_FILES', []):
                        result = await usecase_with_judge.seed_complete_dataset()
        
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_seed_problems_only_success(self, usecase_with_judge, mock_problem_seed_service):
        """Test successful problems-only seeding"""
        result = await usecase_with_judge.seed_problems_only()
        
        assert result["success"] is True
        mock_problem_seed_service.seed_books.assert_called_once()
        mock_problem_seed_service.seed_problems.assert_called_once()

    @pytest.mark.asyncio
    async def test_seed_problems_only_with_custom_data(self, usecase_with_judge, mock_problem_seed_service):
        """Test problems-only seeding with custom data"""
        custom_books = [{"title": "Custom Book"}]
        custom_problems = [{"title": "Custom Problem"}]
        
        result = await usecase_with_judge.seed_problems_only(
            books_data=custom_books,
            problems_data=custom_problems,
            overwrite_existing=True
        )
        
        assert result["success"] is True
        mock_problem_seed_service.seed_books.assert_called_with(custom_books, True)
        mock_problem_seed_service.seed_problems.assert_called_with(custom_problems, True)

    @pytest.mark.asyncio
    async def test_seed_judge_only_success(self, usecase_with_judge, mock_judge_seed_service):
        """Test successful judge-only seeding"""
        result = await usecase_with_judge.seed_judge_only()
        
        assert result["success"] is True
        mock_judge_seed_service.seed_submissions.assert_called_once()
        mock_judge_seed_service.seed_test_case_files.assert_called_once()

    @pytest.mark.asyncio
    async def test_seed_judge_only_without_service(self, usecase_without_judge):
        """Test judge-only seeding without judge service"""
        result = await usecase_without_judge.seed_judge_only()
        
        assert result["success"] is False
        assert result["error"] == "Judge seed service not available"

    @pytest.mark.asyncio
    async def test_seed_judge_only_with_custom_data(self, usecase_with_judge, mock_judge_seed_service):
        """Test judge-only seeding with custom data"""
        custom_submissions = [{"id": "custom-sub"}]
        custom_test_cases = [{"id": "custom-case"}]
        
        result = await usecase_with_judge.seed_judge_only(
            submissions_data=custom_submissions,
            test_cases_data=custom_test_cases,
            create_test_files=True,
            test_files_directory="/custom",
            overwrite_existing=True
        )
        
        assert result["success"] is True
        mock_judge_seed_service.seed_submissions.assert_called_with(custom_submissions, True)
        mock_judge_seed_service.seed_test_case_files.assert_called_with(
            custom_test_cases, True, "/custom", True
        )

    @pytest.mark.asyncio
    async def test_get_comprehensive_statistics_success(self, usecase_with_judge, mock_problem_seed_service, mock_judge_seed_service, seed_statistics):
        """Test successful comprehensive statistics retrieval"""
        result = await usecase_with_judge.get_comprehensive_statistics()
        
        assert result["success"] is True
        assert "problem_domain" in result
        assert "judge_domain" in result
        assert result["problem_domain"]["books_total"] == seed_statistics.books_total
        assert result["problem_domain"]["problems_total"] == seed_statistics.problems_total
        
        mock_problem_seed_service.get_problem_statistics.assert_called_once()
        mock_judge_seed_service.get_judge_statistics.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_comprehensive_statistics_without_judge(self, usecase_without_judge, mock_problem_seed_service, seed_statistics):
        """Test comprehensive statistics without judge service"""
        result = await usecase_without_judge.get_comprehensive_statistics()
        
        assert result["success"] is True
        assert "problem_domain" in result
        assert "judge_domain" in result
        assert result["problem_domain"]["books_total"] == seed_statistics.books_total
        
        mock_problem_seed_service.get_problem_statistics.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_comprehensive_statistics_with_error(self, usecase_with_judge, mock_problem_seed_service):
        """Test comprehensive statistics with error"""
        mock_problem_seed_service.get_problem_statistics.side_effect = Exception("Stats error")
        
        result = await usecase_with_judge.get_comprehensive_statistics()
        
        assert result["success"] is False
        assert len(result["errors"]) == 1
        assert "Stats error" in result["errors"][0]

    def test_prepare_seed_data_with_custom_data(self, usecase_with_judge):
        """Test seed data preparation with custom data"""
        custom_data = {
            "books": [{"title": "Custom Book"}],
            "problems": [{"title": "Custom Problem"}]
        }
        
        result = usecase_with_judge._prepare_seed_data(custom_data)
        
        assert result["books"] == custom_data["books"]
        assert result["problems"] == custom_data["problems"]

    def test_prepare_seed_data_without_custom_data(self, usecase_with_judge):
        """Test seed data preparation without custom data (uses defaults)"""
        with patch('ppseed.usecase.seed_usecase.SAMPLE_BOOKS', [{"title": "Sample Book"}]):
            with patch('ppseed.usecase.seed_usecase.SAMPLE_PROBLEMS', [{"title": "Sample Problem"}]):
                result = usecase_with_judge._prepare_seed_data(None)
        
        assert result["books"] == [{"title": "Sample Book"}]
        assert result["problems"] == [{"title": "Sample Problem"}]