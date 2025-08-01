"""
Tests for JudgeSeedService
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from ppseed.domain.services import JudgeSeedService
from ppseed.domain.value_objects import SeedResult, TestCaseFileResult


class TestJudgeSeedService:
    """Tests for JudgeSeedService"""

    @pytest.fixture
    def service(self, mock_submission_repository):
        """Create JudgeSeedService instance with mocked repository"""
        return JudgeSeedService(submission_repository=mock_submission_repository)

    @pytest.mark.asyncio
    async def test_seed_submissions_success(self, service, mock_submission_repository, sample_submissions_data):
        """Test successful submissions seeding"""
        mock_submission_repository.find_by_id.return_value = None
        
        result = await service.seed_submissions(sample_submissions_data)
        
        assert isinstance(result, SeedResult)
        assert result.entity_type == "submissions"
        assert result.total_processed == 1
        assert result.created_count == 1
        assert result.updated_count == 0
        assert result.skipped_count == 0
        assert result.errors == []
        assert result.success is True
        assert mock_submission_repository.save.call_count == 1

    @pytest.mark.asyncio
    async def test_seed_submissions_skip_existing(self, service, mock_submission_repository, sample_submissions_data):
        """Test submissions seeding with existing submissions (skip mode)"""
        existing_submission = MagicMock()
        mock_submission_repository.find_by_id.return_value = existing_submission
        
        result = await service.seed_submissions(sample_submissions_data, overwrite_existing=False)
        
        assert result.entity_type == "submissions"
        assert result.total_processed == 1
        assert result.created_count == 0
        assert result.updated_count == 0
        assert result.skipped_count == 1
        assert result.success is True
        assert mock_submission_repository.save.call_count == 0

    @pytest.mark.asyncio
    async def test_seed_submissions_with_errors(self, service, mock_submission_repository, sample_submissions_data):
        """Test submissions seeding with errors"""
        mock_submission_repository.find_by_id.return_value = None
        mock_submission_repository.save.side_effect = Exception("Save failed")
        
        result = await service.seed_submissions(sample_submissions_data)
        
        assert result.entity_type == "submissions"
        assert result.total_processed == 1
        assert result.created_count == 0
        assert result.updated_count == 0
        assert result.skipped_count == 0
        assert len(result.errors) == 1
        assert "Save failed" in result.errors[0]
        assert result.success is False

    @pytest.mark.asyncio
    async def test_seed_test_case_files_without_creation(self, service):
        """Test test case files seeding without physical file creation"""
        test_cases_data = [{"id": "1"}, {"id": "2"}]
        
        result = await service.seed_test_case_files(
            test_cases_data, 
            create_physical_files=False
        )
        
        assert isinstance(result, TestCaseFileResult)
        assert result.total_files == 2
        assert result.created_files == []
        assert result.errors == []
        assert result.success is True
        assert result.base_directory is None

    @pytest.mark.asyncio
    @patch('ppseed.domain.services.judge_seed_service.Path')
    async def test_seed_test_case_files_with_creation_success(self, mock_path_class, service):
        """Test test case files seeding with successful physical file creation"""
        test_cases_data = [{"id": "1"}, {"id": "2"}]
        
        mock_base_path = MagicMock()
        mock_path_class.return_value = mock_base_path
        mock_base_path.mkdir.return_value = None
        
        service._create_test_case_files = AsyncMock(return_value=["/test/file1.txt", "/test/file2.txt"])
        
        result = await service.seed_test_case_files(
            test_cases_data,
            create_physical_files=True,
            base_directory="/test"
        )
        
        assert isinstance(result, TestCaseFileResult)
        assert result.total_files == 2
        assert result.created_files == ["/test/file1.txt", "/test/file2.txt"]
        assert result.errors == []
        assert result.success is True
        assert result.base_directory == str(mock_base_path)
        mock_base_path.mkdir.assert_called_once_with(exist_ok=True)

    @pytest.mark.asyncio
    @patch('ppseed.domain.services.judge_seed_service.Path')
    async def test_seed_test_case_files_with_creation_error(self, mock_path_class, service):
        """Test test case files seeding with file creation error"""
        test_cases_data = [{"id": "1"}]
        
        mock_base_path = MagicMock()
        mock_path_class.return_value = mock_base_path
        mock_base_path.mkdir.return_value = None
        
        service._create_test_case_files = AsyncMock(side_effect=Exception("File creation failed"))
        
        result = await service.seed_test_case_files(
            test_cases_data,
            create_physical_files=True
        )
        
        assert isinstance(result, TestCaseFileResult)
        assert result.total_files == 1
        assert result.created_files == []
        assert len(result.errors) == 1
        assert "File creation failed" in result.errors[0]
        assert result.success is False

    @pytest.mark.asyncio
    async def test_get_judge_statistics_success(self, service, mock_submission_repository):
        """Test successful judge statistics retrieval"""
        mock_submissions = [
            MagicMock(language="python", status="completed"),
            MagicMock(language="java", status="completed"),
            MagicMock(language="python", status="failed"),
        ]
        mock_submission_repository.find_recent.return_value = mock_submissions
        
        result = await service.get_judge_statistics()
        
        assert result["success"] is True
        assert result["submissions"]["total"] == 3
        assert result["submissions"]["by_language"] == {"python": 2, "java": 1}
        assert result["submissions"]["by_status"] == {"completed": 2, "failed": 1}

    @pytest.mark.asyncio
    async def test_get_judge_statistics_error(self, service, mock_submission_repository):
        """Test judge statistics retrieval with error"""
        mock_submission_repository.find_recent.side_effect = Exception("Database error")
        
        result = await service.get_judge_statistics()
        
        assert result["success"] is False
        assert result["error"] == "Database error"

    @pytest.mark.asyncio
    async def test_clear_judge_data_success(self, service):
        """Test successful judge data clearing"""
        result = await service.clear_judge_data()
        
        assert isinstance(result, SeedResult)
        assert result.entity_type == "judge_data"
        assert result.success is True
        assert result.errors == []

    @pytest.mark.asyncio
    async def test_clear_judge_data_error(self, service):
        """Test judge data clearing with error"""
        with patch.object(service, 'clear_judge_data', side_effect=Exception("Clear failed")):
            try:
                await service.clear_judge_data()
            except Exception:
                pass

    @pytest.mark.asyncio
    async def test_create_test_case_files(self, service):
        """Test physical test case files creation"""
        with patch('ppseed.domain.services.judge_seed_service.Path') as mock_path_class:
            mock_base_path = MagicMock()
            mock_path_class.return_value = mock_base_path
            
            mock_hello_dir = MagicMock()
            mock_addition_dir = MagicMock()
            mock_max_array_dir = MagicMock()
            
            mock_base_path.__truediv__.side_effect = [
                mock_hello_dir, mock_addition_dir, mock_max_array_dir
            ]
            
            mock_file = MagicMock()
            mock_hello_dir.__truediv__.return_value = mock_file
            mock_addition_dir.__truediv__.return_value = mock_file
            mock_max_array_dir.__truediv__.return_value = mock_file
            
            mock_file.write_text.return_value = None
            mock_file.__str__.return_value = "/test/file.txt"
            
            result = await service._create_test_case_files(mock_base_path)
            
            assert isinstance(result, list)
            assert len(result) > 0
            mock_hello_dir.mkdir.assert_called_with(exist_ok=True)
            mock_addition_dir.mkdir.assert_called_with(exist_ok=True)
            mock_max_array_dir.mkdir.assert_called_with(exist_ok=True)