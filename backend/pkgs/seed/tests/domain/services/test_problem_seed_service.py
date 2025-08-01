"""
Tests for ProblemSeedService
"""

import pytest
from unittest.mock import MagicMock

from ppseed.domain.services import ProblemSeedService
from ppseed.domain.value_objects import SeedResult, SeedStatistics


class TestProblemSeedService:
    """Tests for ProblemSeedService"""

    @pytest.fixture
    def service(self, mock_book_repository, mock_problem_repository):
        """Create ProblemSeedService instance with mocked repositories"""
        return ProblemSeedService(
            book_repository=mock_book_repository,
            problem_repository=mock_problem_repository
        )

    @pytest.mark.asyncio
    async def test_seed_books_success(self, service, mock_book_repository, sample_books_data):
        """Test successful books seeding"""
        mock_book_repository.find_by_title.return_value = None
        
        result = await service.seed_books(sample_books_data)
        
        assert isinstance(result, SeedResult)
        assert result.entity_type == "books"
        assert result.total_processed == 2
        assert result.created_count == 2
        assert result.updated_count == 0
        assert result.skipped_count == 0
        assert result.errors == []
        assert result.success is True
        assert mock_book_repository.create.call_count == 2

    @pytest.mark.asyncio
    async def test_seed_books_skip_existing(self, service, mock_book_repository, sample_books_data):
        """Test books seeding with existing books (skip mode)"""
        existing_book = MagicMock()
        mock_book_repository.find_by_title.return_value = existing_book
        
        result = await service.seed_books(sample_books_data, overwrite_existing=False)
        
        assert result.entity_type == "books"
        assert result.total_processed == 2
        assert result.created_count == 0
        assert result.updated_count == 0
        assert result.skipped_count == 2
        assert result.success is True
        assert mock_book_repository.create.call_count == 0

    @pytest.mark.asyncio
    async def test_seed_books_with_errors(self, service, mock_book_repository, sample_books_data):
        """Test books seeding with errors"""
        mock_book_repository.find_by_title.return_value = None
        mock_book_repository.create.side_effect = [None, Exception("Creation failed")]
        
        result = await service.seed_books(sample_books_data)
        
        assert result.entity_type == "books"
        assert result.total_processed == 2
        assert result.created_count == 1
        assert result.updated_count == 0
        assert result.skipped_count == 0
        assert len(result.errors) == 1
        assert "Creation failed" in result.errors[0]
        assert result.success is False

    @pytest.mark.asyncio
    async def test_seed_problems_success(self, service, mock_problem_repository, sample_problems_data):
        """Test successful problems seeding"""
        mock_problem_repository.find_by_title.return_value = None
        
        result = await service.seed_problems(sample_problems_data)
        
        assert isinstance(result, SeedResult)
        assert result.entity_type == "problems"
        assert result.total_processed == 1
        assert result.created_count == 1
        assert result.updated_count == 0
        assert result.skipped_count == 0
        assert result.errors == []
        assert result.success is True
        assert mock_problem_repository.create.call_count == 1

    @pytest.mark.asyncio
    async def test_seed_problems_skip_existing(self, service, mock_problem_repository, sample_problems_data):
        """Test problems seeding with existing problems (skip mode)"""
        existing_problem = MagicMock()
        mock_problem_repository.find_by_title.return_value = existing_problem
        
        result = await service.seed_problems(sample_problems_data, overwrite_existing=False)
        
        assert result.entity_type == "problems"
        assert result.total_processed == 1
        assert result.created_count == 0
        assert result.updated_count == 0
        assert result.skipped_count == 1
        assert result.success is True
        assert mock_problem_repository.create.call_count == 0

    @pytest.mark.asyncio
    async def test_get_problem_statistics_success(self, service, mock_book_repository, mock_problem_repository):
        """Test successful statistics retrieval"""
        mock_books = [
            MagicMock(difficulty_level="beginner"),
            MagicMock(difficulty_level="intermediate"),
            MagicMock(difficulty_level="beginner")
        ]
        mock_problems = [
            MagicMock(difficulty_level="beginner", status="published"),
            MagicMock(difficulty_level="intermediate", status="published"),
            MagicMock(difficulty_level="beginner", status="draft")
        ]
        
        mock_book_repository.find_published.return_value = mock_books
        mock_book_repository.count_published.return_value = 3
        mock_problem_repository.find_published.return_value = mock_problems
        
        result = await service.get_problem_statistics()
        
        assert isinstance(result, SeedStatistics)
        assert result.books_total == 3
        assert result.books_by_difficulty == {"beginner": 2, "intermediate": 1}
        assert result.problems_total == 3
        assert result.problems_by_difficulty == {"beginner": 2, "intermediate": 1}
        assert result.problems_by_status == {"published": 2, "draft": 1}
        assert result.success is True
        assert result.error is None

    @pytest.mark.asyncio
    async def test_get_problem_statistics_error(self, service, mock_book_repository):
        """Test statistics retrieval with error"""
        mock_book_repository.find_published.side_effect = Exception("Database error")
        
        result = await service.get_problem_statistics()
        
        assert isinstance(result, SeedStatistics)
        assert result.books_total == 0
        assert result.problems_total == 0
        assert result.success is False
        assert result.error == "Database error"

    @pytest.mark.asyncio
    async def test_clear_problem_data_success(self, service, mock_book_repository):
        """Test successful data clearing"""
        mock_book_repository.delete_all.return_value = None
        
        result = await service.clear_problem_data()
        
        assert isinstance(result, SeedResult)
        assert result.entity_type == "problem_data"
        assert result.success is True
        assert result.errors == []
        assert mock_book_repository.delete_all.call_count == 1

    @pytest.mark.asyncio
    async def test_clear_problem_data_error(self, service, mock_book_repository):
        """Test data clearing with error"""
        mock_book_repository.delete_all.side_effect = Exception("Delete failed")
        
        result = await service.clear_problem_data()
        
        assert isinstance(result, SeedResult)
        assert result.entity_type == "problem_data"
        assert result.success is False
        assert len(result.errors) == 1
        assert "Delete failed" in result.errors[0]