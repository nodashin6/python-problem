from pathlib import Path
import os

PRJ_DIR = Path(__file__).resolve().parent.parent.parent
PROBLEM_DIR = PRJ_DIR / "problems"
# 問題集のデフォルトとして"getting-started"を設定
DEFAULT_PROBLEM_SET = "getting-started"

# AppDataのパス設定
APP_DATA_DIR = Path(os.path.expanduser("~")) / ".python-problem"
SUBMISSIONS_DIR = APP_DATA_DIR / "submissions"
