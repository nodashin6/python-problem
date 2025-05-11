from fastapi import APIRouter, Query, Path, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi import Request, Response
from typing import List, Dict
import uuid
import time
from datetime import datetime, timedelta
import hashlib
import json

from src.domain import models
from src.use_case.judge import JudgeUserCode, AppUseCase, ReadProblemListUseCase, CaseLoader
from src.use_case.submission_log import SubmissionLogger
from src.use_case.user_status import UserStatusManager
from src.const import DEFAULT_PROBLEM_SET

# 進行中のジャッジ処理を保存するグローバル辞書
active_judges: Dict[str, Dict] = {}

# レスポンスをキャッシュするための辞書
response_cache: Dict[str, Dict] = {}

router = APIRouter(prefix="/api/v1", tags=["judge-system"])

async def run_judge_task(judge_id: str, problem_id: str, code: str, problem_set: str, user_id: str):
    """
    バックグラウンドでジャッジ処理を実行するタスク
    """
    try:
        # 問題IDからCaseLoaderインスタンスを作成し、テストケース一覧を取得
        problem = models.Problem(id=problem_id)
        case_loader = CaseLoader(problem, problem_set)
        testcase_names = case_loader.load_testcase_names()
        
        # ジャッジ処理を初期化
        active_judges[judge_id]["status"] = "running"
        active_judges[judge_id]["start_time"] = datetime.now().isoformat()
        active_judges[judge_id]["current_testcase"] = None
        
        # 最初から全テストケースをpending状態で作成
        active_judges[judge_id]["progress"] = {
            "current": 0,
            "total": len(testcase_names),
            "testcases": {}
        }
        
        # すべてのテストケースをpendingで初期化
        for testcase_name in testcase_names:
            active_judges[judge_id]["progress"]["testcases"][testcase_name] = {
                "status": "pending",
                "result": None
            }
        
        # 問題IDからJudgeUserCodeインスタンスを作成
        judge = JudgeUserCode(problem, problem_set)
        
        # テストケース進捗状況を更新するコールバック関数
        def update_progress(testcase_id: str, progress_info: Dict):
            # テストケース情報を更新（すでに存在することを前提）
            active_judges[judge_id]["current_testcase"] = testcase_id
            active_judges[judge_id]["progress"]["current"] = progress_info["current"]
            
            # 個別テストケースの状態を上書き
            testcase_info = active_judges[judge_id]["progress"]["testcases"][testcase_id]
            testcase_info["status"] = progress_info["status"]
            
            # テストケースが完了した場合、結果を追加
            if progress_info["status"] == "completed" and "test_result" in progress_info:
                testcase_info["result"] = progress_info["test_result"]
        
        # コードを実行して結果を取得（進捗状況コールバック付き）
        response = judge(code, update_progress)
        
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
        
        # 結果を保存
        active_judges[judge_id]["status"] = "completed"
        active_judges[judge_id]["results"] = response_dict
        active_judges[judge_id]["end_time"] = datetime.now().isoformat()
    except Exception as e:
        # エラーが発生した場合
        active_judges[judge_id]["status"] = "error"
        active_judges[judge_id]["error"] = str(e)
        active_judges[judge_id]["end_time"] = datetime.now().isoformat()

@router.post("/judge")
async def judge_code(
    background_tasks: BackgroundTasks, 
    request: models.JudgeRequest, 
    problem_set: str = Query(DEFAULT_PROBLEM_SET), 
    user_id: str = Query("default")
):
    """
    ユーザーのコードを実行して、テストケースに対する結果を返す
    非同期でジャッジを実行し、ジャッジIDを返す
    """
    # ユニークなジャッジIDを生成
    judge_id = str(uuid.uuid4())
    
    # ジャッジ情報を初期化
    active_judges[judge_id] = {
        "problem_id": request.problem.id,
        "status": "pending",
        "start_time": None,
        "end_time": None,
        "results": None
    }
    
    # バックグラウンドタスクとしてジャッジを実行
    background_tasks.add_task(
        run_judge_task, 
        judge_id, 
        request.problem.id, 
        request.code, 
        problem_set, 
        user_id
    )
    
    # 即座にジャッジIDを返す
    return JSONResponse({
        "judge_id": judge_id,
        "status": "pending",
        "message": "ジャッジを開始しました。/judge-status/{judge_id}で状態を確認できます。"
    })

@router.get("/judge-status/{judge_id}")
async def get_judge_status(judge_id: str, response: Response):
    """
    ジャッジの状態を取得するエンドポイント
    """
    if judge_id not in active_judges:
        raise HTTPException(status_code=404, detail=f"ジャッジID {judge_id} が見つかりません")
    
    # キャッシュキーを生成（judgeIDとステータスに基づく）
    judge_info = active_judges[judge_id]
    cache_key = f"{judge_id}_{judge_info['status']}_{hash(json.dumps(judge_info, sort_keys=True, default=str))}"
    
    # キャッシュがあり、まだ有効期間内なら、キャッシュを返す
    current_time = time.time()
    if cache_key in response_cache and response_cache[cache_key]['expires_at'] > current_time:
        # キャッシュヘッダーを設定
        response.headers["X-Cache"] = "HIT"
        return response_cache[cache_key]['data']
    
    # レスポンスを生成
    if judge_info["status"] == "completed":
        result_data = {
            "judge_id": judge_id,
            "status": judge_info["status"],
            "start_time": judge_info["start_time"],
            "end_time": judge_info["end_time"],
            "results": judge_info["results"]
        }
    elif judge_info["status"] == "error":
        result_data = {
            "judge_id": judge_id,
            "status": judge_info["status"],
            "start_time": judge_info["start_time"],
            "end_time": judge_info["end_time"],
            "error": judge_info["error"]
        }
    else:
        result_data = {
            "judge_id": judge_id,
            "status": judge_info["status"],
            "start_time": judge_info["start_time"],
            "problem_id": judge_info["problem_id"],
            "message": "ジャッジ処理が進行中です",
            "progress": judge_info.get("progress", None)  # 進捗情報も含める
        }
    
    # キャッシュに保存（状態に応じてTTLを調整）
    if judge_info["status"] in ["completed", "error"]:
        # 完了・エラー状態は長くキャッシュ（30秒）
        ttl = 30
    else:
        # 進行中は短めにキャッシュ（1秒）
        ttl = 1
        
    response_cache[cache_key] = {
        'data': result_data,
        'expires_at': current_time + ttl
    }
    
    # キャッシュクリーンアップ（古いキャッシュを削除）
    if len(response_cache) > 1000:  # キャッシュ数が増えすぎたら
        clean_old_cache()
    
    # キャッシュヘッダーを設定
    response.headers["X-Cache"] = "MISS"
    response.headers["Cache-Control"] = f"max-age={ttl}"
    
    return JSONResponse(content=result_data)

def clean_old_cache():
    """古くなったキャッシュエントリを削除する"""
    current_time = time.time()
    expired_keys = [k for k, v in response_cache.items() if v['expires_at'] < current_time]
    for key in expired_keys:
        del response_cache[key]

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


@router.get("/testcases/{problem_id}")
async def get_testcase_list(
    problem_id: str = Path(..., description="取得する問題のID"),
    problem_set: str = Query(DEFAULT_PROBLEM_SET, description="問題セット名")
):
    """
    指定した問題のテストケース一覧を取得するエンドポイント
    """
    try:
        # 問題IDからCaseLoaderインスタンスを作成
        problem = models.Problem(id=problem_id)
        case_loader = CaseLoader(problem, problem_set)
        
        # テストケース名のリストを取得
        testcase_names = case_loader.load_testcase_names()
        
        return JSONResponse(content=testcase_names, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"テストケース一覧の取得に失敗しました: {str(e)}")

@router.get("/health")
async def health_check():
    """
    ヘルスチェックエンドポイント
    """
    return {"status": "ok"}
