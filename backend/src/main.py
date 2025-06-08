import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import __version__
from .const import API_PREFIX

# # Judge Domain
# from .jdg.app import initialize_container, shutdown_container, setup_event_handlers
# from .jdg.api.routes import judge_router

# # Core Domain
# from .core.app import initialize_core_container, shutdown_core_container
# from .core.api.routes import core_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションライフサイクル管理"""
    # Startup
    await initialize_container()  # Judge domain
    await initialize_core_container()  # Core domain
    await setup_event_handlers()
    print("Judge System initialized successfully")

    yield

    # Shutdown
    await shutdown_container()  # Judge domain
    await shutdown_core_container()  # Core domain
    print("Judge System shutdown completed")


app = FastAPI(title="Judge System", version=__version__, lifespan=lifespan)

# CORS設定
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    import uvicorn

    print(f"Starting Judge System version {__version__}")
    uvicorn.run("src.main:app", host="0.0.0.0", port=8901, reload=True, log_level="info")
