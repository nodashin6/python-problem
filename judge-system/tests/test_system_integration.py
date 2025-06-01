"""
System-wide integration tests
システム全体の統合テスト
"""

import pytest
from tests.conftest import IntegrationTestBase


class TestSystemIntegration(IntegrationTestBase):
    """システム全体の統合テスト"""

    async def test_complete_submission_workflow(self):
        """完全な提出ワークフローのテスト"""
        # 1. ユーザーと問題を取得
        user = await self.get_user_by_email("test.user@example.com")
        problem = await self.get_problem_by_title("足し算問題")

        assert user is not None
        assert problem is not None

        # 2. 問題の詳細とジャッジケースを確認
        problem_content = (
            self.supabase.table("problem_contents")
            .select("*")
            .eq("problem_id", problem["id"])
            .eq("language", "ja")
            .execute()
        )

        assert len(problem_content.data) == 1
        content = problem_content.data[0]
        assert "二つの整数" in content["statement"]

        # 3. ジャッジケースを取得
        judge_cases = (
            self.supabase.table("judge_cases")
            .select(
                "*, input_file:case_files!input_id(*), output_file:case_files!output_id(*)"
            )
            .eq("problem_id", problem["id"])
            .execute()
        )

        assert len(judge_cases.data) >= 1

        # 4. 提出を作成
        correct_code = "a, b = map(int, input().split())\nprint(a + b)"
        submission_id = await self.create_test_submission(
            problem["id"], user["id"], correct_code
        )

        # 5. ジャッジプロセスを作成
        process_data = {
            "submission_id": submission_id,
            "status": "running",
            "total_cases": len(judge_cases.data),
            "completed_cases": 0,
        }

        process_result = (
            self.supabase.table("judge_processes").insert(process_data).execute()
        )
        process_id = process_result.data[0]["id"]

        # 6. 各ジャッジケースの結果を作成
        for i, judge_case in enumerate(judge_cases.data):
            case_result_data = {
                "judge_process_id": process_id,
                "judge_case_id": judge_case["id"],
                "status": "accepted",
                "execution_time_ms": 15 + i * 2,  # シミュレーション
                "memory_usage_kb": 1024 + i * 100,
                "output": "8" if i == 0 else "expected_output",  # サンプル出力
            }

            self.supabase.table("judge_case_results").insert(case_result_data).execute()

        # 7. プロセス完了
        self.supabase.table("judge_processes").update(
            {
                "status": "completed",
                "completed_cases": len(judge_cases.data),
                "final_verdict": "accepted",
            }
        ).eq("id", process_id).execute()

        # 8. 提出ステータス更新
        self.supabase.table("submissions").update({"status": "completed"}).eq(
            "id", submission_id
        ).execute()

        # 9. 結果検証
        final_submission = await self.get_submission_by_id(submission_id)
        assert final_submission["status"] == "completed"

        final_process = (
            self.supabase.table("judge_processes")
            .select("*")
            .eq("id", process_id)
            .execute()
            .data[0]
        )
        assert final_process["final_verdict"] == "accepted"
        assert final_process["completed_cases"] == len(judge_cases.data)

    async def test_multiple_users_same_problem(self):
        """複数ユーザーが同じ問題に提出するテスト"""
        # ユーザーと問題を取得
        user1 = await self.get_user_by_email("test.user@example.com")
        user2 = await self.get_user_by_email("admin@example.com")
        problem = await self.get_problem_by_title("Hello World")

        # 両方のユーザーが提出
        submission1_id = await self.create_test_submission(
            problem["id"], user1["id"], 'print("Hello, World!")'
        )
        submission2_id = await self.create_test_submission(
            problem["id"], user2["id"], 'print("Hello, World!")'
        )

        # 提出が独立していることを確認
        submission1 = await self.get_submission_by_id(submission1_id)
        submission2 = await self.get_submission_by_id(submission2_id)

        assert submission1["user_id"] == user1["id"]
        assert submission2["user_id"] == user2["id"]
        assert submission1["problem_id"] == submission2["problem_id"]
        assert submission1["id"] != submission2["id"]

    async def test_problem_with_multiple_languages(self):
        """複数言語での提出テスト"""
        user = await self.get_user_by_email("test.user@example.com")
        problem = await self.get_problem_by_title("Hello World")

        # 異なる言語での提出
        languages_and_codes = [
            ("python", 'print("Hello, World!")'),
            ("javascript", 'console.log("Hello, World!");'),
            (
                "java",
                'public class Main { public static void main(String[] args) { System.out.println("Hello, World!"); } }',
            ),
        ]

        submission_ids = []
        for language, code in languages_and_codes:
            submission_id = await self.create_test_submission(
                problem["id"], user["id"], code, language
            )
            submission_ids.append(submission_id)

        # 各提出が正しく作成されていることを確認
        for i, submission_id in enumerate(submission_ids):
            submission = await self.get_submission_by_id(submission_id)
            expected_language, expected_code = languages_and_codes[i]
            assert submission["language"] == expected_language
            assert submission["source_code"] == expected_code

    async def test_book_problems_hierarchy(self):
        """書籍-問題の階層構造テスト"""
        # 書籍と関連問題を取得
        books = (
            self.supabase.table("books")
            .select("*, problems:problems(*)")
            .order("order_index")
            .execute()
        )

        assert len(books.data) >= 2

        for book in books.data:
            assert book["problems"] is not None
            if book["problems"]:  # 問題がある場合
                for problem in book["problems"]:
                    assert problem["book_id"] == book["id"]

                    # 問題の内容を確認
                    content = (
                        self.supabase.table("problem_contents")
                        .select("*")
                        .eq("problem_id", problem["id"])
                        .eq("language", "ja")
                        .execute()
                    )

                    if content.data:
                        assert content.data[0]["statement"] is not None

    async def test_user_progress_tracking(self):
        """ユーザーの進捗追跡テスト"""
        user = await self.get_user_by_email("test.user@example.com")

        # ユーザーの提出履歴を取得
        submissions = (
            self.supabase.table("submissions")
            .select("*, problem:problems(title, difficulty_level)")
            .eq("user_id", user["id"])
            .execute()
        )

        # 提出に基づいた統計情報の計算
        total_submissions = len(submissions.data)
        completed_submissions = len(
            [s for s in submissions.data if s["status"] == "completed"]
        )

        # 難易度別の統計
        difficulty_stats = {}
        for submission in submissions.data:
            difficulty = submission["problem"]["difficulty_level"]
            if difficulty not in difficulty_stats:
                difficulty_stats[difficulty] = {"total": 0, "completed": 0}
            difficulty_stats[difficulty]["total"] += 1
            if submission["status"] == "completed":
                difficulty_stats[difficulty]["completed"] += 1

        # 統計が正しく計算されることを確認
        assert total_submissions >= 0
        assert completed_submissions <= total_submissions
        assert all(
            stats["completed"] <= stats["total"] for stats in difficulty_stats.values()
        )

    async def test_judge_case_type_distribution(self):
        """ジャッジケースタイプの分布テスト"""
        # 全問題のジャッジケースタイプを確認
        judge_cases = (
            self.supabase.table("judge_cases")
            .select("judge_case_type, is_sample, problem:problems(title)")
            .execute()
        )

        type_counts = {}
        sample_counts = {"sample": 0, "non_sample": 0}

        for case in judge_cases.data:
            case_type = case["judge_case_type"]
            type_counts[case_type] = type_counts.get(case_type, 0) + 1

            if case["is_sample"]:
                sample_counts["sample"] += 1
            else:
                sample_counts["non_sample"] += 1

        # 基本的な検証
        assert "sample" in type_counts
        assert sample_counts["sample"] > 0  # サンプルケースが存在する

        # サンプルケースは通常sample typeである
        sample_cases = [c for c in judge_cases.data if c["is_sample"]]
        for case in sample_cases:
            assert case["judge_case_type"] in ["sample", "normal"]  # 通常はsample


class TestSystemPerformance(IntegrationTestBase):
    """システムパフォーマンステスト"""

    async def test_bulk_submission_handling(self):
        """大量提出の処理テスト"""
        user = await self.get_user_by_email("test.user@example.com")
        problem = await self.get_problem_by_title("Hello World")

        # 複数の提出を短時間で作成
        submission_ids = []
        for i in range(5):  # テスト環境では少数に抑制
            submission_data = {
                "problem_id": problem["id"],
                "user_id": user["id"],
                "language": "python",
                "source_code": f'print("Hello, World! #{i}")',
                "status": "pending",
            }

            result = (
                self.supabase.table("submissions").insert(submission_data).execute()
            )
            submission_ids.append(result.data[0]["id"])

        # すべての提出が正しく作成されたことを確認
        assert len(submission_ids) == 5

        for submission_id in submission_ids:
            submission = await self.get_submission_by_id(submission_id)
            assert submission is not None
            assert submission["status"] == "pending"

    async def test_complex_query_performance(self):
        """複雑なクエリのパフォーマンステスト"""
        # 複数テーブルを結合するクエリ
        complex_query = (
            self.supabase.table("submissions")
            .select(
                """
            *,
            user:users(username, display_name),
            problem:problems(
                title,
                difficulty_level,
                book:books(title),
                judge_cases:judge_cases(
                    judge_case_type,
                    is_sample
                )
            )
            """
            )
            .limit(10)
            .execute()
        )

        # クエリが正常に実行されることを確認
        assert complex_query.data is not None

        # データ構造の検証
        for submission in complex_query.data:
            assert "user" in submission
            assert "problem" in submission
            if submission["user"]:
                assert "username" in submission["user"]
            if submission["problem"]:
                assert "title" in submission["problem"]
                if submission["problem"].get("book"):
                    assert "title" in submission["problem"]["book"]
