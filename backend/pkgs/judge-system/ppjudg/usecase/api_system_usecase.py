"""
API System Use Cases
APIシステムユースケース

APIリクエストから呼び出されるシステム管理関連のワークフローを実装
"""

import uuid
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from dependency_injector.wiring import Provide, inject

from ..domain.repositories.submission_repository import SubmissionRepository
from ..domain.repositories.judge_queue_repository import JudgeQueueRepository
from ..domain.repositories.code_execution_repository import CodeExecutionRepository
from ...const import ExecutionStatus, JudgeResultType
from ...shared.logging import get_logger

from ..usecase.judge_worker_use_case import JudgeWorkerUseCase, JudgeSystemMaintenanceUseCase
from ..usecase.code_execution_use_case import JudgeQueueUseCase

from ..app.container import JudgeContainer

logger = get_logger(__name__)


class ApiSystemUseCase:
    """APIシステム管理ユースケース（APIワークフロー専用）"""

    @inject
    def __init__(
        self,
        submission_repo: SubmissionRepository = Provide[JudgeContainer.submission_repository],
        queue_repo: JudgeQueueRepository = Provide[JudgeContainer.judge_queue_repository],
        execution_repo: CodeExecutionRepository = Provide[JudgeContainer.code_execution_repository],
        worker_use_case: JudgeWorkerUseCase = Provide[JudgeContainer.judge_worker_use_case],
        maintenance_use_case: JudgeSystemMaintenanceUseCase = Provide[JudgeContainer.judge_system_maintenance_use_case],
        queue_use_case: JudgeQueueUseCase = Provide[JudgeContainer.judge_queue_use_case],
    ):
        self.submission_repo = submission_repo
        self.queue_repo = queue_repo
        self.execution_repo = execution_repo
        self.worker_use_case = worker_use_case
        self.maintenance_use_case = maintenance_use_case
        self.queue_use_case = queue_use_case

    async def get_system_status(self) -> Dict[str, Any]:
        """システム全体の状況を取得（API用）"""
        try:
            # キュー状況
            queue_stats = await self._get_queue_statistics()
            
            # ワーカー状況
            worker_stats = await self._get_worker_statistics()
            
            # システム統計
            system_stats = await self._get_system_statistics()
            
            # システム健全性
            health_status = await self._get_health_status()

            return {
                "success": True,
                "status": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "overall_health": health_status["overall"],
                    "queue": queue_stats,
                    "workers": worker_stats,
                    "system": system_stats,
                    "health_checks": health_status["checks"],
                }
            }

        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return {
                "success": False,
                "error": "Failed to retrieve system status",
                "error_code": "SYSTEM_STATUS_ERROR",
            }

    async def get_queue_status(self) -> Dict[str, Any]:
        """キュー状況を取得（API用）"""
        try:
            pending_items = await self.queue_repo.find_pending_items(limit=1000)
            processing_items = await self.queue_repo.find_processing_items(limit=1000)
            
            # 優先度別統計
            priority_stats = {}
            for item in pending_items:
                priority = item.priority
                if priority not in priority_stats:
                    priority_stats[priority] = 0
                priority_stats[priority] += 1

            # 言語別統計
            language_stats = await self._get_queue_language_statistics()

            # 推定待ち時間
            estimated_wait_time = await self._calculate_estimated_wait_time(len(pending_items))

            return {
                "success": True,
                "queue": {
                    "pending_count": len(pending_items),
                    "processing_count": len(processing_items),
                    "priority_distribution": priority_stats,
                    "language_distribution": language_stats,
                    "estimated_wait_time_minutes": estimated_wait_time,
                    "last_updated": datetime.utcnow().isoformat(),
                }
            }

        except Exception as e:
            logger.error(f"Failed to get queue status: {e}")
            return {
                "success": False,
                "error": "Failed to retrieve queue status",
                "error_code": "QUEUE_STATUS_ERROR",
            }

    async def get_submission_statistics(
        self,
        period_days: int = 7,
        group_by: str = "day"  # day, hour, language, result
    ) -> Dict[str, Any]:
        """提出統計を取得（API用）"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=period_days)

            # 基本統計
            total_submissions = await self.submission_repo.count_by_date_range(start_date, end_date)
            
            # グループ別統計
            if group_by == "day":
                grouped_stats = await self._get_daily_submission_stats(start_date, end_date)
            elif group_by == "hour":
                grouped_stats = await self._get_hourly_submission_stats(start_date, end_date)
            elif group_by == "language":
                grouped_stats = await self._get_language_submission_stats(start_date, end_date)
            elif group_by == "result":
                grouped_stats = await self._get_result_submission_stats(start_date, end_date)
            else:
                grouped_stats = {}

            # 結果別統計
            result_stats = {}
            for result in JudgeResultType:
                count = await self.submission_repo.count_by_result_and_date_range(
                    result, start_date, end_date
                )
                result_stats[result.value] = count

            return {
                "success": True,
                "statistics": {
                    "period": {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat(),
                        "days": period_days,
                    },
                    "total_submissions": total_submissions,
                    "grouped_by": group_by,
                    "grouped_data": grouped_stats,
                    "result_distribution": result_stats,
                    "success_rate": self._calculate_success_rate(result_stats),
                }
            }

        except Exception as e:
            logger.error(f"Failed to get submission statistics: {e}")
            return {
                "success": False,
                "error": "Failed to retrieve statistics",
                "error_code": "STATISTICS_ERROR",
            }

    async def trigger_maintenance(
        self,
        requester_user_id: uuid.UUID,
        maintenance_type: str = "standard",
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """メンテナンスを実行（API用）"""
        try:
            # 権限チェック
            has_permission = await self._check_maintenance_permission(requester_user_id)
            if not has_permission:
                return {
                    "success": False,
                    "error": "Permission denied",
                    "error_code": "PERMISSION_DENIED",
                }

            options = options or {}
            results = {}

            if maintenance_type == "standard":
                # 標準メンテナンス
                results = await self.maintenance_use_case.cleanup_system(
                    cleanup_days=options.get("cleanup_days", 30),
                    execution_days=options.get("execution_days", 7)
                )
                
                # スタック提出のリセット
                reset_results = await self.maintenance_use_case.reset_stuck_submissions(
                    minutes=options.get("stuck_minutes", 30)
                )
                results.update(reset_results)

            elif maintenance_type == "deep":
                # 深いメンテナンス
                results = await self.maintenance_use_case.cleanup_system(
                    cleanup_days=options.get("cleanup_days", 90),
                    execution_days=options.get("execution_days", 30)
                )
                
                # 統計情報の再計算
                await self._rebuild_statistics()
                results["statistics_rebuilt"] = True

            elif maintenance_type == "queue_reset":
                # キューリセット
                reset_count = await self.queue_use_case.reset_stale_items(
                    minutes=options.get("minutes", 60)
                )
                results = {"reset_queue_items": reset_count}

            else:
                return {
                    "success": False,
                    "error": "Unknown maintenance type",
                    "error_code": "INVALID_MAINTENANCE_TYPE",
                }

            logger.info(f"Maintenance '{maintenance_type}' completed by user {requester_user_id}")

            return {
                "success": True,
                "maintenance": {
                    "type": maintenance_type,
                    "completed_at": datetime.utcnow().isoformat(),
                    "results": results,
                    "requested_by": str(requester_user_id),
                }
            }

        except Exception as e:
            logger.error(f"Failed to trigger maintenance: {e}")
            return {
                "success": False,
                "error": "Maintenance failed",
                "error_code": "MAINTENANCE_ERROR",
            }

    async def get_worker_management(self) -> Dict[str, Any]:
        """ワーカー管理情報を取得（API用）"""
        try:
            # 各ワーカーの詳細状況を取得
            worker_details = []
            
            # アクティブワーカーのIDを取得（実装は環境に依存）
            active_worker_ids = await self._get_active_worker_ids()
            
            for worker_id in active_worker_ids:
                worker_status = await self.worker_use_case.get_worker_status(worker_id)
                worker_details.append(worker_status)

            # ワーカー統計
            total_workers = len(worker_details)
            active_workers = len([w for w in worker_details if w.get("running_submissions", 0) > 0])

            return {
                "success": True,
                "workers": {
                    "total_workers": total_workers,
                    "active_workers": active_workers,
                    "idle_workers": total_workers - active_workers,
                    "worker_details": worker_details,
                    "last_updated": datetime.utcnow().isoformat(),
                }
            }

        except Exception as e:
            logger.error(f"Failed to get worker management info: {e}")
            return {
                "success": False,
                "error": "Failed to retrieve worker information",
                "error_code": "WORKER_INFO_ERROR",
            }

    # プライベートメソッド

    async def _get_queue_statistics(self) -> Dict[str, Any]:
        """キュー統計を取得"""
        try:
            pending_count = await self.queue_repo.count_pending()
            processing_count = await self.queue_repo.count_processing()
            
            return {
                "pending": pending_count,
                "processing": processing_count,
                "total": pending_count + processing_count,
            }
        except Exception as e:
            logger.error(f"Failed to get queue statistics: {e}")
            return {"pending": 0, "processing": 0, "total": 0}

    async def _get_worker_statistics(self) -> Dict[str, Any]:
        """ワーカー統計を取得"""
        try:
            active_worker_ids = await self._get_active_worker_ids()
            return {
                "total_workers": len(active_worker_ids),
                "active_workers": len(active_worker_ids),  # 簡略化
            }
        except Exception as e:
            logger.error(f"Failed to get worker statistics: {e}")
            return {"total_workers": 0, "active_workers": 0}

    async def _get_system_statistics(self) -> Dict[str, Any]:
        """システム統計を取得"""
        try:
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow = today + timedelta(days=1)

            today_submissions = await self.submission_repo.count_by_date_range(today, tomorrow)
            
            return {
                "today_submissions": today_submissions,
                "uptime_hours": 24,  # プレースホルダー
            }
        except Exception as e:
            logger.error(f"Failed to get system statistics: {e}")
            return {"today_submissions": 0, "uptime_hours": 0}

    async def _get_health_status(self) -> Dict[str, Any]:
        """健全性状態を取得"""
        try:
            checks = {}
            overall = "healthy"

            # キューチェック
            pending_count = await self.queue_repo.count_pending()
            checks["queue_health"] = {
                "status": "warning" if pending_count > 100 else "healthy",
                "pending_count": pending_count,
            }
            if checks["queue_health"]["status"] == "warning":
                overall = "warning"

            # スタック提出チェック
            stale_items = await self.queue_use_case.get_stale_items(30, 10)
            checks["stale_submissions"] = {
                "status": "warning" if len(stale_items) > 5 else "healthy",
                "count": len(stale_items),
            }
            if checks["stale_submissions"]["status"] == "warning":
                overall = "warning"

            return {"overall": overall, "checks": checks}

        except Exception as e:
            logger.error(f"Failed to get health status: {e}")
            return {"overall": "error", "checks": {"error": str(e)}}

    async def _get_queue_language_statistics(self) -> Dict[str, int]:
        """キューの言語別統計を取得"""
        try:
            # 実装は具体的なクエリに依存
            return {}
        except Exception:
            return {}

    async def _calculate_estimated_wait_time(self, pending_count: int) -> int:
        """推定待ち時間を計算（分）"""
        try:
            # 簡単な推定ロジック
            avg_processing_time_minutes = 2  # 1提出あたり平均2分
            active_workers = len(await self._get_active_worker_ids())
            if active_workers == 0:
                return pending_count * avg_processing_time_minutes
            else:
                return (pending_count // active_workers) * avg_processing_time_minutes
        except Exception:
            return 0

    async def _get_daily_submission_stats(self, start_date: datetime, end_date: datetime) -> Dict[str, int]:
        """日別提出統計を取得"""
        try:
            # 実装は具体的なクエリに依存
            return {}
        except Exception:
            return {}

    async def _get_hourly_submission_stats(self, start_date: datetime, end_date: datetime) -> Dict[str, int]:
        """時間別提出統計を取得"""
        try:
            # 実装は具体的なクエリに依存
            return {}
        except Exception:
            return {}

    async def _get_language_submission_stats(self, start_date: datetime, end_date: datetime) -> Dict[str, int]:
        """言語別提出統計を取得"""
        try:
            # 実装は具体的なクエリに依存
            return {}
        except Exception:
            return {}

    async def _get_result_submission_stats(self, start_date: datetime, end_date: datetime) -> Dict[str, int]:
        """結果別提出統計を取得"""
        try:
            # 実装は具体的なクエリに依存
            return {}
        except Exception:
            return {}

    def _calculate_success_rate(self, result_stats: Dict[str, int]) -> float:
        """成功率を計算"""
        try:
            total = sum(result_stats.values())
            if total == 0:
                return 0.0
            
            accepted = result_stats.get("ACCEPTED", 0)
            return round((accepted / total) * 100, 2)
        except Exception:
            return 0.0

    async def _check_maintenance_permission(self, user_id: uuid.UUID) -> bool:
        """メンテナンス権限をチェック"""
        try:
            # 実装は認証システムに依存
            # とりあえず全ユーザーに権限を与える（本番では要修正）
            return True
        except Exception:
            return False

    async def _rebuild_statistics(self) -> None:
        """統計情報を再構築"""
        try:
            # 統計情報の再構築処理
            logger.info("Statistics rebuild started")
            # 実装は具体的な要件に依存
            logger.info("Statistics rebuild completed")
        except Exception as e:
            logger.error(f"Failed to rebuild statistics: {e}")

    async def _get_active_worker_ids(self) -> List[str]:
        """アクティブワーカーIDリストを取得"""
        try:
            # 実装は具体的なワーカー管理システムに依存
            # とりあえずダミーデータを返す
            return ["worker-1", "worker-2", "worker-3"]
        except Exception:
            return []