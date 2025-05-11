from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.app.router import router
from src import __version__


app = FastAPI(title="Judge System", version=__version__)
# Allow CORS for all origins
origins = [
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターを接続
app.include_router(router)


@app.get("/version")
def get_version():
    return {"version": __version__}


if __name__ == "__main__":
    import uvicorn
    print(f"Starting Judge System version {__version__}")
    uvicorn.run(app, host="0.0.0.0", port=8901)
