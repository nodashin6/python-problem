from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi import Request
from fastapi import Depends

from src.domain import models
from src.use_case.judge import JudgeUserCode


router = APIRouter(prefix="/api/v1", tags=["judge-system"])

@router.post("/judge")
async def judge_code(request: models.JudgeRequest):
    """
    ユーザーのコードを実行して、テストケースに対する結果を返す
    """
    # 問題IDからJudgeUserCodeインスタンスを作成
    judge = JudgeUserCode(request.problem)
    
    # コードを実行して結果を取得
    response = judge(request.code)
    
    # レスポンスを返す
    return response


@router.get("/health")
async def health_check():
    """
    ヘルスチェックエンドポイント
    """
    return {"status": "ok"}
