"""
Judge Domain API Routes
ジャッジドメインAPIルーティング
"""

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.security import HTTPBearer

from ...shared.auth import User, get_current_user, require_admin
from ...shared.logging import get_logger
from ..app.controllers import (
    CodeExecutionController,
    ExecuteCodeRequest,
    JudgeSystemController,
    RejudgeRequest,
    StartWorkerRequest,
    SubmissionController,
    SubmitSolutionRequest,
)

logger = get_logger(__name__)
security = HTTPBearer()

# サブルーター
submission_router = APIRouter()
execution_router = APIRouter()
system_router = APIRouter()


# Submission endpoints
@submission_router.post("/submit/{problem_id}")
async def submit_solution(
    problem_id: str = Path(..., description="問題ID"),
    request: SubmitSolutionRequest = ...,
    current_user: User = Depends(get_current_user),
    controller: SubmissionController = Depends(SubmissionController),
):
    """解答を提出"""
    return await controller.submit_solution(
        user_id=current_user.user_id, problem_id=problem_id, request=request
    )


@submission_router.get("/submissions/{submission_id}")
async def get_submission(
    submission_id: str = Path(..., description="提出ID"),
    current_user: User = Depends(get_current_user),
    controller: SubmissionController = Depends(SubmissionController),
):
    """提出を取得"""
    submission = await controller.get_submission(submission_id)

    # 権限チェック: 自分の提出またはモデレーター以上
    if (
        submission["data"]["user_id"] != current_user.user_id
        and not current_user.is_moderator()
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    return submission


@submission_router.get("/users/{user_id}/submissions")
async def get_user_submissions(
    user_id: str = Path(..., description="ユーザーID"),
    problem_id: str | None = Query(None, description="問題ID"),
    limit: int = Query(20, ge=1, le=100, description="取得件数"),
    offset: int = Query(0, ge=0, description="オフセット"),
    current_user: User = Depends(get_current_user),
    controller: SubmissionController = Depends(SubmissionController),
):
    """ユーザーの提出一覧を取得"""
    # 権限チェック: 自分の提出またはモデレーター以上
    if user_id != current_user.user_id and not current_user.is_moderator():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    return await controller.get_user_submissions(
        user_id=user_id, problem_id=problem_id, limit=limit, offset=offset
    )


@submission_router.get("/problems/{problem_id}/submissions")
async def get_problem_submissions(
    problem_id: str = Path(..., description="問題ID"),
    status: str | None = Query(None, description="提出ステータス"),
    limit: int = Query(50, ge=1, le=200, description="取得件数"),
    offset: int = Query(0, ge=0, description="オフセット"),
    current_user: User = Depends(get_current_user),
    controller: SubmissionController = Depends(SubmissionController),
):
    """問題の提出一覧を取得 (モデレーター以上)"""
    if not current_user.is_moderator():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Moderator access required"
        )

    return await controller.get_problem_submissions(
        problem_id=problem_id, status=status, limit=limit, offset=offset
    )


@submission_router.post("/submissions/{submission_id}/rejudge")
async def rejudge_submission(
    submission_id: str = Path(..., description="提出ID"),
    request: RejudgeRequest = RejudgeRequest(),
    current_user: User = Depends(require_admin),
    controller: SubmissionController = Depends(SubmissionController),
):
    """提出を再ジャッジ (管理者のみ)"""
    return await controller.rejudge_submission(
        submission_id=submission_id, request=request
    )


# Code execution endpoints
@execution_router.post("/execute")
async def execute_code(
    request: ExecuteCodeRequest = ...,
    current_user: User = Depends(get_current_user),
    controller: CodeExecutionController = Depends(CodeExecutionController),
):
    """コードを実行"""
    return await controller.execute_code(request)


@execution_router.get("/executions/{execution_id}")
async def get_execution_result(
    execution_id: str = Path(..., description="実行ID"),
    current_user: User = Depends(get_current_user),
    controller: CodeExecutionController = Depends(CodeExecutionController),
):
    """実行結果を取得"""
    return await controller.get_execution_result(execution_id)


# System management endpoints
@system_router.post("/workers/start")
async def start_worker(
    request: StartWorkerRequest = StartWorkerRequest(),
    current_user: User = Depends(require_admin),
    controller: JudgeSystemController = Depends(JudgeSystemController),
):
    """ジャッジワーカーを開始 (管理者のみ)"""
    return await controller.start_worker(request)


@system_router.post("/workers/{worker_id}/stop")
async def stop_worker(
    worker_id: str = Path(..., description="ワーカーID"),
    current_user: User = Depends(require_admin),
    controller: JudgeSystemController = Depends(JudgeSystemController),
):
    """ジャッジワーカーを停止 (管理者のみ)"""
    return await controller.stop_worker(worker_id)


@system_router.get("/status")
async def get_system_status(
    current_user: User = Depends(get_current_user),
    controller: JudgeSystemController = Depends(JudgeSystemController),
):
    """システム状態を取得"""
    # モデレーター以上でないと詳細情報は見せない
    if not current_user.is_moderator():
        return {
            "success": True,
            "data": {"status": "running", "message": "System is operational"},
        }

    return await controller.get_system_status()


@system_router.post("/maintenance")
async def run_maintenance(
    current_user: User = Depends(require_admin),
    controller: JudgeSystemController = Depends(JudgeSystemController),
):
    """メンテナンス作業を実行 (管理者のみ)"""
    return await controller.run_maintenance()


@system_router.get("/health")
async def health_check(
    controller: JudgeSystemController = Depends(JudgeSystemController),
):
    """ヘルスチェック (認証不要)"""
    return await controller.health_check()


@system_router.delete("/executions/cleanup")
async def cleanup_executions(
    days: int = Query(7, ge=1, le=365, description="保持日数"),
    current_user: User = Depends(require_admin),
    controller: JudgeSystemController = Depends(JudgeSystemController),
):
    """古い実行結果をクリーンアップ (管理者のみ)"""
    return await controller.cleanup_executions(days)


# メインルーター
judge_router = APIRouter()

# サブルーターを統合
judge_router.include_router(submission_router, tags=["submissions"])
judge_router.include_router(execution_router, tags=["executions"])
judge_router.include_router(system_router, prefix="/system", tags=["system"])


@judge_router.get("/")
async def judge_root():
    """ジャッジドメインルート"""
    return {
        "domain": "judge",
        "description": "Judge System API",
        "endpoints": {
            "submissions": "Submission management",
            "executions": "Code execution",
            "system": "System management",
        },
    }
