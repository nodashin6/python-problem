#!/usr/bin/env python3
"""
Simple login test endpoint for debugging
シンプルなログインテスト用エンドポイント
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Simple Login Test")

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

@app.post("/api/auth/login")
async def simple_login(request: LoginRequest):
    """Simple login endpoint for testing"""
    
    # シンプルなテスト用認証
    # Seededデータのユーザー情報
    test_users = {
        "test.user@example.com": {
            "id": "550e8400-e29b-41d4-a716-446655440020",
            "user_name": "test_user",
            "display_name": "Test User",
            "email": "test.user@example.com",
            "role": "user"
        },
        "admin@example.com": {
            "id": "550e8400-e29b-41d4-a716-446655440021", 
            "user_name": "admin",
            "display_name": "Admin User",
            "email": "admin@example.com",
            "role": "admin"
        }
    }
    
    # 簡単な認証チェック
    if request.email not in test_users:
        raise HTTPException(status_code=401, detail="Invalid email")
        
    # パスワードチェック（今回はシンプルに）
    if not request.password:
        raise HTTPException(status_code=401, detail="Password required")
    
    user_data = test_users[request.email]
    
    # 簡単なJWTトークンの代わり
    mock_token = f"mock_jwt_token_for_{user_data['id']}"
    
    return LoginResponse(
        access_token=mock_token,
        user=user_data
    )

@app.get("/api/auth/users/me")
async def get_current_user():
    """Mock current user endpoint"""
    return {
        "id": "550e8400-e29b-41d4-a716-446655440020",
        "user_name": "test_user", 
        "display_name": "Test User",
        "email": "test.user@example.com",
        "role": "user",
        "is_active": True,
        "created_at": "2025-08-18T00:00:00Z"
    }

@app.get("/health")
async def health():
    return {"status": "ok", "service": "simple_login_test"}

if __name__ == "__main__":
    print("🧪 Starting Simple Login Test Server")
    print("📍 Available at: http://localhost:8902")
    print("🔗 Test login: POST /api/auth/login")
    print("👤 Test emails: test.user@example.com, admin@example.com")
    uvicorn.run(app, host="0.0.0.0", port=8902)