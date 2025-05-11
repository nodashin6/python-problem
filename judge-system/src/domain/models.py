from pydantic import BaseModel, Field
from datetime import datetime


class Problem(BaseModel):
    id: str
    title: str | None = None
    markdown : str | None = None
    level: int = 1  # 問題の難易度レベル (1-10)
    solved: bool = False  # 解いた状態かどうか
    solved_at: datetime | None = None  # いつ解いたか

class Stdin(BaseModel):
    id: str | None = None
    name: str | None = None
    content: str
    
class Stdout(BaseModel):
    id: str | None = None
    name: str | None = None
    content: str

class Testcase(BaseModel):
    id: str
    name: str
    problem: Problem
    stdin: Stdin
    stdout: Stdout

    model_config = {
        "arbitrary_types_allowed": True
    }


class JudgeRequest(BaseModel):
    id: str
    problem: Problem
    code: str
    
    
class JudgeResultMetadata(BaseModel):
    memory_used: int | None = None
    time_used: int | None = None
    compile_error: str | None = None
    runtime_error: str | None = None
    output: str | None = None


class JudgeResult(BaseModel):
    id: str
    problem: Problem
    test_case: Testcase
    status: str
    metadata: JudgeResultMetadata | None = None

    model_config = {
        "arbitrary_types_allowed": True
    }


class JudgeResponse(BaseModel):
    id: str
    problem: Problem
    code: str
    results: list[JudgeResult]

    model_config = {
        "arbitrary_types_allowed": True
    }


# 提出ログ用の新しいモデル
class SubmissionLog(BaseModel):
    id: str
    problem_id: str
    problem_set: str
    code: str
    submitted_at: datetime
    status: str  # 全体のステータス (AC/WA/RE/TLE)
    result_path: str  # 結果の詳細が保存されているファイルへのパス
    
    model_config = {
        "arbitrary_types_allowed": True
    }
    
    
# 提出結果の詳細を保存するためのモデル
class SubmissionResult(BaseModel):
    id: str
    submission_id: str
    problem_id: str
    problem_set: str
    submitted_at: datetime
    results: list[JudgeResult]
    
    model_config = {
        "arbitrary_types_allowed": True
    }


# ユーザーの問題解決状態を管理するモデル
class UserProblemStatus(BaseModel):
    user_id: str
    problem_id: str
    problem_set: str
    solved: bool = False
    solved_at: datetime | None = None
    submission_count: int = 0
    last_submission_id: str | None = None
    
    model_config = {
        "arbitrary_types_allowed": True
    }