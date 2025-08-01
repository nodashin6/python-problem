# ppseed Tests

This directory contains comprehensive tests for the `ppseed` package, which handles data seeding functionality for the competitive programming platform.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py                     # Test fixtures and configuration
├── pytest.ini                     # Pytest configuration
├── test_basic_functionality.py    # Basic functionality tests (working)
├── test_integration.py            # Integration tests
├── test_sample_data.py            # Sample data validation tests
├── app/
│   ├── __init__.py
│   └── test_seed_facade.py        # SeedFacade tests
├── domain/
│   ├── __init__.py
│   ├── test_value_objects.py      # Value objects tests
│   └── services/
│       ├── __init__.py
│       ├── test_problem_seed_service.py
│       └── test_judge_seed_service.py
└── usecase/
    ├── __init__.py
    └── test_seed_usecase.py        # UseCase tests
```

## Running Tests

### Basic Functionality Tests (Currently Working)
```bash
cd /mnt/d/nodashin/python-problem/backend/pkgs/seed
poetry run pytest tests/test_basic_functionality.py -v
```

These tests verify:
- ✅ Sample data creation and structure
- ✅ Value objects (SeedResult, SeedStatistics, TestCaseFileResult)
- ✅ Error handling in value objects
- ✅ Data validation and relationships

### Full Test Suite (Requires dependency fixes)
```bash
poetry run pytest -v
```

## Test Categories

### Unit Tests
- **Value Objects** (`test_value_objects.py`): Tests for domain value objects
- **Domain Services** (`test_problem_seed_service.py`, `test_judge_seed_service.py`): Tests for domain services
- **Use Cases** (`test_seed_usecase.py`): Tests for application use cases
- **Facade** (`test_seed_facade.py`): Tests for application facade

### Integration Tests
- **Full Workflow** (`test_integration.py`): End-to-end seeding workflows
- **Sample Data** (`test_sample_data.py`): Sample data validation and relationships

## Test Features

### Comprehensive Mocking
- Mock repositories for isolated testing
- AsyncMock for async operations
- Test data fixtures for consistent testing

### Test Markers
- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests  
- `@pytest.mark.slow`: Slow tests

### Coverage Areas
1. **Domain Value Objects**
   - SeedResult creation and properties
   - SeedStatistics validation
   - TestCaseFileResult file tracking

2. **Domain Services**
   - ProblemSeedService book/problem seeding
   - JudgeSeedService submission/test case seeding
   - Error handling and statistics

3. **Use Cases**
   - Complete dataset seeding
   - Problems-only seeding
   - Judge-only seeding
   - Statistics retrieval

4. **Application Facade**
   - Simplified API interface
   - Factory functions
   - Integration coordination

5. **Sample Data**
   - Data structure validation
   - Relationship integrity
   - UUID format verification

## Current Status

### ✅ Working Tests
- `test_basic_functionality.py` - 4/4 tests passing
- Core value objects functionality
- Sample data validation
- Direct imports without circular dependencies

### ⚠️ Tests Requiring Fixes
- Complex integration tests require dependency resolution
- Cross-package imports need circular dependency fixes
- Repository interface alignment needed

## Key Implementation Features

### Domain-Driven Design (DDD)
- Clear separation of concerns
- Value objects for immutable data
- Domain services for business logic
- Use cases for application workflows

### Async/Await Support
- All repository operations are async
- Proper error handling for async operations
- Mock support for async testing

### Comprehensive Error Handling
- Detailed error reporting in results
- Graceful degradation on failures
- Statistics tracking for success rates

### Factory Pattern
- Service factories for dependency injection
- Facade factory for simplified creation
- Mock factories for testing

## Test Data

The tests use realistic sample data including:
- Books with different difficulty levels
- Problems with multilingual content
- Users with role assignments
- Judge cases and test files
- Submissions with various languages

All test data maintains referential integrity and follows UUID conventions.

## Future Improvements

1. **Dependency Resolution**: Fix circular import issues for full test suite
2. **Performance Tests**: Add performance benchmarks for large datasets
3. **Database Integration**: Add tests with real database connections
4. **Concurrency Tests**: Test concurrent seeding operations
5. **Configuration Tests**: Test different configuration scenarios