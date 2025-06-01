"""
JudgeCase Repository implementation with Supabase
ジャッジケースリポジトリの Supabase 実装
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from ...domain.models import JudgeCase
from ...domain.repositories.judge_case_repository import JudgeCaseRepository
from ....shared.database import DatabaseManager, BaseRepository
from ....shared.logging import get_logger
from ....const import JudgeCaseType

logger = get_logger(__name__)


class JudgeCaseRepositoryImpl(JudgeCaseRepository):
    """JudgeCase リポジトリの Supabase 実装"""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.table_name = "judge_cases"

    async def save(self, judge_case: JudgeCase) -> bool:
        """ジャッジケースを保存"""
        try:
            judge_case_data = {
                "id": str(judge_case.id),
                "problem_id": str(judge_case.problem_id),
                "input_data": judge_case.input_data,
                "expected_output": judge_case.expected_output,
                "case_type": judge_case.case_type.value,
                "order_index": judge_case.order_index,
                "is_hidden": judge_case.is_hidden,
                "points": judge_case.points,
                "description": judge_case.description,
                "created_at": judge_case.created_at.isoformat(),
                "updated_at": judge_case.updated_at.isoformat(),
            }

            # 既存のジャッジケースをチェック
            existing = await self._find_by_id(str(judge_case.id))

            if existing:
                # 更新
                await self._update({"id": str(judge_case.id)}, judge_case_data)
                logger.info(f"JudgeCase updated: {judge_case.id}")
            else:
                # 新規作成
                await self._create(judge_case_data)
                logger.info(f"JudgeCase created: {judge_case.id}")

            return True

        except Exception as e:
            logger.error(f"Failed to save judge_case {judge_case.id}: {e}")
            return False

    async def find_by_id(self, judge_case_id: uuid.UUID) -> Optional[JudgeCase]:
        """IDでジャッジケースを検索"""
        try:
            data = await self._find_by_id(str(judge_case_id))
            if not data:
                return None

            return self._map_to_domain(data)

        except Exception as e:
            logger.error(f"Failed to find judge_case {judge_case_id}: {e}")
            return None

    async def find_by_problem(self, problem_id: uuid.UUID) -> List[JudgeCase]:
        """問題IDでジャッジケースを検索"""
        try:
            conditions = {"problem_id": str(problem_id)}
            data_list = await self._find_by_conditions(
                conditions, order_by="order_index"
            )

            judge_cases = []
            for data in data_list:
                judge_case = self._map_to_domain(data)
                if judge_case:
                    judge_cases.append(judge_case)

            return judge_cases

        except Exception as e:
            logger.error(f"Failed to find judge_cases by problem {problem_id}: {e}")
            return []

    async def find_visible_by_problem(self, problem_id: uuid.UUID) -> List[JudgeCase]:
        """問題IDで表示可能なジャッジケースを検索"""
        try:
            conditions = {"problem_id": str(problem_id), "is_hidden": False}
            data_list = await self._find_by_conditions(
                conditions, order_by="order_index"
            )

            judge_cases = []
            for data in data_list:
                judge_case = self._map_to_domain(data)
                if judge_case:
                    judge_cases.append(judge_case)

            return judge_cases

        except Exception as e:
            logger.error(
                f"Failed to find visible judge_cases by problem {problem_id}: {e}"
            )
            return []

    async def find_by_type(
        self, problem_id: uuid.UUID, case_type: JudgeCaseType
    ) -> List[JudgeCase]:
        """問題IDとタイプでジャッジケースを検索"""
        try:
            conditions = {"problem_id": str(problem_id), "case_type": case_type.value}
            data_list = await self._find_by_conditions(
                conditions, order_by="order_index"
            )

            judge_cases = []
            for data in data_list:
                judge_case = self._map_to_domain(data)
                if judge_case:
                    judge_cases.append(judge_case)

            return judge_cases

        except Exception as e:
            logger.error(
                f"Failed to find judge_cases by type {case_type} for problem {problem_id}: {e}"
            )
            return []

    async def count_by_problem(self, problem_id: uuid.UUID) -> int:
        """問題のジャッジケース数をカウント"""
        try:
            return await self._count({"problem_id": str(problem_id)})
        except Exception as e:
            logger.error(f"Failed to count judge_cases by problem {problem_id}: {e}")
            return 0

    async def count_by_type(
        self, problem_id: uuid.UUID, case_type: JudgeCaseType
    ) -> int:
        """問題の特定タイプのジャッジケース数をカウント"""
        try:
            conditions = {"problem_id": str(problem_id), "case_type": case_type.value}
            return await self._count(conditions)
        except Exception as e:
            logger.error(
                f"Failed to count judge_cases by type {case_type} for problem {problem_id}: {e}"
            )
            return 0

    async def get_max_order_index(self, problem_id: uuid.UUID) -> int:
        """問題の最大順序インデックスを取得"""
        try:
            query = "SELECT COALESCE(MAX(order_index), -1) FROM judge_cases WHERE problem_id = %s"
            db = await self.db_manager.get_connection()
            result = await db.fetchval(query, [str(problem_id)])
            return result if result is not None else -1

        except Exception as e:
            logger.error(f"Failed to get max order index for problem {problem_id}: {e}")
            return -1

    async def reorder_cases(
        self, problem_id: uuid.UUID, case_orders: List[Dict[str, Any]]
    ) -> bool:
        """ジャッジケースの順序を変更"""
        try:
            db = await self.db_manager.get_connection()

            async with db.transaction():
                for order_info in case_orders:
                    case_id = order_info["case_id"]
                    new_order = order_info["order_index"]

                    query = """
                    UPDATE judge_cases 
                    SET order_index = %s, updated_at = %s 
                    WHERE id = %s AND problem_id = %s
                    """
                    await db.execute(
                        query,
                        [
                            new_order,
                            datetime.utcnow().isoformat(),
                            str(case_id),
                            str(problem_id),
                        ],
                    )

            logger.info(f"Reordered judge_cases for problem {problem_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to reorder judge_cases for problem {problem_id}: {e}")
            return False

    async def delete(self, judge_case_id: uuid.UUID) -> bool:
        """ジャッジケースを削除"""
        try:
            success = await self._delete({"id": str(judge_case_id)})

            if success:
                logger.info(f"JudgeCase deleted: {judge_case_id}")

            return success

        except Exception as e:
            logger.error(f"Failed to delete judge_case {judge_case_id}: {e}")
            return False

    async def delete_by_problem(self, problem_id: uuid.UUID) -> bool:
        """問題のすべてのジャッジケースを削除"""
        try:
            count = await self._count({"problem_id": str(problem_id)})
            success = await self._delete({"problem_id": str(problem_id)})

            if success:
                logger.info(f"Deleted {count} judge_cases for problem {problem_id}")

            return success

        except Exception as e:
            logger.error(f"Failed to delete judge_cases for problem {problem_id}: {e}")
            return False

    async def bulk_create(self, judge_cases: List[JudgeCase]) -> bool:
        """ジャッジケースを一括作成"""
        try:
            if not judge_cases:
                return True

            judge_case_data_list = []
            for judge_case in judge_cases:
                judge_case_data = {
                    "id": str(judge_case.id),
                    "problem_id": str(judge_case.problem_id),
                    "input_data": judge_case.input_data,
                    "expected_output": judge_case.expected_output,
                    "case_type": judge_case.case_type.value,
                    "order_index": judge_case.order_index,
                    "is_hidden": judge_case.is_hidden,
                    "points": judge_case.points,
                    "description": judge_case.description,
                    "created_at": judge_case.created_at.isoformat(),
                    "updated_at": judge_case.updated_at.isoformat(),
                }
                judge_case_data_list.append(judge_case_data)

            # 一括挿入
            db = await self.db_manager.get_connection()
            query = """
            INSERT INTO judge_cases (
                id, problem_id, input_data, expected_output, case_type,
                order_index, is_hidden, points, description, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            async with db.transaction():
                for data in judge_case_data_list:
                    await db.execute(
                        query,
                        [
                            data["id"],
                            data["problem_id"],
                            data["input_data"],
                            data["expected_output"],
                            data["case_type"],
                            data["order_index"],
                            data["is_hidden"],
                            data["points"],
                            data["description"],
                            data["created_at"],
                            data["updated_at"],
                        ],
                    )

            logger.info(f"Bulk created {len(judge_cases)} judge_cases")
            return True

        except Exception as e:
            logger.error(f"Failed to bulk create judge_cases: {e}")
            return False

    def _map_to_domain(self, data: Dict[str, Any]) -> Optional[JudgeCase]:
        """データベースレコードをドメインオブジェクトにマップ"""
        try:
            judge_case = JudgeCase(
                id=uuid.UUID(data["id"]),
                problem_id=uuid.UUID(data["problem_id"]),
                input_data=data["input_data"],
                expected_output=data["expected_output"],
                case_type=JudgeCaseType(data["case_type"]),
                order_index=data["order_index"],
                is_hidden=data["is_hidden"],
                points=data.get("points", 0),
                description=data.get("description"),
                created_at=datetime.fromisoformat(data["created_at"]),
                updated_at=datetime.fromisoformat(data["updated_at"]),
            )

            return judge_case

        except Exception as e:
            logger.error(f"Failed to map data to JudgeCase domain: {e}")
            return None
