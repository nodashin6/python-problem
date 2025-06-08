class ProgrammingLanguage(str, Enum):
    """プログラミング言語"""

    PYTHON3 = "python3"
    JAVA = "java"
    CPP = "cpp"
    C = "c"
    JAVASCRIPT = "javascript"
    GO = "go"
    RUST = "rust"


# Judge Domain Enums
class ExecutionStatus(str, Enum):
    """実行ステータス"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    MEMORY_EXCEEDED = "memory_exceeded"
    CANCELLED = "cancelled"


class JudgeStatus(str, Enum):
    """ジャッジステータス"""

    AC = "AC"  # Accepted
    WA = "WA"  # Wrong Answer
    TLE = "TLE"  # Time Limit Exceeded
    MLE = "MLE"  # Memory Limit Exceeded
    RE = "RE"  # Runtime Error
    CE = "CE"  # Compilation Error


class JudgeCaseType(str, Enum):
    """ジャッジケースタイプ"""

    SAMPLE = "sample"
    HIDDEN = "hidden"
    PRETEST = "pretest"


# 判定結果の種類
class JudgeResultType(str, Enum):
    """ジャッジ結果タイプ"""

    AC = "AC"  # Accepted
    WA = "WA"  # Wrong Answer
    TLE = "TLE"  # Time Limit Exceeded
    MLE = "MLE"  # Memory Limit Exceeded
    RE = "RE"  # Runtime Error
    CE = "CE"  # Compilation Error
    IE = "IE"  # Internal Error
    PE = "PE"  # Presentation Error
    JUDGING = "JUDGING"  # まだジャッジ中
    PENDING = "PENDING"  # ジャッジ待ち
