from pathlib import Path
import os

PRJ_DIR = Path(__file__).resolve().parent.parent.parent
PROBLEM_DIR = PRJ_DIR / "problems"
# 問題集のデフォルトとして"getting-started"を設定
DEFAULT_PROBLEM_SET = "getting-started"
# テストケースは各問題ディレクトリの下に移動
# 以下は互換性のために残すけど、実際には使わない
TESTCASE_DIR = PRJ_DIR / "testcases" 
IN_DIR = TESTCASE_DIR / "in"
OUT_DIR = TESTCASE_DIR / "out"
TESTCASE_YAML_EXT = "yaml"

# AppDataのパス設定
APP_DATA_DIR = Path(os.path.expanduser("~")) / ".python-problem"
SUBMISSIONS_DIR = APP_DATA_DIR / "submissions"