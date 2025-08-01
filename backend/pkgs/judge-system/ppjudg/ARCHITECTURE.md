# Judge System Architecture
ジャッジシステム アーキテクチャ

## 概要
ジャッジシステムを以下の方針で改修しました：

- **メッセージキューからの呼び出し** → `event/` ディレクトリに実装
- **APIリクエストからの呼び出し** → `usecase/api_*_usecase.py` に実装

## ディレクトリ構造

```
ppjudg/
├── event/                          # メッセージキューイベントハンドラー
│   ├── __init__.py
│   ├── message_queue_handlers.py   # MQからの処理
│   └── domain_event_handlers.py    # ドメインイベント処理
├── usecase/                        # ユースケース層
│   ├── api_submission_usecase.py   # API: 提出関連ワークフロー
│   ├── api_system_usecase.py       # API: システム管理ワークフロー
│   ├── submission_use_case.py      # 内部: 提出処理
│   ├── code_execution_use_case.py  # 内部: コード実行処理
│   └── judge_worker_use_case.py    # 内部: ワーカー処理
├── app/                            # アプリケーション層
│   ├── handlers.py                 # レガシー（DEPRECATED）
│   └── services.py                 # アプリケーションサービス
└── domain/                         # ドメイン層
```

## 処理の流れ

### APIリクエスト処理
```
API Request → Controllers → ApiSubmissionUseCase/ApiSystemUseCase → Domain Services → Repository
```

### メッセージキュー処理
```
Message Queue → MessageQueueEventHandler → Domain Services → Repository
```

### ドメインイベント処理
```
Domain Event → DomainEventHandler → Domain Services → Repository
```

## 依存関係の原則

Clean Architectureに従って、以下の依存関係を厳守します：

```
Controllers → API UseCases → Domain Services → Repository
Event Handlers → Domain Services → Repository
```

**重要な制約:**
- **Event** は **UseCase** に依存してはいけない
- **UseCase** は **Event** を使ってはいけない（EventBusへの発行は除く）
- すべての処理は **Domain Services** と **Repository** を通じて実行

## 主要コンポーネント

### Event Handlers

#### `event/message_queue_handlers.py`
- `SubmissionQueueHandler`: 提出関連MQメッセージの処理
- `JudgeWorkerEventHandler`: ワーカー関連MQメッセージの処理
- `MessageQueueDispatcher`: メッセージルーティング

#### `event/domain_event_handlers.py`
- `CoreDomainEventHandler`: コアドメインイベント処理
- `JudgeSystemEventHandler`: ジャッジシステム内部イベント処理

### API Use Cases

#### `usecase/api_submission_usecase.py`
- `ApiSubmissionUseCase`: 提出関連APIワークフロー
  - `submit_solution()`: 解答提出
  - `get_submission_status()`: 提出状況取得
  - `get_user_submissions()`: ユーザー提出一覧
  - `rejudge_submission()`: 再ジャッジ

#### `usecase/api_system_usecase.py`
- `ApiSystemUseCase`: システム管理APIワークフロー
  - `get_system_status()`: システム状況取得
  - `get_queue_status()`: キュー状況取得
  - `get_submission_statistics()`: 提出統計取得
  - `trigger_maintenance()`: メンテナンス実行

### Internal Use Cases
内部処理用のユースケース（既存）:
- `SubmissionUseCase`: 提出内部処理
- `JudgeWorkerUseCase`: ワーカー処理
- `CodeExecutionUseCase`: コード実行処理

## 使用方法

### APIからの提出処理
```python
from ppjudg.usecase import ApiSubmissionUseCase

api_usecase = ApiSubmissionUseCase()
result = await api_usecase.submit_solution(
    user_id=uuid.UUID("..."),
    problem_id=uuid.UUID("..."),
    code="print('Hello World')",
    language=Language.PYTHON
)
```

### メッセージキューからの処理
```python
from ppjudg.event import MessageQueueDispatcher

dispatcher = MessageQueueDispatcher()
success = await dispatcher.dispatch_message({
    "type": "judge.request",
    "submission_id": "...",
    "worker_id": "worker-1"
})
```

## 使用ガイド

### ドメインイベント処理
```python
from ppjudg.event.domain_event_handlers import setup_event_handlers

# イベントハンドラーを設定
handlers = await setup_event_handlers()
```

### メッセージキュー処理
```python
from ppjudg.event.message_queue_handlers import MessageQueueDispatcher

# メッセージディスパッチャーを使用
dispatcher = MessageQueueDispatcher()
success = await dispatcher.dispatch_message({
    "type": "judge.request",
    "submission_id": "...",
    "worker_id": "worker-1"
})
```

### APIワークフロー
```python
# API用ユースケース（APIリクエスト処理）
from ppjudg.usecase import ApiSubmissionUseCase, ApiSystemUseCase

# 内部ユースケース（ビジネスロジック）
from ppjudg.usecase import SubmissionUseCase, JudgeWorkerUseCase
```

## 設計原則

1. **責任の分離**:
   - API用ユースケース: バリデーション、レスポンス形成、エラーハンドリング
   - 内部ユースケース: ビジネスロジック、ドメインサービス呼び出し
   - イベントハンドラー: メッセージ処理、ドメインサービス呼び出し

2. **イベント処理**:
   - ドメインイベント: `event/domain_event_handlers.py`
   - MQメッセージ: `event/message_queue_handlers.py`

3. **エラーハンドリング**: API用ユースケースは構造化されたエラーレスポンスを返します。

4. **依存関係**: イベントハンドラーはユースケースに依存せず、ドメインサービスとリポジトリのみを使用します。

## 今後の拡張

- WebSocket通知機能
- リアルタイム進行状況更新
- コンテスト機能との統合
- 分散ワーカー管理
- メトリクス収集・監視機能