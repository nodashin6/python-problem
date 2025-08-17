"""
Sample data for testing
テスト用サンプルデータ
"""

from datetime import datetime
from typing import Any, Dict, List
from uuid import uuid4

# Core Domain Sample Data
SAMPLE_BOOKS = [
    {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "はじめてのプログラミング",
        "author_id": "550e8400-e29b-41d4-a716-446655440020",
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "title": "アルゴリズム入門",
        "author_id": "550e8400-e29b-41d4-a716-446655440021",
    },
]

SAMPLE_PROBLEMS = [
    {
        "id": "550e8400-e29b-41d4-a716-446655440010",
        "book_id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "Hello World",
        "description": "基本的な出力問題",
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440011",
        "book_id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "足し算問題",
        "description": "二つの数値を足し算する問題",
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440012",
        "book_id": "550e8400-e29b-41d4-a716-446655440001",
        "title": "配列の最大値",
        "description": "配列から最大値を見つける問題",
    },
]

SAMPLE_PROBLEM_CONTENTS = [
    {
        "problem_id": "550e8400-e29b-41d4-a716-446655440010",
        "language": "ja",
        "markdown": '''# Hello World

## 問題文
"Hello, World!"と出力してください。

## 入力
入力はありません。

## 出力
Hello, World!

## 制約
制約はありません。

## サンプル

### 入力
```

```

### 出力
```
Hello, World!
```''',
    },
    {
        "problem_id": "550e8400-e29b-41d4-a716-446655440011",
        "language": "ja",
        "markdown": '''# 足し算問題

## 問題文
二つの整数A, Bが与えられます。A + Bを出力してください。

## 入力
1行目に整数A, Bが空白区切りで与えられます。

## 出力
A + Bの値を出力してください。

## 制約
1 ≤ A, B ≤ 1000

## サンプル

### 入力
```
3 5
```

### 出力
```
8
```''',
    },
    {
        "problem_id": "550e8400-e29b-41d4-a716-446655440012",
        "language": "ja",
        "markdown": '''# 配列の最大値

## 問題文
N個の整数からなる配列が与えられます。その中の最大値を出力してください。

## 入力
1行目に整数N、2行目にN個の整数が空白区切りで与えられます。

## 出力
配列の最大値を出力してください。

## 制約
- 1 ≤ N ≤ 100
- 1 ≤ 各要素 ≤ 1000

## サンプル

### 入力
```
5
3 1 4 1 5
```

### 出力
```
5
```''',
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
        "code": 'print("Hello, World!")',
        "status": "completed",
    },
    {
        "id": "750e8400-e29b-41d4-a716-446655440002",
        "problem_id": "550e8400-e29b-41d4-a716-446655440011",
        "user_id": "550e8400-e29b-41d4-a716-446655440020",
        "language": "python",
        "code": "a, b = map(int, input().split())\\nprint(a + b)",
        "status": "completed",
    },
]


def get_all_sample_data() -> dict[str, list[dict[str, Any]]]:
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
