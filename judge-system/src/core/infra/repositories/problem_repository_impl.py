"""
Problem Repository implementation with Supabase
問題リポジトリの Supabase 実装
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import uuid

from ...domain.models import Problem, JudgeCase, Tag, ProblemMetadata
from ...domain.repositories.problem_repository import ProblemRepository
from ....shared.database import DatabaseManager, BaseRepository
from ....shared.logging import get_logger
from ....const import DifficultyLevel, ProblemStatus

logger = get_logger(__name__)


class ProblemRepositoryImpl(BaseRepository, ProblemRepository):
    """Problem リポジトリの Supabase 実装"""

    def __init__(self, db_manager: DatabaseManager):
        super().__init__(db_manager, "problems")

    async def save(self, problem: Problem) -> bool:
        """問題を保存"""
        try:
            # メタデータをJSON形式で準備
            metadata_dict = {
                "time_limit": problem.metadata.time_limit,
                "memory_limit": problem.metadata.memory_limit,
                "constraints": problem.metadata.constraints,
                "hints": problem.metadata.hints,
                "custom_fields": problem.metadata.custom_fields,
            }

            # 問題データの準備
            problem_data = {
                "id": str(problem.id),
                "title": problem.title,
                "statement": problem.statement,
                "difficulty": problem.difficulty.value,
                "status": problem.status.value,
                "metadata": json.dumps(metadata_dict),
                "author_id": str(problem.author_id),
                "book_id": str(problem.book_id) if problem.book_id else None,
                "order_index": problem.order_index,
                "created_at": problem.created_at.isoformat(),
                "updated_at": problem.updated_at.isoformat(),
            }

            # 既存の問題をチェック
            existing = await self._find_by_id(str(problem.id))

            if existing:
                # 更新
                await self._update({"id": str(problem.id)}, problem_data)
                logger.info(f"Problem updated: {problem.id}")
            else:
                # 新規作成
                await self._create(problem_data)
                logger.info(f"Problem created: {problem.id}")

            # タグの保存
            await self._save_problem_tags(problem.id, problem.tags)

            return True

        except Exception as e:
            logger.error(f"Failed to save problem {problem.id}: {e}")
            return False

    async def find_by_id(self, problem_id: uuid.UUID) -> Optional[Problem]:
        """IDで問題を検索"""
        try:
            data = await self._find_by_id(str(problem_id))
            if not data:
                return None

            return await self._map_to_domain(data)

        except Exception as e:
            logger.error(f"Failed to find problem {problem_id}: {e}")
            return None

    async def find_by_title(self, title: str) -> Optional[Problem]:
        """タイトルで問題を検索"""
        try:
            conditions = {"title": title}
            data = await self._find_by_conditions(conditions)

            if not data:
                return None

            return await self._map_to_domain(data[0])

        except Exception as e:
            logger.error(f"Failed to find problem by title {title}: {e}")
            return None

    async def find_by_author(self, author_id: uuid.UUID) -> List[Problem]:
        """作成者IDで問題を検索"""
        try:
            conditions = {"author_id": str(author_id)}
            data_list = await self._find_by_conditions(conditions)

            problems = []
            for data in data_list:
                problem = await self._map_to_domain(data)
                if problem:
                    problems.append(problem)

            return problems

        except Exception as e:
            logger.error(f"Failed to find problems by author {author_id}: {e}")
            return []

    async def find_by_book(self, book_id: uuid.UUID) -> List[Problem]:
        """ブックIDで問題を検索"""
        try:
            conditions = {"book_id": str(book_id)}
            data_list = await self._find_by_conditions(
                conditions, order_by="order_index"
            )

            problems = []
            for data in data_list:
                problem = await self._map_to_domain(data)
                if problem:
                    problems.append(problem)

            return problems

        except Exception as e:
            logger.error(f"Failed to find problems by book {book_id}: {e}")
            return []

    async def find_by_difficulty(self, difficulty: DifficultyLevel) -> List[Problem]:
        """難易度で問題を検索"""
        try:
            conditions = {"difficulty": difficulty.value}
            data_list = await self._find_by_conditions(conditions)

            problems = []
            for data in data_list:
                problem = await self._map_to_domain(data)
                if problem:
                    problems.append(problem)

            return problems

        except Exception as e:
            logger.error(f"Failed to find problems by difficulty {difficulty}: {e}")
            return []

    async def find_by_tags(self, tags: List[str]) -> List[Problem]:
        """タグで問題を検索"""
        try:
            # タグテーブルを結合してクエリ
            query = """
            SELECT DISTINCT p.* FROM problems p
            JOIN problem_tags pt ON p.id = pt.problem_id
            WHERE pt.tag_name = ANY(%s)
            """

            db = await self.db_manager.get_connection()
            results = await db.fetch(query, [tags])

            problems = []
            for data in results:
                problem = await self._map_to_domain(dict(data))
                if problem:
                    problems.append(problem)

            return problems

        except Exception as e:
            logger.error(f"Failed to find problems by tags {tags}: {e}")
            return []

    async def search(
        self,
        title: Optional[str] = None,
        tags: Optional[List[str]] = None,
        difficulty: Optional[DifficultyLevel] = None,
        status: Optional[ProblemStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Problem]:
        """複合条件で問題を検索"""
        try:
            query_parts = ["SELECT DISTINCT p.* FROM problems p"]
            conditions = []
            params = []

            # タグ条件がある場合は結合
            if tags:
                query_parts.append("JOIN problem_tags pt ON p.id = pt.problem_id")
                conditions.append("pt.tag_name = ANY(%s)")
                params.append(tags)

            # その他の条件
            if title:
                conditions.append("p.title ILIKE %s")
                params.append(f"%{title}%")

            if difficulty:
                conditions.append("p.difficulty = %s")
                params.append(difficulty.value)

            if status:
                conditions.append("p.status = %s")
                params.append(status.value)

            # WHERE句の構築
            if conditions:
                query_parts.append("WHERE " + " AND ".join(conditions))

            # ソートとページング
            query_parts.append("ORDER BY p.created_at DESC")
            query_parts.append("LIMIT %s OFFSET %s")
            params.extend([limit, offset])

            query = " ".join(query_parts)

            db = await self.db_manager.get_connection()
            results = await db.fetch(query, params)

            problems = []
            for data in results:
                problem = await self._map_to_domain(dict(data))
                if problem:
                    problems.append(problem)

            return problems

        except Exception as e:
            logger.error(f"Failed to search problems: {e}")
            return []

    async def delete(self, problem_id: uuid.UUID) -> bool:
        """問題を削除"""
        try:
            # 関連するタグも削除
            await self._delete_problem_tags(problem_id)

            # 問題を削除
            success = await self._delete({"id": str(problem_id)})

            if success:
                logger.info(f"Problem deleted: {problem_id}")

            return success

        except Exception as e:
            logger.error(f"Failed to delete problem {problem_id}: {e}")
            return False

    async def count_by_author(self, author_id: uuid.UUID) -> int:
        """作成者の問題数をカウント"""
        try:
            return await self._count({"author_id": str(author_id)})
        except Exception as e:
            logger.error(f"Failed to count problems by author {author_id}: {e}")
            return 0

    async def count_by_book(self, book_id: uuid.UUID) -> int:
        """ブックの問題数をカウント"""
        try:
            return await self._count({"book_id": str(book_id)})
        except Exception as e:
            logger.error(f"Failed to count problems by book {book_id}: {e}")
            return 0

    async def exists_title(
        self, title: str, exclude_id: Optional[uuid.UUID] = None
    ) -> bool:
        """タイトルの重複チェック"""
        try:
            conditions = {"title": title}
            if exclude_id:
                # 指定されたIDは除外
                query = "SELECT COUNT(*) FROM problems WHERE title = %s AND id != %s"
                db = await self.db_manager.get_connection()
                result = await db.fetchval(query, [title, str(exclude_id)])
                return result > 0
            else:
                count = await self._count(conditions)
                return count > 0

        except Exception as e:
            logger.error(f"Failed to check title existence {title}: {e}")
            return False

    async def _map_to_domain(self, data: Dict[str, Any]) -> Optional[Problem]:
        """データベースレコードをドメインオブジェクトにマップ"""
        try:
            # メタデータのパース
            metadata_dict = json.loads(data["metadata"]) if data["metadata"] else {}
            metadata = ProblemMetadata(
                time_limit=metadata_dict.get("time_limit", 1.0),
                memory_limit=metadata_dict.get("memory_limit", 256),
                constraints=metadata_dict.get("constraints", []),
                hints=metadata_dict.get("hints", []),
                custom_fields=metadata_dict.get("custom_fields", {}),
            )

            # タグの取得
            tags = await self._load_problem_tags(uuid.UUID(data["id"]))

            # ジャッジケースの取得（別のリポジトリから）
            # 注意: 循環参照を避けるため、ここでは空のリストを使用
            # 実際のジャッジケースは必要に応じて別途ロードする
            judge_cases = []

            problem = Problem(
                id=uuid.UUID(data["id"]),
                title=data["title"],
                statement=data["statement"],
                difficulty=DifficultyLevel(data["difficulty"]),
                status=ProblemStatus(data["status"]),
                metadata=metadata,
                author_id=uuid.UUID(data["author_id"]),
                book_id=uuid.UUID(data["book_id"]) if data["book_id"] else None,
                order_index=data.get("order_index", 0),
                tags=tags,
                judge_cases=judge_cases,  # 空のリスト
                created_at=datetime.fromisoformat(data["created_at"]),
                updated_at=datetime.fromisoformat(data["updated_at"]),
            )

            return problem

        except Exception as e:
            logger.error(f"Failed to map data to Problem domain: {e}")
            return None

    async def _save_problem_tags(self, problem_id: uuid.UUID, tags: List[Tag]) -> None:
        """問題のタグを保存"""
        try:
            # 既存のタグを削除
            await self._delete_problem_tags(problem_id)

            # 新しいタグを挿入
            if tags:
                tag_data = [
                    {
                        "problem_id": str(problem_id),
                        "tag_name": tag.name,
                        "tag_color": tag.color,
                    }
                    for tag in tags
                ]

                db = await self.db_manager.get_connection()
                query = """
                INSERT INTO problem_tags (problem_id, tag_name, tag_color)
                VALUES (%s, %s, %s)
                """

                for tag in tag_data:
                    await db.execute(
                        query, [tag["problem_id"], tag["tag_name"], tag["tag_color"]]
                    )

        except Exception as e:
            logger.error(f"Failed to save problem tags for {problem_id}: {e}")

    async def _load_problem_tags(self, problem_id: uuid.UUID) -> List[Tag]:
        """問題のタグを読み込み"""
        try:
            query = "SELECT tag_name, tag_color FROM problem_tags WHERE problem_id = %s"
            db = await self.db_manager.get_connection()
            results = await db.fetch(query, [str(problem_id)])

            return [
                Tag(name=row["tag_name"], color=row["tag_color"]) for row in results
            ]

        except Exception as e:
            logger.error(f"Failed to load problem tags for {problem_id}: {e}")
            return []

    async def _delete_problem_tags(self, problem_id: uuid.UUID) -> None:
        """問題のタグを削除"""
        try:
            query = "DELETE FROM problem_tags WHERE problem_id = %s"
            db = await self.db_manager.get_connection()
            await db.execute(query, [str(problem_id)])

        except Exception as e:
            logger.error(f"Failed to delete problem tags for {problem_id}: {e}")
