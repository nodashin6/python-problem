import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def mock_book_repository():
    """Mock book repository for testing"""
    mock = AsyncMock()
    mock.find_published.return_value = []
    mock.count_published.return_value = 0
    mock.find_by_title.return_value = None
    mock.create.return_value = MagicMock()
    mock.delete_all.return_value = None
    return mock


@pytest.fixture
def mock_problem_repository():
    """Mock problem repository for testing"""
    mock = AsyncMock()
    mock.find_published.return_value = []
    mock.find_by_title.return_value = None
    mock.create.return_value = MagicMock()
    return mock


@pytest.fixture
def mock_submission_repository():
    """Mock submission repository for testing"""
    mock = AsyncMock()
    mock.find_recent.return_value = []
    mock.find_by_id.return_value = None
    mock.save.return_value = MagicMock()
    return mock


@pytest.fixture
def sample_books_data():
    """Sample books data for testing"""
    return [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "title": "Test Book 1",
            "author_id": "test-author-1",
            "published_at": "2025-01-01T00:00:00Z",
        },
        {
            "id": "550e8400-e29b-41d4-a716-446655440001", 
            "title": "Test Book 2",
            "author_id": "test-author-2",
            "published_at": "2025-01-02T00:00:00Z",
        }
    ]


@pytest.fixture
def sample_problems_data():
    """Sample problems data for testing"""
    return [
        {
            "id": "550e8400-e29b-41d4-a716-446655440010",
            "book_id": "550e8400-e29b-41d4-a716-446655440000",
            "title": "Test Problem 1",
            "description": "Test problem description",
            "tags": ["test"],
            "published_at": "2025-01-01T00:00:00Z",
            "content_markdown": "# Test Problem\nThis is a test problem."
        }
    ]


@pytest.fixture
def sample_submissions_data():
    """Sample submissions data for testing"""
    return [
        {
            "id": "750e8400-e29b-41d4-a716-446655440001",
            "problem_id": "550e8400-e29b-41d4-a716-446655440010",
            "user_id": "user-1",
            "language": "python",
            "source_code": "print('Hello')",
            "status": "completed"
        }
    ]


@pytest.fixture
def seed_result_success():
    """Successful seed result for testing"""
    from ppseed.domain.value_objects import SeedResult
    return SeedResult(
        entity_type="test",
        total_processed=2,
        created_count=2,
        updated_count=0,
        skipped_count=0,
        errors=[],
        success=True
    )


@pytest.fixture
def seed_result_with_errors():
    """Seed result with errors for testing"""
    from ppseed.domain.value_objects import SeedResult
    return SeedResult(
        entity_type="test",
        total_processed=2,
        created_count=1,
        updated_count=0,
        skipped_count=0,
        errors=["Test error"],
        success=False
    )


@pytest.fixture
def seed_statistics():
    """Sample seed statistics for testing"""
    from ppseed.domain.value_objects import SeedStatistics
    return SeedStatistics(
        books_total=2,
        books_by_difficulty={"beginner": 1, "intermediate": 1},
        problems_total=3,
        problems_by_difficulty={"beginner": 2, "intermediate": 1},
        problems_by_status={"published": 3},
        success=True
    )


@pytest.fixture
def test_case_file_result():
    """Sample test case file result for testing"""
    from ppseed.domain.value_objects import TestCaseFileResult
    return TestCaseFileResult(
        total_files=4,
        created_files=["/test/input1.txt", "/test/output1.txt"],
        errors=[],
        success=True,
        base_directory="/test"
    )