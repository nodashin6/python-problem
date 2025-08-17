"""
Tests for Auth Domain Value Objects
認証ドメインバリューオブジェクトのテスト
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from ppauth.domain.value_objects.jwt_token import JWTClaims, JWTToken
from ppauth.domain.enums import UserRole


class TestJWTClaims:
    """Test JWTClaims value object"""

    def test_creation(self):
        """Test JWT claims creation"""
        user_id = str(uuid4())
        iat_time = datetime.now()
        exp_time = datetime.now() + timedelta(hours=1)
        
        claims = JWTClaims(
            user_id=user_id,
            email="test@example.com",
            user_name="testuser",
            display_name="Test User",
            role=UserRole.USER.value,
            iat=iat_time,
            exp=exp_time
        )
        
        assert claims.user_id == user_id
        assert claims.email == "test@example.com"
        assert claims.user_name == "testuser"
        assert claims.display_name == "Test User"
        assert claims.role == UserRole.USER.value
        assert claims.iat == iat_time
        assert claims.exp == exp_time

    def test_immutability(self):
        """Test that JWT claims are immutable"""
        claims = JWTClaims(
            user_id=str(uuid4()),
            email="test@example.com",
            user_name="testuser",
            display_name="Test User",
            role=UserRole.USER.value,
            iat=datetime.now(),
            exp=datetime.now() + timedelta(hours=1)
        )
        
        with pytest.raises(ValueError, match=".*frozen.*"):
            claims.user_id = "new_id"

    def test_expiry_check(self):
        """Test JWT claims expiry checking"""
        # Create expired claims
        expired_claims = JWTClaims(
            user_id=str(uuid4()),
            email="test@example.com",
            user_name="testuser",
            display_name="Test User",
            role=UserRole.USER.value,
            iat=datetime.now() - timedelta(hours=2),
            exp=datetime.now() - timedelta(hours=1)
        )
        
        assert expired_claims.is_expired()
        
        # Create valid claims
        valid_claims = JWTClaims(
            user_id=str(uuid4()),
            email="test@example.com",
            user_name="testuser",
            display_name="Test User",
            role=UserRole.USER.value,
            iat=datetime.now(),
            exp=datetime.now() + timedelta(hours=1)
        )
        
        assert not valid_claims.is_expired()

    def test_to_dict(self):
        """Test converting claims to dictionary"""
        user_id = str(uuid4())
        iat_time = datetime.now()
        exp_time = datetime.now() + timedelta(hours=1)
        
        claims = JWTClaims(
            user_id=user_id,
            email="test@example.com",
            user_name="testuser",
            display_name="Test User",
            role=UserRole.ADMIN.value,
            iat=iat_time,
            exp=exp_time
        )
        
        result = claims.to_dict()
        
        assert isinstance(result, dict)
        assert result["user_id"] == user_id
        assert result["email"] == "test@example.com"
        assert result["user_name"] == "testuser"
        assert result["display_name"] == "Test User"
        assert result["role"] == UserRole.ADMIN.value
        assert "iat" in result
        assert "exp" in result

    def test_from_dict(self):
        """Test creating claims from dictionary"""
        user_id = str(uuid4())
        iat_timestamp = datetime.now().timestamp()
        exp_timestamp = (datetime.now() + timedelta(hours=1)).timestamp()
        
        data = {
            "user_id": user_id,
            "email": "test@example.com",
            "user_name": "testuser",
            "display_name": "Test User",
            "role": UserRole.MODERATOR.value,
            "iat": iat_timestamp,
            "exp": exp_timestamp
        }
        
        claims = JWTClaims.from_dict(data)
        
        assert claims.user_id == user_id
        assert claims.email == "test@example.com"
        assert claims.user_name == "testuser"
        assert claims.display_name == "Test User"
        assert claims.role == UserRole.MODERATOR.value


class TestJWTToken:
    """Test JWTToken value object"""

    def test_creation(self):
        """Test JWT token creation"""
        token_string = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.signature"
        
        claims = JWTClaims(
            user_id=str(uuid4()),
            email="test@example.com",
            user_name="testuser",
            display_name="Test User",
            role=UserRole.USER.value,
            iat=datetime.now(),
            exp=datetime.now() + timedelta(hours=1)
        )
        
        token = JWTToken(
            raw_token=token_string,
            claims=claims
        )
        
        assert token.raw_token == token_string
        assert token.claims == claims
        assert isinstance(token.claims.exp, datetime)

    def test_immutability(self):
        """Test that JWT token is immutable"""
        claims = JWTClaims(
            user_id=str(uuid4()),
            email="test@example.com",
            user_name="testuser",
            display_name="Test User",
            role=UserRole.USER.value,
            iat=datetime.now(),
            exp=datetime.now() + timedelta(hours=1)
        )
        
        token = JWTToken(
            raw_token="test_token",
            claims=claims
        )
        
        with pytest.raises(ValueError, match=".*frozen.*"):
            token.raw_token = "new_token"

    def test_is_expired(self):
        """Test token expiry checking"""
        # Create expired token
        expired_claims = JWTClaims(
            user_id=str(uuid4()),
            email="test@example.com",
            user_name="testuser",
            display_name="Test User",
            role=UserRole.USER.value,
            iat=datetime.now() - timedelta(hours=2),
            exp=datetime.now() - timedelta(hours=1)
        )
        
        expired_token = JWTToken(
            raw_token="expired_token",
            claims=expired_claims
        )
        
        assert not expired_token.is_valid()
        
        # Create valid token
        valid_claims = JWTClaims(
            user_id=str(uuid4()),
            email="test@example.com",
            user_name="testuser",
            display_name="Test User",
            role=UserRole.USER.value,
            iat=datetime.now(),
            exp=datetime.now() + timedelta(hours=1)
        )
        
        valid_token = JWTToken(
            raw_token="valid_token",
            claims=valid_claims
        )
        
        assert valid_token.is_valid()

    def test_time_until_expiry(self):
        """Test token user info extraction"""
        user_id = str(uuid4())
        claims = JWTClaims(
            user_id=user_id,
            email="test@example.com",
            user_name="testuser",
            display_name="Test User",
            role=UserRole.ADMIN.value,
            iat=datetime.now(),
            exp=datetime.now() + timedelta(hours=1)
        )
        
        token = JWTToken(
            raw_token="test_token",
            claims=claims
        )
        
        assert token.get_user_id() == user_id
        assert token.get_user_email() == "test@example.com"
        assert token.get_user_role() == UserRole.ADMIN.value

    def test_refresh_token_type(self):
        """Test refresh token creation"""
        claims = JWTClaims(
            user_id=str(uuid4()),
            email="test@example.com",
            user_name="testuser",
            display_name="Test User",
            role=UserRole.USER.value,
            iat=datetime.now(),
            exp=datetime.now() + timedelta(days=7)
        )
        
        token = JWTToken(
            raw_token="refresh_token_string",
            claims=claims
        )
        
        assert token.raw_token == "refresh_token_string"
        assert token.claims.role == UserRole.USER.value

    def test_access_token_type(self):
        """Test access token creation"""
        claims = JWTClaims(
            user_id=str(uuid4()),
            email="test@example.com",
            user_name="testuser",
            display_name="Test User",
            role=UserRole.USER.value,
            iat=datetime.now(),
            exp=datetime.now() + timedelta(hours=1)
        )
        
        token = JWTToken(
            raw_token="access_token_string",
            claims=claims
        )
        
        assert token.raw_token == "access_token_string"
        assert token.claims.role == UserRole.USER.value

    def test_bearer_format(self):
        """Test token properties"""
        claims = JWTClaims(
            user_id=str(uuid4()),
            email="test@example.com",
            user_name="testuser",
            display_name="Test User",
            role=UserRole.USER.value,
            iat=datetime.now(),
            exp=datetime.now() + timedelta(hours=1)
        )
        
        token = JWTToken(
            raw_token="test_token_123",
            claims=claims
        )
        
        assert token.raw_token == "test_token_123"
        assert token.is_valid()