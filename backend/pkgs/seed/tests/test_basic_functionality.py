"""
Basic functionality tests that don't require complex imports
"""


def test_sample_data_direct_import():
    """Test importing sample data directly"""
    import sys
    import os
    
    # Add the ppseed directory to path to avoid circular imports
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ppseed'))
    
    from sample_data import get_all_sample_data
    
    data = get_all_sample_data()
    
    assert isinstance(data, dict)
    assert "books" in data
    assert "problems" in data
    assert len(data["books"]) > 0
    assert len(data["problems"]) > 0
    
    # Clean up
    sys.path.pop(0)


def test_value_objects_direct_import():
    """Test importing value objects directly"""
    import sys
    import os
    
    # Add the ppseed directory to path to avoid circular imports
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ppseed'))
    
    from domain.value_objects.seed_result import SeedResult, SeedStatistics, TestCaseFileResult
    
    # Test SeedResult
    result = SeedResult(
        entity_type="test",
        total_processed=5,
        created_count=3,
        updated_count=1,
        skipped_count=1,
        errors=[],
        success=True
    )
    
    assert result.entity_type == "test"
    assert result.total_processed == 5
    assert result.is_successful is True
    assert result.success_rate == 0.8
    
    # Test SeedStatistics
    stats = SeedStatistics(
        books_total=5,
        books_by_difficulty={"beginner": 3},
        problems_total=10,
        problems_by_difficulty={"beginner": 6},
        problems_by_status={"published": 8},
        success=True
    )
    
    assert stats.books_total == 5
    assert stats.is_valid is True
    
    # Test TestCaseFileResult
    file_result = TestCaseFileResult(
        total_files=4,
        created_files=["/test/file1.txt", "/test/file2.txt"],
        errors=[],
        success=True,
        base_directory="/test"
    )
    
    assert file_result.total_files == 4
    assert file_result.created_count == 2
    assert file_result.is_successful is True
    
    # Clean up
    sys.path.pop(0)


def test_seed_result_error_cases():
    """Test SeedResult with error conditions"""
    import sys
    import os
    
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ppseed'))
    
    from domain.value_objects.seed_result import SeedResult
    
    # Test with errors
    result_with_errors = SeedResult(
        entity_type="test",
        total_processed=3,
        created_count=1,
        updated_count=0,
        skipped_count=1,
        errors=["Error 1", "Error 2"],
        success=False
    )
    
    assert result_with_errors.is_successful is False
    assert len(result_with_errors.errors) == 2
    assert result_with_errors.success_rate == 1/3
    
    # Test with zero processed
    empty_result = SeedResult(
        entity_type="empty",
        total_processed=0,
        created_count=0,
        updated_count=0,
        skipped_count=0,
        errors=[],
        success=True
    )
    
    assert empty_result.success_rate == 1.0
    
    sys.path.pop(0)


def test_sample_data_structure():
    """Test that sample data has the expected structure"""
    import sys
    import os
    
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ppseed'))
    
    from sample_data import (
        SAMPLE_BOOKS,
        SAMPLE_PROBLEMS,
        SAMPLE_USERS,
        SAMPLE_SUBMISSIONS,
        get_all_sample_data
    )
    
    # Test individual constants
    assert isinstance(SAMPLE_BOOKS, list)
    assert len(SAMPLE_BOOKS) > 0
    assert "id" in SAMPLE_BOOKS[0]
    assert "title" in SAMPLE_BOOKS[0]
    
    assert isinstance(SAMPLE_PROBLEMS, list)
    assert len(SAMPLE_PROBLEMS) > 0
    assert "id" in SAMPLE_PROBLEMS[0]
    assert "title" in SAMPLE_PROBLEMS[0]
    
    assert isinstance(SAMPLE_USERS, list)
    assert len(SAMPLE_USERS) > 0
    assert "id" in SAMPLE_USERS[0]
    assert "email" in SAMPLE_USERS[0]
    
    assert isinstance(SAMPLE_SUBMISSIONS, list)
    assert len(SAMPLE_SUBMISSIONS) > 0
    assert "id" in SAMPLE_SUBMISSIONS[0]
    assert "problem_id" in SAMPLE_SUBMISSIONS[0]
    
    # Test aggregated data
    all_data = get_all_sample_data()
    assert isinstance(all_data, dict)
    
    expected_keys = {
        "books", "problems", "problem_contents", 
        "users", "user_roles", "case_files", 
        "judge_cases", "submissions"
    }
    assert set(all_data.keys()) == expected_keys
    
    sys.path.pop(0)