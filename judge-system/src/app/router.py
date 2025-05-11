from fastapi import APIRouter, Query, Path, HTTPException
from fastapi.responses import JSONResponse
from fastapi import Request
from typing import List

from src.domain import models
from src.use_case.judge import JudgeUserCode, AppUseCase, ReadProblemListUseCase
from src.use_case.submission_log import SubmissionLogger
from src.use_case.user_status import UserStatusManager
from src.const import DEFAULT_PROBLEM_SET


router = APIRouter(prefix="/api/v1", tags=["judge-system"])

@router.post("/judge")
async def judge_code(request: models.JudgeRequest, problem_set: str = Query(DEFAULT_PROBLEM_SET), user_id: str = Query("default")):
    """
    ユーザーのコードを実行して、テストケースに対する結果を返す
    """
    # 問題IDからJudgeUserCodeインスタンスを作成
    judge = JudgeUserCode(request.problem, problem_set)
    
    # コードを実行して結果を取得
    response = judge(request.code)
    
    # 提出ログを保存
    logger = SubmissionLogger()
    submission_log = logger.save_submission(response, problem_set)
    
    # ユーザーの解決状態を更新
    status_manager = UserStatusManager(user_id)
    problem_status = status_manager.update_problem_status(response, submission_log.id, problem_set)
    
    # 結果にsubmission_idと解決状態を追加
    response_dict = response.model_dump()
    response_dict["submission_id"] = submission_log.id
    
    # problem_statusのdatetimeを文字列に変換
    problem_status_dict = problem_status.model_dump()
    if problem_status_dict.get("solved_at"):
        problem_status_dict["solved_at"] = problem_status.solved_at.isoformat() if problem_status.solved_at else None
    response_dict["problem_status"] = problem_status_dict
    
    # レスポンスを返す
    return JSONResponse(content=response_dict)


@router.get("/problem/{problem_id}")
async def get_problem(problem_id: str, problem_set: str = Query(DEFAULT_PROBLEM_SET), user_id: str = Query("default")):
    """
    問題の詳細を取得するエンドポイント
    """
    # 問題IDから問題を取得
    problem = models.Problem(id=problem_id)
    app_use_case = AppUseCase(problem, problem_set)
    problem = app_use_case.read_problem()
    
    # ユーザーの解決状態を取得
    status_manager = UserStatusManager(user_id)
    problem_status = status_manager.get_problem_status(problem_id, problem_set)
    
    # 問題情報に解決状態を追加
    problem_dict = problem.model_dump()
    problem_dict["solved"] = problem_status.solved
    # datetimeオブジェクトを文字列に変換
    problem_dict["solved_at"] = problem_status.solved_at.isoformat() if problem_status.solved_at else None
    problem_dict["submission_count"] = problem_status.submission_count
    
    # レスポンスを返す
    return JSONResponse(content=problem_dict, status_code=200)


@router.get("/problem-list", response_model=List[dict])
async def get_problem_list(problem_set: str = Query(DEFAULT_PROBLEM_SET), user_id: str = Query("default")):
    """
    問題のリストを取得するエンドポイント
    """
    # 問題のリストを取得
    use_case = ReadProblemListUseCase(problem_set)
    problem_list = use_case()
    
    # ユーザーの解決状態を取得
    status_manager = UserStatusManager(user_id)
    all_statuses = status_manager.get_all_problem_statuses()
    
    # 問題リストに解決状態を追加
    result = []
    for problem in problem_list:
        problem_dict = problem.model_dump()
        
        # この問題の解決状態を取得
        key = f"{problem_set}_{problem.id}"
        status = all_statuses.get(key)
        
        if status:
            problem_dict["solved"] = status.solved
            # datetimeオブジェクトを文字列に変換
            problem_dict["solved_at"] = status.solved_at.isoformat() if status.solved_at else None
            problem_dict["submission_count"] = status.submission_count
        else:
            problem_dict["solved"] = False
            problem_dict["solved_at"] = None
            problem_dict["submission_count"] = 0
        
        result.append(problem_dict)
    
    # レスポンスを返す
    return JSONResponse(content=result, status_code=200)


@router.get("/user/status", response_model=dict)
async def get_user_status(user_id: str = Query("default"), problem_set: str = Query(DEFAULT_PROBLEM_SET)):
    """
    ユーザーの全問題の解決状態を取得
    """
    status_manager = UserStatusManager(user_id)
    all_statuses = status_manager.get_all_problem_statuses()
    
    # 指定された問題セットのステータスだけフィルタリング
    filtered_statuses = {}
    for key, status in all_statuses.items():
        if status.problem_set == problem_set:
            status_dict = status.model_dump()
            # datetimeオブジェクトを文字列に変換
            if status_dict.get("solved_at"):
                status_dict["solved_at"] = status.solved_at.isoformat() if status.solved_at else None
            filtered_statuses[status.problem_id] = status_dict
    
    return JSONResponse(content=filtered_statuses, status_code=200)


@router.get("/submissions/{problem_id}", response_model=List[dict])
async def get_submissions(
    problem_id: str = Path(..., description="取得する問題のID"),
    problem_set: str = Query(DEFAULT_PROBLEM_SET, description="問題セット名"),
    limit: int = Query(10, description="取得する提出数")
):
    """
    指定した問題の提出履歴を取得する
    """
    logger = SubmissionLogger()
    submissions = logger.get_submission_logs(problem_id, problem_set, limit)
    
    # 取得した提出履歴をJSONに変換して返す
    return JSONResponse(
        content=[submission.model_dump(mode='json') for submission in submissions],
        status_code=200
    )


@router.get("/submission/{submission_id}", response_model=dict)
async def get_submission_detail(
    submission_id: str = Path(..., description="取得する提出のID")
):
    """
    指定した提出IDの詳細情報を取得する
    """
    logger = SubmissionLogger()
    result = logger.get_submission_details(submission_id)
    
    if not result:
        raise HTTPException(status_code=404, detail=f"提出ID {submission_id} が見つかりません")
        
    submission_log, submission_result = result
    
    # 提出詳細を返す
    return JSONResponse(
        content={
            "log": submission_log.model_dump(mode='json'),
            "result": submission_result.model_dump(mode='json')
        },
        status_code=200
    )


@router.get("/health")
async def health_check():
    """
    ヘルスチェックエンドポイント
    """
    return {"status": "ok"}
