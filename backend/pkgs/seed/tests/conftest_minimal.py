import pytest
from unittest.mock import AsyncMock

from ppseed.domain.value_objects import SeedResult, SeedStatistics, TestCaseFileResult


@pytest.fixture
def seed_result_success():
    """Successful seed result for testing"""
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
    return SeedResult(
        entity_type="test",
        total_processed=2,
        created_count=1,
        updated_count=0,
        skipped_count=0,
        errors=["Test error"],
        success=False
    )