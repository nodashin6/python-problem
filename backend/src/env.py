"""
Environment configuration for Judge System
環境設定とシークレット管理
"""

from pathlib import Path

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseModel):
    """データベース設定"""

    host: str = "localhost"
    port: int = 5432
    name: str = "judge_system"
    user: str = "postgres"
    password: str = ""
    pool_size: int = 10
    timeout: int = 30


class RedisConfig(BaseModel):
    """Redis設定 (キャッシュ用)"""

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: str | None = None
    timeout: int = 5


class SecurityConfig(BaseModel):
    """セキュリティ設定"""

    jwt_secret_key: str = "your-secret-key-here"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    cors_origins: list[str] = ["http://localhost:3000"]
    allowed_hosts: list[str] = ["*"]


class JudgeConfig(BaseModel):
    """ジャッジ実行設定"""

    time_limit_ms: int = 5000
    memory_limit_mb: int = 256
    output_limit_kb: int = 64
    max_concurrent_judges: int = 5
    judge_timeout_seconds: int = 30


class StorageConfig(BaseModel):
    """ストレージ設定"""

    upload_dir: Path = Path.home() / ".python-problem" / "uploads"
    max_file_size_mb: int = 10
    allowed_extensions: list[str] = [".py", ".cpp", ".java", ".js", ".txt"]


class EnvSettings(BaseSettings):
    """アプリケーションの統合設定"""

    model_config = SettingsConfigDict(
        env_file=[".env", "../.env", "../../.env"],
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # 環境情報
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # Supabase設定
    supabase_url: str = Field(alias="SUPABASE_URL")
    supabase_anon_key: str = Field(alias="SUPABASE_ANON_KEY")
    supabase_service_key: str | None = Field(default=None, alias="SUPABASE_SERVICE_KEY")

    # データベース設定
    database_url: str | None = Field(default=None, alias="DATABASE_URL")

    # Redis設定
    redis_url: str | None = Field(default=None, alias="REDIS_URL")

    # セキュリティ設定
    secret_key: str = Field(default="your-secret-key-here", alias="SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_expire_minutes: int = Field(default=30, alias="JWT_EXPIRE_MINUTES")

    # API設定
    host: str = Field(default="localhost", alias="HOST")
    port: int = Field(default=8000, alias="PORT")

    # ジャッジ実行制限設定
    default_time_limit_ms: int = Field(default=5000, alias="DEFAULT_TIME_LIMIT_MS")
    default_memory_limit_mb: int = Field(default=256, alias="DEFAULT_MEMORY_LIMIT_MB")
    default_output_limit_kb: int = Field(default=64, alias="DEFAULT_OUTPUT_LIMIT_KB")

    # ジャッジワーカー設定
    max_concurrent_judges: int = Field(default=3, alias="MAX_CONCURRENT_JUDGES")
    judge_timeout_seconds: int = Field(default=30, alias="JUDGE_TIMEOUT_SECONDS")

    # キャッシュ設定
    cache_ttl_seconds: int = Field(default=300, alias="CACHE_TTL_SECONDS")
    cache_max_size: int = Field(default=1000, alias="CACHE_MAX_SIZE")

    # 外部サービス設定
    smtp_host: str | None = Field(default=None, alias="SMTP_HOST")
    smtp_port: int | None = Field(default=587, alias="SMTP_PORT")
    smtp_user: str | None = Field(default=None, alias="SMTP_USER")
    smtp_password: str | None = Field(default=None, alias="SMTP_PASSWORD")

    @field_validator("environment")
    def validate_environment(cls, v):
        allowed_envs = ["development", "testing", "staging", "production"]
        if v not in allowed_envs:
            raise ValueError(f"Environment must be one of {allowed_envs}")
        return v

    @field_validator("log_level")
    def validate_log_level(cls, v):
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed_levels:
            raise ValueError(f"Log level must be one of {allowed_levels}")
        return v.upper()

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_testing(self) -> bool:
        return self.environment == "testing"

    def get_database_config(self) -> DatabaseConfig:
        """データベース設定を取得"""
        if self.database_url:
            # DATABASE_URLをパースしてDatabaseConfigを作成
            # 簡易実装 (本来はより堅牢なパーサーが必要)
            return DatabaseConfig()
        return DatabaseConfig()

    def get_redis_config(self) -> RedisConfig:
        """Redis設定を取得"""
        return RedisConfig()

    def get_security_config(self) -> SecurityConfig:
        """セキュリティ設定を取得"""
        return SecurityConfig(jwt_secret_key=self.secret_key)

    def get_judge_config(self) -> JudgeConfig:
        """ジャッジ設定を取得"""
        return JudgeConfig()

    def get_storage_config(self) -> StorageConfig:
        """ストレージ設定を取得"""
        return StorageConfig()


# グローバル設定インスタンス
settings = EnvSettings()
SUPABASE_URL = settings.supabase_url
SUPABASE_ANON_KEY = settings.supabase_anon_key
SUPABASE_SERVICE_KEY = settings.supabase_service_key
