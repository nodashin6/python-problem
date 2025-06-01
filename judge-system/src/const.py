"""
Constants and configuration for Judge System
共通定数と設定情報
"""

from pathlib import Path
import os
from enum import Enum


class Environment(str, Enum):
    """実行環境"""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class DomainType(str, Enum):
    """ドメインタイプ"""

    CORE = "core"  # 問題管理ドメイン
    JUDGE = "judge"  # ジャッジシステムドメイン


# プロジェクト構造
PRJ_DIR = Path(__file__).resolve().parent.parent.parent
PROBLEM_DIR = PRJ_DIR / "problems"
FRONTEND_DIR = PRJ_DIR / "frontend"
BACKEND_DIR = PRJ_DIR / "judge-system"
SUPABASE_DIR = PRJ_DIR / "supabase"

# 問題集のデフォルト設定
DEFAULT_PROBLEM_SET = "getting-started"

# AppDataのパス設定
APP_DATA_DIR = Path(os.path.expanduser("~")) / ".python-problem"
SUBMISSIONS_DIR = APP_DATA_DIR / "submissions"
LOGS_DIR = APP_DATA_DIR / "logs"
CACHE_DIR = APP_DATA_DIR / "cache"

# ドメイン別ディレクトリ
CORE_DOMAIN_DIR = BACKEND_DIR / "src" / "core"
JUDGE_DOMAIN_DIR = BACKEND_DIR / "src" / "jdg"
SHARED_DIR = BACKEND_DIR / "src" / "shared"

# 実行制限
DEFAULT_TIME_LIMIT_MS = 5000  # 5秒
DEFAULT_MEMORY_LIMIT_MB = 256  # 256MB
DEFAULT_OUTPUT_LIMIT_KB = 64  # 64KB


# 判定結果の種類
class JudgeResultType(str, Enum):
    """ジャッジ結果タイプ"""

    AC = "AC"  # Accepted
    WA = "WA"  # Wrong Answer
    TLE = "TLE"  # Time Limit Exceeded
    MLE = "MLE"  # Memory Limit Exceeded
    RE = "RE"  # Runtime Error
    CE = "CE"  # Compilation Error
    IE = "IE"  # Internal Error
    PE = "PE"  # Presentation Error
    JUDGING = "JUDGING"  # まだジャッジ中
    PENDING = "PENDING"  # ジャッジ待ち


# Core Domain Enums
class UserRole(str, Enum):
    """ユーザーロール"""

    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"
    GUEST = "guest"


class DifficultyLevel(str, Enum):
    """難易度レベル"""

    VERY_EASY = "very_easy"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    VERY_HARD = "very_hard"


class ProblemStatus(str, Enum):
    """問題ステータス"""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DELETED = "deleted"


class JudgeCaseType(str, Enum):
    """ジャッジケースタイプ"""

    SAMPLE = "sample"
    HIDDEN = "hidden"
    PRETEST = "pretest"


class Language(str, Enum):
    """対応言語"""

    JAPANESE = "ja"
    ENGLISH = "en"
    KOREAN = "ko"
    CHINESE_SIMPLIFIED = "zh-cn"
    CHINESE_TRADITIONAL = "zh-tw"


class ContentType(str, Enum):
    """コンテンツタイプ"""

    PROBLEM_STATEMENT = "problem_statement"
    EDITORIAL = "editorial"
    TUTORIAL = "tutorial"
    HINT = "hint"
    SAMPLE_CODE = "sample_code"
    EXPLANATION = "explanation"


class ProgrammingLanguage(str, Enum):
    """プログラミング言語"""

    PYTHON = "python"
    JAVA = "java"
    CPP = "cpp"
    C = "c"
    JAVASCRIPT = "javascript"
    GO = "go"
    RUST = "rust"


# Judge Domain Enums
class ExecutionStatus(str, Enum):
    """実行ステータス"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    MEMORY_EXCEEDED = "memory_exceeded"
    CANCELLED = "cancelled"


class JudgeStatus(str, Enum):
    """ジャッジステータス"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"
    TIMEOUT = "timeout"


# ログレベル設定
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DEBUG_MODE = os.getenv("DEBUG", "false").lower() == "true"

# データベース設定
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
DB_TIMEOUT = int(os.getenv("DB_TIMEOUT", "30"))

# キャッシュ設定
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "300"))  # 5分
CACHE_MAX_SIZE = int(os.getenv("CACHE_MAX_SIZE", "1000"))

# セキュリティ設定
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))

# API設定
API_VERSION = "v1"
API_PREFIX = f"/api/{API_VERSION}"
MAX_REQUEST_SIZE = int(os.getenv("MAX_REQUEST_SIZE", "10485760"))  # 10MB
