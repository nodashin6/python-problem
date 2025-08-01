"""
Tests for SeedFacade
"""

import pytest
from unittest.mock import AsyncMock

from ppseed.app import SeedFacade, create_seed_facade
from ppseed.domain.services import ProblemSeedService, JudgeSeedService
from ppseed.usecase import SeedUseCase


class TestSeedFacade:
    """Tests for SeedFacade"""

    @pytest.fixture
    def mock_seed_usecase(self):
        """Mock SeedUseCase"""
        mock = AsyncMock(spec=SeedUseCase)
        mock.seed_complete_dataset.return_value = {"success": True}
        mock.seed_problems_only.return_value = {"success": True}
        mock.get_comprehensive_statistics.return_value = {"success": True}
        return mock

    @pytest.fixture
    def facade_with_judge(self, mock_book_repository, mock_problem_repository, mock_submission_repository):
        """Create SeedFacade with judge service"""
        return SeedFacade(
            book_repository=mock_book_repository,
            problem_repository=mock_problem_repository,
            submission_repository=mock_submission_repository
        )

    @pytest.fixture
    def facade_without_judge(self, mock_book_repository, mock_problem_repository):
        """Create SeedFacade without judge service"""
        return SeedFacade(
            book_repository=mock_book_repository,
            problem_repository=mock_problem_repository,
            submission_repository=None
        )

    def test_facade_initialization_with_judge(self, facade_with_judge):
        """Test SeedFacade initialization with judge service"""
        assert isinstance(facade_with_judge.problem_seed_service, ProblemSeedService)
        assert isinstance(facade_with_judge.judge_seed_service, JudgeSeedService)
        assert isinstance(facade_with_judge.seed_usecase, SeedUseCase)

    def test_facade_initialization_without_judge(self, facade_without_judge):
        """Test SeedFacade initialization without judge service"""
        assert isinstance(facade_without_judge.problem_seed_service, ProblemSeedService)
        assert facade_without_judge.judge_seed_service is None
        assert isinstance(facade_without_judge.seed_usecase, SeedUseCase)

    @pytest.mark.asyncio
    async def test_seed_all_success(self, facade_with_judge, mock_seed_usecase):
        """Test successful seed_all operation"""
        facade_with_judge.seed_usecase = mock_seed_usecase
        
        result = await facade_with_judge.seed_all(
            clear_existing=True,
            create_test_files=True,
            custom_data={"books": []}
        )
        
        assert result["success"] is True
        mock_seed_usecase.seed_complete_dataset.assert_called_once_with(
            clear_existing=True,
            custom_data={"books": []},
            create_test_files=True
        )

    @pytest.mark.asyncio
    async def test_seed_all_default_params(self, facade_with_judge, mock_seed_usecase):
        """Test seed_all with default parameters"""
        facade_with_judge.seed_usecase = mock_seed_usecase
        
        result = await facade_with_judge.seed_all()
        
        assert result["success"] is True
        mock_seed_usecase.seed_complete_dataset.assert_called_once_with(
            clear_existing=False,
            custom_data=None,
            create_test_files=False
        )

    @pytest.mark.asyncio
    async def test_seed_problems_only_success(self, facade_with_judge, mock_seed_usecase):
        """Test successful seed_problems_only operation"""
        facade_with_judge.seed_usecase = mock_seed_usecase
        
        custom_books = [{"title": "Custom Book"}]
        custom_problems = [{"title": "Custom Problem"}]
        
        result = await facade_with_judge.seed_problems_only(
            custom_books=custom_books,
            custom_problems=custom_problems,
            overwrite_existing=True
        )
        
        assert result["success"] is True
        mock_seed_usecase.seed_problems_only.assert_called_once_with(
            books_data=custom_books,
            problems_data=custom_problems,
            overwrite_existing=True
        )

    @pytest.mark.asyncio
    async def test_seed_problems_only_default_params(self, facade_with_judge, mock_seed_usecase):
        """Test seed_problems_only with default parameters"""
        facade_with_judge.seed_usecase = mock_seed_usecase
        
        result = await facade_with_judge.seed_problems_only()
        
        assert result["success"] is True
        mock_seed_usecase.seed_problems_only.assert_called_once_with(
            books_data=None,
            problems_data=None,
            overwrite_existing=False
        )

    @pytest.mark.asyncio
    async def test_get_statistics(self, facade_with_judge, mock_seed_usecase):
        """Test get_statistics operation"""
        facade_with_judge.seed_usecase = mock_seed_usecase
        
        result = await facade_with_judge.get_statistics()
        
        assert result["success"] is True
        mock_seed_usecase.get_comprehensive_statistics.assert_called_once()

    @pytest.mark.asyncio
    async def test_verify_data(self, facade_with_judge, mock_seed_usecase):
        """Test verify_data operation"""
        facade_with_judge.seed_usecase = mock_seed_usecase
        
        result = await facade_with_judge.verify_data()
        
        assert result["success"] is True
        mock_seed_usecase.get_comprehensive_statistics.assert_called_once()


class TestCreateSeedFacade:
    """Tests for create_seed_facade factory function"""

    def test_create_seed_facade_with_judge(
        self, 
        mock_book_repository, 
        mock_problem_repository, 
        mock_submission_repository
    ):
        """Test factory function with judge service"""
        facade = create_seed_facade(
            book_repository=mock_book_repository,
            problem_repository=mock_problem_repository,
            submission_repository=mock_submission_repository
        )
        
        assert isinstance(facade, SeedFacade)
        assert isinstance(facade.problem_seed_service, ProblemSeedService)
        assert isinstance(facade.judge_seed_service, JudgeSeedService)

    def test_create_seed_facade_without_judge(
        self, 
        mock_book_repository, 
        mock_problem_repository
    ):
        """Test factory function without judge service"""
        facade = create_seed_facade(
            book_repository=mock_book_repository,
            problem_repository=mock_problem_repository,
            submission_repository=None
        )
        
        assert isinstance(facade, SeedFacade)
        assert isinstance(facade.problem_seed_service, ProblemSeedService)
        assert facade.judge_seed_service is None

    def test_create_seed_facade_default_submission_repo(
        self, 
        mock_book_repository, 
        mock_problem_repository
    ):
        """Test factory function with default submission repository (None)"""
        facade = create_seed_facade(
            book_repository=mock_book_repository,
            problem_repository=mock_problem_repository
        )
        
        assert isinstance(facade, SeedFacade)
        assert isinstance(facade.problem_seed_service, ProblemSeedService)
        assert facade.judge_seed_service is None