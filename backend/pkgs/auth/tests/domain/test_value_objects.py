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
        exp_time = datetime.now() + timedelta(hours=1)
        
        claims = JWTClaims(
            user_id=user_id,
            email="test@example.com",
            exp=exp_time,
            role=UserRole.USER
        )
        
        assert claims.user_id == user_id
        assert claims.email == "test@example.com"
        assert claims.exp == exp_time
        assert claims.role == UserRole.USER

    def test_immutability(self):
        """Test that JWT claims are immutable"""
        claims = JWTClaims(
            user_id=str(uuid4()),
            email="test@example.com",
            exp=datetime.now() + timedelta(hours=1),
            role=UserRole.USER
        )
        
        with pytest.raises(ValueError, match=".*frozen.*"):
            claims.user_id = "new_id"

    def test_expiry_check(self):
        """Test JWT claims expiry checking"""
        # Create expired claims
        expired_claims = JWTClaims(
            user_id=str(uuid4()),
            email="test@example.com", 
            exp=datetime.now() - timedelta(hours=1),  # Expired
            role=UserRole.USER
        )
        
        assert expired_claims.is_expired()
        
        # Create valid claims
        valid_claims = JWTClaims(
            user_id=str(uuid4()),
            email="test@example.com",
            exp=datetime.now() + timedelta(hours=1),  # Not expired
            role=UserRole.USER
        )
        
        assert not valid_claims.is_expired()

    def test_to_dict(self):
        """Test converting claims to dictionary"""
        user_id = str(uuid4())
        exp_time = datetime.now() + timedelta(hours=1)
        
        claims = JWTClaims(
            user_id=user_id,
            email="test@example.com",
            exp=exp_time,
            role=UserRole.ADMIN
        )
        
        result = claims.to_dict()
        
        assert isinstance(result, dict)
        assert result["user_id"] == user_id
        assert result["email"] == "test@example.com"
        assert result["role"] == UserRole.ADMIN.value
        assert "exp" in result

    def test_from_dict(self):
        """Test creating claims from dictionary"""
        user_id = str(uuid4())
        exp_timestamp = (datetime.now() + timedelta(hours=1)).timestamp()
        
        data = {
            "user_id": user_id,
            "email": "test@example.com",
            "exp": exp_timestamp,
            "role": UserRole.MODERATOR.value
        }
        
        claims = JWTClaims.from_dict(data)
        
        assert claims.user_id == user_id
        assert claims.email == "test@example.com"
        assert claims.role == UserRole.MODERATOR


class TestJWTToken:
    """Test JWTToken value object"""

    def test_creation(self):
        """Test JWT token creation"""
        token_string = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.signature"
        
        token = JWTToken(
            token=token_string,
            expires_at=datetime.now() + timedelta(hours=1),
            token_type="access"
        )
        
        assert token.token == token_string
        assert token.token_type == "access"
        assert isinstance(token.expires_at, datetime)

    def test_immutability(self):
        """Test that JWT token is immutable"""
        token = JWTToken(
            token="test_token",
            expires_at=datetime.now() + timedelta(hours=1),
            token_type="access"
        )
        
        with pytest.raises(ValueError, match=".*frozen.*"):
            token.token = "new_token"

    def test_is_expired(self):
        """Test token expiry checking"""
        # Create expired token
        expired_token = JWTToken(
            token="expired_token",
            expires_at=datetime.now() - timedelta(hours=1),
            token_type="access"
        )
        
        assert expired_token.is_expired()
        
        # Create valid token
        valid_token = JWTToken(
            token="valid_token", 
            expires_at=datetime.now() + timedelta(hours=1),
            token_type="access"
        )
        
        assert not valid_token.is_expired()

    def test_time_until_expiry(self):
        """Test calculating time until expiry"""
        future_time = datetime.now() + timedelta(minutes=30)
        
        token = JWTToken(
            token="test_token",
            expires_at=future_time,
            token_type="access"
        )
        
        time_left = token.time_until_expiry()
        
        # Should be approximately 30 minutes (with some tolerance)
        assert timedelta(minutes=29) <= time_left <= timedelta(minutes=31)

    def test_refresh_token_type(self):
        """Test refresh token creation"""
        token = JWTToken(
            token="refresh_token_string",
            expires_at=datetime.now() + timedelta(days=7),
            token_type="refresh"
        )
        
        assert token.token_type == "refresh"
        assert token.is_refresh_token()
        assert not token.is_access_token()

    def test_access_token_type(self):
        """Test access token creation"""
        token = JWTToken(
            token="access_token_string",
            expires_at=datetime.now() + timedelta(hours=1),
            token_type="access"
        )
        
        assert token.token_type == "access"
        assert token.is_access_token()
        assert not token.is_refresh_token()

    def test_bearer_format(self):
        """Test getting token in Bearer format"""
        token = JWTToken(
            token="test_token_123",
            expires_at=datetime.now() + timedelta(hours=1),
            token_type="access"
        )
        
        bearer_token = token.to_bearer_format()
        
        assert bearer_token == "Bearer test_token_123"