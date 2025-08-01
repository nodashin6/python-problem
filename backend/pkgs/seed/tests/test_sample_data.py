"""
Tests for sample data module
"""

from ppseed.sample_data import (
    SAMPLE_BOOKS,
    SAMPLE_PROBLEMS,
    SAMPLE_PROBLEM_CONTENTS,
    SAMPLE_USERS,
    SAMPLE_USER_ROLES,
    SAMPLE_CASE_FILES,
    SAMPLE_JUDGE_CASES,
    SAMPLE_SUBMISSIONS,
    get_all_sample_data
)


class TestSampleDataConstants:
    """Tests for sample data constants"""

    def test_sample_books_structure(self):
        """Test SAMPLE_BOOKS has correct structure"""
        assert isinstance(SAMPLE_BOOKS, list)
        assert len(SAMPLE_BOOKS) > 0
        
        for book in SAMPLE_BOOKS:
            assert isinstance(book, dict)
            assert "id" in book
            assert "title" in book
            assert "description" in book
            assert "author" in book
            assert "difficulty_level" in book
            assert "is_public" in book

    def test_sample_problems_structure(self):
        """Test SAMPLE_PROBLEMS has correct structure"""
        assert isinstance(SAMPLE_PROBLEMS, list)
        assert len(SAMPLE_PROBLEMS) > 0
        
        for problem in SAMPLE_PROBLEMS:
            assert isinstance(problem, dict)
            assert "id" in problem
            assert "book_id" in problem
            assert "title" in problem
            assert "description" in problem
            assert "difficulty_level" in problem
            assert "status" in problem
            assert "created_by" in problem

    def test_sample_problem_contents_structure(self):
        """Test SAMPLE_PROBLEM_CONTENTS has correct structure"""
        assert isinstance(SAMPLE_PROBLEM_CONTENTS, list)
        assert len(SAMPLE_PROBLEM_CONTENTS) > 0
        
        for content in SAMPLE_PROBLEM_CONTENTS:
            assert isinstance(content, dict)
            assert "problem_id" in content
            assert "language" in content
            assert "statement" in content
            assert "input_format" in content
            assert "output_format" in content
            assert "sample_input" in content
            assert "sample_output" in content

    def test_sample_users_structure(self):
        """Test SAMPLE_USERS has correct structure"""
        assert isinstance(SAMPLE_USERS, list)
        assert len(SAMPLE_USERS) > 0
        
        for user in SAMPLE_USERS:
            assert isinstance(user, dict)
            assert "id" in user
            assert "email" in user
            assert "user_name" in user
            assert "display_name" in user

    def test_sample_user_roles_structure(self):
        """Test SAMPLE_USER_ROLES has correct structure"""
        assert isinstance(SAMPLE_USER_ROLES, list)
        assert len(SAMPLE_USER_ROLES) > 0
        
        for role in SAMPLE_USER_ROLES:
            assert isinstance(role, dict)
            assert "user_id" in role
            assert "role" in role

    def test_sample_case_files_structure(self):
        """Test SAMPLE_CASE_FILES has correct structure"""
        assert isinstance(SAMPLE_CASE_FILES, list)
        assert len(SAMPLE_CASE_FILES) > 0
        
        for case_file in SAMPLE_CASE_FILES:
            assert isinstance(case_file, dict)
            assert "id" in case_file
            assert "url" in case_file
            assert "file_hash" in case_file

    def test_sample_judge_cases_structure(self):
        """Test SAMPLE_JUDGE_CASES has correct structure"""
        assert isinstance(SAMPLE_JUDGE_CASES, list)
        assert len(SAMPLE_JUDGE_CASES) > 0
        
        for judge_case in SAMPLE_JUDGE_CASES:
            assert isinstance(judge_case, dict)
            assert "problem_id" in judge_case
            assert "input_id" in judge_case
            assert "output_id" in judge_case
            assert "is_sample" in judge_case
            assert "display_order" in judge_case

    def test_sample_submissions_structure(self):
        """Test SAMPLE_SUBMISSIONS has correct structure"""
        assert isinstance(SAMPLE_SUBMISSIONS, list)
        assert len(SAMPLE_SUBMISSIONS) > 0
        
        for submission in SAMPLE_SUBMISSIONS:
            assert isinstance(submission, dict)
            assert "id" in submission
            assert "problem_id" in submission
            assert "user_id" in submission
            assert "language" in submission
            assert "source_code" in submission
            assert "status" in submission


class TestSampleDataRelationships:
    """Tests for relationships between sample data"""

    def test_problems_reference_valid_books(self):
        """Test that problems reference existing books"""
        book_ids = {book["id"] for book in SAMPLE_BOOKS}
        
        for problem in SAMPLE_PROBLEMS:
            assert problem["book_id"] in book_ids

    def test_problem_contents_reference_valid_problems(self):
        """Test that problem contents reference existing problems"""
        problem_ids = {problem["id"] for problem in SAMPLE_PROBLEMS}
        
        for content in SAMPLE_PROBLEM_CONTENTS:
            assert content["problem_id"] in problem_ids

    def test_user_roles_reference_valid_users(self):
        """Test that user roles reference existing users"""
        user_ids = {user["id"] for user in SAMPLE_USERS}
        
        for role in SAMPLE_USER_ROLES:
            assert role["user_id"] in user_ids

    def test_judge_cases_reference_valid_problems_and_files(self):
        """Test that judge cases reference existing problems and case files"""
        problem_ids = {problem["id"] for problem in SAMPLE_PROBLEMS}
        case_file_ids = {case_file["id"] for case_file in SAMPLE_CASE_FILES}
        
        for judge_case in SAMPLE_JUDGE_CASES:
            assert judge_case["problem_id"] in problem_ids
            assert judge_case["input_id"] in case_file_ids
            assert judge_case["output_id"] in case_file_ids

    def test_submissions_reference_valid_problems_and_users(self):
        """Test that submissions reference existing problems and users"""
        problem_ids = {problem["id"] for problem in SAMPLE_PROBLEMS}
        user_ids = {user["id"] for user in SAMPLE_USERS}
        
        for submission in SAMPLE_SUBMISSIONS:
            assert submission["problem_id"] in problem_ids
            assert submission["user_id"] in user_ids

    def test_problems_reference_valid_creators(self):
        """Test that problems reference valid user creators"""
        user_ids = {user["id"] for user in SAMPLE_USERS}
        
        for problem in SAMPLE_PROBLEMS:
            assert problem["created_by"] in user_ids


class TestGetAllSampleData:
    """Tests for get_all_sample_data function"""

    def test_get_all_sample_data_returns_dict(self):
        """Test that get_all_sample_data returns a dictionary"""
        result = get_all_sample_data()
        assert isinstance(result, dict)

    def test_get_all_sample_data_contains_all_keys(self):
        """Test that get_all_sample_data contains all expected keys"""
        result = get_all_sample_data()
        
        expected_keys = {
            "books",
            "problems",
            "problem_contents",
            "users",
            "user_roles",
            "case_files",
            "judge_cases",
            "submissions"
        }
        
        assert set(result.keys()) == expected_keys

    def test_get_all_sample_data_values_are_lists(self):
        """Test that all values in get_all_sample_data are lists"""
        result = get_all_sample_data()
        
        for key, value in result.items():
            assert isinstance(value, list), f"Value for key '{key}' is not a list"

    def test_get_all_sample_data_contains_expected_data(self):
        """Test that get_all_sample_data contains the expected sample data"""
        result = get_all_sample_data()
        
        assert result["books"] == SAMPLE_BOOKS
        assert result["problems"] == SAMPLE_PROBLEMS
        assert result["problem_contents"] == SAMPLE_PROBLEM_CONTENTS
        assert result["users"] == SAMPLE_USERS
        assert result["user_roles"] == SAMPLE_USER_ROLES
        assert result["case_files"] == SAMPLE_CASE_FILES
        assert result["judge_cases"] == SAMPLE_JUDGE_CASES
        assert result["submissions"] == SAMPLE_SUBMISSIONS

    def test_get_all_sample_data_is_consistent(self):
        """Test that get_all_sample_data returns consistent data across calls"""
        result1 = get_all_sample_data()
        result2 = get_all_sample_data()
        
        assert result1 == result2

    def test_sample_data_has_sufficient_test_data(self):
        """Test that sample data has sufficient variety for testing"""
        result = get_all_sample_data()
        
        # Should have multiple books with different difficulty levels
        assert len(result["books"]) >= 2
        difficulty_levels = {book["difficulty_level"] for book in result["books"]}
        assert len(difficulty_levels) >= 2
        
        # Should have multiple problems
        assert len(result["problems"]) >= 2
        
        # Should have both sample and non-sample judge cases
        judge_case_types = {case.get("is_sample", False) for case in result["judge_cases"]}
        assert True in judge_case_types
        assert False in judge_case_types

    def test_sample_data_uuids_are_valid_format(self):
        """Test that UUIDs in sample data follow valid format"""
        import re
        uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
        
        result = get_all_sample_data()
        
        # Check book IDs
        for book in result["books"]:
            assert uuid_pattern.match(book["id"]), f"Invalid UUID format: {book['id']}"
        
        # Check problem IDs
        for problem in result["problems"]:
            assert uuid_pattern.match(problem["id"]), f"Invalid UUID format: {problem['id']}"
            assert uuid_pattern.match(problem["book_id"]), f"Invalid UUID format: {problem['book_id']}"
        
        # Check user IDs
        for user in result["users"]:
            assert uuid_pattern.match(user["id"]), f"Invalid UUID format: {user['id']}"