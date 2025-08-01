"""
Tests for domain value objects
"""

from ppseed.domain.value_objects import SeedResult, SeedStatistics, TestCaseFileResult


class TestSeedResult:
    """Tests for SeedResult value object"""

    def test_seed_result_creation(self):
        """Test basic SeedResult creation"""
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

    def test_is_successful_property_true(self):
        """Test is_successful returns True when success=True and no errors"""
        result = SeedResult(
            entity_type="test",
            total_processed=2,
            created_count=2,
            updated_count=0,
            skipped_count=0,
            errors=[],
            success=True
        )
        
        assert result.is_successful is True

    def test_is_successful_property_false_with_errors(self):
        """Test is_successful returns False when there are errors"""
        result = SeedResult(
            entity_type="test",
            total_processed=2,
            created_count=1,
            updated_count=0,
            skipped_count=0,
            errors=["Test error"],
            success=True
        )
        
        assert result.is_successful is False

    def test_is_successful_property_false_when_failed(self):
        """Test is_successful returns False when success=False"""
        result = SeedResult(
            entity_type="test",
            total_processed=2,
            created_count=1,
            updated_count=0,
            skipped_count=0,
            errors=[],
            success=False
        )
        
        assert result.is_successful is False

    def test_success_rate_calculation(self):
        """Test success rate calculation"""
        result = SeedResult(
            entity_type="test",
            total_processed=10,
            created_count=6,
            updated_count=2,
            skipped_count=2,
            errors=[],
            success=True
        )
        
        # (6 + 2) / 10 = 0.8
        assert result.success_rate == 0.8

    def test_success_rate_zero_processed(self):
        """Test success rate when no items processed"""
        result = SeedResult(
            entity_type="test",
            total_processed=0,
            created_count=0,
            updated_count=0,
            skipped_count=0,
            errors=[],
            success=True
        )
        
        assert result.success_rate == 1.0


class TestSeedStatistics:
    """Tests for SeedStatistics value object"""

    def test_seed_statistics_creation(self):
        """Test basic SeedStatistics creation"""
        stats = SeedStatistics(
            books_total=5,
            books_by_difficulty={"beginner": 3, "intermediate": 2},
            problems_total=10,
            problems_by_difficulty={"beginner": 6, "intermediate": 4},
            problems_by_status={"published": 8, "draft": 2},
            success=True
        )
        
        assert stats.books_total == 5
        assert stats.books_by_difficulty == {"beginner": 3, "intermediate": 2}
        assert stats.problems_total == 10
        assert stats.problems_by_difficulty == {"beginner": 6, "intermediate": 4}
        assert stats.problems_by_status == {"published": 8, "draft": 2}
        assert stats.success is True
        assert stats.error is None

    def test_seed_statistics_with_error(self):
        """Test SeedStatistics with error"""
        stats = SeedStatistics(
            books_total=0,
            books_by_difficulty={},
            problems_total=0,
            problems_by_difficulty={},
            problems_by_status={},
            success=False,
            error="Database connection failed"
        )
        
        assert stats.success is False
        assert stats.error == "Database connection failed"

    def test_is_valid_property_true(self):
        """Test is_valid returns True when success=True and no error"""
        stats = SeedStatistics(
            books_total=5,
            books_by_difficulty={},
            problems_total=10,
            problems_by_difficulty={},
            problems_by_status={},
            success=True
        )
        
        assert stats.is_valid is True

    def test_is_valid_property_false_with_error(self):
        """Test is_valid returns False when there's an error"""
        stats = SeedStatistics(
            books_total=0,
            books_by_difficulty={},
            problems_total=0,
            problems_by_difficulty={},
            problems_by_status={},
            success=True,
            error="Some error"
        )
        
        assert stats.is_valid is False

    def test_is_valid_property_false_when_failed(self):
        """Test is_valid returns False when success=False"""
        stats = SeedStatistics(
            books_total=0,
            books_by_difficulty={},
            problems_total=0,
            problems_by_difficulty={},
            problems_by_status={},
            success=False
        )
        
        assert stats.is_valid is False


class TestTestCaseFileResult:
    """Tests for TestCaseFileResult value object"""

    def test_test_case_file_result_creation(self):
        """Test basic TestCaseFileResult creation"""
        result = TestCaseFileResult(
            total_files=6,
            created_files=["/test/input1.txt", "/test/output1.txt", "/test/input2.txt"],
            errors=[],
            success=True,
            base_directory="/test"
        )
        
        assert result.total_files == 6
        assert len(result.created_files) == 3
        assert result.errors == []
        assert result.success is True
        assert result.base_directory == "/test"

    def test_created_count_property(self):
        """Test created_count property"""
        result = TestCaseFileResult(
            total_files=4,
            created_files=["/test/file1.txt", "/test/file2.txt"],
            errors=[],
            success=True
        )
        
        assert result.created_count == 2

    def test_is_successful_property_true(self):
        """Test is_successful returns True when success=True and no errors"""
        result = TestCaseFileResult(
            total_files=2,
            created_files=["/test/file1.txt"],
            errors=[],
            success=True
        )
        
        assert result.is_successful is True

    def test_is_successful_property_false_with_errors(self):
        """Test is_successful returns False when there are errors"""
        result = TestCaseFileResult(
            total_files=2,
            created_files=["/test/file1.txt"],
            errors=["Failed to create file2.txt"],
            success=True
        )
        
        assert result.is_successful is False

    def test_is_successful_property_false_when_failed(self):
        """Test is_successful returns False when success=False"""
        result = TestCaseFileResult(
            total_files=2,
            created_files=[],
            errors=[],
            success=False
        )
        
        assert result.is_successful is False

    def test_empty_created_files(self):
        """Test with empty created_files list"""
        result = TestCaseFileResult(
            total_files=5,
            created_files=[],
            errors=["All file creations failed"],
            success=False
        )
        
        assert result.created_count == 0
        assert result.is_successful is False