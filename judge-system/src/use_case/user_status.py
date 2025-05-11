import json
import uuid
from datetime import datetime
from pathlib import Path
import os

from src.const import APP_DATA_DIR
from src.domain import models


class UserStatusManager:
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.user_status_dir = APP_DATA_DIR / "user_status"
        self.user_status_dir.mkdir(parents=True, exist_ok=True)
        self.status_file = self.user_status_dir / f"{user_id}.json"
        
        # ユーザーのステータスファイルがなければ作成
        if not self.status_file.exists():
            with open(self.status_file, "w", encoding="utf-8") as f:
                json.dump({}, f)
        
    def _load_status(self) -> dict:
        """ユーザーの問題解決状態を読み込む"""
        with open(self.status_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _save_status(self, status: dict):
        """ユーザーの問題解決状態を保存する"""
        with open(self.status_file, "w", encoding="utf-8") as f:
            json.dump(status, f, default=str)  # datetimeを文字列に変換
    
    def get_problem_status(self, problem_id: str, problem_set: str) -> models.UserProblemStatus:
        """指定した問題の解決状態を取得"""
        status = self._load_status()
        key = f"{problem_set}_{problem_id}"
        
        if key not in status:
            # 初めての問題
            return models.UserProblemStatus(
                user_id=self.user_id,
                problem_id=problem_id,
                problem_set=problem_set
            )
        
        # 既存データを復元
        problem_status = status[key]
        
        # solved_atが文字列の場合はdatetimeに変換
        if isinstance(problem_status.get("solved_at"), str):
            problem_status["solved_at"] = datetime.fromisoformat(problem_status["solved_at"])
        
        return models.UserProblemStatus(**problem_status)
    
    def update_problem_status(self, judge_response: models.JudgeResponse, submission_id: str, problem_set: str):
        """ジャッジ結果に基づいて問題の解決状態を更新"""
        status = self._load_status()
        
        # 問題IDを取得
        problem_id = judge_response.problem["id"] if isinstance(judge_response.problem, dict) else judge_response.problem.id
        key = f"{problem_set}_{problem_id}"
        
        # 既存のステータスを取得、なければ新規作成
        if key not in status:
            problem_status = {
                "user_id": self.user_id,
                "problem_id": problem_id,
                "problem_set": problem_set,
                "solved": False,
                "submission_count": 0,
                "last_submission_id": None
            }
        else:
            problem_status = status[key]
        
        # 提出回数を更新
        problem_status["submission_count"] = problem_status.get("submission_count", 0) + 1
        problem_status["last_submission_id"] = submission_id
        
        # 全テストケースがACかチェック
        all_ac = all(result.status == "AC" for result in judge_response.results)
        
        # 初めて全部ACならば解決済みに
        if all_ac and not problem_status.get("solved", False):
            problem_status["solved"] = True
            problem_status["solved_at"] = datetime.now()
        
        # 状態を保存
        status[key] = problem_status
        self._save_status(status)
        
        return models.UserProblemStatus(**problem_status)
    
    def get_all_problem_statuses(self) -> dict[str, models.UserProblemStatus]:
        """すべての問題解決状態を取得"""
        status = self._load_status()
        result = {}
        
        for key, problem_status in status.items():
            # solved_atが文字列の場合はdatetimeに変換
            if isinstance(problem_status.get("solved_at"), str):
                problem_status["solved_at"] = datetime.fromisoformat(problem_status["solved_at"])
            
            result[key] = models.UserProblemStatus(**problem_status)
        
        return result