from ....domain.repositories import SupabaseRepository
from ..client import Client


class SupabaseRepositoryImpl(SupabaseRepository):
    """
    Supabaseリポジトリの基底クラス
    Supabaseのクライアントを保持し、共通の操作を提供する
    """


__all__ = [
    "SupabaseRepositoryImpl",
]
