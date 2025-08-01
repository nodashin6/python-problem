import asyncio
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ppauth.app.api.routers import auth_router
# from ppjudg.app.api.judge_router import judge_router  # TODO: fix judge system imports
from ppprob.app.api.problem_router import problem_router

# Temporarily disable judge router
judge_router = None

__version__ = "0.2.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションライフサイクル管理"""
    # Startup
    print("Programming Problem Platform initializing...")

    yield

    # Shutdown
    print("Programming Problem Platform shutdown completed")


app = FastAPI(
    title="Programming Problem Platform",
    version=__version__,
    description="Comprehensive platform for competitive programming with authentication, problems, and judging",
    lifespan=lifespan,
)

# CORS configuration for frontend
origins = [
    "http://localhost:3000",  # Next.js dev server
    "http://localhost:3001",  # Alternative dev port
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "https://localhost:3000",  # HTTPS dev
    "https://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include system routers
if auth_router:
    app.include_router(auth_router, prefix="/api")
    print("✅ Auth system router included")

if problem_router:
    app.include_router(problem_router)
    print("✅ Problem system router included")

if judge_router:
    app.include_router(judge_router)
    print("✅ Judge system router included")


# Root endpoint
@app.get("/")
async def root():
    """API root endpoint"""
    available_systems = []
    if auth_router:
        available_systems.append("authentication")
    if problem_router:
        available_systems.append("problems")
    if judge_router:
        available_systems.append("judge")

    return {
        "name": "Programming Problem Platform",
        "version": __version__,
        "description": "Comprehensive platform for competitive programming",
        "available_systems": available_systems,
        "endpoints": {
            "auth": "/api/auth" if auth_router else "Not available",
            "problems": "/api/problems" if problem_router else "Not available",
            "judge": "/api/judge" if judge_router else "Not available",
            "docs": "/docs",
            "openapi": "/openapi.json",
        },
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """System health check"""
    system_status = {
        "status": "healthy",
        "timestamp": "2025-08-02T06:30:00Z",
        "systems": {
            "auth": "available" if auth_router else "unavailable",
            "problems": "available" if problem_router else "unavailable",
            "judge": "available" if judge_router else "unavailable",
        },
    }

    return system_status


if __name__ == "__main__":
    import uvicorn

    print(f"🚀 Starting Programming Problem Platform version {__version__}")
    print("📊 Available endpoints:")
    print("  - API Documentation: http://localhost:8901/docs")
    print("  - Health Check: http://localhost:8901/health")
    if auth_router:
        print("  - Authentication: http://localhost:8901/api/auth")
    if problem_router:
        print("  - Problems: http://localhost:8901/api/problems")
    if judge_router:
        print("  - Judge: http://localhost:8901/api/judge")

    uvicorn.run("src.main:app", host="0.0.0.0", port=8901, reload=True, log_level="info")
