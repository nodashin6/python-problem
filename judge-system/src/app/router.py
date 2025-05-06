from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi import Request
from fastapi import Depends

from src.domain import models
from src.use_case.judge import JudgeUserCode, AppUseCase, ReadProblemListUseCase


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


@router.get("/problem/{problem_id}")
async def get_problem(problem_id: str):
    """
    問題の詳細を取得するエンドポイント
    """
    # 問題IDから問題を取得
    problem = models.Problem(id=problem_id)
    app_use_case = AppUseCase(problem)
    problem = app_use_case.read_problem()
    
    # レスポンスを返す
    return JSONResponse(content=problem.model_dump(), status_code=200)


@router.get("/problem-list", response_model=list[models.Problem])
async def get_problem_list():
    """
    問題のリストを取得するエンドポイント
    """
    # 問題のリストを取得
    use_case = ReadProblemListUseCase()
    problem_list = use_case()
    problem_list = [problem.model_dump() for problem in problem_list]
    
    # レスポンスを返す
    return JSONResponse(content=problem_list, status_code=200)





@router.get("/health")
async def health_check():
    """
    ヘルスチェックエンドポイント
    """
    return {"status": "ok"}
