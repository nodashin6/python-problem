from supabase import Client


class SupabaseRepository:
    """
    Supabaseリポジトリの基底クラス
    Supabaseのクライアントを保持し、共通の操作を提供する
    """

    def __init__(self, client: Client):
        self.client = client
