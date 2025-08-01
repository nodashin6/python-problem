"""
CLI Seeder Script
CLIシーダースクリプト

コマンドラインから実行可能なシーダー機能
"""

import asyncio
import logging
import sys
from typing import Optional

# Supabaseクライアントを使用した従来型シーダー
from .problem_seeder import ProblemSeeder
from .seeder import DatabaseSeeder

logger = logging.getLogger(__name__)


class CLISeeder:
    """CLI用のシーダー統合クラス"""

    def __init__(self):
        self.problem_seeder = ProblemSeeder()
        self.database_seeder = DatabaseSeeder()

    async def seed_all_complete(self, clear_existing: bool = False) -> bool:
        """全データの完全シード"""
        logger.info("🚀 Starting complete seeding process...")

        try:
            # 1. 全データのシード（従来のDB直接方式）
            success = await self.database_seeder.seed_all(clear_existing=clear_existing)

            if success:
                logger.info("✅ Complete seeding finished successfully!")
                
                # 検証
                verification = await self.database_seeder.verify_data()
                await self._print_verification_results(verification)
                
                return True
            else:
                logger.error("❌ Complete seeding failed!")
                return False

        except Exception as e:
            logger.error(f"❌ Seeding process failed: {e}")
            return False

    async def seed_problems_only(self, create_files: bool = False) -> bool:
        """問題データのみをシード"""
        logger.info("📚 Starting problems-only seeding...")

        try:
            success = await self.problem_seeder.seed_problems_complete(
                clear_existing=False,
                create_test_case_files=create_files
            )

            if success:
                logger.info("✅ Problems seeding completed!")
                
                # 検証
                verification = await self.problem_seeder.verify_problem_data()
                await self._print_problem_verification(verification)
                
                # 統計表示
                stats = await self.problem_seeder.get_problem_statistics()
                await self._print_problem_statistics(stats)
                
                return True
            else:
                logger.error("❌ Problems seeding failed!")
                return False

        except Exception as e:
            logger.error(f"❌ Problems seeding failed: {e}")
            return False

    async def clear_all_data(self) -> bool:
        """全データをクリア"""
        logger.info("🧹 Clearing all data...")

        try:
            await self.database_seeder.clear_all_data()
            logger.info("✅ All data cleared successfully!")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to clear data: {e}")
            return False

    async def verify_data(self) -> bool:
        """データの検証"""
        logger.info("🔍 Verifying database data...")

        try:
            verification = await self.database_seeder.verify_data()
            await self._print_verification_results(verification)
            return True
        except Exception as e:
            logger.error(f"❌ Verification failed: {e}")
            return False

    async def _print_verification_results(self, verification: dict) -> None:
        """検証結果を表示"""
        logger.info("📊 Database Verification Results:")
        logger.info("=" * 50)
        
        for table, info in verification.items():
            if "error" in info:
                logger.error(f"❌ {table}: {info['error']}")
            else:
                count = info.get("count", 0)
                logger.info(f"✅ {table}: {count} records")
                
                # サンプルデータ表示
                if info.get("sample"):
                    for i, sample in enumerate(info["sample"][:2]):
                        sample_str = str(sample)[:100] + "..." if len(str(sample)) > 100 else str(sample)
                        logger.info(f"   Sample {i+1}: {sample_str}")

    async def _print_problem_verification(self, verification: dict) -> None:
        """問題データ検証結果を表示"""
        logger.info("📊 Problem Data Verification:")
        logger.info("=" * 40)
        
        for table, info in verification.items():
            if "error" in info:
                logger.error(f"❌ {table}: {info['error']}")
            else:
                count = info.get("count", 0)
                logger.info(f"✅ {table}: {count} records")

    async def _print_problem_statistics(self, stats: dict) -> None:
        """問題統計を表示"""
        if "error" in stats:
            logger.error(f"❌ Statistics error: {stats['error']}")
            return

        logger.info("📈 Problem Statistics:")
        logger.info("=" * 30)
        
        for category, info in stats.items():
            if isinstance(info, dict) and "total" in info:
                logger.info(f"📁 {category.title()}: {info['total']} total")
                
                # 詳細統計
                for sub_category, sub_info in info.items():
                    if sub_category != "total" and isinstance(sub_info, dict):
                        logger.info(f"   {sub_category}: {sub_info}")


async def run_cli_seeder(command: str, options: Optional[dict] = None) -> bool:
    """
    CLI シーダーを実行
    
    Args:
        command: 実行コマンド ('all', 'problems', 'clear', 'verify')
        options: オプション辞書
    """
    options = options or {}
    seeder = CLISeeder()

    if command == "all":
        clear_existing = options.get("clear", False)
        return await seeder.seed_all_complete(clear_existing=clear_existing)
    
    elif command == "problems":
        create_files = options.get("create_files", False)
        return await seeder.seed_problems_only(create_files=create_files)
    
    elif command == "clear":
        return await seeder.clear_all_data()
    
    elif command == "verify":
        return await seeder.verify_data()
    
    else:
        logger.error(f"❌ Unknown command: {command}")
        return False


def main():
    """メイン関数 - コマンドライン引数に応じて実行"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python -m ppseed.cli_seeder all [--clear]")
        print("  python -m ppseed.cli_seeder problems [--create-files]")
        print("  python -m ppseed.cli_seeder clear")
        print("  python -m ppseed.cli_seeder verify")
        sys.exit(1)

    command = sys.argv[1]
    options = {}

    # オプション解析
    if "--clear" in sys.argv:
        options["clear"] = True
    if "--create-files" in sys.argv:
        options["create_files"] = True

    # 実行
    async def run():
        success = await run_cli_seeder(command, options)
        if not success:
            sys.exit(1)

    asyncio.run(run())


if __name__ == "__main__":
    main()