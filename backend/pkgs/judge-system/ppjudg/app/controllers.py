"""
Judge Domain API Controllers
ジャッジドメインAPIコントローラー
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import HTTPException, status
from pydantic import BaseModel, Field, validator

from dependency_injector.wiring import Provide, inject

from ...const import ProgrammingLanguage, JudgeResultType, ExecutionStatus
from ...shared.logging import get_logger

from ..domain.models.submission import SubmissionStatus
from .services import (
    SubmissionApplicationService,
    CodeExecutionApplicationService,
    JudgeSystemApplicationService,
)
from .container import JudgeContainer

logger = get_logger(__name__)


# Request/Response Models
class SubmitSolutionRequest(BaseModel):
    """解答提出リクエスト"""

    code: str = Field(..., min_length=1, max_length=100000, description="ソースコード")
    language: ProgrammingLanguage = Field(..., description="プログラミング言語")
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="メタデータ"
    )

    @field_validator("code")
    def validate_code(cls, v):
        if not v.strip():
            raise ValueError("Code cannot be empty")
        return v


class ExecuteCodeRequest(BaseModel):
    """コード実行リクエスト"""

    code: str = Field(..., min_length=1, max_length=50000, description="ソースコード")
    language: ProgrammingLanguage = Field(..., description="プログラミング言語")
    input_data: str = Field(default="", max_length=10000, description="入力データ")
    time_limit_ms: int = Field(
        default=5000, ge=100, le=30000, description="時間制限(ms)"
    )
    memory_limit_mb: int = Field(
        default=256, ge=16, le=1024, description="メモリ制限(MB)"
    )


class RejudgeRequest(BaseModel):
    """再ジャッジリクエスト"""

    reason: Optional[str] = Field(None, max_length=500, description="再ジャッジ理由")


class StartWorkerRequest(BaseModel):
    """ワーカー開始リクエスト"""

    worker_id: Optional[str] = Field(None, description="ワーカーID")
    max_concurrent_jobs: int = Field(
        default=3, ge=1, le=10, description="最大同時実行数"
    )


class SubmissionResponse(BaseModel):
    """提出レスポンス"""

    submission_id: str
    user_id: str
    problem_id: str
    language: str
    status: str
    result: Optional[str]
    score: Optional[float]
    execution_time_ms: Optional[int]
    memory_usage_mb: Optional[float]
    created_at: str
    judged_at: Optional[str]
    queue_position: Optional[int]


class ExecutionResponse(BaseModel):
    """実行結果レスポンス"""

    execution_id: str
    status: str
    output: Optional[str]
    error: Optional[str]
    exit_code: Optional[int]
    execution_time_ms: Optional[int]
    memory_usage_mb: Optional[float]
    created_at: str
    completed_at: Optional[str]


class SystemStatusResponse(BaseModel):
    """システム状態レスポンス"""

    queue: Dict[str, int]
    workers: Dict[str, Any]
    system: Dict[str, Any]
    event_bus: Dict[str, Any]


class SubmissionController:
    """提出管理コントローラー"""

    @inject
    def __init__(
        self,
        submission_service: SubmissionApplicationService = Provide[
            JudgeContainer.submission_use_case
        ],
    ):
        self.submission_service = submission_service

    async def submit_solution(
        self, user_id: str, problem_id: str, request: SubmitSolutionRequest
    ) -> Dict[str, Any]:
        """解答を提出"""
        try:
            result = await self.submission_service.submit_solution(
                user_id=user_id,
                problem_id=problem_id,
                code=request.code,
                language=request.language,
                metadata=request.metadata,
            )

            return {"success": True, "data": result}

        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            logger.error(f"Failed to submit solution: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    async def get_submission(self, submission_id: str) -> Dict[str, Any]:
        """提出を取得"""
        try:
            submission = await self.submission_service.get_submission(submission_id)

            if not submission:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found"
                )

            return {"success": True, "data": submission}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get submission: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    async def get_user_submissions(
        self,
        user_id: str,
        problem_id: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """ユーザーの提出一覧を取得"""
        try:
            if limit > 100:
                limit = 100  # 最大件数制限

            result = await self.submission_service.get_user_submissions(
                user_id=user_id, problem_id=problem_id, limit=limit, offset=offset
            )

            return {"success": True, "data": result}

        except Exception as e:
            logger.error(f"Failed to get user submissions: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    async def get_problem_submissions(
        self,
        problem_id: str,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """問題の提出一覧を取得"""
        try:
            if limit > 200:
                limit = 200  # 最大件数制限

            submission_status = None
            if status:
                try:
                    submission_status = SubmissionStatus(status)
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid status: {status}",
                    )

            result = await self.submission_service.get_problem_submissions(
                problem_id=problem_id,
                status=submission_status,
                limit=limit,
                offset=offset,
            )

            return {"success": True, "data": result}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get problem submissions: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    async def rejudge_submission(
        self, submission_id: str, request: RejudgeRequest
    ) -> Dict[str, Any]:
        """提出を再ジャッジ"""
        try:
            result = await self.submission_service.rejudge_submission(
                submission_id=submission_id, reason=request.reason
            )

            return {"success": True, "data": result}

        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            logger.error(f"Failed to rejudge submission: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )


class CodeExecutionController:
    """コード実行コントローラー"""

    @inject
    def __init__(
        self,
        execution_service: CodeExecutionApplicationService = Provide[
            JudgeContainer.code_execution_use_case
        ],
    ):
        self.execution_service = execution_service

    async def execute_code(self, request: ExecuteCodeRequest) -> Dict[str, Any]:
        """コードを実行"""
        try:
            result = await self.execution_service.execute_code(
                code=request.code,
                language=request.language,
                input_data=request.input_data,
                time_limit_ms=request.time_limit_ms,
                memory_limit_mb=request.memory_limit_mb,
            )

            return {"success": True, "data": result}

        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            logger.error(f"Failed to execute code: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    async def get_execution_result(self, execution_id: str) -> Dict[str, Any]:
        """実行結果を取得"""
        try:
            result = await self.execution_service.get_execution_result(execution_id)

            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Execution result not found",
                )

            return {"success": True, "data": result}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get execution result: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )


class JudgeSystemController:
    """ジャッジシステム管理コントローラー"""

    @inject
    def __init__(
        self,
        system_service: JudgeSystemApplicationService = Provide[
            JudgeContainer.judge_worker_use_case
        ],
    ):
        self.system_service = system_service

    async def start_worker(self, request: StartWorkerRequest) -> Dict[str, Any]:
        """ジャッジワーカーを開始"""
        try:
            result = await self.system_service.start_judge_worker(
                worker_id=request.worker_id,
                max_concurrent_jobs=request.max_concurrent_jobs,
            )

            return {"success": True, "data": result}

        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            logger.error(f"Failed to start worker: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    async def stop_worker(self, worker_id: str) -> Dict[str, Any]:
        """ジャッジワーカーを停止"""
        try:
            result = await self.system_service.stop_judge_worker(worker_id)

            return {"success": True, "data": result}

        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            logger.error(f"Failed to stop worker: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    async def get_system_status(self) -> Dict[str, Any]:
        """システム状態を取得"""
        try:
            result = await self.system_service.get_system_status()

            return {"success": True, "data": result}

        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    async def run_maintenance(self) -> Dict[str, Any]:
        """メンテナンス作業を実行"""
        try:
            result = await self.system_service.run_maintenance()

            return {"success": True, "data": result}

        except Exception as e:
            logger.error(f"Failed to run maintenance: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    async def health_check(self) -> Dict[str, Any]:
        """ヘルスチェック"""
        try:
            result = await self.system_service.get_health_check()

            return {"success": True, "data": result}

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            # ヘルスチェックは失敗しても500エラーにはしない
            return {
                "success": False,
                "data": {
                    "healthy": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                },
            }

    async def cleanup_executions(self, days: int = 7) -> Dict[str, Any]:
        """古い実行結果をクリーンアップ"""
        try:
            if days < 1 or days > 365:
                raise ValueError("Days must be between 1 and 365")

            result = await self.execution_service.cleanup_old_executions(days)

            return {"success": True, "data": result}

        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            logger.error(f"Failed to cleanup executions: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )


# コントローラーファクトリー
class ControllerFactory:
    """コントローラーファクトリー"""

    @staticmethod
    def create_controllers() -> Dict[str, Any]:
        """全てのコントローラーを作成"""
        return {
            "submission_controller": SubmissionController(),
            "execution_controller": CodeExecutionController(),
            "system_controller": JudgeSystemController(),
        }


# 便利関数
def get_controllers() -> Dict[str, Any]:
    """コントローラーを取得"""
    return ControllerFactory.create_controllers()
