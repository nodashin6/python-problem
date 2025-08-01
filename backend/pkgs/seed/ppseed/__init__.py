"""
Seed Package
シードパッケージ - データシード機能

責任領域:
- 問題データのシード（ppprob依存）
- ジャッジデータのシード（ppjudg依存）
- テストデータの生成と投入
- データベース初期化

DDD構造:
- domain.services: ProblemSeedService, JudgeSeedService
- domain.value_objects: SeedResult, SeedStatistics, TestCaseFileResult
- usecase: SeedUseCase（統合ユースケース）
"""

# Sample Data
from .sample_data import get_all_sample_data

# Traditional DB-direct seeders (Legacy)
from .seeder import DatabaseSeeder, seed_database, verify_database
from .problem_seeder import (
    ProblemSeeder,
    seed_problems_complete,
    seed_problems_only,
    verify_problems,
    get_problems_stats,
)

# DDD Structure
from .domain.value_objects import SeedResult, SeedStatistics, TestCaseFileResult
from .usecase import SeedUseCase
from .app import SeedFacade

# Services are imported separately to avoid circular dependencies  
def get_problem_seed_service():
    from .domain.services import ProblemSeedService
    return ProblemSeedService

def get_judge_seed_service():
    from .domain.services import JudgeSeedService
    return JudgeSeedService

__all__ = [
    # Sample Data
    "get_all_sample_data",
    # Traditional Seeders (Legacy)
    "DatabaseSeeder",
    "seed_database",
    "verify_database",
    "ProblemSeeder",
    "seed_problems_complete",
    "seed_problems_only",
    "verify_problems",
    "get_problems_stats",
    # DDD Structure
    "get_problem_seed_service",
    "get_judge_seed_service",
    "SeedResult",
    "SeedStatistics",
    "TestCaseFileResult",
    "SeedUseCase",
    "SeedFacade",
]
