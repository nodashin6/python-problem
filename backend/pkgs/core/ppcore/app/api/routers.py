from fastapi import APIRouter
from src import __version__


core_router = APIRouter(prefix="/api/v1/core", tags=["ppcore"])


@core_router.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "service": "Judge System",
        "version": __version__,
        "status": "running",
        "domains": ["judge", "core"],
    }


@core_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "PPCore is running"}


@core_router.get("/version")
async def get_version():
    """バージョン情報"""
    return {"version": __version__}
