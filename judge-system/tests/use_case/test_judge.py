import src
from packaging.version import Version, parse
import pytest
from src.use_case.judge import JudgeUserCode, CaseLoader
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


def test_testcase_loader():
    """
    テストケースローダーが正しく動作するかテスト
    """
    # 001問題を読み込むテスト
    problem = models.Problem(id="001")
    loader = CaseLoader(problem, "getting-started")
    testcase_names = loader.load_testcase_names()
    
    # getting-started/001のテストケースが読み込めるか
    assert len(testcase_names) > 0
    
    # イテレータが正しく動作するか
    testcases = list(loader)
    assert len(testcases) == len(testcase_names)
    
    # 最初のテストケースの中身をチェック
    first_testcase = testcases[0]
    assert first_testcase.id is not None
    assert isinstance(first_testcase.stdin.content, str)
    assert isinstance(first_testcase.stdout.content, str)


def test_judge_user_code_ac():
    """
    正解のコードが正しく判定されるかテスト
    """
    problem = models.Problem(id="001")
    judge = JudgeUserCode(problem, "getting-started")
    
    # 正解するコード（カンマと感嘆符あり！）
    correct_code = 'print("Hello, World!")'
    
    # テストケースの入出力内容
    stdin = ""
    expected_stdout = "Hello, World!"
    
    # 判定
    result = judge.judge(correct_code, stdin, expected_stdout)
    
    # 正解していることを確認
    assert result.is_ac is True
    assert result.metadata.runtime_error is None
    assert result.metadata.compile_error is None
    assert result.metadata.time_used > 0


def test_judge_user_code_wa():
    """
    不正解のコードが正しく判定されるかテスト
    """
    problem = models.Problem(id="001")
    judge = JudgeUserCode(problem, "getting-started")
    
    # 不正解のコード（カンマなし）
    wrong_code = 'print("Hello World")'
    
    # テストケースの入出力内容
    stdin = ""
    expected_stdout = "Hello, World!"
    
    # 判定
    result = judge.judge(wrong_code, stdin, expected_stdout)
    
    # 不正解であることを確認
    assert result.is_ac is False
    assert result.metadata.runtime_error is None
    assert result.metadata.compile_error is None
    assert result.metadata.output == "Hello World"


def test_judge_user_code_re():
    """
    実行時エラーを起こすコードが正しく判定されるかテスト
    """
    problem = models.Problem(id="001")
    judge = JudgeUserCode(problem, "getting-started")
    
    # 実行時エラーを起こすコード
    error_code = 'print(undefined_variable)'
    
    # テストケースの入出力内容
    stdin = ""
    expected_stdout = "Hello, World!"
    
    # 判定
    result = judge.judge(error_code, stdin, expected_stdout)
    
    # 実行時エラーであることを確認
    assert result.is_ac is False
    assert result.metadata.runtime_error is not None
    assert "undefined_variable" in result.metadata.runtime_error


def test_judge_user_code_tle():
    """
    時間制限を超えるコードが正しく判定されるかテスト
    """
    problem = models.Problem(id="001")
    judge = JudgeUserCode(problem, "getting-started")
    judge.TIME_LIMIT = 1  # テスト用に時間制限を短くする
    
    # 時間制限を超えるコード
    tle_code = 'import time\nwhile True: time.sleep(0.1)'
    
    # テストケースの入出力内容
    stdin = ""
    expected_stdout = "Hello, World!"
    
    # 判定
    result = judge.judge(tle_code, stdin, expected_stdout)
    
    # 時間制限超過であることを確認
    assert result.is_ac is False
    assert "Time Limit Exceeded" in result.metadata.runtime_error or result.metadata.time_used >= judge.TIME_LIMIT * 1000


def test_judge_complete_flow():
    """
    judgeの一連の流れをテスト
    """
    problem = models.Problem(id="001")
    judge = JudgeUserCode(problem, ".pytest")
    
    # 正解するコード（カンマと感嘆符あり！）
    correct_code = 'print("Hello, World!")'
    
    # 判定実行
    response = judge(correct_code)
    
    # レスポンスの形式を確認
    assert isinstance(response, models.JudgeResponse)
    assert response.problem.id == "001"  # 辞書ではなくオブジェクトアクセス
    assert response.code == correct_code
    assert len(response.results) > 0
    
    # 全テストケースがACであることを確認
    for result in response.results:
        assert result.status == "AC"
        assert result.metadata.runtime_error is None
        assert result.metadata.time_used > 0