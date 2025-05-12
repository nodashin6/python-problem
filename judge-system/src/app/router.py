from fastapi import APIRouter, Query, Path, HTTPException, BackgroundTasks, Request, Response, Depends
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional, Any
import uuid
import time
import logging
from datetime import datetime, timedelta

from src.domain import models
from src.domain.services.judge_service import JudgeService
from src.const import DEFAULT_PROBLEM_SET
from src.use_case.judge_use_case import AppUseCase, ReadProblemListUseCase, CaseLoader
from src.use_case.submission_log import SubmissionLogger
from src.use_case.user_status import UserStatusManager

# インスタンス作成
judge_service = JudgeService()

# レスポンスをキャッシュするための辞書
response_cache: Dict[str, Dict[str, Any]] = {}
# キャッシュの有効期限（秒）
CACHE_EXPIRY_COMPLETED = 30  # 完了状態のキャッシュ保持時間
CACHE_EXPIRY_IN_PROGRESS = 1  # 進行中のキャッシュ保持時間
MAX_CACHE_SIZE = 500  # キャッシュの最大サイズ

router = APIRouter(prefix="/api/v1", tags=["judge-system"])


def clean_old_cache() -> None:
    """古くなったキャッシュエントリを削除する"""
    current_time = time.time()
    expired_keys = [k for k, v in response_cache.items() if v['expires_at'] < current_time]
    
    for key in expired_keys:
        del response_cache[key]
    
    # キャッシュが最大サイズを超えた場合、古い順に削除
    if len(response_cache) > MAX_CACHE_SIZE:
        sorted_items = sorted(response_cache.items(), key=lambda x: x[1]['expires_at'])
        for key, _ in sorted_items[:len(response_cache) - MAX_CACHE_SIZE]:
            del response_cache[key]


@router.post("/judge", response_model=Dict[str, str])
async def judge_code(
    background_tasks: BackgroundTasks,
    request: models.JudgeRequest,
    problem_set: str = Query(DEFAULT_PROBLEM_SET, description="問題セット名"),
    user_id: str = Query("default", description="ユーザーID")
) -> JSONResponse:
    """
    ユーザーのコードを実行して、テストケースに対する結果を返します。
    非同期でジャッジを実行し、リアルタイムで結果をファイルに保存します。
    
    Args:
        background_tasks: バックグラウンドタスク
        request: ジャッジリクエスト
        problem_set: 問題セット名
        user_id: ユーザーID
        
    Returns:
        ジャッジIDとステータス
    """
    try:
        # ジャッジを開始
        judge_id = judge_service.start_judge(request.problem.id, request.code, problem_set)
        
        # バックグラウンドでジャッジを実行
        background_tasks.add_task(
            judge_service.process_judge_results,
            judge_id=judge_id,
            problem_id=request.problem.id,
            code=request.code,
            problem_set=problem_set
        )
        
        # 完了したらログを保存するタスクを追加
        background_tasks.add_task(
            judge_service.save_submission_result,
            judge_id=judge_id,
            user_id=user_id,
            problem_set=problem_set
        )
        
        return JSONResponse(content={"judge_id": judge_id, "status": "started"})
    except Exception as e:
        logging.error(f"ジャッジ開始エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"ジャッジ実行中にエラーが発生しました: {str(e)}")


@router.get("/judge-status/{judge_id}", response_model=Dict[str, Any])
async def get_judge_status(
    judge_id: str = Path(..., description="ジャッジID"),
    response: Response = None
) -> JSONResponse:
    """
    ジャッジの状態を取得するエンドポイント
    
    Args:
        judge_id: ジャッジID
        response: レスポンスオブジェクト
        
    Returns:
        ジャッジの状態
    """
    # キャッシュキーを生成
    cache_key = f"status_{judge_id}"
    
    # キャッシュがあり、まだ有効期間内なら、キャッシュを返す
    current_time = time.time()
    if cache_key in response_cache and response_cache[cache_key]['expires_at'] > current_time:
        # キャッシュヘッダーを設定
        response.headers["X-Cache"] = "HIT"
        return response_cache[cache_key]['data']
    
    try:
        # ジャッジの状態を取得
        result = judge_service.get_judge_status(judge_id)
        
        if result.get("status") == "not_found":
            raise HTTPException(status_code=404, detail=result.get("message", "ジャッジIDが見つかりません"))
        
        # キャッシュに保存（状態に応じてTTLを調整）
        if result.get("status") == "completed":
            # 完了状態は長くキャッシュ
            ttl = CACHE_EXPIRY_COMPLETED
        else:
            # 進行中は短めにキャッシュ
            ttl = CACHE_EXPIRY_IN_PROGRESS
            
        response_cache[cache_key] = {
            'data': result,
            'expires_at': current_time + ttl
        }
        
        # キャッシュクリーンアップ
        clean_old_cache()
        
        # キャッシュヘッダーを設定
        response.headers["X-Cache"] = "MISS"
        response.headers["Cache-Control"] = f"max-age={ttl}"
        
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"ジャッジステータス取得エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"ジャッジ状態の取得中にエラーが発生しました: {str(e)}")


@router.get("/problem/{problem_id}", response_model=Dict[str, Any])
async def get_problem(
    problem_id: str = Path(..., description="問題ID"),
    problem_set: str = Query(DEFAULT_PROBLEM_SET, description="問題セット名"),
    user_id: str = Query("default", description="ユーザーID")
) -> JSONResponse:
    """
    問題の詳細を取得するエンドポイント
    
    Args:
        problem_id: 問題ID
        problem_set: 問題セット名
        user_id: ユーザーID
        
    Returns:
        問題の詳細情報
    """
    try:
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
        problem_dict["solved_at"] = problem_status.solved_at.isoformat() if problem_status.solved_at else None
        problem_dict["submission_count"] = problem_status.submission_count
        
        # レスポンスを返す
        return JSONResponse(content=problem_dict, status_code=200)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"問題 {problem_id} が見つかりません")
    except Exception as e:
        logging.error(f"問題取得エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"問題の取得中にエラーが発生しました: {str(e)}")


@router.get("/problem-list", response_model=List[Dict[str, Any]])
async def get_problem_list(
    problem_set: str = Query(DEFAULT_PROBLEM_SET, description="問題セット名"),
    user_id: str = Query("default", description="ユーザーID")
) -> JSONResponse:
    """
    問題のリストを取得するエンドポイント
    
    Args:
        problem_set: 問題セット名
        user_id: ユーザーID
        
    Returns:
        問題リスト
    """
    try:
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
                problem_dict["solved_at"] = status.solved_at.isoformat() if status.solved_at else None
                problem_dict["submission_count"] = status.submission_count
            else:
                problem_dict["solved"] = False
                problem_dict["solved_at"] = None
                problem_dict["submission_count"] = 0
            
            result.append(problem_dict)
        
        # レスポンスを返す
        return JSONResponse(content=result, status_code=200)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"問題セット {problem_set} が見つかりません")
    except Exception as e:
        logging.error(f"問題リスト取得エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"問題リストの取得中にエラーが発生しました: {str(e)}")


@router.get("/user/status", response_model=Dict[str, Any])
async def get_user_status(
    user_id: str = Query("default", description="ユーザーID"),
    problem_set: str = Query(DEFAULT_PROBLEM_SET, description="問題セット名")
) -> JSONResponse:
    """
    ユーザーの全問題の解決状態を取得
    
    Args:
        user_id: ユーザーID
        problem_set: 問題セット名
        
    Returns:
        ユーザーの解決状態
    """
    try:
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
    except Exception as e:
        logging.error(f"ユーザーステータス取得エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"ユーザーステータスの取得中にエラーが発生しました: {str(e)}")


@router.get("/submissions/{problem_id}", response_model=List[Dict[str, Any]])
async def get_submissions(
    problem_id: str = Path(..., description="取得する問題のID"),
    problem_set: str = Query(DEFAULT_PROBLEM_SET, description="問題セット名"),
    limit: int = Query(10, description="取得する提出数")
) -> JSONResponse:
    """
    指定した問題の提出履歴を取得する
    
    Args:
        problem_id: 問題ID
        problem_set: 問題セット名
        limit: 取得する提出数の上限
        
    Returns:
        提出履歴リスト
    """
    try:
        logger = SubmissionLogger()
        submissions = logger.get_submission_logs(problem_id, problem_set, limit)
        
        # 取得した提出履歴をJSONに変換して返す
        return JSONResponse(
            content=[submission.model_dump(mode='json') for submission in submissions],
            status_code=200
        )
    except Exception as e:
        logging.error(f"提出履歴取得エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"提出履歴の取得中にエラーが発生しました: {str(e)}")


@router.get("/submission/{submission_id}", response_model=Dict[str, Any])
async def get_submission_detail(
    submission_id: str = Path(..., description="取得する提出のID")
) -> JSONResponse:
    """
    指定した提出IDの詳細情報を取得する
    
    Args:
        submission_id: 提出ID
        
    Returns:
        提出詳細情報
    """
    try:
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
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"提出詳細取得エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"提出詳細の取得中にエラーが発生しました: {str(e)}")


@router.get("/testcases/{problem_id}", response_model=List[str])
async def get_testcase_list(
    problem_id: str = Path(..., description="取得する問題のID"),
    problem_set: str = Query(DEFAULT_PROBLEM_SET, description="問題セット名")
) -> JSONResponse:
    """
    指定した問題のテストケース一覧を取得するエンドポイント
    
    Args:
        problem_id: 問題ID
        problem_set: 問題セット名
        
    Returns:
        テストケース名のリスト
    """
    try:
        # 問題IDからCaseLoaderインスタンスを作成
        problem = models.Problem(id=problem_id)
        case_loader = CaseLoader(problem, problem_set)
        
        # テストケース名のリストを取得
        testcase_names = case_loader.load_testcase_names()
        
        return JSONResponse(content=testcase_names, status_code=200)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"問題 {problem_id} のテストケースが見つかりません")
    except Exception as e:
        logging.error(f"テストケース一覧取得エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"テストケース一覧の取得に失敗しました: {str(e)}")


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    ヘルスチェックエンドポイント
    
    Returns:
        ステータス情報
    """
    return {"status": "ok", "timestamp": datetime.now().isoformat()}
