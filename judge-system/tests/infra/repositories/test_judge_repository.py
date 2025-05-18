import pytest
import os
import json
import tempfile
from src.infra.repositories.judge_repository import (
    JudgeResultRepository,
    JudgeCaseResultRepository,
)


@pytest.fixture
def temp_dir():
    """テスト用の一時ディレクトリを作成"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


def test_judge_repository_save_and_get(temp_dir):
    """保存と取得のテスト"""
    # テスト用のリポジトリを作成
    repo = JudgeResultRepository(base_dir=temp_dir)
    judge_id = "test-judge-id"
    test_data = {"status": "running", "problem_id": "001", "results": []}

    # データを保存
    repo.save(judge_id, test_data)

    # メモリから取得できるか
    result = repo.get(judge_id)
    assert result == test_data

    # ファイルからも取得できるか（リポジトリを再作成して確認）
    repo2 = JudgeResultRepository(base_dir=temp_dir)
    result2 = repo2.get(judge_id)
    assert result2 == test_data

    # ファイルパスを確認
    file_path = os.path.join(temp_dir, f"judge_{judge_id}.json")
    assert os.path.exists(file_path)

    # 直接ファイル内容を確認
    with open(file_path, "r") as f:
        file_content = json.load(f)
    assert file_content == test_data


def test_judge_repository_update(temp_dir):
    """更新のテスト"""
    # テスト用のリポジトリを作成
    repo = JudgeResultRepository(base_dir=temp_dir)
    judge_id = "test-judge-id"

    # 初期データ
    initial_data = {"status": "running", "problem_id": "001", "results": []}
    repo.save(judge_id, initial_data)

    # テスト結果を追加
    test_result = {"JudgeCase_id": "01", "status": "AC", "time_used": 100}
    repo.update(judge_id, test_result)

    # 更新されたデータを確認
    updated_data = repo.get(judge_id)
    assert updated_data["status"] == "running"
    assert len(updated_data["results"]) == 1
    assert updated_data["results"][0] == test_result


def test_judge_repository_finalize(temp_dir):
    """完了状態にするテスト"""
    # テスト用のリポジトリを作成
    repo = JudgeResultRepository(base_dir=temp_dir)
    judge_id = "test-judge-id"

    # 初期データ
    initial_data = {"status": "running", "problem_id": "001", "results": []}
    repo.save(judge_id, initial_data)

    # 完了状態にする
    repo.finalize(judge_id)

    # 更新されたデータを確認
    updated_data = repo.get(judge_id)
    assert updated_data["status"] == "completed"


def test_judge_repository_exists(temp_dir):
    """存在確認のテスト"""
    # テスト用のリポジトリを作成
    repo = JudgeResultRepository(base_dir=temp_dir)
    judge_id = "test-judge-id"
    non_existent_id = "non-existent-id"

    # データを保存
    test_data = {"status": "running"}
    repo.save(judge_id, test_data)

    # 存在確認
    assert repo.exists(judge_id) is True
    assert repo.exists(non_existent_id) is False
