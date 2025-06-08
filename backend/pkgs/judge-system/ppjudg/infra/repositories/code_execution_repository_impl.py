"""
Code Execution Repository implementation using Supabase
コード実行リポジトリのSupabase実装
"""

import logging
import uuid
from datetime import datetime
from typing import Any

from supabase import Client

from ....const import ExecutionStatus
from ....const import ProgrammingLanguage as Language
from ...domain.models import CodeExecution, ExecutionResult
from ...domain.repositories.code_execution_repository import CodeExecutionRepository

logger = logging.getLogger(__name__)


class CodeExecutionRepositoryImpl(CodeExecutionRepository):
    """Supabaseを使ったコード実行リポジトリの実装"""

    def __init__(self, supabase_client: Client):
        self.client = supabase_client

    async def save(self, execution: CodeExecution) -> bool:
        """コード実行を保存"""
        try:
            data = {
                "id": str(execution.id),
                "code": execution.code,
                "language": execution.language.value,
                "input_data": execution.input_data,
                "status": execution.status.value,
                "created_at": execution.created_at.isoformat(),
                "started_at": (
                    execution.started_at.isoformat() if execution.started_at else None
                ),
                "completed_at": (
                    execution.completed_at.isoformat()
                    if execution.completed_at
                    else None
                ),
                "timeout_seconds": execution.timeout_seconds,
                "memory_limit_mb": execution.memory_limit_mb,
                "metadata": execution.metadata,
            }

            # ExecutionResult が存在する場合は含める
            if execution.result:
                data.update(
                    {
                        "result_status": execution.result.status.value,
                        "result_output": execution.result.output,
                        "result_error": execution.result.error,
                        "result_execution_time": execution.result.execution_time,
                        "result_memory_usage": execution.result.memory_usage,
                        "result_exit_code": execution.result.exit_code,
                        "result_stdout": execution.result.stdout,
                        "result_stderr": execution.result.stderr,
                    }
                )

            # 既存レコードがあるかチェック
            existing = (
                self.client.table("code_executions")
                .select("id")
                .eq("id", str(execution.id))
                .execute()
            )

            if existing.data:
                # 更新
                result = (
                    self.client.table("code_executions")
                    .update(data)
                    .eq("id", str(execution.id))
                    .execute()
                )
            else:
                # 新規作成
                result = self.client.table("code_executions").insert(data).execute()

            logger.info(f"Code execution saved successfully: {execution.id}")
            return True

        except Exception as e:
            logger.error(f"Failed to save code execution {execution.id}: {e}")
            return False

    async def find_by_id(self, execution_id: uuid.UUID) -> CodeExecution | None:
        """IDでコード実行を検索"""
        try:
            result = (
                self.client.table("code_executions")
                .select("*")
                .eq("id", str(execution_id))
                .execute()
            )

            if not result.data:
                return None

            return self._map_to_code_execution(result.data[0])

        except Exception as e:
            logger.error(f"Failed to find code execution by id {execution_id}: {e}")
            return None

    async def find_by_status(
        self, status: ExecutionStatus, limit: int = 50
    ) -> list[CodeExecution]:
        """ステータスでコード実行を検索"""
        try:
            result = (
                self.client.table("code_executions")
                .select("*")
                .eq("status", status.value)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )

            executions = []
            for data in result.data:
                execution = self._map_to_code_execution(data)
                executions.append(execution)

            return executions

        except Exception as e:
            logger.error(f"Failed to find code executions by status {status}: {e}")
            return []

    async def find_by_language(
        self, language: Language, limit: int = 50
    ) -> list[CodeExecution]:
        """言語でコード実行を検索"""
        try:
            result = (
                self.client.table("code_executions")
                .select("*")
                .eq("language", language.value)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )

            executions = []
            for data in result.data:
                execution = self._map_to_code_execution(data)
                executions.append(execution)

            return executions

        except Exception as e:
            logger.error(f"Failed to find code executions by language {language}: {e}")
            return []

    async def find_recent(self, limit: int = 50) -> list[CodeExecution]:
        """最近のコード実行を検索"""
        try:
            result = (
                self.client.table("code_executions")
                .select("*")
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )

            executions = []
            for data in result.data:
                execution = self._map_to_code_execution(data)
                executions.append(execution)

            return executions

        except Exception as e:
            logger.error(f"Failed to find recent code executions: {e}")
            return []

    async def find_pending(self, limit: int = 50) -> list[CodeExecution]:
        """実行待ちのコード実行を検索"""
        try:
            result = (
                self.client.table("code_executions")
                .select("*")
                .eq("status", ExecutionStatus.PENDING.value)
                .order("created_at")  # FIFO order
                .limit(limit)
                .execute()
            )

            executions = []
            for data in result.data:
                execution = self._map_to_code_execution(data)
                executions.append(execution)

            return executions

        except Exception as e:
            logger.error(f"Failed to find pending code executions: {e}")
            return []

    async def find_by_date_range(
        self, start_date: datetime, end_date: datetime, limit: int = 100
    ) -> list[CodeExecution]:
        """日付範囲でコード実行を検索"""
        try:
            result = (
                self.client.table("code_executions")
                .select("*")
                .gte("created_at", start_date.isoformat())
                .lte("created_at", end_date.isoformat())
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )

            executions = []
            for data in result.data:
                execution = self._map_to_code_execution(data)
                executions.append(execution)

            return executions

        except Exception as e:
            logger.error(f"Failed to find code executions by date range: {e}")
            return []

    async def count_by_status(self, status: ExecutionStatus) -> int:
        """ステータス別のコード実行数をカウント"""
        try:
            result = (
                self.client.table("code_executions")
                .select("id", count="exact")
                .eq("status", status.value)
                .execute()
            )

            return result.count or 0

        except Exception as e:
            logger.error(f"Failed to count code executions by status {status}: {e}")
            return 0

    async def count_by_language(self, language: Language) -> int:
        """言語別のコード実行数をカウント"""
        try:
            result = (
                self.client.table("code_executions")
                .select("id", count="exact")
                .eq("language", language.value)
                .execute()
            )

            return result.count or 0

        except Exception as e:
            logger.error(f"Failed to count code executions by language {language}: {e}")
            return 0

    async def get_execution_statistics(
        self, start_date: datetime, end_date: datetime
    ) -> dict:
        """実行統計を取得"""
        try:
            # 期間内の総実行数
            total_result = (
                self.client.table("code_executions")
                .select("id", count="exact")
                .gte("created_at", start_date.isoformat())
                .lte("created_at", end_date.isoformat())
                .execute()
            )

            stats = {"total_executions": total_result.count or 0}

            # ステータス別統計
            for status in ExecutionStatus:
                status_result = (
                    self.client.table("code_executions")
                    .select("id", count="exact")
                    .gte("created_at", start_date.isoformat())
                    .lte("created_at", end_date.isoformat())
                    .eq("status", status.value)
                    .execute()
                )
                stats[f"{status.value}_count"] = status_result.count or 0

            # 言語別統計
            language_stats = {}
            for language in Language:
                lang_result = (
                    self.client.table("code_executions")
                    .select("id", count="exact")
                    .gte("created_at", start_date.isoformat())
                    .lte("created_at", end_date.isoformat())
                    .eq("language", language.value)
                    .execute()
                )
                language_stats[language.value] = lang_result.count or 0

            stats["language_breakdown"] = language_stats

            # 実行時間統計 (完了したもののみ)
            time_result = (
                self.client.table("code_executions")
                .select("result_execution_time")
                .gte("created_at", start_date.isoformat())
                .lte("created_at", end_date.isoformat())
                .eq("status", ExecutionStatus.COMPLETED.value)
                .not_.is_("result_execution_time", "null")
                .execute()
            )

            if time_result.data:
                execution_times = [
                    data["result_execution_time"] for data in time_result.data
                ]
                stats["avg_execution_time"] = sum(execution_times) / len(
                    execution_times
                )
                stats["max_execution_time"] = max(execution_times)
                stats["min_execution_time"] = min(execution_times)
            else:
                stats["avg_execution_time"] = 0
                stats["max_execution_time"] = 0
                stats["min_execution_time"] = 0

            # メモリ使用量統計 (完了したもののみ)
            memory_result = (
                self.client.table("code_executions")
                .select("result_memory_usage")
                .gte("created_at", start_date.isoformat())
                .lte("created_at", end_date.isoformat())
                .eq("status", ExecutionStatus.COMPLETED.value)
                .not_.is_("result_memory_usage", "null")
                .execute()
            )

            if memory_result.data:
                memory_usages = [
                    data["result_memory_usage"] for data in memory_result.data
                ]
                stats["avg_memory_usage"] = sum(memory_usages) / len(memory_usages)
                stats["max_memory_usage"] = max(memory_usages)
            else:
                stats["avg_memory_usage"] = 0
                stats["max_memory_usage"] = 0

            return stats

        except Exception as e:
            logger.error(f"Failed to get execution statistics: {e}")
            return {}

    async def delete(self, execution_id: uuid.UUID) -> bool:
        """コード実行を削除"""
        try:
            result = (
                self.client.table("code_executions")
                .delete()
                .eq("id", str(execution_id))
                .execute()
            )

            logger.info(f"Code execution deleted successfully: {execution_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete code execution {execution_id}: {e}")
            return False

    async def delete_old_executions(self, before_date: datetime) -> int:
        """古いコード実行を削除"""
        try:
            # まず削除対象のレコード数を取得
            count_result = (
                self.client.table("code_executions")
                .select("id", count="exact")
                .lt("created_at", before_date.isoformat())
                .execute()
            )

            delete_count = count_result.count or 0

            if delete_count > 0:
                # 実際に削除
                self.client.table("code_executions").delete().lt(
                    "created_at", before_date.isoformat()
                ).execute()

                logger.info(
                    f"Deleted {delete_count} old code executions before {before_date}"
                )

            return delete_count

        except Exception as e:
            logger.error(f"Failed to delete old code executions: {e}")
            return 0

    def _map_to_code_execution(self, data: dict[str, Any]) -> CodeExecution:
        """データベースレコードをCodeExecutionオブジェクトにマップ"""
        # ExecutionResult を構築
        result = None
        if data.get("result_status"):
            result = ExecutionResult(
                status=ExecutionStatus(data["result_status"]),
                output=data.get("result_output", ""),
                error=data.get("result_error", ""),
                execution_time=data.get("result_execution_time", 0.0),
                memory_usage=data.get("result_memory_usage", 0),
                exit_code=data.get("result_exit_code", 0),
                stdout=data.get("result_stdout", ""),
                stderr=data.get("result_stderr", ""),
            )

        return CodeExecution(
            id=uuid.UUID(data["id"]),
            code=data["code"],
            language=Language(data["language"]),
            input_data=data.get("input_data", ""),
            status=ExecutionStatus(data["status"]),
            result=result,
            created_at=datetime.fromisoformat(data["created_at"]),
            started_at=(
                datetime.fromisoformat(data["started_at"])
                if data.get("started_at")
                else None
            ),
            completed_at=(
                datetime.fromisoformat(data["completed_at"])
                if data.get("completed_at")
                else None
            ),
            timeout_seconds=data.get("timeout_seconds", 30),
            memory_limit_mb=data.get("memory_limit_mb", 256),
            metadata=data.get("metadata", {}),
        )
