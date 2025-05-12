import yaml
import subprocess
import os
import sys
import tempfile
import time
import resource
import copy
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List, Iterator
from src.const import TESTCASE_DIR, PRJ_DIR, IN_DIR, OUT_DIR, PROBLEM_DIR, DEFAULT_PROBLEM_SET
from src.domain import models


class CaseLoader:
    """テストケースをロードするためのクラス"""
    
    def __init__(self, problem: models.Problem, problem_set: str = DEFAULT_PROBLEM_SET):
        self.problem = problem
        self.problem_set = problem_set
        
    def __iter__(self) -> Iterator[models.Testcase]:
        """テストケースのイテレータを返します"""
        testcase_names = self.load_testcase_names()
        for testcase_name in testcase_names:
            try:
                yield self.load_testcase(testcase_name)
            except FileNotFoundError as e:
                logging.error(f"テストケース {testcase_name} の読み込みに失敗: {str(e)}")
            
    def load_testcase_names(self) -> List[str]:
        """テストケース名のリストを読み込みます"""
        # パス: problems/問題集/問題ID/testcase.yaml
        yaml_path = PROBLEM_DIR / self.problem_set / f"{self.problem.id}" / "testcase.yaml"
        
        try:
            with open(yaml_path, "r") as f:
                testcase_names = yaml.safe_load(f)
                
            # 数値のテストケース名を適切にフォーマット
            for i in range(len(testcase_names)):
                if isinstance(testcase_names[i], int):
                    testcase_names[i] = f"{testcase_names[i]:02d}"
                    
            return testcase_names
            
        except FileNotFoundError:
            logging.error(f"テストケースの定義ファイルが見つかりません: {yaml_path}")
            return []
        except Exception as e:
            logging.error(f"テストケース名の読み込みエラー: {str(e)}")
            return []
            
    def get_input_path(self, testcase_name: str) -> Path:
        """入力ファイルのパスを返します"""
        # パス: problems/問題集/問題ID/testcases/in/テストケース名.txt
        return PROBLEM_DIR / self.problem_set / f"{self.problem.id}" / "testcases" / "in" / f"{testcase_name}.txt"
    
    def get_output_path(self, testcase_name: str) -> Path:
        """出力ファイルのパスを返します"""
        # パス: problems/問題集/問題ID/testcases/out/テストケース名.txt
        return PROBLEM_DIR / self.problem_set / f"{self.problem.id}" / "testcases" / "out" / f"{testcase_name}.txt"
    
    def load_testcase(self, testcase_name: str) -> models.Testcase:
        """テストケース名からテストケースを読み込みます"""
        in_path = self.get_input_path(testcase_name)
        out_path = self.get_output_path(testcase_name)
        
        # 入力ファイルは必須
        if not in_path.exists():
            raise FileNotFoundError(f"入力ファイルが見つかりません: {in_path}")
        
        # 入力を読み込む
        with open(in_path, "r") as f:
            stdin = f.read()
        
        # 出力ファイルがある場合は読み込む、ない場合は空文字を設定
        stdout = ""
        if out_path.exists():
            with open(out_path, "r") as f:
                stdout = f.read()
        else:
            logging.warning(f"出力ファイルが見つかりません: {out_path}")
        
        return models.Testcase(
            id=testcase_name,
            name=testcase_name,
            problem=self.problem.model_dump(),
            stdin=models.Stdin(id="", name=testcase_name, content=stdin),
            stdout=models.Stdout(id="", name=testcase_name, content=stdout),
        )


class JudgeResult:
    """ジャッジ結果を表すクラス"""
    def __init__(self, is_ac: bool, metadata: models.JudgeResultMetadata):
        self.is_ac = is_ac
        self.metadata = metadata


class CodeExecutor:
    """コードの実行とリソース制限を担当するクラス"""
    
    def __init__(self):
        self.TIME_LIMIT = 5  # 5秒のタイムリミット
        self.MEMORY_LIMIT = 256 * 1024 * 1024  # 256MBのメモリ制限
    
    def execute(self, code: str, stdin: str) -> tuple[str, str, int, int, Optional[int]]:
        """
        コードを実行して結果を返す
        
        Args:
            code: 実行するPythonコード
            stdin: 標準入力として与えるテキスト
            
        Returns:
            tuple: (標準出力, 標準エラー出力, 実行時間(ms), 終了コード, メモリ使用量(バイト))
        """
        # 一時ファイルにコードを書き込む
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(code.encode('utf-8'))
        
        memory_used = None
        process = None
        
        try:
            # リソース制限を設定するラッパー関数
            def set_limits():
                # CPUタイムの制限
                resource.setrlimit(resource.RLIMIT_CPU, (self.TIME_LIMIT, self.TIME_LIMIT))
                # メモリ使用量の制限
                resource.setrlimit(resource.RLIMIT_AS, (self.MEMORY_LIMIT, self.MEMORY_LIMIT))
            
            start_time = time.time()
            
            # コードを実行
            process = subprocess.Popen(
                [sys.executable, temp_file_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=set_limits  # リソース制限を設定
            )
            
            # 標準入力を渡して結果を取得
            stdout, stderr = process.communicate(input=stdin, timeout=self.TIME_LIMIT)
            
            end_time = time.time()
            execution_time = int((end_time - start_time) * 1000)  # ミリ秒に変換
            
            # プロセスが使用したメモリを取得（Linux限定）
            try:
                with open(f"/proc/{process.pid}/status", "r") as f:
                    for line in f:
                        if line.startswith("VmPeak:"):
                            memory_used = int(line.split()[1]) * 1024  # KBからバイトに変換
                            break
            except (FileNotFoundError, PermissionError):
                # /proc が使えない環境では測定しない
                pass
            
            return stdout, stderr, execution_time, process.returncode, memory_used
            
        except subprocess.TimeoutExpired:
            # タイムアウト
            if process:
                try:
                    process.kill()  # 念のためプロセスを強制終了
                except:
                    pass
            return "", "Time Limit Exceeded", self.TIME_LIMIT * 1000, -1, memory_used
            
        finally:
            # 一時ファイルを削除
            try:
                os.unlink(temp_file_path)
            except:
                pass


class JudgeUserCode:
    """単一のテストケースに対してコードを評価するクラス"""
    
    def __init__(self):
        self.code_executor = CodeExecutor()
    
    def judge_testcase(self, code: str, testcase: models.Testcase) -> JudgeResult:
        """
        単一のテストケースに対してコードを実行・評価する
        
        Args:
            code: 評価するPythonコード
            testcase: テストケース
            
        Returns:
            JudgeResult: ジャッジ結果
        """
        stdin = testcase.stdin.content
        expected_stdout = testcase.stdout.content
        
        try:
            # コードを実行
            stdout, stderr, execution_time, return_code, memory_used = self.code_executor.execute(code, stdin)
            
            # 結果の判定
            if return_code != 0:
                # 実行時エラー
                metadata = models.JudgeResultMetadata(
                    memory_used=memory_used,
                    time_used=execution_time,
                    compile_error=None,
                    runtime_error=stderr,
                    output=stdout
                )
                return JudgeResult(False, metadata)
            
            # 出力の比較（空白・改行を正規化）
            stdout = stdout.strip()
            expected_stdout = expected_stdout.strip()
            is_ac = stdout == expected_stdout
            
            metadata = models.JudgeResultMetadata(
                memory_used=memory_used,
                time_used=execution_time,
                compile_error=None,
                runtime_error=None,
                output=stdout
            )
            return JudgeResult(is_ac, metadata)
            
        except Exception as e:
            # その他のエラー
            metadata = models.JudgeResultMetadata(
                memory_used=None,
                time_used=None,
                compile_error=None,
                runtime_error=str(e),
                output=None
            )
            return JudgeResult(False, metadata)
    
    def determine_status(self, result: JudgeResult) -> str:
        """ジャッジ結果のステータスを決定する"""
        if result.is_ac:
            return "AC"
        
        # 失敗の種類を判定
        if result.metadata.runtime_error:
            if "Time Limit Exceeded" in result.metadata.runtime_error:
                return "TLE"
            return "RE"
        elif result.metadata.compile_error:
            return "CE"
        else:
            return "WA"


class AppUseCase:
    """問題に関する操作を行うユースケース"""
    
    def __init__(self, problem: models.Problem, problem_set: str = DEFAULT_PROBLEM_SET):
        self.problem = problem
        self.problem_set = problem_set
        
    def read_problem(self) -> models.Problem:
        """問題文を読み込む"""
        # 新しいパス: problems/問題集/問題ID/problem/ja.md
        problem_path = PROBLEM_DIR / self.problem_set / f"{self.problem.id}" / "problem" / "ja.md"
        with open(problem_path, "r") as f:
            problem_md = f.read()
        
        return models.Problem(
            id=self.problem.id,
            markdown=problem_md
        )


class ReadProblemListUseCase:
    """問題リストを読み込むユースケース"""
    
    def __init__(self, problem_set: str = DEFAULT_PROBLEM_SET):
        self.problem_set = problem_set
        
    def __call__(self) -> list[models.Problem]:
        """問題のリストを読み込む"""
        # 新しいパス: problems/問題集/problems.yaml
        yaml_path = PROBLEM_DIR / self.problem_set / "problems.yaml"
        with open(yaml_path, "r") as f:
            rows = yaml.safe_load(f)
        
        problems = []
        for row in rows:
            # レベル情報も取得する
            level = row.get("level", 1)  # デフォルトは1
            problems.append(models.Problem(
                id=row["id"], 
                title=row["title"],
                level=level
            ))
        return problems