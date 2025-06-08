"""
Judge Domain API Middleware
ジャッジドメインAPIミドルウェア
"""

import time
from collections.abc import Callable

from fastapi import HTTPException, Request, Response, status
from fastapi.middleware.base import BaseHTTPMiddleware

from ...const import MAX_REQUEST_SIZE
from ...shared.logging import get_logger

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """リクエストログミドルウェア"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        # リクエスト情報をログ
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "client_ip": request.client.host if request.client else None,
            },
        )

        try:
            response = await call_next(request)

            # レスポンス時間を計算
            process_time = time.time() - start_time

            # レスポンス情報をログ
            logger.info(
                f"Request completed: {request.method} {request.url.path} - {response.status_code}",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "process_time": process_time,
                },
            )

            # レスポンスヘッダーに処理時間を追加
            response.headers["X-Process-Time"] = str(process_time)

            return response

        except Exception as e:
            process_time = time.time() - start_time

            logger.error(
                f"Request failed: {request.method} {request.url.path} - {e!s}",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(e),
                    "process_time": process_time,
                },
            )

            raise


class RateLimitMiddleware(BaseHTTPMiddleware):
    """レート制限ミドルウェア"""

    def __init__(self, app, calls_per_minute: int = 60):
        super().__init__(app)
        self.calls_per_minute = calls_per_minute
        self.client_requests = {}  # {client_ip: [timestamp, ...]}
        self.cleanup_interval = 60  # 1分ごとにクリーンアップ
        self.last_cleanup = time.time()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()

        # 定期的に古いエントリをクリーンアップ
        if current_time - self.last_cleanup > self.cleanup_interval:
            await self._cleanup_old_requests(current_time)
            self.last_cleanup = current_time

        # クライアントのリクエスト履歴を取得
        if client_ip not in self.client_requests:
            self.client_requests[client_ip] = []

        client_request_times = self.client_requests[client_ip]

        # 過去1分間のリクエストをカウント
        minute_ago = current_time - 60
        recent_requests = [t for t in client_request_times if t > minute_ago]

        # レート制限チェック
        if len(recent_requests) >= self.calls_per_minute:
            logger.warning(
                f"Rate limit exceeded for {client_ip}: {len(recent_requests)} requests in the last minute"
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
            )

        # 現在のリクエストを記録
        recent_requests.append(current_time)
        self.client_requests[client_ip] = recent_requests

        return await call_next(request)

    async def _cleanup_old_requests(self, current_time: float):
        """古いリクエスト履歴をクリーンアップ"""
        minute_ago = current_time - 60

        for client_ip in list(self.client_requests.keys()):
            self.client_requests[client_ip] = [
                t for t in self.client_requests[client_ip] if t > minute_ago
            ]

            # 空のエントリを削除
            if not self.client_requests[client_ip]:
                del self.client_requests[client_ip]


class RequestSizeMiddleware(BaseHTTPMiddleware):
    """リクエストサイズ制限ミドルウェア"""

    def __init__(self, app, max_size: int = MAX_REQUEST_SIZE):
        super().__init__(app)
        self.max_size = max_size

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Content-Lengthヘッダーをチェック
        content_length = request.headers.get("content-length")

        if content_length:
            content_length = int(content_length)
            if content_length > self.max_size:
                logger.warning(f"Request size too large: {content_length} bytes")
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"Request size too large. Maximum allowed: {self.max_size} bytes",
                )

        return await call_next(request)


class JudgeSystemMiddleware(BaseHTTPMiddleware):
    """ジャッジシステム固有のミドルウェア"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # ジャッジ関連の特別な処理があればここに実装

        # コード実行エンドポイントの場合は特別な制限
        if request.url.path.endswith("/execute"):
            # 同時実行数の制限
            # (実際の実装では専用のセマフォやキューを使用)
            pass

        return await call_next(request)


# ミドルウェア設定関数
def setup_middleware(app):
    """ジャッジドメインのミドルウェアを設定"""

    # リクエストサイズ制限
    app.add_middleware(RequestSizeMiddleware)

    # レート制限
    app.add_middleware(RateLimitMiddleware, calls_per_minute=120)  # 少し緩めに設定

    # ジャッジシステム固有のミドルウェア
    app.add_middleware(JudgeSystemMiddleware)

    # リクエストログ (最後に追加して全てをキャッチ)
    app.add_middleware(RequestLoggingMiddleware)

    logger.info("Judge domain middleware configured")


# カスタム例外ハンドラー
async def judge_system_exception_handler(request: Request, exc: Exception) -> Response:
    """ジャッジシステム固有の例外ハンドラー"""

    logger.error(f"Unhandled exception in judge system: {exc}", exc_info=True)

    # 本番環境では詳細なエラー情報を隠す
    return Response(
        content='{"detail": "Internal server error"}',
        status_code=500,
        media_type="application/json",
    )
