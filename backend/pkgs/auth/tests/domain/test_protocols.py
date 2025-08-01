"""
Tests for Auth Domain Protocols
認証ドメインプロトコルのテスト
"""

import pytest
from typing import Dict, Any

from ppauth.domain.protocols import (
    CryptoProvider, 
    JWTEncoder, 
    Logger,
    AuthConfig,
    DatabaseConfig,
    JWTConfig,
    PasswordConfig,
    ConfigurationProvider
)


class TestConfigurationValueObjects:
    """Test configuration value objects"""

    def test_database_config_creation(self):
        """Test DatabaseConfig creation"""
        config = DatabaseConfig(
            url="postgresql://localhost:5432/auth",
            key="secret_key",
            timeout=30.0,
            max_connections=20
        )
        
        assert config.url == "postgresql://localhost:5432/auth"
        assert config.key == "secret_key"
        assert config.timeout == 30.0
        assert config.max_connections == 20

    def test_jwt_config_creation(self):
        """Test JWTConfig creation"""
        config = JWTConfig(
            secret_key="jwt_secret",
            algorithm="HS256",
            access_token_expire_minutes=60,
            refresh_token_expire_days=30
        )
        
        assert config.secret_key == "jwt_secret"
        assert config.algorithm == "HS256"
        assert config.access_token_expire_minutes == 60
        assert config.refresh_token_expire_days == 30

    def test_password_config_creation(self):
        """Test PasswordConfig creation"""
        config = PasswordConfig(
            salt_length=32,
            iterations=100000,
            hash_length=64
        )
        
        assert config.salt_length == 32
        assert config.iterations == 100000
        assert config.hash_length == 64

    def test_auth_config_creation(self):
        """Test AuthConfig creation"""
        db_config = DatabaseConfig(url="test", key="key")
        jwt_config = JWTConfig(secret_key="secret")
        pwd_config = PasswordConfig()
        
        auth_config = AuthConfig(
            database=db_config,
            jwt=jwt_config,
            password=pwd_config,
            enable_refresh_tokens=True,
            max_login_attempts=3
        )
        
        assert auth_config.database == db_config
        assert auth_config.jwt == jwt_config
        assert auth_config.password == pwd_config
        assert auth_config.enable_refresh_tokens is True
        assert auth_config.max_login_attempts == 3

    def test_config_immutability(self):
        """Test that configs are immutable"""
        config = DatabaseConfig(url="test", key="key")
        
        with pytest.raises(ValueError, match=".*frozen.*"):
            config.url = "new_url"


class MockCryptoProvider(CryptoProvider):
    """Mock crypto provider for testing"""
    
    def __init__(self):
        self.generated_salts = []
        self.hash_calls = []
    
    def pbkdf2_hash(self, password: str, salt: str, iterations: int) -> str:
        self.hash_calls.append((password, salt, iterations))
        return f"hashed_{password}_{salt}_{iterations}"
    
    def generate_salt(self, length: int = 32) -> str:
        salt = f"salt_{length}_{''.join(['a'] * length)}"
        self.generated_salts.append(salt)
        return salt


class MockJWTEncoder(JWTEncoder):
    """Mock JWT encoder for testing"""
    
    def __init__(self):
        self.encoded_tokens = []
        self.decoded_tokens = {}
    
    def encode_token(self, payload: Dict[str, Any], secret: str, algorithm: str = "HS256") -> str:
        token = f"encoded_{hash(str(payload))}_{secret}_{algorithm}"
        self.encoded_tokens.append((payload, secret, algorithm, token))
        self.decoded_tokens[token] = payload
        return token
    
    def decode_token(self, token: str, secret: str, algorithm: str = "HS256") -> Dict[str, Any]:
        if token in self.decoded_tokens:
            return self.decoded_tokens[token]
        raise ValueError("Invalid token")


class MockLogger(Logger):
    """Mock logger for testing"""
    
    def __init__(self):
        self.logs = []
    
    def info(self, message: str) -> None:
        self.logs.append(("INFO", message))
    
    def warning(self, message: str) -> None:
        self.logs.append(("WARNING", message))
    
    def error(self, message: str) -> None:
        self.logs.append(("ERROR", message))
    
    def debug(self, message: str) -> None:
        self.logs.append(("DEBUG", message))


class MockConfigurationProvider(ConfigurationProvider):
    """Mock configuration provider for testing"""
    
    def __init__(self):
        self.auth_config = AuthConfig(
            database=DatabaseConfig(url="test://db", key="db_key"),
            jwt=JWTConfig(secret_key="jwt_secret"),
            password=PasswordConfig()
        )
    
    def get_auth_config(self) -> AuthConfig:
        return self.auth_config
    
    def get_database_config(self) -> DatabaseConfig:
        return self.auth_config.database
    
    def get_jwt_config(self) -> JWTConfig:
        return self.auth_config.jwt
    
    def get_password_config(self) -> PasswordConfig:
        return self.auth_config.password


class TestCryptoProvider:
    """Test CryptoProvider protocol"""

    @pytest.fixture
    def crypto_provider(self):
        return MockCryptoProvider()

    def test_pbkdf2_hash(self, crypto_provider):
        """Test PBKDF2 hash generation"""
        password = "test_password"
        salt = "test_salt"
        iterations = 100000
        
        result = crypto_provider.pbkdf2_hash(password, salt, iterations)
        
        assert result == f"hashed_{password}_{salt}_{iterations}"
        assert (password, salt, iterations) in crypto_provider.hash_calls

    def test_generate_salt(self, crypto_provider):
        """Test salt generation"""
        salt = crypto_provider.generate_salt(32)
        
        assert salt.startswith("salt_32_")
        assert len(salt) > 32  # Should be longer due to prefix
        assert salt in crypto_provider.generated_salts

    def test_generate_salt_custom_length(self, crypto_provider):
        """Test salt generation with custom length"""
        salt = crypto_provider.generate_salt(16)
        
        assert salt.startswith("salt_16_")
        assert salt in crypto_provider.generated_salts


class TestJWTEncoder:
    """Test JWTEncoder protocol"""

    @pytest.fixture
    def jwt_encoder(self):
        return MockJWTEncoder()

    def test_encode_token(self, jwt_encoder):
        """Test JWT token encoding"""
        payload = {"user_id": "123", "email": "test@example.com"}
        secret = "secret_key"
        algorithm = "HS256"
        
        token = jwt_encoder.encode_token(payload, secret, algorithm)
        
        assert token.startswith("encoded_")
        assert (payload, secret, algorithm, token) in jwt_encoder.encoded_tokens

    def test_decode_token(self, jwt_encoder):
        """Test JWT token decoding"""
        payload = {"user_id": "456", "email": "user@example.com"}
        secret = "secret_key"
        
        # First encode a token
        token = jwt_encoder.encode_token(payload, secret)
        
        # Then decode it
        decoded = jwt_encoder.decode_token(token, secret)
        
        assert decoded == payload

    def test_decode_invalid_token(self, jwt_encoder):
        """Test decoding invalid token"""
        with pytest.raises(ValueError, match="Invalid token"):
            jwt_encoder.decode_token("invalid_token", "secret")

    def test_encode_with_different_algorithms(self, jwt_encoder):
        """Test encoding with different algorithms"""
        payload = {"test": "data"}
        
        token_hs256 = jwt_encoder.encode_token(payload, "secret", "HS256")
        token_hs512 = jwt_encoder.encode_token(payload, "secret", "HS512")
        
        assert token_hs256 != token_hs512
        assert "HS256" in token_hs256
        assert "HS512" in token_hs512


class TestLogger:
    """Test Logger protocol"""

    @pytest.fixture
    def logger(self):
        return MockLogger()

    def test_info_logging(self, logger):
        """Test info level logging"""
        message = "This is an info message"
        logger.info(message)
        
        assert ("INFO", message) in logger.logs

    def test_warning_logging(self, logger):
        """Test warning level logging"""
        message = "This is a warning message"
        logger.warning(message)
        
        assert ("WARNING", message) in logger.logs

    def test_error_logging(self, logger):
        """Test error level logging"""
        message = "This is an error message"
        logger.error(message)
        
        assert ("ERROR", message) in logger.logs

    def test_debug_logging(self, logger):
        """Test debug level logging"""
        message = "This is a debug message"
        logger.debug(message)
        
        assert ("DEBUG", message) in logger.logs

    def test_multiple_log_levels(self, logger):
        """Test logging at multiple levels"""
        logger.info("Info message")
        logger.error("Error message")
        logger.debug("Debug message")
        
        assert len(logger.logs) == 3
        assert ("INFO", "Info message") in logger.logs
        assert ("ERROR", "Error message") in logger.logs
        assert ("DEBUG", "Debug message") in logger.logs


class TestConfigurationProvider:
    """Test ConfigurationProvider protocol"""

    @pytest.fixture
    def config_provider(self):
        return MockConfigurationProvider()

    def test_get_auth_config(self, config_provider):
        """Test getting auth configuration"""
        config = config_provider.get_auth_config()
        
        assert isinstance(config, AuthConfig)
        assert isinstance(config.database, DatabaseConfig)
        assert isinstance(config.jwt, JWTConfig)
        assert isinstance(config.password, PasswordConfig)

    def test_get_database_config(self, config_provider):
        """Test getting database configuration"""
        config = config_provider.get_database_config()
        
        assert isinstance(config, DatabaseConfig)
        assert config.url == "test://db"
        assert config.key == "db_key"

    def test_get_jwt_config(self, config_provider):
        """Test getting JWT configuration"""
        config = config_provider.get_jwt_config()
        
        assert isinstance(config, JWTConfig)
        assert config.secret_key == "jwt_secret"

    def test_get_password_config(self, config_provider):
        """Test getting password configuration"""
        config = config_provider.get_password_config()
        
        assert isinstance(config, PasswordConfig)
        assert config.iterations == 100000  # Default value