"""
Tests for Problem Content Validator
問題コンテンツバリデーターのテスト

Author: Judge System Team
Date: 2025-06-30
"""

import pytest

from ppprob.domain.helpers.validator.problem_validator import ProblemContentValidator


class TestProblemContentValidator:
    """ProblemContentValidatorのテストクラス"""

    def test_validate_markdown_content_valid_content(self):
        """有効なMarkdownコンテンツのテスト"""
        # Arrange
        valid_content = """
# 問題タイトル

問題の説明文です。

## 入力

```python
input_data = "test"
```

## 出力

```python
print("result")
```
"""

        # Act
        result = ProblemContentValidator.validate_markdown_content(valid_content)

        # Assert
        assert result["is_valid"] is True
        assert len(result["issues"]) == 0
        assert result["content_length"] > 0

    def test_validate_markdown_content_empty_content(self):
        """空のコンテンツのテスト"""
        # Arrange
        empty_content = ""

        # Act
        result = ProblemContentValidator.validate_markdown_content(empty_content)

        # Assert
        assert result["is_valid"] is False
        assert "Content cannot be empty" in result["issues"]
        assert result["content_length"] == 0

    def test_validate_markdown_content_whitespace_only(self):
        """空白のみのコンテンツのテスト"""
        # Arrange
        whitespace_content = "   \n\t  \n  "

        # Act
        result = ProblemContentValidator.validate_markdown_content(whitespace_content)

        # Assert
        assert result["is_valid"] is False
        assert "Content cannot be empty" in result["issues"]

    def test_validate_markdown_content_no_heading(self):
        """見出しがないコンテンツのテスト"""
        # Arrange
        no_heading_content = """
問題の説明文です。

```python
print("test")
```
"""

        # Act
        result = ProblemContentValidator.validate_markdown_content(no_heading_content)

        # Assert
        assert result["is_valid"] is False
        assert "Content should contain at least one heading" in result["issues"]

    def test_validate_markdown_content_no_code_blocks(self):
        """コードブロックがないコンテンツのテスト"""
        # Arrange
        no_code_content = """
# 問題タイトル

問題の説明文です。
"""

        # Act
        result = ProblemContentValidator.validate_markdown_content(no_code_content)

        # Assert
        assert result["is_valid"] is False
        assert "Content should contain code examples in code blocks" in result["issues"]

    def test_validate_markdown_content_multiple_issues(self):
        """複数の問題があるコンテンツのテスト"""
        # Arrange
        invalid_content = "問題の説明文です。"

        # Act
        result = ProblemContentValidator.validate_markdown_content(invalid_content)

        # Assert
        assert result["is_valid"] is False
        assert len(result["issues"]) == 2
        assert "Content should contain at least one heading" in result["issues"]
        assert "Content should contain code examples in code blocks" in result["issues"]

    def test_validate_problem_title_valid_title(self):
        """有効なタイトルのテスト"""
        # Arrange
        valid_title = "有効な問題タイトル"

        # Act
        result = ProblemContentValidator.validate_problem_title(valid_title)

        # Assert
        assert result["is_valid"] is True
        assert len(result["issues"]) == 0

    def test_validate_problem_title_empty_title(self):
        """空のタイトルのテスト"""
        # Arrange
        empty_title = ""

        # Act
        result = ProblemContentValidator.validate_problem_title(empty_title)

        # Assert
        assert result["is_valid"] is False
        assert "Title cannot be empty" in result["issues"]

    def test_validate_problem_title_whitespace_only(self):
        """空白のみのタイトルのテスト"""
        # Arrange
        whitespace_title = "   \n\t  "

        # Act
        result = ProblemContentValidator.validate_problem_title(whitespace_title)

        # Assert
        assert result["is_valid"] is False
        assert "Title cannot be empty" in result["issues"]

    def test_validate_problem_title_too_long(self):
        """長すぎるタイトルのテスト"""
        # Arrange
        long_title = "a" * 201  # 201文字

        # Act
        result = ProblemContentValidator.validate_problem_title(long_title)

        # Assert
        assert result["is_valid"] is False
        assert "Title is too long (max 200 characters)" in result["issues"]

    def test_validate_problem_title_too_short(self):
        """短すぎるタイトルのテスト"""
        # Arrange
        short_title = "a"  # 1文字

        # Act
        result = ProblemContentValidator.validate_problem_title(short_title)

        # Assert
        assert result["is_valid"] is False
        assert "Title is too short (min 5 characters)" in result["issues"]

    def test_validate_problem_title_boundary_cases(self):
        """境界値のタイトルテスト"""
        # 5文字（最小有効長）
        min_title = "12345"
        result = ProblemContentValidator.validate_problem_title(min_title)
        assert result["is_valid"] is True

        # 200文字（最大有効長）
        max_title = "a" * 200
        result = ProblemContentValidator.validate_problem_title(max_title)
        assert result["is_valid"] is True

    def test_validate_tags_valid_tags(self):
        """有効なタグのテスト"""
        # Arrange
        valid_tags = ["python", "algorithm", "easy"]

        # Act
        result = ProblemContentValidator.validate_tags(valid_tags)

        # Assert
        assert result["is_valid"] is True
        assert len(result["issues"]) == 0

    def test_validate_tags_empty_list(self):
        """空のタグリストのテスト"""
        # Arrange
        empty_tags = []

        # Act
        result = ProblemContentValidator.validate_tags(empty_tags)

        # Assert
        assert result["is_valid"] is True
        assert len(result["issues"]) == 0

    def test_validate_tags_too_many_tags(self):
        """タグが多すぎる場合のテスト"""
        # Arrange
        too_many_tags = [f"tag{i}" for i in range(11)]  # 11個のタグ

        # Act
        result = ProblemContentValidator.validate_tags(too_many_tags)

        # Assert
        assert result["is_valid"] is False
        assert "Too many tags (max 10)" in result["issues"]

    def test_validate_tags_empty_tag(self):
        """空のタグが含まれる場合のテスト"""
        # Arrange
        tags_with_empty = ["valid_tag", "", "another_tag"]

        # Act
        result = ProblemContentValidator.validate_tags(tags_with_empty)

        # Assert
        assert result["is_valid"] is False
        assert "Tags cannot be empty" in result["issues"]

    def test_validate_tags_whitespace_tag(self):
        """空白のみのタグが含まれる場合のテスト"""
        # Arrange
        tags_with_whitespace = ["valid_tag", "   ", "another_tag"]

        # Act
        result = ProblemContentValidator.validate_tags(tags_with_whitespace)

        # Assert
        assert result["is_valid"] is False
        assert "Tags cannot be empty" in result["issues"]

    def test_validate_tags_too_long_tag(self):
        """長すぎるタグが含まれる場合のテスト"""
        # Arrange
        long_tag = "a" * 51  # 51文字
        tags_with_long = ["valid_tag", long_tag]

        # Act
        result = ProblemContentValidator.validate_tags(tags_with_long)

        # Assert
        assert result["is_valid"] is False
        assert f"Tag '{long_tag}' is too long (max 50 characters)" in result["issues"]

    def test_validate_tags_boundary_cases(self):
        """タグの境界値テスト"""
        # 10個のタグ（最大有効数）
        max_tags = [f"tag{i}" for i in range(10)]
        result = ProblemContentValidator.validate_tags(max_tags)
        assert result["is_valid"] is True

        # 50文字のタグ（最大有効長）
        max_length_tag = "a" * 50
        result = ProblemContentValidator.validate_tags([max_length_tag])
        assert result["is_valid"] is True
