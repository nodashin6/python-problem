"""
Execution Status Enums for Judge Domain
ジャッジドメイン用実行ステータス列挙型
"""

from enum import Enum


class ExecutionStatus(Enum):
    """実行ステータス"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    MEMORY_LIMIT_EXCEEDED = "memory_limit_exceeded"
    COMPILATION_ERROR = "compilation_error"
    RUNTIME_ERROR = "runtime_error"


class JudgeResultType(Enum):
    """ジャッジ結果タイプ"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    WRONG_ANSWER = "wrong_answer"
    TIME_LIMIT_EXCEEDED = "time_limit_exceeded"
    MEMORY_LIMIT_EXCEEDED = "memory_limit_exceeded"
    RUNTIME_ERROR = "runtime_error"
    COMPILATION_ERROR = "compilation_error"
    PRESENTATION_ERROR = "presentation_error"
    PARTIAL_ACCEPTED = "partial_accepted"


class ProgrammingLanguage(Enum):
    """プログラミング言語"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    CPP = "cpp"
    C = "c"
    RUST = "rust"
    GO = "go"