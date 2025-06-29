"""
Problem System tests configuration
"""

from uuid import uuid4

import pytest
from pydantic import UUID4
from supabase import Client

from ppcore.infrastructure.supabase.client import create_client


@pytest.fixture
def client() -> Client:
    """Supabaseクライアントのインスタンス"""
    return create_client()


@pytest.fixture
def created_user(client):
    """テスト用のユーザーを実際にDBに作成"""
    user_id = uuid4()

    # usersテーブルに直接テストユーザーを挿入
    try:
        response = (
            client.table("users")
            .insert(
                {
                    "id": str(user_id),
                    "username": "testuser",
                    "display_name": "Test User",
                    "email": "test@example.com",
                }
            )
            .execute()
        )

        class DummyUser:
            def __init__(self, user_id):
                self.id = user_id
                self.username = "testuser"
                self.display_name = "Test User"
                self.email = "test@example.com"

        yield DummyUser(user_id)

        # クリーンアップ: テスト後にユーザーを削除
        client.table("users").delete().eq("id", str(user_id)).execute()

    except Exception as e:
        # usersテーブルがない場合は、author_idをNULLにして処理を継続
        class DummyUser:
            def __init__(self):
                self.id = None
                self.username = "testuser"
                self.display_name = "Test User"
                self.email = "test@example.com"

        yield DummyUser()
