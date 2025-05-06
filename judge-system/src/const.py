from pathlib import Path

PRJ_DIR = Path(__file__).resolve().parent.parent.parent
PROBLEM_DIR = PRJ_DIR / "problems"
TESTCASE_DIR = PRJ_DIR / "testcases"
IN_DIR = TESTCASE_DIR / "in"
OUT_DIR = TESTCASE_DIR / "out"
TESTCASE_YAML_EXT = "yaml"