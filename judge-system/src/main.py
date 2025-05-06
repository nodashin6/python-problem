from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.app.router import router


app = FastAPI()
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8901)
