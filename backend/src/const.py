"""
Constants and configuration for Judge System
共通定数と設定情報
"""

import os
from enum import Enum
from pathlib import Path

# プロジェクト構造
PRJ_DIR = Path(__file__).resolve().parent.parent.parent
PROBLEM_DIR = PRJ_DIR / "problems"
FRONTEND_DIR = PRJ_DIR / "frontend"
BACKEND_DIR = PRJ_DIR / "judge-system"
SUPABASE_DIR = PRJ_DIR / "supabase"

# 問題集のデフォルト設定
DEFAULT_PROBLEM_SET = "getting-started"

# AppDataのパス設定
APP_DATA_DIR = Path(__file__).resolve().parent.parent / "app_data"
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
SUBMISSIONS_DIR = APP_DATA_DIR / "submissions"
LOGS_DIR = APP_DATA_DIR / "logs"
CACHE_DIR = APP_DATA_DIR / "cache"


# 実行制限
DEFAULT_TIME_LIMIT_MS = 5000  # 5秒
DEFAULT_MEMORY_LIMIT_MB = 256  # 256MB
DEFAULT_OUTPUT_LIMIT_KB = 64  # 64KB

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
