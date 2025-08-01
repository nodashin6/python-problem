"""
Simple tests for domain value objects (no external dependencies)
"""


def test_seed_result_creation():
    """Test basic SeedResult creation"""
    from ppseed.domain.value_objects import SeedResult
    
    result = SeedResult(
        entity_type="books",
        total_processed=5,
        created_count=3,
        updated_count=1,
        skipped_count=1,
        errors=[],
        success=True
    )
    
    assert result.entity_type == "books"
    assert result.total_processed == 5
    assert result.created_count == 3
    assert result.updated_count == 1
    assert result.skipped_count == 1
    assert result.errors == []
    assert result.success is True


def test_seed_result_is_successful():
    """Test is_successful property"""
    from ppseed.domain.value_objects import SeedResult
    
    # Success case
    result1 = SeedResult(
        entity_type="test",
        total_processed=2,
        created_count=2,
        updated_count=0,
        skipped_count=0,
        errors=[],
        success=True
    )
    assert result1.is_successful is True
    
    # Error case
    result2 = SeedResult(
        entity_type="test",
        total_processed=2,
        created_count=1,
        updated_count=0,
        skipped_count=0,
        errors=["Test error"],
        success=True
    )
    assert result2.is_successful is False


def test_seed_result_success_rate():
    """Test success rate calculation"""
    from ppseed.domain.value_objects import SeedResult
    
    result = SeedResult(
        entity_type="test",
        total_processed=10,
        created_count=6,
        updated_count=2,
        skipped_count=2,
        errors=[],
        success=True
    )
    
    assert result.success_rate == 0.8


def test_seed_statistics_creation():
    """Test SeedStatistics creation"""
    from ppseed.domain.value_objects import SeedStatistics
    
    stats = SeedStatistics(
        books_total=5,
        books_by_difficulty={"beginner": 3, "intermediate": 2},
        problems_total=10,
        problems_by_difficulty={"beginner": 6, "intermediate": 4},
        problems_by_status={"published": 8, "draft": 2},
        success=True
    )
    
    assert stats.books_total == 5
    assert stats.problems_total == 10
    assert stats.success is True
    assert stats.is_valid is True


def test_test_case_file_result_creation():
    """Test TestCaseFileResult creation"""
    from ppseed.domain.value_objects import TestCaseFileResult
    
    result = TestCaseFileResult(
        total_files=6,
        created_files=["/test/input1.txt", "/test/output1.txt"],
        errors=[],
        success=True,
        base_directory="/test"
    )
    
    assert result.total_files == 6
    assert result.created_count == 2
    assert result.success is True
    assert result.is_successful is True


def test_sample_data_function():
    """Test sample data function works"""
    from ppseed.sample_data import get_all_sample_data
    
    data = get_all_sample_data()
    
    assert isinstance(data, dict)
    assert "books" in data
    assert "problems" in data
    assert len(data["books"]) > 0
    assert len(data["problems"]) > 0