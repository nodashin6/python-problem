"""
Sample data for testing
テスト用サンプルデータ
"""

from uuid import uuid4
from datetime import datetime
from typing import Dict, List, Any

# Core Domain Sample Data
SAMPLE_BOOKS = [
    {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "はじめてのプログラミング",
        "description": "プログラミング初心者向けの基礎問題集",
        "author": "テスト太郎",
        "difficulty_level": "beginner",
        "category": "basic",
        "is_public": True,
        "order_index": 1,
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "title": "アルゴリズム入門",
        "description": "基本的なアルゴリズムを学ぶ問題集",
        "author": "アルゴ花子",
        "difficulty_level": "intermediate",
        "category": "algorithm",
        "is_public": True,
        "order_index": 2,
    },
]

SAMPLE_PROBLEMS = [
    {
        "id": "550e8400-e29b-41d4-a716-446655440010",
        "book_id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "Hello World",
        "description": "基本的な出力問題",
        "difficulty_level": "beginner",
        "time_limit_ms": 1000,
        "memory_limit_mb": 64,
        "status": "published",
        "order_index": 1,
        "created_by": "550e8400-e29b-41d4-a716-446655440020",
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440011",
        "book_id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "足し算問題",
        "description": "二つの数値を足し算する問題",
        "difficulty_level": "beginner",
        "time_limit_ms": 2000,
        "memory_limit_mb": 128,
        "status": "published",
        "order_index": 2,
        "created_by": "550e8400-e29b-41d4-a716-446655440020",
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440012",
        "book_id": "550e8400-e29b-41d4-a716-446655440001",
        "title": "配列の最大値",
        "description": "配列から最大値を見つける問題",
        "difficulty_level": "intermediate",
        "time_limit_ms": 3000,
        "memory_limit_mb": 256,
        "status": "published",
        "order_index": 1,
        "created_by": "550e8400-e29b-41d4-a716-446655440021",
    },
]

SAMPLE_PROBLEM_CONTENTS = [
    {
        "problem_id": "550e8400-e29b-41d4-a716-446655440010",
        "language": "ja",
        "statement": '"Hello, World!"と出力してください。',
        "input_format": "入力はありません。",
        "output_format": "Hello, World!",
        "constraints": "制約はありません。",
        "sample_input": "",
        "sample_output": "Hello, World!",
    },
    {
        "problem_id": "550e8400-e29b-41d4-a716-446655440011",
        "language": "ja",
        "statement": "二つの整数A, Bが与えられます。A + Bを出力してください。",
        "input_format": "1行目に整数A, Bが空白区切りで与えられます。",
        "output_format": "A + Bの値を出力してください。",
        "constraints": "1 ≤ A, B ≤ 1000",
        "sample_input": "3 5",
        "sample_output": "8",
    },
    {
        "problem_id": "550e8400-e29b-41d4-a716-446655440012",
        "language": "ja",
        "statement": "N個の整数からなる配列が与えられます。その中の最大値を出力してください。",
        "input_format": "1行目に整数N、2行目にN個の整数が空白区切りで与えられます。",
        "output_format": "配列の最大値を出力してください。",
        "constraints": "1 ≤ N ≤ 100\\n1 ≤ 各要素 ≤ 1000",
        "sample_input": "5\\n3 1 4 1 5",
        "sample_output": "5",
    },
]

SAMPLE_USERS = [
    {
        "id": "550e8400-e29b-41d4-a716-446655440020",
        "email": "test.user@example.com",
        "username": "testuser",
        "display_name": "テストユーザー",
        "bio": "テスト用のユーザーです",
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440021",
        "email": "admin@example.com",
        "username": "admin",
        "display_name": "管理者",
        "bio": "システム管理者",
    },
]

SAMPLE_USER_ROLES = [
    {"user_id": "550e8400-e29b-41d4-a716-446655440020", "role": "user"},
    {"user_id": "550e8400-e29b-41d4-a716-446655440021", "role": "admin"},
]

SAMPLE_CASE_FILES = [
    {
        "id": "650e8400-e29b-41d4-a716-446655440001",
        "url": "/testcases/hello_world/input1.txt",
        "file_hash": "empty_input_hash",
    },
    {
        "id": "650e8400-e29b-41d4-a716-446655440002",
        "url": "/testcases/hello_world/output1.txt",
        "file_hash": "hello_world_output_hash",
    },
    {
        "id": "650e8400-e29b-41d4-a716-446655440003",
        "url": "/testcases/addition/input1.txt",
        "file_hash": "addition_input1_hash",
    },
    {
        "id": "650e8400-e29b-41d4-a716-446655440004",
        "url": "/testcases/addition/output1.txt",
        "file_hash": "addition_output1_hash",
    },
    {
        "id": "650e8400-e29b-41d4-a716-446655440005",
        "url": "/testcases/addition/input2.txt",
        "file_hash": "addition_input2_hash",
    },
    {
        "id": "650e8400-e29b-41d4-a716-446655440006",
        "url": "/testcases/addition/output2.txt",
        "file_hash": "addition_output2_hash",
    },
    {
        "id": "650e8400-e29b-41d4-a716-446655440007",
        "url": "/testcases/max_array/input1.txt",
        "file_hash": "max_array_input1_hash",
    },
    {
        "id": "650e8400-e29b-41d4-a716-446655440008",
        "url": "/testcases/max_array/output1.txt",
        "file_hash": "max_array_output1_hash",
    },
]

SAMPLE_JUDGE_CASES = [
    # Hello World problem
    {
        "problem_id": "550e8400-e29b-41d4-a716-446655440010",
        "input_id": "650e8400-e29b-41d4-a716-446655440001",
        "output_id": "650e8400-e29b-41d4-a716-446655440002",
        "is_sample": True,
        "display_order": 1,
        "judge_case_type": "sample",
    },
    # Addition problem
    {
        "problem_id": "550e8400-e29b-41d4-a716-446655440011",
        "input_id": "650e8400-e29b-41d4-a716-446655440003",
        "output_id": "650e8400-e29b-41d4-a716-446655440004",
        "is_sample": True,
        "display_order": 1,
        "judge_case_type": "sample",
    },
    {
        "problem_id": "550e8400-e29b-41d4-a716-446655440011",
        "input_id": "650e8400-e29b-41d4-a716-446655440005",
        "output_id": "650e8400-e29b-41d4-a716-446655440006",
        "is_sample": False,
        "display_order": 2,
        "judge_case_type": "normal",
    },
    # Max array problem
    {
        "problem_id": "550e8400-e29b-41d4-a716-446655440012",
        "input_id": "650e8400-e29b-41d4-a716-446655440007",
        "output_id": "650e8400-e29b-41d4-a716-446655440008",
        "is_sample": True,
        "display_order": 1,
        "judge_case_type": "sample",
    },
]

# Judge Domain Sample Data
SAMPLE_SUBMISSIONS = [
    {
        "id": "750e8400-e29b-41d4-a716-446655440001",
        "problem_id": "550e8400-e29b-41d4-a716-446655440010",
        "user_id": "550e8400-e29b-41d4-a716-446655440020",
        "language": "python",
        "source_code": 'print("Hello, World!")',
        "status": "completed",
    },
    {
        "id": "750e8400-e29b-41d4-a716-446655440002",
        "problem_id": "550e8400-e29b-41d4-a716-446655440011",
        "user_id": "550e8400-e29b-41d4-a716-446655440020",
        "language": "python",
        "source_code": "a, b = map(int, input().split())\\nprint(a + b)",
        "status": "completed",
    },
]


def get_all_sample_data() -> Dict[str, List[Dict[str, Any]]]:
    """すべてのサンプルデータを取得"""
    return {
        "books": SAMPLE_BOOKS,
        "problems": SAMPLE_PROBLEMS,
        "problem_contents": SAMPLE_PROBLEM_CONTENTS,
        "users": SAMPLE_USERS,
        "user_roles": SAMPLE_USER_ROLES,
        "case_files": SAMPLE_CASE_FILES,
        "judge_cases": SAMPLE_JUDGE_CASES,
        "submissions": SAMPLE_SUBMISSIONS,
    }
