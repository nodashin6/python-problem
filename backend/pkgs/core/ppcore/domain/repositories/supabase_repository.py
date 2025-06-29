"""
Supabase Repository Base
Supabaseリポジトリ基底クラス
"""

from typing import Any

from supabase import Client


class SupabaseRepository:
    """
    Supabase repository base class
    Supabaseリポジトリの基底クラス - 共通操作を提供
    """

    def __init__(self, client: Client):
        self.client = client

    def _handle_supabase_error(self, error: Exception) -> None:
        """Handle Supabase errors"""
        # TODO: ログ出力やエラーハンドリングの共通処理
        raise error

    def _validate_response(self, response: Any) -> Any:
        """Validate Supabase response"""
        if not response.data:
            return None
        return response.data
