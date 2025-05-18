from pydantic import BaseModel, Field, UUID4
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any, Union
from uuid import UUID


class JudgeStatus(str, Enum):
    """ジャッジプロセスの状態"""

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"  # 修正: FAILD → SUCCEEDED (スペルミス)
    FAILED = "failed"  # 修正: FAILD → FAILED (スペルミス)
    ERROR = "error"
    OTHER = "other"


class CaseFile(BaseModel):
    """テストケースの入力・出力ファイル"""

    id: UUID4
    url: str
    file_hash: str
    created_at: datetime
    updated_at: datetime


class Book(BaseModel):
    """問題集"""

    id: UUID4
    title: str
    author: str
    published_date: datetime
    is_published: bool = False
    created_at: datetime
    updated_at: datetime


class Problem(BaseModel):
    """問題定義"""

    id: UUID4
    book_id: Optional[UUID4] = None
    title: str
    description: str
    difficulty: int = Field(ge=1, le=5)  # 1-5の難易度
    tags: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

    # ユーザー状態情報（DB内には存在しない計算フィールド）
    solved: bool = False
    solved_at: Optional[datetime] = None


class ProblemContent(BaseModel):
    """問題コンテンツ（多言語対応）"""

    id: UUID4
    problem_id: UUID4
    language: str
    md_content: str
    created_at: datetime
    updated_at: datetime


class Editorial(BaseModel):
    """問題解説"""

    id: UUID4
    problem_id: UUID4
    created_at: datetime
    updated_at: datetime


class EditorialContent(BaseModel):
    """解説内容（多言語対応）"""

    id: UUID4
    editorial_id: UUID4
    language: str
    md_content: str
    created_at: datetime
    updated_at: datetime


class JudgeCase(BaseModel):
    """テストケース定義"""

    id: UUID4
    problem_id: UUID4
    input_id: UUID4
    output_id: UUID4
    is_sample: bool = False
    display_order: int = 0
    created_at: datetime
    updated_at: datetime

    # 関連オブジェクト
    problem: Optional[Problem] = None
    input_file: Optional[CaseFile] = None
    output_file: Optional[CaseFile] = None

    # 便宜的なプロパティ
    @property
    def name(self) -> str:
        return f"Case {self.display_order}"

    @property
    def stdin(self) -> "Stdin":
        if not self.input_file:
            return Stdin(content="")
        return Stdin(
            id=str(self.input_id),
            name=f"input_{self.display_order}",
            content=self.input_file.url,  # 実際はコンテンツを取得するロジックが必要
        )

    @property
    def stdout(self) -> "Stdout":
        if not self.output_file:
            return Stdout(content="")
        return Stdout(
            id=str(self.output_id),
            name=f"output_{self.display_order}",
            content=self.output_file.url,  # 実際はコンテンツを取得するロジックが必要
        )

    model_config = {"arbitrary_types_allowed": True}


class Submission(BaseModel):
    """ユーザーの提出"""

    id: UUID4
    problem_id: UUID4
    user_id: UUID4
    code: str
    language: str
    status: str = "pending"
    score: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    # 関連オブジェクト
    problem: Optional[Problem] = None

    model_config = {"arbitrary_types_allowed": True}


class JudgeProcess(BaseModel):
    """ジャッジプロセス実行情報"""

    id: UUID4
    submission_id: UUID4
    status: JudgeStatus = JudgeStatus.PENDING
    result: Optional[str] = None
    execution_time_ms: Optional[int] = None
    memory_usage_kb: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    # 関連オブジェクト
    submission: Optional[Submission] = None
    results: List["JudgeCaseResult"] = []

    @property
    def problem(self) -> Optional[Problem]:
        if self.submission and self.submission.problem:
            return self.submission.problem
        return None

    @property
    def code(self) -> str:
        if self.submission:
            return self.submission.code
        return ""


class JudgeCaseResultMetadata(BaseModel):
    """ジャッジ結果のメタデータ"""

    memory_used_kb: Optional[int] = None
    time_used_ms: Optional[int] = None
    compile_error: Optional[str] = None
    runtime_error: Optional[str] = None
    output: Optional[str] = None


class JudgeCaseResult(BaseModel):
    """テストケースごとの実行結果"""

    id: UUID4
    judge_process_id: UUID4
    judge_case_id: UUID4
    status: str
    result: str
    error: Optional[str] = None
    warning: Optional[str] = None
    processing_time_ms: Optional[int] = None
    memory_usage_kb: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    # 関連オブジェクト
    judge_case: Optional[JudgeCase] = None
    judge_process: Optional[JudgeProcess] = None
    metadata: Optional[JudgeCaseResultMetadata] = None

    @property
    def problem(self) -> Optional[Problem]:
        if self.judge_case and self.judge_case.problem:
            return self.judge_case.problem
        return None

    model_config = {"arbitrary_types_allowed": True}


# リクエスト・レスポンスモデル


class Stdin(BaseModel):
    """標準入力データ"""

    id: Optional[str] = None
    name: Optional[str] = None
    content: str


class Stdout(BaseModel):
    """標準出力データ"""

    id: Optional[str] = None
    name: Optional[str] = None
    content: str


class JudgeProcessRequest(BaseModel):
    """ジャッジプロセスのリクエスト"""

    id: str
    problem_id: str
    code: str
    language: str = "python"


class JudgeProcessResponse(BaseModel):
    """ジャッジプロセスのレスポンス"""

    id: str
    problem_id: str
    code: str
    status: JudgeStatus
    execution_time_ms: Optional[int] = None
    memory_usage_kb: Optional[int] = None
    results: List[Dict[str, Any]] = []

    model_config = {"arbitrary_types_allowed": True}


# ユーザー関連モデル


class UserRole(BaseModel):
    """ユーザーロール情報"""

    id: UUID4
    user_id: UUID4
    role: str  # 'user', 'admin', 'moderator'
    created_at: datetime
    updated_at: datetime


class UserStat(BaseModel):
    """ユーザー統計情報"""

    id: UUID4
    user_id: UUID4
    problems_solved: int = 0
    submissions_count: int = 0
    streak_days: int = 0
    rank_score: float = 0.0
    created_at: datetime
    updated_at: datetime


class UserProblemStatus(BaseModel):
    """ユーザーの問題解決状態"""

    user_id: str
    problem_id: str
    solved: bool = False
    solved_at: Optional[datetime] = None
    submission_count: int = 0
    last_submission_id: Optional[str] = None
    best_score: Optional[float] = None

    model_config = {"arbitrary_types_allowed": True}
