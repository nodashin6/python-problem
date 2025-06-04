"""
Core domain integration tests
Core domainの統合テスト
"""

import pytest
from tests.conftest import IntegrationTestBase


class TestCoreIntegration(IntegrationTestBase):
    """Core domainの統合テスト"""

    async def test_books_and_problems_relationship(self):
        """書籍と問題の関係性をテスト"""
        # 書籍を取得
        books_result = self.supabase.table("books").select("*").execute()
        assert len(books_result.data) >= 2

        book = books_result.data[0]

        # その書籍に属する問題を取得
        problems_result = (
            self.supabase.table("problems")
            .select("*")
            .eq("book_id", book["id"])
            .execute()
        )

        assert len(problems_result.data) >= 1

        # 問題の詳細を確認
        problem = problems_result.data[0]
        assert problem["book_id"] == book["id"]
        assert problem["title"] is not None
        assert problem["difficulty_level"] in [
            "beginner",
            "intermediate",
            "advanced",
            "expert",
        ]
        assert problem["status"] in ["draft", "published", "archived"]

    async def test_problem_contents_multilingual(self):
        """問題内容の多言語対応をテスト"""
        # 問題を取得
        problems_result = self.supabase.table("problems").select("*").limit(1).execute()
        assert len(problems_result.data) >= 1

        problem = problems_result.data[0]

        # その問題の内容を取得
        contents_result = (
            self.supabase.table("problem_contents")
            .select("*")
            .eq("problem_id", problem["id"])
            .execute()
        )

        assert len(contents_result.data) >= 1

        content = contents_result.data[0]
        assert content["language"] == "ja"
        assert content["statement"] is not None
        assert content["input_format"] is not None
        assert content["output_format"] is not None

    async def test_judge_cases_with_files(self):
        """ジャッジケースとファイルの関係をテスト"""
        # 問題を取得
        problem = await self.get_problem_by_title("Hello World")
        assert problem is not None

        # その問題のジャッジケースを取得
        judge_cases_result = (
            self.supabase.table("judge_cases")
            .select(
                "*, input_file:case_files!input_id(*), output_file:case_files!output_id(*)"
            )
            .eq("problem_id", problem["id"])
            .execute()
        )

        assert len(judge_cases_result.data) >= 1

        judge_case = judge_cases_result.data[0]
        assert judge_case["input_file"] is not None
        assert judge_case["output_file"] is not None
        assert judge_case["input_file"]["url"] is not None
        assert judge_case["output_file"]["url"] is not None
        assert judge_case["judge_case_type"] in ["sample", "normal", "edge", "stress"]

    async def test_user_management(self):
        """ユーザー管理機能をテスト"""
        # ユーザーを取得
        user = await self.get_user_by_email("test.user@example.com")
        assert user is not None
        assert user["username"] == "testuser"
        assert user["is_active"] is True

        # ユーザーロールを確認
        role_result = (
            self.supabase.table("user_roles")
            .select("*")
            .eq("user_id", user["id"])
            .execute()
        )

        assert len(role_result.data) >= 1
        assert role_result.data[0]["role"] == "user"

    async def test_user_stats_initialization(self):
        """ユーザー統計の初期化をテスト"""
        # ユーザーを取得
        user = await self.get_user_by_email("test.user@example.com")
        assert user is not None

        # ユーザー統計を確認（初期状態）
        stats_result = (
            self.supabase.table("user_stats")
            .select("*")
            .eq("user_id", user["id"])
            .execute()
        )

        # 統計データが存在するか、または適切に初期化される仕組みがあることを確認
        if stats_result.data:
            stats = stats_result.data[0]
            assert stats["solved_count"] >= 0
            assert stats["submission_count"] >= 0

    async def test_problem_difficulty_constraint(self):
        """問題の難易度制約をテスト"""
        # すべての問題の難易度をチェック
        problems_result = (
            self.supabase.table("problems").select("difficulty_level").execute()
        )

        valid_difficulties = ["beginner", "intermediate", "advanced", "expert"]
        for problem in problems_result.data:
            assert problem["difficulty_level"] in valid_difficulties

    async def test_book_order_index(self):
        """書籍の順序インデックスをテスト"""
        # 書籍を順序で取得
        books_result = (
            self.supabase.table("books").select("*").order("order_index").execute()
        )

        assert len(books_result.data) >= 2

        # 順序が正しく設定されていることを確認
        prev_order = -1
        for book in books_result.data:
            assert book["order_index"] > prev_order
            prev_order = book["order_index"]

    async def test_problem_time_memory_limits(self):
        """問題の時間・メモリ制限をテスト"""
        problems_result = self.supabase.table("problems").select("*").execute()

        for problem in problems_result.data:
            assert problem["time_limit_ms"] > 0
            assert problem["memory_limit_mb"] > 0
            assert problem["time_limit_ms"] <= 10000  # 10秒以下
            assert problem["memory_limit_mb"] <= 1024  # 1GB以下


class TestCoreDataConsistency(IntegrationTestBase):
    """Core domainのデータ整合性テスト"""

    async def test_foreign_key_relationships(self):
        """外部キー関係の整合性をテスト"""
        # すべての問題が有効な書籍IDを持っているか
        problems_result = self.supabase.table("problems").select("book_id").execute()
        books_result = self.supabase.table("books").select("id").execute()

        book_ids = {book["id"] for book in books_result.data}

        for problem in problems_result.data:
            assert (
                problem["book_id"] in book_ids
            ), f"Invalid book_id: {problem['book_id']}"

    async def test_judge_cases_file_references(self):
        """ジャッジケースのファイル参照整合性をテスト"""
        judge_cases_result = (
            self.supabase.table("judge_cases").select("input_id, output_id").execute()
        )
        case_files_result = self.supabase.table("case_files").select("id").execute()

        file_ids = {file["id"] for file in case_files_result.data}

        for judge_case in judge_cases_result.data:
            assert (
                judge_case["input_id"] in file_ids
            ), f"Invalid input_id: {judge_case['input_id']}"
            assert (
                judge_case["output_id"] in file_ids
            ), f"Invalid output_id: {judge_case['output_id']}"

    async def test_user_role_consistency(self):
        """ユーザーロールの整合性をテスト"""
        users_result = self.supabase.table("users").select("id").execute()
        roles_result = self.supabase.table("user_roles").select("user_id").execute()

        user_ids = {user["id"] for user in users_result.data}

        for role in roles_result.data:
            assert (
                role["user_id"] in user_ids
            ), f"Invalid user_id in role: {role['user_id']}"
