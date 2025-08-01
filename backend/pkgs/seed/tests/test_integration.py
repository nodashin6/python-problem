"""
Integration tests for ppseed package
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from ppseed import (
    SeedFacade, 
    create_seed_facade,
    ProblemSeedService, 
    JudgeSeedService,
    SeedUseCase,
    get_all_sample_data
)


@pytest.mark.integration
class TestPpseedIntegration:
    """Integration tests for the complete ppseed workflow"""

    @pytest.fixture
    def repositories(self):
        """Create mock repositories for integration testing"""
        book_repo = AsyncMock()
        problem_repo = AsyncMock()
        submission_repo = AsyncMock()
        
        # Mock successful repository operations
        book_repo.find_by_title.return_value = None
        book_repo.create.return_value = MagicMock()
        book_repo.find_published.return_value = []
        book_repo.count_published.return_value = 0
        book_repo.delete_all.return_value = None
        
        problem_repo.find_by_title.return_value = None
        problem_repo.create.return_value = MagicMock()
        problem_repo.find_published.return_value = []
        
        submission_repo.find_by_id.return_value = None
        submission_repo.save.return_value = MagicMock()
        submission_repo.find_recent.return_value = []
        
        return {
            "book": book_repo,
            "problem": problem_repo,
            "submission": submission_repo
        }

    @pytest.mark.asyncio
    async def test_full_seeding_workflow(self, repositories):
        """Test complete seeding workflow from facade to repositories"""
        facade = create_seed_facade(
            book_repository=repositories["book"],
            problem_repository=repositories["problem"],
            submission_repository=repositories["submission"]
        )
        
        sample_data = get_all_sample_data()
        custom_data = {
            "books": sample_data["books"][:1],
            "problems": sample_data["problems"][:1],
            "submissions": sample_data["submissions"][:1],
            "test_cases": []
        }
        
        result = await facade.seed_all(
            clear_existing=True,
            create_test_files=False,
            custom_data=custom_data
        )
        
        assert result["success"] is True
        assert "problem_domain" in result
        assert "judge_domain" in result
        
        # Verify repository interactions
        repositories["book"].delete_all.assert_called()
        repositories["book"].create.assert_called()
        repositories["problem"].create.assert_called()
        repositories["submission"].save.assert_called()

    @pytest.mark.asyncio
    async def test_problems_only_workflow(self, repositories):
        """Test problems-only seeding workflow"""
        facade = SeedFacade(
            book_repository=repositories["book"],
            problem_repository=repositories["problem"],
            submission_repository=None
        )
        
        sample_data = get_all_sample_data()
        
        result = await facade.seed_problems_only(
            custom_books=sample_data["books"][:1],
            custom_problems=sample_data["problems"][:1],
            overwrite_existing=False
        )
        
        assert result["success"] is True
        assert "books" in result
        assert "problems" in result
        
        repositories["book"].create.assert_called()
        repositories["problem"].create.assert_called()

    @pytest.mark.asyncio
    async def test_statistics_workflow(self, repositories):
        """Test statistics retrieval workflow"""
        facade = create_seed_facade(
            book_repository=repositories["book"],
            problem_repository=repositories["problem"],
            submission_repository=repositories["submission"]
        )
        
        result = await facade.get_statistics()
        
        assert result["success"] is True
        repositories["book"].find_published.assert_called()
        repositories["book"].count_published.assert_called()
        repositories["problem"].find_published.assert_called()
        repositories["submission"].find_recent.assert_called()

    @pytest.mark.asyncio
    async def test_service_layer_integration(self, repositories):
        """Test direct service layer integration"""
        problem_service = ProblemSeedService(
            book_repository=repositories["book"],
            problem_repository=repositories["problem"]
        )
        
        judge_service = JudgeSeedService(
            submission_repository=repositories["submission"]
        )
        
        usecase = SeedUseCase(
            problem_seed_service=problem_service,
            judge_seed_service=judge_service
        )
        
        sample_data = get_all_sample_data()
        
        result = await usecase.seed_problems_only(
            books_data=sample_data["books"][:1],
            problems_data=sample_data["problems"][:1]
        )
        
        assert result["success"] is True
        repositories["book"].create.assert_called()
        repositories["problem"].create.assert_called()

    @pytest.mark.asyncio
    async def test_error_handling_integration(self, repositories):
        """Test error handling throughout the integration"""
        repositories["book"].create.side_effect = Exception("Repository error")
        
        facade = create_seed_facade(
            book_repository=repositories["book"],
            problem_repository=repositories["problem"],
            submission_repository=repositories["submission"]
        )
        
        sample_data = get_all_sample_data()
        
        result = await facade.seed_problems_only(
            custom_books=sample_data["books"][:1],
            custom_problems=sample_data["problems"][:1]
        )
        
        assert result["success"] is False
        assert "books" in result
        assert len(result["books"]["errors"]) > 0

    def test_sample_data_availability(self):
        """Test that sample data is properly structured"""
        sample_data = get_all_sample_data()
        
        assert isinstance(sample_data, dict)
        assert "books" in sample_data
        assert "problems" in sample_data
        assert "submissions" in sample_data
        assert "users" in sample_data
        assert "case_files" in sample_data
        assert "judge_cases" in sample_data
        
        assert isinstance(sample_data["books"], list)
        assert isinstance(sample_data["problems"], list)
        assert len(sample_data["books"]) > 0
        assert len(sample_data["problems"]) > 0

    @pytest.mark.asyncio
    async def test_facade_without_judge_service(self, repositories):
        """Test facade functionality without judge service"""
        facade = SeedFacade(
            book_repository=repositories["book"],
            problem_repository=repositories["problem"],
            submission_repository=None
        )
        
        assert facade.judge_seed_service is None
        
        result = await facade.seed_all()
        
        assert result["success"] is True
        assert "problem_domain" in result
        assert "judge_domain" in result

    @pytest.mark.asyncio
    async def test_custom_vs_default_data_integration(self, repositories):
        """Test integration with both custom and default data"""
        facade = create_seed_facade(
            book_repository=repositories["book"],
            problem_repository=repositories["problem"],
            submission_repository=repositories["submission"]
        )
        
        # Test with default data
        result1 = await facade.seed_problems_only()
        assert result1["success"] is True
        
        # Test with custom data
        custom_data = {
            "books": [{"title": "Custom Integration Book"}],
            "problems": [{"title": "Custom Integration Problem"}]
        }
        
        result2 = await facade.seed_problems_only(
            custom_books=custom_data["books"],
            custom_problems=custom_data["problems"]
        )
        assert result2["success"] is True
        
        # Verify both calls worked
        assert repositories["book"].create.call_count >= 2
        assert repositories["problem"].create.call_count >= 2