import json
import os
from typing import Dict, Optional


class JudgeResultRepository:
    """
    ジャッジ結果を保存するリポジトリ
    メモリとファイルの両方に対応
    """

    def __init__(self, base_dir: str = "/tmp"):
        self.judge_results = {}
        self.base_dir = base_dir

    def _get_file_path(self, judge_id: str) -> str:
        """ジャッジIDからファイルパスを生成"""
        return os.path.join(self.base_dir, f"judge_{judge_id}.json")

    def save(self, judge_id: str, result: Dict) -> None:
        """
        ジャッジ結果を保存（メモリとファイルの両方）
        """
        # メモリに保存
        self.judge_results[judge_id] = result

        # ファイルに保存
        file_path = self._get_file_path(judge_id)
        with open(file_path, "w") as f:
            json.dump(result, f)

    def update(self, judge_id: str, result_item: Dict, status: str = "running") -> None:
        """
        既存のジャッジ結果に新しいテスト結果を追加・更新
        """
        # 既存のデータを取得
        current_data = self.get(judge_id) or {"status": status, "results": []}

        # 結果リストに追加
        current_data["results"].append(result_item)
        current_data["status"] = status

        # 保存
        self.save(judge_id, current_data)

    def finalize(self, judge_id: str) -> None:
        """
        ジャッジを完了状態にする
        """
        current_data = self.get(judge_id)
        if current_data:
            current_data["status"] = "completed"
            self.save(judge_id, current_data)

    def get(self, judge_id: str) -> Optional[Dict]:
        """
        ジャッジ結果を取得（メモリ→ファイルの順で試行）
        """
        # まずメモリから取得を試みる
        if judge_id in self.judge_results:
            return self.judge_results[judge_id]

        # メモリになければファイルから読み込む
        file_path = self._get_file_path(judge_id)
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return json.load(f)

        # 見つからない場合はNone
        return None

    def exists(self, judge_id: str) -> bool:
        """
        指定されたジャッジIDが存在するか確認
        """
        if judge_id in self.judge_results:
            return True

        file_path = self._get_file_path(judge_id)
        return os.path.exists(file_path)


class JudgeCaseResultRepository:
    """
    テストケースの結果を保存するリポジトリ
    """

    def __init__(self, base_dir: str = "/tmp"):
        self.case_results = {}
        self.base_dir = base_dir

    def _get_file_path(self, case_id: str) -> str:
        """テストケースIDからファイルパスを生成"""
        return os.path.join(self.base_dir, f"case_{case_id}.json")

    def save(self, case_id: str, result: Dict) -> None:
        """
        テストケース結果を保存（メモリとファイルの両方）
        """
        # メモリに保存
        self.case_results[case_id] = result

        # ファイルに保存
        file_path = self._get_file_path(case_id)
        with open(file_path, "w") as f:
            json.dump(result, f)

    def get(self, case_id: str) -> Optional[Dict]:
        """
        テストケース結果を取得（メモリ→ファイルの順で試行）
        """
        # まずメモリから取得を試みる
        if case_id in self.case_results:
            return self.case_results[case_id]

        # メモリになければファイルから読み込む
        file_path = self._get_file_path(case_id)
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return json.load(f)

        # 見つからない場合はNone
        return None

    def exists(self, case_id: str) -> bool:
        """
        指定されたテストケースIDが存在するか確認
        """
        if case_id in self.case_results:
            return True

        file_path = self._get_file_path(case_id)
        return os.path.exists(file_path)

    def update(self, case_id: str, result_item: Dict) -> None:
        """
        既存のテストケース結果に新しいテスト結果を追加・更新
        """
        # 既存のデータを取得
        current_data = self.get(case_id) or {"results": []}

        # 結果リストに追加
        current_data["results"].append(result_item)

        # 保存
        self.save(case_id, current_data)
