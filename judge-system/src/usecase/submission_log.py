import json
import uuid
from datetime import datetime
from pathlib import Path

from src.const import SUBMISSIONS_DIR
from src.domain import models


class SubmissionLogger:
    def __init__(self):
        # 必要なディレクトリが存在しない場合は作成
        SUBMISSIONS_DIR.mkdir(parents=True, exist_ok=True)

    def save_submission(
        self, judge_response: models.JudgeResponse, problem_set: str
    ) -> models.SubmissionLog:
        """
        提出内容と結果をログとして保存する
        """
        # 提出IDを生成（UUIDv4）
        submission_id = str(uuid.uuid4())
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")

        # 全体の結果ステータスを判定
        status = self._determine_overall_status(judge_response.results)

        # 問題IDを取得
        problem_id = (
            judge_response.problem["id"]
            if isinstance(judge_response.problem, dict)
            else judge_response.problem.id
        )

        # 提出ログディレクトリ（問題セット/問題ID/日付）
        submission_dir = (
            SUBMISSIONS_DIR / problem_set / problem_id / now.strftime("%Y/%m/%d")
        )
        submission_dir.mkdir(parents=True, exist_ok=True)

        # 提出コードを保存
        code_path = submission_dir / f"{timestamp}_{submission_id}_code.py"
        with open(code_path, "w", encoding="utf-8") as f:
            f.write(judge_response.code)

        # 結果を保存
        result_path = submission_dir / f"{timestamp}_{submission_id}_result.json"
        submission_result = models.SubmissionResult(
            id=str(uuid.uuid4()),
            submission_id=submission_id,
            problem_id=problem_id,
            problem_set=problem_set,
            submitted_at=now,
            results=judge_response.results,
        )

        with open(result_path, "w", encoding="utf-8") as f:
            f.write(submission_result.model_dump_json())

        # 提出ログを作成
        submission_log = models.SubmissionLog(
            id=submission_id,
            problem_id=problem_id,
            problem_set=problem_set,
            code=judge_response.code,
            submitted_at=now,
            status=status,
            result_path=str(result_path),
        )

        # 提出ログを保存（インデックスとして）
        log_file = submission_dir / f"{timestamp}_{submission_id}_log.json"
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(submission_log.model_dump_json())

        return submission_log

    def _determine_overall_status(self, results: list[models.JudgeResult]) -> str:
        """
        テストケース結果から全体のステータスを判定
        優先順位: RE > TLE > CE > WA > AC
        """
        status_priority = {"RE": 5, "TLE": 4, "CE": 3, "WA": 2, "AC": 1}

        # デフォルトはAC
        overall_status = "AC"
        highest_priority = 0

        for result in results:
            current_priority = status_priority.get(result.status, 0)
            if current_priority > highest_priority:
                highest_priority = current_priority
                overall_status = result.status

        return overall_status

    def get_submission_logs(
        self, problem_id: str, problem_set: str, limit: int = 10
    ) -> list[models.SubmissionLog]:
        """
        指定した問題の提出ログを取得（新しい順）
        """
        # 提出ログディレクトリ
        submissions_dir = SUBMISSIONS_DIR / problem_set / problem_id
        if not submissions_dir.exists():
            return []

        # すべてのログファイルを検索
        log_files = []
        for year_dir in submissions_dir.glob("*"):
            if not year_dir.is_dir():
                continue

            for month_dir in year_dir.glob("*"):
                if not month_dir.is_dir():
                    continue

                for day_dir in month_dir.glob("*"):
                    if not day_dir.is_dir():
                        continue

                    for log_file in day_dir.glob("*_log.json"):
                        log_files.append(log_file)

        # 日付の新しい順にソート
        log_files.sort(reverse=True)

        # 指定された数だけログを取得
        submissions = []
        for log_file in log_files[:limit]:
            with open(log_file, "r", encoding="utf-8") as f:
                log_data = json.load(f)
                submissions.append(models.SubmissionLog(**log_data))

        return submissions

    def get_submission_details(
        self, submission_id: str
    ) -> tuple[models.SubmissionLog, models.SubmissionResult] | None:
        """
        提出IDから提出ログと結果の詳細を取得
        """
        # 提出ログを含むファイルを検索
        for log_file in SUBMISSIONS_DIR.glob("**/*_log.json"):
            with open(log_file, "r", encoding="utf-8") as f:
                log_data = json.load(f)
                if log_data.get("id") == submission_id:
                    submission_log = models.SubmissionLog(**log_data)

                    # 対応する結果ファイルを読み込む
                    result_path = Path(submission_log.result_path)
                    if result_path.exists():
                        with open(result_path, "r", encoding="utf-8") as rf:
                            result_data = json.load(rf)
                            submission_result = models.SubmissionResult(**result_data)
                            return submission_log, submission_result

        return None
