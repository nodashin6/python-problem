"""
Logging infrastructure components
ロギングインフラストラクチャ
"""

import json
import logging
import logging.handlers
import sys
from contextlib import contextmanager
from datetime import datetime
from typing import Any, ClassVar

from ..const import LOGS_DIR
from ..env import settings


class JsonFormatter(logging.Formatter):
    """JSON形式のログフォーマッター"""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # 追加情報があれば含める
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)

        # 例外情報があれば含める
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)


class ContextualFormatter(logging.Formatter):
    """コンテキスト情報付きフォーマッター"""

    def format(self, record: logging.LogRecord) -> str:
        # 基本フォーマット
        formatted = super().format(record)

        # コンテキスト情報を追加
        context_info = []
        if hasattr(record, "user_id"):
            context_info.append(f"user:{record.user_id}")
        if hasattr(record, "request_id"):
            context_info.append(f"req:{record.request_id}")
        if hasattr(record, "domain"):
            context_info.append(f"domain:{record.domain}")

        if context_info:
            formatted = f"[{','.join(context_info)}] {formatted}"

        return formatted


class SimpleLoggerAdapter(logging.LoggerAdapter):
    """シンプルなログアダプター"""

    def __init__(
        self,
        logger: logging.Logger,
        module: str,
        extra: dict[str, Any] | None = None,
    ):
        super().__init__(logger, extra or {})
        self.module = module

    def process(self, msg, kwargs):
        # モジュール情報を追加
        if "extra" not in kwargs:
            kwargs["extra"] = {}
        kwargs["extra"]["module"] = self.module

        # 既存のextraとマージ
        kwargs["extra"].update(self.extra)

        return msg, kwargs


class LoggerFactory:
    """ロガーファクトリー"""

    _loggers: ClassVar[dict[str, logging.Logger]] = {}
    _configured: ClassVar[bool] = False

    @classmethod
    def configure(cls):
        """ログ設定を初期化"""
        if cls._configured:
            return

        # ログディレクトリを作成
        LOGS_DIR.mkdir(parents=True, exist_ok=True)

        # ルートロガーの設定
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, settings.log_level))

        # 既存のハンドラーをクリア
        root_logger.handlers.clear()

        # コンソールハンドラー
        console_handler = logging.StreamHandler(sys.stdout)

        if settings.is_production:
            console_handler.setFormatter(JsonFormatter())
        else:
            console_handler.setFormatter(
                ContextualFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            )

        root_logger.addHandler(console_handler)

        # ファイルハンドラー (本番環境のみ)
        if settings.is_production:
            file_handler = logging.handlers.RotatingFileHandler(
                LOGS_DIR / "app.log",
                maxBytes=10 * 1024 * 1024,
                backupCount=5,  # 10MB
            )
            file_handler.setFormatter(JsonFormatter())
            root_logger.addHandler(file_handler)

        # エラーログファイル
        error_handler = logging.handlers.RotatingFileHandler(
            LOGS_DIR / "error.log",
            maxBytes=10 * 1024 * 1024,
            backupCount=5,  # 10MB
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(
            JsonFormatter()
            if settings.is_production
            else ContextualFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        root_logger.addHandler(error_handler)

        cls._configured = True

    @classmethod
    def get_logger(cls, name: str, module: str | None = None) -> logging.Logger:
        """ロガーを取得"""
        cls.configure()

        if name not in cls._loggers:
            logger = logging.getLogger(name)
            cls._loggers[name] = logger

        logger = cls._loggers[name]

        # モジュール固有のアダプターを返す
        if module:
            return SimpleLoggerAdapter(logger, module)

        return logger

    @classmethod
    def get_module_logger(cls, module: str) -> SimpleLoggerAdapter:
        """モジュール固有のロガーを取得"""
        logger_name = f"app.{module}"
        logger = cls.get_logger(logger_name)
        return SimpleLoggerAdapter(logger, module)


class RequestLogger:
    """リクエストログ管理"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    @contextmanager
    def log_request(
        self,
        request_id: str,
        user_id: str | None = None,
        operation: str | None = None,
    ):
        """リクエストコンテキストでログ"""
        extra = {"request_id": request_id}
        if user_id:
            extra["user_id"] = user_id
        if operation:
            extra["operation"] = operation

        start_time = datetime.now()

        # リクエスト開始ログ
        adapter = logging.LoggerAdapter(self.logger, extra)
        adapter.info(f"Request started: {operation}")

        try:
            yield adapter
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            adapter.error(f"Request failed after {duration:.3f}s: {e!s}", exc_info=True)
            raise
        else:
            duration = (datetime.now() - start_time).total_seconds()
            adapter.info(f"Request completed in {duration:.3f}s: {operation}")


class PerformanceLogger:
    """パフォーマンスログ"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    @contextmanager
    def measure(self, operation: str, threshold_ms: float = 1000.0):
        """操作時間を測定"""
        start_time = datetime.now()

        try:
            yield
        finally:
            duration = (datetime.now() - start_time).total_seconds() * 1000

            if duration > threshold_ms:
                self.logger.warning(f"Slow operation detected: {operation} took {duration:.2f}ms")
            else:
                self.logger.debug(f"Operation completed: {operation} took {duration:.2f}ms")


# 便利関数
def get_logger(name: str, module: str | None = None) -> logging.Logger:
    """ロガーを取得 (便利関数)"""
    if module is None:
        module = "default"
    return LoggerFactory.get_logger(name, module)


def get_module_logger(module: str) -> SimpleLoggerAdapter:
    """モジュール固有のロガーを取得"""
    return LoggerFactory.get_module_logger(module)


# モジュールレベルでの初期化
LoggerFactory.configure()
