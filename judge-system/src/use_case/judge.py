import yaml
import subprocess
import os
import sys
import tempfile
import time
import resource
import copy
from pathlib import Path
from src.const import TESTCASE_DIR, PRJ_DIR, IN_DIR, OUT_DIR, PROBLEM_DIR, DEFAULT_PROBLEM_SET
from src.domain import models


class TestcaseLoader:
    def __init__(self, problem: models.Problem, problem_set: str = DEFAULT_PROBLEM_SET):
        self.problem = problem
        self.problem_set = problem_set
        
    def __iter__(self):
        testcase_names = self.load_testcase_names()
        for testcase_name in testcase_names:
            yield self.load_testcase(testcase_name)
            
    def load_testcase_names(self) -> list[str]:
        # 新しいパス: problems/問題集/問題ID/testcase.yaml
        yaml_path = PROBLEM_DIR / self.problem_set / f"{self.problem.id}" / "testcase.yaml"
        with open(yaml_path, "r") as f:
            testcase_names = yaml.safe_load(f)
        print(testcase_names)
        for i in range(len(testcase_names)):
            if isinstance(testcase_names[i], int):
                testcase_names[i] = "{x:0>2}".format(x=testcase_names[i])
        return testcase_names
            
    def get_input_path(self, testcase_name: str):
        # 新しいパス: problems/問題集/問題ID/testcases/in/テストケース名.txt
        return PROBLEM_DIR / self.problem_set / f"{self.problem.id}" / "testcases" / "in" / f"{testcase_name}.txt"
    
    def get_output_path(self, testcase_name: str):
        # 新しいパス: problems/問題集/問題ID/testcases/out/テストケース名.txt
        return PROBLEM_DIR / self.problem_set / f"{self.problem.id}" / "testcases" / "out" / f"{testcase_name}.txt"
    
    def load_testcase(self, testcase_name: str):
        in_path = self.get_input_path(testcase_name)
        out_path = self.get_output_path(testcase_name)
        
        if not in_path.exists() or not out_path.exists():
            raise FileNotFoundError(f"Testcase files not found for {testcase_name}")
        
        with open(in_path, "r") as f:
            stdin = f.read()
        
        with open(out_path, "r") as f:
            stdout = f.read()
        
        return models.Testcase(
            id=testcase_name,
            name=testcase_name,
            problem=self.problem.model_dump(),
            stdin=models.Stdin(id="", name=testcase_name, content=stdin),
            stdout=models.Stdout(id="", name=testcase_name, content=stdout),
        )


class JudgeUserCode:
    def __init__(self, problem: models.Problem, problem_set: str = DEFAULT_PROBLEM_SET):
        self.problem = problem
        self.problem_set = problem_set
        self.TIME_LIMIT = 5  # 5秒のタイムリミット
        self.MEMORY_LIMIT = 256 * 1024 * 1024  # 256MBのメモリ制限
        
    def judge(self, code: str, stdin: str, expected_stdout: str) -> tuple[bool, models.JudgeResultMetadata]:
        # 一時ファイルにコードを書き込む
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(code.encode('utf-8'))
        
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
            
            # プロセスのリターンコード
            return_code = process.returncode
            
            # 結果の判定
            if return_code != 0:
                # 実行時エラー
                return models.JudgeResultMetadata(
                    memory_used=None,
                    time_used=execution_time,
                    compile_error=None,
                    runtime_error=stderr,
                    output=stdout
                )
            
            # 出力の比較（空白・改行を正規化）
            stdout = stdout.strip()
            expected_stdout = expected_stdout.strip()
            is_ac = stdout == expected_stdout
            
            metadata = models.JudgeResultMetadata(
                memory_used=None,  # 現在のバージョンではメモリ使用量は測定していない
                time_used=execution_time,
                compile_error=None,
                runtime_error=None,
                output=stdout
            )
            return is_ac, metadata
            
        except subprocess.TimeoutExpired:
            # タイムアウト
            metadata = models.JudgeResultMetadata(
                memory_used=None,
                time_used=self.TIME_LIMIT * 1000,  # ミリ秒に変換
                compile_error=None,
                runtime_error="Time Limit Exceeded",
                output=None
            )
            return False, metadata
        
        except Exception as e:
            # その他のエラー
            metadata = models.JudgeResultMetadata(
                memory_used=None,
                time_used=None,
                compile_error=None,
                runtime_error=str(e),
                output=None
            )
            return False, metadata
        
        finally:
            # 一時ファイルを削除
            os.unlink(temp_file_path)
    
    
    def __call__(self, code: str):
        results = []
        testcase_loader = TestcaseLoader(self.problem, self.problem_set)
        
        for testcase in testcase_loader:
            is_ac, result_metadata = self.judge(code, testcase.stdin.content, testcase.stdout.content)
            
            # ステータスを設定
            if is_ac:
                status = "AC"
            else:
                status = "WA"
                if result_metadata.runtime_error:
                    status = "RE"
                elif result_metadata.time_used > self.TIME_LIMIT * 1000:
                    status = "TLE"
                elif result_metadata.compile_error:
                    status = "CE"
            
            # 結果オブジェクトを作成
            judge_result = models.JudgeResult(
                id=f"{self.problem.id}_{testcase.id}",
                problem={"id": self.problem.id},  # 辞書で渡す
                test_case=testcase,
                status=status,
                metadata=result_metadata
            )
            
            results.append(judge_result)
        
        # すべてのテストケース結果を返す
        return models.JudgeResponse(
            id=f"judge_{self.problem.id}",
            problem={"id": self.problem.id},  # 辞書で渡す
            code=code,
            results=results
        )
        
        
class AppUseCase:
    def __init__(self, problem: models.Problem, problem_set: str = DEFAULT_PROBLEM_SET):
        self.problem = problem
        self.problem_set = problem_set
        
    def read_problem(self) -> models.Problem:
        # 新しいパス: problems/問題集/問題ID/problem/ja.md
        problem_path = PROBLEM_DIR / self.problem_set / f"{self.problem.id}" / "problem" / "ja.md"
        with open(problem_path, "r") as f:
            problem_md = f.read()
        
        return models.Problem(
            id=self.problem.id,
            markdown=problem_md
        )


class ReadProblemListUseCase:
    def __init__(self, problem_set: str = DEFAULT_PROBLEM_SET):
        self.problem_set = problem_set
        
    def __call__(self) -> list[models.Problem]:
        # 問題のリストを読み込む
        # 新しいパス: problems/問題集/problems.yaml
        
        # ----------------------------------------
        # problems.yaml
        # - id: "001"
        #   title: "Hello World"
        #   level: 1
        # - id: "002"
        #   title: "Addition of Two Numbers" 
        #   level: 2
        # ----------------------------------------
        
        yaml_path = PROBLEM_DIR / self.problem_set / "problems.yaml"
        with open(yaml_path, "r") as f:
            rows = yaml.safe_load(f)
        print(rows)
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