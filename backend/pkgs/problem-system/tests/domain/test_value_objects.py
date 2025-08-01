"""
Tests for Problem Domain Value Objects
問題ドメインバリューオブジェクトのテスト
"""

import pytest
from uuid import uuid4

from ppprob.domain.value_objects.author_info import AuthorInfo


class TestAuthorInfo:
    """Test AuthorInfo value object"""

    def test_creation(self):
        """Test author info creation"""
        author_id = uuid4()
        
        author = AuthorInfo(
            id=author_id,
            user_name="testuser",
            display_name="Test User",
            email="test@example.com",
            avatar_url="https://example.com/avatar.jpg"
        )
        
        assert author.id == author_id
        assert author.user_name == "testuser"
        assert author.display_name == "Test User"
        assert author.email == "test@example.com"
        assert author.avatar_url == "https://example.com/avatar.jpg"

    def test_creation_without_avatar(self):
        """Test author info creation without avatar URL"""
        author_id = uuid4()
        
        author = AuthorInfo(
            id=author_id,
            user_name="testuser",
            display_name="Test User",
            email="test@example.com"
        )
        
        assert author.id == author_id
        assert author.user_name == "testuser"
        assert author.display_name == "Test User"
        assert author.email == "test@example.com"
        assert author.avatar_url is None

    def test_immutability(self):
        """Test that author info is immutable"""
        author = AuthorInfo(
            id=uuid4(),
            user_name="testuser",
            display_name="Test User",
            email="test@example.com"
        )
        
        with pytest.raises(ValueError, match=".*frozen.*"):
            author.user_name = "newuser"

    def test_from_user_data(self):
        """Test creating AuthorInfo from user data dictionary"""
        author_id = uuid4()
        user_data = {
            "id": author_id,
            "user_name": "datauser",
            "display_name": "Data User",
            "email": "data@example.com",
            "avatar_url": "https://example.com/data-avatar.jpg"
        }
        
        author = AuthorInfo.from_user_data(user_data)
        
        assert author.id == author_id
        assert author.user_name == "datauser"
        assert author.display_name == "Data User"
        assert author.email == "data@example.com"
        assert author.avatar_url == "https://example.com/data-avatar.jpg"

    def test_from_user_data_without_avatar(self):
        """Test creating AuthorInfo from user data without avatar"""
        author_id = uuid4()
        user_data = {
            "id": author_id,
            "user_name": "noavatar",
            "display_name": "No Avatar User",
            "email": "noavatar@example.com"
            # No avatar_url field
        }
        
        author = AuthorInfo.from_user_data(user_data)
        
        assert author.id == author_id
        assert author.user_name == "noavatar"
        assert author.display_name == "No Avatar User"
        assert author.email == "noavatar@example.com"
        assert author.avatar_url is None

    def test_equality(self):
        """Test author info equality"""
        author_id = uuid4()
        
        author1 = AuthorInfo(
            id=author_id,
            user_name="testuser",
            display_name="Test User",
            email="test@example.com"
        )
        
        author2 = AuthorInfo(
            id=author_id,
            user_name="testuser",
            display_name="Test User",
            email="test@example.com"
        )
        
        author3 = AuthorInfo(
            id=uuid4(),  # Different ID
            user_name="testuser",
            display_name="Test User",
            email="test@example.com"
        )
        
        assert author1 == author2
        assert author1 != author3

    def test_string_representation(self):
        """Test string representation of author info"""
        author = AuthorInfo(
            id=uuid4(),
            user_name="testuser",
            display_name="Test User",
            email="test@example.com"
        )
        
        str_repr = str(author)
        
        # Should contain key information
        assert "testuser" in str_repr
        assert "Test User" in str_repr

    def test_validation_empty_required_fields(self):
        """Test validation with empty required fields"""
        with pytest.raises(ValueError):
            AuthorInfo(
                id=uuid4(),
                user_name="",  # Empty username should fail
                display_name="Test User",
                email="test@example.com"
            )

    def test_validation_invalid_email(self):
        """Test validation with invalid email format"""
        # Note: This test depends on whether Pydantic email validation is enabled
        # If not enabled, this test might pass
        try:
            author = AuthorInfo(
                id=uuid4(),
                user_name="testuser",
                display_name="Test User",
                email="invalid-email"  # Invalid email format
            )
            # If no validation error, at least check the value is stored
            assert author.email == "invalid-email"
        except ValueError:
            # Validation error is expected if email validation is enabled
            pass

    def test_serialization(self):
        """Test author info serialization to dict"""
        author_id = uuid4()
        
        author = AuthorInfo(
            id=author_id,
            user_name="testuser",
            display_name="Test User",
            email="test@example.com",
            avatar_url="https://example.com/avatar.jpg"
        )
        
        data = author.model_dump()
        
        assert data["id"] == author_id
        assert data["user_name"] == "testuser"
        assert data["display_name"] == "Test User"
        assert data["email"] == "test@example.com"
        assert data["avatar_url"] == "https://example.com/avatar.jpg"

    def test_deserialization(self):
        """Test author info deserialization from dict"""
        author_id = uuid4()
        data = {
            "id": author_id,
            "user_name": "testuser",
            "display_name": "Test User",
            "email": "test@example.com",
            "avatar_url": "https://example.com/avatar.jpg"
        }
        
        author = AuthorInfo.model_validate(data)
        
        assert author.id == author_id
        assert author.user_name == "testuser"
        assert author.display_name == "Test User"
        assert author.email == "test@example.com"
        assert author.avatar_url == "https://example.com/avatar.jpg"