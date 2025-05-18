import src
from packaging.version import Version, parse
import pytest
from src.usecase.judge_use_case import (
    JudgeUserCode,
    JudgeCaseLoader,
    JudgeProcessResult,
)
from src.domain import models
import os
from pathlib import Path


# フィクスチャの部分は削除して、単純なテストにするわよ～
@pytest.mark.skipif(
    parse(src.__version__) < Version("0.1.0"),
    reason="Judge System version is less than 0.1.0",
)
def test_judge_system_version():
    """
    Test the version of the Judge System.
    """
    assert parse(src.__version__) >= Version("0.1.0")


def test_judge_case_loader():
    """
    テストケースローダーが正しく動作するかテスト
    """
    # 001問題を読み込むテスト
    problem = models.Problem(id="001")
    loader = JudgeCaseLoader(problem, "getting-started")
    judge_case_names = loader.load_judge_case_names()

    # getting-started/001のテストケースが読み込めるか
    assert len(judge_case_names) > 0

    # イテレータが正しく動作するか
    JudgeCases = list(loader)
    assert len(JudgeCases) == len(judge_case_names)

    # 最初のテストケースの中身をチェック
    first_JudgeCase = JudgeCases[0]
    assert first_JudgeCase.id is not None
    assert isinstance(first_JudgeCase.stdin.content, str)
    assert isinstance(first_JudgeCase.stdout.content, str)


def test_judge_user_code_ac():
    """
    正解のコードが正しく判定されるかテスト
    """
    judge = JudgeUserCode()

    # 正解するコード（カンマと感嘆符あり！）
    correct_code = 'print("Hello, World!")'

    # テストケースを作成
    problem = models.Problem(id="001")
    judge_case = models.JudgeCase(
        id="01",
        name="sample",
        problem=problem.model_dump(),
        stdin=models.Stdin(id="", name="sample", content=""),
        stdout=models.Stdout(id="", name="sample", content="Hello, World!"),
    )

    # 判定
    result = judge.judge_case(correct_code, judge_case)

    # 正解していることを確認
    assert result.is_ac is True
    assert result.metadata.runtime_error is None
    assert result.metadata.compile_error is None
    assert result.metadata.time_used > 0

    # ステータス確認
    status = judge.determine_status(result)
    assert status == "AC"


def test_judge_user_code_wa():
    """
    不正解のコードが正しく判定されるかテスト
    """
    judge = JudgeUserCode()

    # 不正解のコード（カンマなし）
    wrong_code = 'print("Hello World")'

    # テストケースを作成
    problem = models.Problem(id="001")
    JudgeCase = models.JudgeCase(
        id="01",
        name="sample",
        problem=problem.model_dump(),
        stdin=models.Stdin(id="", name="sample", content=""),
        stdout=models.Stdout(id="", name="sample", content="Hello, World!"),
    )

    # 判定
    result = judge.judge_case(wrong_code, JudgeCase)

    # 不正解であることを確認
    assert result.is_ac is False
    assert result.metadata.runtime_error is None
    assert result.metadata.compile_error is None
    assert result.metadata.output == "Hello World"

    # ステータス確認
    status = judge.determine_status(result)
    assert status == "WA"


def test_judge_user_code_re():
    """
    実行時エラーを起こすコードが正しく判定されるかテスト
    """
    judge = JudgeUserCode()

    # 実行時エラーを起こすコード
    error_code = "print(undefined_variable)"

    # テストケースを作成
    problem = models.Problem(id="001")
    JudgeCase = models.JudgeCase(
        id="01",
        name="sample",
        problem=problem.model_dump(),
        stdin=models.Stdin(id="", name="sample", content=""),
        stdout=models.Stdout(id="", name="sample", content="Hello, World!"),
    )

    # 判定
    result = judge.judge_case(error_code, JudgeCase)

    # 実行時エラーであることを確認
    assert result.is_ac is False
    assert result.metadata.runtime_error is not None
    assert "undefined_variable" in result.metadata.runtime_error

    # ステータス確認
    status = judge.determine_status(result)
    assert status == "RE"


def test_judge_user_code_tle():
    """
    時間制限を超えるコードが正しく判定されるかテスト
    """
    judge = JudgeUserCode()
    judge.code_executor.TIME_LIMIT = 1  # テスト用に時間制限を短くする

    # 時間制限を超えるコード
    tle_code = "import time\nwhile True: time.sleep(0.1)"

    # テストケースを作成
    problem = models.Problem(id="001")
    JudgeCase = models.JudgeCase(
        id="01",
        name="sample",
        problem=problem.model_dump(),
        stdin=models.Stdin(id="", name="sample", content=""),
        stdout=models.Stdout(id="", name="sample", content="Hello, World!"),
    )

    # 判定
    result = judge.judge_case(tle_code, JudgeCase)

    # 時間制限超過であることを確認
    assert result.is_ac is False
    assert "Time Limit Exceeded" in result.metadata.runtime_error

    # ステータス確認
    status = judge.determine_status(result)
    assert status == "TLE"
