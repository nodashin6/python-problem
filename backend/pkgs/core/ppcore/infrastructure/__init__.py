"""
Core Infrastructure Layer
コアインフラストラクチャ層
"""

from ..domain.repositories.supabase_repository import DatabaseRepositoryBase

# Alias for backward compatibility  
SupabaseRepository = DatabaseRepositoryBase

__all__ = [
    "SupabaseRepository",
    "DatabaseRepositoryBase",
]
