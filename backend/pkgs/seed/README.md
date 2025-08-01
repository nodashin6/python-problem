# Seed Package (ppseed)

データシード機能を提供するパッケージです。問題データ、ジャッジデータ、テストケースなどの初期データを生成・投入します。

## 🏗️ アーキテクチャ

### 依存関係

```
ppseed
├── ppprob (Problems Domain) - 問題・問題集データ
├── ppjudg (Judge Domain)    - ジャッジ・提出データ  
└── Supabase Direct         - テストケースファイルなど
```

### シーダー種類

1. **従来型シーダー** (`seeder.py`, `problem_seeder.py`)
   - Supabaseクライアントを直接使用
   - 高速で確実なデータ投入
   - テストケースファイルの作成も対応

2. **ドメイン型シーダー** (`domain_seeder.py`) 
   - ドメインリポジトリを通じてデータ投入
   - Clean Architectureに準拠
   - ビジネスロジックを通したデータ整合性

3. **ハイブリッドシーダー**
   - ドメイン型＋従来型の組み合わせ
   - 最適な方法で各データを処理

## 📦 主要モジュール

### `sample_data.py`
```python
# サンプルデータ定義
SAMPLE_BOOKS = [...]           # 問題集データ
SAMPLE_PROBLEMS = [...]        # 問題データ
SAMPLE_PROBLEM_CONTENTS = [...] # 問題内容データ
SAMPLE_JUDGE_CASES = [...]     # ジャッジケースデータ
SAMPLE_SUBMISSIONS = [...]     # 提出データ
```

### `problem_seeder.py`
```python
from ppseed import ProblemSeeder

seeder = ProblemSeeder()

# 完全シード実行
await seeder.seed_problems_complete(
    clear_existing=True,
    create_test_case_files=True
)

# 問題のみシード
await seeder.seed_problems_only()

# テストケースのみシード
await seeder.seed_test_cases_only(create_files=True)
```

### `domain_seeder.py`
```python
from ppseed import DomainBasedSeeder, create_domain_seeder

# DIコンテナからリポジトリを取得
book_repo = container.get(BookRepositoryBase)
problem_repo = container.get(ProblemRepositoryBase)

# ドメインシーダー作成
seeder = await create_domain_seeder(book_repo, problem_repo)

# ドメイン経由でシード
await seeder.seed_complete_via_domain(clear_existing=True)
```

### `cli_seeder.py`
```bash
# 全データシード
python -m ppseed.cli_seeder all --clear

# 問題データのみシード
python -m ppseed.cli_seeder problems --create-files

# データクリア
python -m ppseed.cli_seeder clear

# データ検証
python -m ppseed.cli_seeder verify
```

## 🚀 使用方法

### 1. 基本的なシード実行

```python
import asyncio
from ppseed import seed_problems_complete

async def main():
    # 問題データの完全シード
    success = await seed_problems_complete(clear_existing=True)
    if success:
        print("✅ シード完了!")
    else:
        print("❌ シード失敗")

asyncio.run(main())
```

### 2. カスタムデータでのシード

```python
from ppseed import ProblemSeeder

# カスタム問題集データ
custom_books = [
    {
        "id": "custom-book-id",
        "title": "カスタム問題集",
        "description": "独自の問題集",
        "difficulty_level": "beginner",
        # ...
    }
]

seeder = ProblemSeeder()
await seeder.seed_books_only(custom_books)
```

### 3. ドメインレイヤー経由でのシード

```python
from ppseed import DomainBasedSeeder
from ppprob.infrastructure.supabase.repositories import (
    BookRepositoryImpl,
    ProblemRepositoryImpl
)

# リポジトリインスタンス作成
book_repo = BookRepositoryImpl()
problem_repo = ProblemRepositoryImpl()

# ドメインシーダー作成
seeder = DomainBasedSeeder(book_repo, problem_repo)

# ドメインロジックを通してシード
await seeder.seed_problems_domain(clear_existing=True)
```

### 4. ハイブリッドシード

```python
from ppseed import HybridSeeder, DomainBasedSeeder, ProblemSeeder

# 両方のシーダーを組み合わせ
domain_seeder = DomainBasedSeeder(book_repo, problem_repo)
direct_seeder = ProblemSeeder()

hybrid = HybridSeeder(domain_seeder, direct_seeder)

# ドメイン部分はClean Architecture、
# テストケース部分は直接DB操作
await hybrid.seed_complete_hybrid(
    clear_existing=True,
    include_test_cases=True,
    create_test_files=True
)
```

## 📊 データ検証・統計

### 検証機能

```python
from ppseed import verify_problems, get_problems_stats

# データ検証
verification = await verify_problems()
print(f"Books: {verification['books']['count']} records")
print(f"Problems: {verification['problems']['count']} records")

# 統計情報取得
stats = await get_problems_stats()
print(f"Total problems: {stats['problems']['total']}")
print(f"By difficulty: {stats['problems']['by_difficulty']}")
```

### 統計出力例

```
📈 Problem Statistics:
==============================
📁 Books: 2 total
   by_difficulty: {'beginner': 1, 'intermediate': 1}
📁 Problems: 3 total  
   by_difficulty: {'beginner': 2, 'intermediate': 1}
   by_status: {'published': 3}
📁 Judge_cases: 4 total
   sample_cases: 3
   by_type: {'sample': 3, 'normal': 1}
```

## 🧪 テストケースファイル作成

実際のジャッジ用テストケースファイルも自動生成可能：

```python
await seeder.seed_problems_complete(
    clear_existing=True,
    create_test_case_files=True  # ファイル作成ON
)
```

生成されるファイル構造：
```
testcases/
├── hello_world/
│   ├── input1.txt   # (空)
│   └── output1.txt  # "Hello, World!"
├── addition/
│   ├── input1.txt   # "3 5"
│   ├── output1.txt  # "8"
│   ├── input2.txt   # "10 20"
│   └── output2.txt  # "30"
└── max_array/
    ├── input1.txt   # "5\n3 1 4 1 5"
    └── output1.txt  # "5"
```

## ⚡ パフォーマンス

- **従来型シーダー**: 最高速度、バッチ処理最適化
- **ドメイン型シーダー**: 中程度、ビジネスロジック通過
- **ハイブリッド**: バランス型、適材適所

## 🛠️ 開発・デバッグ

### ログ設定

```python
import logging
logging.basicConfig(level=logging.INFO)

# より詳細なログ
logging.basicConfig(level=logging.DEBUG)
```

### エラーハンドリング

各シーダーは例外を適切にキャッチし、ログ出力します：

```
❌ Failed to seed problem Hello World: Unique constraint violation
⚠️ Problem content upsert failed, trying insert: duplicate key
✅ Books seeded: 2 records
```

## 🔧 カスタマイズ

### 独自サンプルデータ

`sample_data.py` を参考に独自データを作成：

```python
MY_CUSTOM_PROBLEMS = [
    {
        "id": "my-problem-id",
        "title": "My Custom Problem",
        # ... 他のフィールド
    }
]

seeder = ProblemSeeder()
await seeder.seed_problems_only(problems_data=MY_CUSTOM_PROBLEMS)
```

### 独自リポジトリ実装

ドメイン型シーダーで独自リポジトリを使用：

```python
class MyBookRepository(BookRepositoryBase):
    # 独自実装
    pass

seeder = DomainBasedSeeder(
    book_repository=MyBookRepository(),
    problem_repository=MyProblemRepository()
)
```

## 📚 関連ドキュメント

- [ppprob Domain Documentation](../problem-system/README.md)
- [ppjudg Domain Documentation](../judge-system/README.md)
- [Clean Architecture Guide](../../docs/clean-architecture.md)
- [Testing Strategy](../../docs/testing.md)