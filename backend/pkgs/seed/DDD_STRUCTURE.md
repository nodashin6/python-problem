# ppseed DDD Structure

## 🏗️ Domain-Driven Design 構造

ppseedパッケージは、Clean ArchitectureとDDD原則に沿って設計されています。

```
ppseed/
├── domain/
│   ├── services/
│   │   ├── problem_seed_service.py    # 問題シードビジネスロジック
│   │   └── judge_seed_service.py      # ジャッジシードビジネスロジック
│   └── value_objects/
│       └── seed_result.py             # シード結果値オブジェクト
├── usecase/
│   └── seed_usecase.py                # シード統合ユースケース
├── app/
│   └── seed_facade.py                 # 外部向けファサード
├── sample_data.py                     # サンプルデータ定義
└── cli_seeder.py                      # CLI実行用スクリプト
```

## 📋 レイヤー責任

### Domain Layer

#### `ProblemSeedService`
- **責任**: 問題ドメイン（ppprob）のシード処理ビジネスロジック
- **依存**: `BookRepositoryBase`, `ProblemRepositoryBase`
- **機能**:
  - 問題集データのシード
  - 問題データのシード
  - 問題統計情報の取得
  - 問題データのクリア

```python
from ppseed import ProblemSeedService

service = ProblemSeedService(book_repo, problem_repo)
result = await service.seed_books(books_data, overwrite_existing=False)
print(f"Created: {result.created_count}, Skipped: {result.skipped_count}")
```

#### `JudgeSeedService`
- **責任**: ジャッジドメイン（ppjudg）のシード処理ビジネスロジック
- **依存**: `SubmissionRepositoryBase`
- **機能**:
  - 提出データのシード
  - テストケースファイルの作成
  - ジャッジ統計情報の取得
  - ジャッジデータのクリア

```python
from ppseed import JudgeSeedService

service = JudgeSeedService(submission_repo)
result = await service.seed_submissions(submissions_data)
```

#### Value Objects
- `SeedResult`: シード処理結果の詳細情報
- `SeedStatistics`: 統計情報
- `TestCaseFileResult`: テストケースファイル作成結果

### Use Case Layer

#### `SeedUseCase`
- **責任**: 問題とジャッジのシードサービスを協調させる統合ユースケース
- **依存**: `ProblemSeedService`, `JudgeSeedService`
- **機能**:
  - 完全データセットのシード
  - 問題のみのシード
  - ジャッジのみのシード
  - 包括的統計情報の取得

```python
from ppseed import SeedUseCase

usecase = SeedUseCase(problem_service, judge_service)
result = await usecase.seed_complete_dataset(
    clear_existing=True,
    create_test_files=True
)
```

### Application Layer

#### `SeedFacade`
- **責任**: 外部クライアント向けのシンプルなインターフェース
- **依存**: DI済みリポジトリを受け取り、内部でサービス/ユースケースを構築
- **機能**:
  - ワンライナーでの完全シード
  - 設定の抽象化
  - エラーハンドリングの統一

```python
from ppseed import SeedFacade, create_seed_facade

facade = create_seed_facade(book_repo, problem_repo, submission_repo)
result = await facade.seed_all(clear_existing=True, create_test_files=True)
```

## 🔄 依存関係フロー

```
External Client
       ↓
   SeedFacade
       ↓  
   SeedUseCase
    ↙    ↘
ProblemSeedService  JudgeSeedService
    ↓                    ↓
BookRepository      SubmissionRepository
ProblemRepository
    ↓                    ↓
  ppprob              ppjudg
```

## 🎯 使用パターン

### 1. シンプル使用（推奨）

```python
from ppseed import create_seed_facade

# DIコンテナからリポジトリを取得
facade = create_seed_facade(book_repo, problem_repo, submission_repo)

# ワンライナーで全シード
result = await facade.seed_all(clear_existing=True)
```

### 2. 詳細制御

```python
from ppseed import SeedUseCase, ProblemSeedService, JudgeSeedService

# サービス個別作成
problem_service = ProblemSeedService(book_repo, problem_repo)
judge_service = JudgeSeedService(submission_repo)

# ユースケース作成
usecase = SeedUseCase(problem_service, judge_service)

# カスタムデータでシード
result = await usecase.seed_complete_dataset(
    custom_data=my_custom_data,
    clear_existing=True
)
```

### 3. ドメインサービス直接使用

```python
from ppseed import ProblemSeedService

service = ProblemSeedService(book_repo, problem_repo)

# 問題集のみシード
books_result = await service.seed_books(books_data)

# 統計取得
stats = await service.get_problem_statistics()
print(f"Total books: {stats.books_total}")
```

## 🧪 テスタビリティ

### Domain Services
- リポジトリをMockして単体テスト可能
- ビジネスロジックの詳細テスト

```python
from unittest.mock import AsyncMock
from ppseed import ProblemSeedService

async def test_seed_books():
    mock_book_repo = AsyncMock()
    mock_problem_repo = AsyncMock()
    
    service = ProblemSeedService(mock_book_repo, mock_problem_repo)
    result = await service.seed_books([sample_book])
    
    assert result.is_successful
    mock_book_repo.create.assert_called_once()
```

### Use Cases
- ドメインサービスをMockして統合テスト

```python
async def test_seed_complete_dataset():
    mock_problem_service = AsyncMock()
    mock_judge_service = AsyncMock()
    
    usecase = SeedUseCase(mock_problem_service, mock_judge_service)
    result = await usecase.seed_complete_dataset()
    
    assert result["success"]
    mock_problem_service.seed_books.assert_called_once()
```

## 🔧 拡張性

### 新しいドメインサービス追加

```python
class EducationSeedService:
    """チュートリアルシード処理"""
    
    def __init__(self, tutorial_repository):
        self.tutorial_repository = tutorial_repository
    
    async def seed_tutorials(self, data):
        # チュートリアルシードロジック
        pass

# ユースケースに追加
class SeedUseCase:
    def __init__(self, problem_service, judge_service, education_service=None):
        # ...
```

### カスタム値オブジェクト

```python
@dataclass(frozen=True)
class EducationSeedResult:
    tutorials_created: int
    lessons_created: int
    # ...
```

## 📊 メトリクス・モニタリング

各レイヤーでのロギング:

```python
# Domain Service
logger.info(f"📚 Seeding {len(books_data)} books...")

# Use Case  
logger.info("🚀 Starting complete dataset seeding...")

# Facade
logger.info("🎯 Facade seeding completed!")
```

統計情報の取得:

```python
stats = await facade.get_statistics()
print(f"Books: {stats['problem_domain']['books_total']}")
print(f"Problems: {stats['problem_domain']['problems_total']}")
```

## 🚀 パフォーマンス

- **Domain Services**: 単一責任でパフォーマンス最適化
- **Use Cases**: 複数サービスの協調処理
- **Facade**: シンプル性重視、内部最適化は隠蔽

## 💡 ベストプラクティス

1. **Facade使用を推奨**: 外部クライアントは基本的にFacadeを使用
2. **DI活用**: リポジトリはDIコンテナから注入
3. **エラーハンドリング**: 各レイヤーで適切な例外処理
4. **ログ出力**: 処理の進行状況を適切にログ出力
5. **統計取得**: シード後は必ず統計情報で検証

このDDD構造により、保守性、テスタビリティ、拡張性を確保しながら、シンプルなインターフェースを提供できます。