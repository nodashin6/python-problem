"""
Judge domain integration tests
Judge domainの統合テスト
"""

import pytest
from tests.conftest import IntegrationTestBase


class TestJudgeIntegration(IntegrationTestBase):
    """Judge domainの統合テスト"""

    async def test_submission_lifecycle(self):
        """提出のライフサイクルをテスト"""
        # テスト用のユーザーと問題を取得
        user = await self.get_user_by_email("test.user@example.com")
        problem = await self.get_problem_by_title("Hello World")

        assert user is not None
        assert problem is not None

        # 提出を作成
        source_code = 'print("Hello, World!")'
        submission_id = await self.create_test_submission(
            problem["id"], user["id"], source_code
        )

        # 提出が正しく作成されたことを確認
        submission = await self.get_submission_by_id(submission_id)
        assert submission["problem_id"] == problem["id"]
        assert submission["user_id"] == user["id"]
        assert submission["language"] == "python"
        assert submission["source_code"] == source_code
        assert submission["status"] == "pending"

    async def test_judge_process_creation(self):
        """ジャッジプロセスの作成をテスト"""
        # テスト用の提出を作成
        user = await self.get_user_by_email("test.user@example.com")
        problem = await self.get_problem_by_title("足し算問題")

        submission_id = await self.create_test_submission(
            problem["id"], user["id"], "a, b = map(int, input().split())\nprint(a + b)"
        )

        # ジャッジプロセスを作成
        process_data = {
            "submission_id": submission_id,
            "status": "pending",
            "total_cases": 2,
            "completed_cases": 0,
        }

        process_result = (
            self.supabase.table("judge_processes").insert(process_data).execute()
        )
        assert len(process_result.data) == 1

        process = process_result.data[0]
        assert process["submission_id"] == submission_id
        assert process["status"] == "pending"
        assert process["total_cases"] == 2
        assert process["completed_cases"] == 0

    async def test_judge_case_results(self):
        """ジャッジケース結果のテスト"""
        # ジャッジプロセスを作成
        user = await self.get_user_by_email("test.user@example.com")
        problem = await self.get_problem_by_title("Hello World")

        submission_id = await self.create_test_submission(
            problem["id"], user["id"], 'print("Hello, World!")'
        )

        process_data = {
            "submission_id": submission_id,
            "status": "running",
            "total_cases": 1,
            "completed_cases": 0,
        }

        process_result = (
            self.supabase.table("judge_processes").insert(process_data).execute()
        )
        process_id = process_result.data[0]["id"]

        # ジャッジケースを取得
        judge_cases_result = (
            self.supabase.table("judge_cases")
            .select("id")
            .eq("problem_id", problem["id"])
            .execute()
        )

        assert len(judge_cases_result.data) >= 1
        judge_case_id = judge_cases_result.data[0]["id"]

        # ジャッジケース結果を作成
        case_result_data = {
            "judge_process_id": process_id,
            "judge_case_id": judge_case_id,
            "status": "accepted",
            "execution_time_ms": 10,
            "memory_usage_kb": 1024,
            "output": "Hello, World!",
        }

        result = (
            self.supabase.table("judge_case_results").insert(case_result_data).execute()
        )
        assert len(result.data) == 1

        case_result = result.data[0]
        assert case_result["status"] == "accepted"
        assert case_result["execution_time_ms"] == 10
        assert case_result["memory_usage_kb"] == 1024

    async def test_submission_status_constraints(self):
        """提出ステータスの制約をテスト"""
        # 有効なステータスでの提出作成
        user = await self.get_user_by_email("test.user@example.com")
        problem = await self.get_problem_by_title("Hello World")

        valid_statuses = ["pending", "judging", "completed", "error"]

        for status in valid_statuses:
            submission_data = {
                "problem_id": problem["id"],
                "user_id": user["id"],
                "language": "python",
                "source_code": "test",
                "status": status,
            }

            result = (
                self.supabase.table("submissions").insert(submission_data).execute()
            )
            assert len(result.data) == 1
            assert result.data[0]["status"] == status

    async def test_language_constraints(self):
        """言語制約のテスト"""
        user = await self.get_user_by_email("test.user@example.com")
        problem = await self.get_problem_by_title("Hello World")

        valid_languages = [
            "python",
            "javascript",
            "typescript",
            "java",
            "cpp",
            "c",
            "go",
            "rust",
        ]

        for language in valid_languages:
            submission_data = {
                "problem_id": problem["id"],
                "user_id": user["id"],
                "language": language,
                "source_code": "test code",
                "status": "pending",
            }

            result = (
                self.supabase.table("submissions").insert(submission_data).execute()
            )
            assert len(result.data) == 1
            assert result.data[0]["language"] == language

    async def test_judge_process_completion(self):
        """ジャッジプロセス完了のテスト"""
        # 提出とプロセスを作成
        user = await self.get_user_by_email("test.user@example.com")
        problem = await self.get_problem_by_title("足し算問題")

        submission_id = await self.create_test_submission(
            problem["id"], user["id"], "a, b = map(int, input().split())\nprint(a + b)"
        )

        # 初期プロセス状態
        process_data = {
            "submission_id": submission_id,
            "status": "running",
            "total_cases": 2,
            "completed_cases": 0,
        }

        process_result = (
            self.supabase.table("judge_processes").insert(process_data).execute()
        )
        process_id = process_result.data[0]["id"]

        # プロセス完了の更新
        update_result = (
            self.supabase.table("judge_processes")
            .update(
                {
                    "status": "completed",
                    "completed_cases": 2,
                    "final_verdict": "accepted",
                }
            )
            .eq("id", process_id)
            .execute()
        )

        assert len(update_result.data) == 1
        updated_process = update_result.data[0]
        assert updated_process["status"] == "completed"
        assert updated_process["completed_cases"] == 2
        assert updated_process["final_verdict"] == "accepted"

    async def test_submission_problem_relationship(self):
        """提出と問題の関係性をテスト"""
        # 既存の提出を取得
        submissions_result = (
            self.supabase.table("submissions")
            .select("*, problem:problems(*)")
            .limit(1)
            .execute()
        )

        if submissions_result.data:
            submission = submissions_result.data[0]
            assert submission["problem"] is not None
            assert submission["problem"]["id"] == submission["problem_id"]
            assert submission["problem"]["title"] is not None


class TestJudgeDomainConstraints(IntegrationTestBase):
    """Judge domainの制約テスト"""

    async def test_foreign_key_integrity(self):
        """外部キー整合性のテスト"""
        # 提出の外部キー制約
        submissions_result = (
            self.supabase.table("submissions").select("problem_id, user_id").execute()
        )

        problems_result = self.supabase.table("problems").select("id").execute()
        users_result = self.supabase.table("users").select("id").execute()

        problem_ids = {p["id"] for p in problems_result.data}
        user_ids = {u["id"] for u in users_result.data}

        for submission in submissions_result.data:
            assert submission["problem_id"] in problem_ids
            assert submission["user_id"] in user_ids

    async def test_judge_process_submission_relationship(self):
        """ジャッジプロセスと提出の関係テスト"""
        processes_result = (
            self.supabase.table("judge_processes").select("submission_id").execute()
        )

        submissions_result = self.supabase.table("submissions").select("id").execute()
        submission_ids = {s["id"] for s in submissions_result.data}

        for process in processes_result.data:
            assert process["submission_id"] in submission_ids

    async def test_judge_case_results_relationships(self):
        """ジャッジケース結果の関係性テスト"""
        # ジャッジケース結果がある場合のテスト
        results = (
            self.supabase.table("judge_case_results")
            .select("judge_process_id, judge_case_id")
            .execute()
        )

        if results.data:
            processes_result = (
                self.supabase.table("judge_processes").select("id").execute()
            )
            judge_cases_result = (
                self.supabase.table("judge_cases").select("id").execute()
            )

            process_ids = {p["id"] for p in processes_result.data}
            judge_case_ids = {jc["id"] for jc in judge_cases_result.data}

            for result in results.data:
                assert result["judge_process_id"] in process_ids
                assert result["judge_case_id"] in judge_case_ids


class TestCrossOriginIntegration(IntegrationTestBase):
    """Core-Judge間の統合テスト"""

    async def test_submission_to_problem_reference(self):
        """提出から問題への参照テスト"""
        # Core domainの問題を取得
        problem = await self.get_problem_by_title("Hello World")
        assert problem is not None

        # Judge domainで提出を作成
        user = await self.get_user_by_email("test.user@example.com")
        submission_id = await self.create_test_submission(
            problem["id"], user["id"], 'print("Hello, World!")'
        )

        # 提出から問題情報を取得（結合クエリ）
        submission_with_problem = (
            self.supabase.table("submissions")
            .select("*, problem:problems(title, difficulty_level, time_limit_ms)")
            .eq("id", submission_id)
            .execute()
        )

        assert len(submission_with_problem.data) == 1
        submission = submission_with_problem.data[0]
        assert submission["problem"]["title"] == "Hello World"
        assert submission["problem"]["difficulty_level"] == "beginner"

    async def test_user_submission_history(self):
        """ユーザーの提出履歴テスト"""
        user = await self.get_user_by_email("test.user@example.com")
        assert user is not None

        # ユーザーの全提出を取得
        user_submissions = (
            self.supabase.table("submissions")
            .select("*, problem:problems(title)")
            .eq("user_id", user["id"])
            .execute()
        )

        # サンプルデータに基づいて提出が存在することを確認
        assert len(user_submissions.data) >= 1

        for submission in user_submissions.data:
            assert submission["user_id"] == user["id"]
            assert submission["problem"]["title"] is not None
