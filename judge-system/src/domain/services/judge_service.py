import uuid
from typing import Dict, Any, Iterator, Optional, List
import logging

from src.domain import models
from src.use_case.judge_use_case import JudgeUserCode, CaseLoader, JudgeResult
from src.infra.repositories.judge_repository import JudgeResultRepository
from src.use_case.submission_log import SubmissionLogger
from src.use_case.user_status import UserStatusManager
from src.const import DEFAULT_PROBLEM_SET

class JudgeService:
    """
    ジャッジのワークフローを管理するサービス
    """
    def __init__(self, repository: Optional[JudgeResultRepository] = None):
        """
        Args:
            repository: ジャッジ結果を保存するリポジトリ。省略時は標準のものを使用
        """
        self.repository = repository or JudgeResultRepository()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.judge_executor = JudgeUserCode()
        self.submission_logger = SubmissionLogger()
        self.user_status_manager = None  # ユーザーIDによって初期化するのでここでは設定しない
    
    def start_judge(self, problem_id: str, code: str, problem_set: str = DEFAULT_PROBLEM_SET) -> str:
        """
        ジャッジプロセスを開始する
        
        Args:
            problem_id: 問題ID
            code: ユーザーのコード
            problem_set: 問題セット
            
        Returns:
            生成されたジャッジID
        """
        # ユニークなジャッジIDを生成
        judge_id = str(uuid.uuid4())
        
        try:
            # 初期状態を保存
            self.repository.save(judge_id, {
                "status": "running",
                "problem_id": problem_id,
                "problem_set": problem_set,
                "code": code,
                "results": []
            })
            
            self.logger.info(f"ジャッジ開始: ID={judge_id}, 問題ID={problem_id}, 問題セット={problem_set}")
            return judge_id
        
        except Exception as e:
            self.logger.error(f"ジャッジ開始エラー: {str(e)}")
            raise
        
    def process_judge_results(self, judge_id: str, problem_id: str, 
                             code: str, problem_set: str = DEFAULT_PROBLEM_SET) -> None:
        """
        ジャッジを実行し、結果をリアルタイムで処理する
        
        Args:
            judge_id: ジャッジID
            problem_id: 問題ID
            code: ユーザーのコード
            problem_set: 問題セット
        """
        try:
            # 問題を準備
            problem = models.Problem(id=problem_id)
            
            # テストケースをロード
            case_loader = CaseLoader(problem, problem_set)
            testcase_names = case_loader.load_testcase_names()
            total_testcases = len(testcase_names)
            processed_testcases = 0
            
            results = []
            # 各テストケースを処理
            for testcase in case_loader:
                # テストケース処理中の状態を報告
                progress_status = {
                    "status": "processing",
                    "current": processed_testcases + 1,
                    "total": total_testcases,
                    "testcase_id": testcase.id
                }
                self.repository.update(judge_id, progress_status)
                
                # 単一テストケースを実行
                result = self.judge_executor.judge_testcase(code, testcase)
                
                # ステータスを設定
                status = self.judge_executor.determine_status(result)
                
                # 結果オブジェクトを作成
                judge_result = models.JudgeResult(
                    id=f"{problem_id}_{testcase.id}",
                    problem=problem,
                    test_case=testcase,
                    status=status,
                    metadata=result.metadata
                )
                
                results.append(judge_result)
                processed_testcases += 1
                
                # テストケース処理完了の状態を報告
                completion_status = {
                    "status": "completed",
                    "current": processed_testcases,
                    "total": total_testcases,
                    "testcase_id": testcase.id,
                    "test_result": {
                        "status": status,
                        "time_used": result.metadata.time_used,
                        "memory_used": result.metadata.memory_used
                    }
                }
                self.repository.update(judge_id, completion_status)
                
                # もしコンパイルエラーなら、残りのテストケースは実行しない
                if status == "CE":
                    break
            
            # すべてのテストケース結果を保存
            response = models.JudgeResponse(
                id=f"judge_{problem_id}",
                problem=problem,
                results=results,
                code=code
            )
            
            # リポジトリに完了した結果を保存
            result_dicts = []
            for result in response.results:
                result_dicts.append(result.model_dump())
                
            self.repository.save(judge_id, {
                "status": "completed",
                "problem_id": problem_id,
                "problem_set": problem_set,
                "code": code,
                "results": result_dicts
            })
            
            self.logger.info(f"ジャッジ完了: ID={judge_id}, 問題ID={problem_id}")
            
        except Exception as e:
            self.logger.error(f"ジャッジ処理エラー: ID={judge_id}, エラー={str(e)}")
            # エラー状態を保存
            self.repository.save(judge_id, {
                "status": "error",
                "problem_id": problem_id,
                "problem_set": problem_set,
                "error_message": str(e)
            })
        finally:
            # 完了状態を記録
            self.repository.finalize(judge_id)
        
    def get_judge_status(self, judge_id: str) -> Dict[str, Any]:
        """
        ジャッジの状態を取得する
        
        Args:
            judge_id: ジャッジID
            
        Returns:
            ジャッジ状態の辞書
        """
        result = self.repository.get(judge_id)
        if not result:
            self.logger.warning(f"ジャッジID {judge_id} が見つかりません")
            return {"status": "not_found", "message": f"ジャッジID {judge_id} が見つかりません"}
            
        return result
        
    def save_submission_result(self, judge_id: str, 
                              user_id: str, problem_set: str = DEFAULT_PROBLEM_SET) -> Dict[str, Any]:
        """
        完了したジャッジの結果を提出記録として保存
        
        Args:
            judge_id: ジャッジID
            user_id: ユーザーID
            problem_set: 問題セット
            
        Returns:
            保存結果情報
        """
        # ジャッジ結果を取得
        judge_data = self.repository.get(judge_id)
        if not judge_data:
            self.logger.warning(f"ジャッジID {judge_id} が見つかりません")
            return {"status": "error", "message": "ジャッジIDが見つかりません"}
            
        if judge_data["status"] != "completed":
            self.logger.warning(f"ジャッジID {judge_id} が完了していません: {judge_data['status']}")
            return {"status": "error", "message": "ジャッジが完了していません"}
            
        try:
            # 結果からレスポンスモデルを構築
            problem_id = judge_data.get("problem_id")
            problem = models.Problem(id=problem_id)
            
            results = []
            for result_dict in judge_data.get("results", []):
                # テストケース情報がない場合はスキップ
                if "test_case" not in result_dict:
                    continue
                    
                # テストケース情報を復元
                testcase = models.Testcase(
                    id=result_dict["test_case"]["id"],
                    name=result_dict["test_case"]["name"],
                    problem=result_dict["test_case"]["problem"],
                    stdin=models.Stdin(**result_dict["test_case"]["stdin"]),
                    stdout=models.Stdout(**result_dict["test_case"]["stdout"])
                )
                
                # メタデータ情報を復元
                metadata = None
                if "metadata" in result_dict:
                    metadata = models.JudgeResultMetadata(**result_dict["metadata"])
                
                # 結果オブジェクトを作成
                judge_result = models.JudgeResult(
                    id=result_dict["id"],
                    problem=problem,
                    test_case=testcase,
                    status=result_dict["status"],
                    metadata=metadata
                )
                
                results.append(judge_result)
            
            # レスポンスモデルを作成
            response = models.JudgeResponse(
                id=f"judge_{problem_id}",
                problem=problem,
                results=results,
                code=judge_data.get("code", "")
            )
            
            # 提出ログとユーザーステータスを更新
            result_info = self._update_logs_and_status(response, user_id, problem_set)
            
            self.logger.info(f"提出結果保存成功: ジャッジID={judge_id}, ユーザーID={user_id}, 提出ID={result_info.get('submission_id')}")
            return result_info
        
        except Exception as e:
            self.logger.error(f"提出結果保存エラー: ジャッジID={judge_id}, エラー={str(e)}")
            return {"status": "error", "message": f"提出記録の保存に失敗しました: {str(e)}"}
    
    def _update_logs_and_status(self, response: models.JudgeResponse, 
                              user_id: str, problem_set: str) -> Dict[str, Any]:
        """
        提出ログとユーザーステータスを更新する
        
        Args:
            response: ジャッジレスポンス
            user_id: ユーザーID
            problem_set: 問題セット
            
        Returns:
            更新結果情報
        """
        # 提出ログを保存
        submission_log = self.submission_logger.save_submission(response, problem_set)
        
        # ユーザーの解決状態を更新（ユーザーIDが変わる可能性があるのでここで初期化）
        if not self.user_status_manager or self.user_status_manager.user_id != user_id:
            self.user_status_manager = UserStatusManager(user_id)
        problem_status = self.user_status_manager.update_problem_status(response, submission_log.id, problem_set)
        
        # 結果にsubmission_idと解決状態を追加
        result_info = {
            "submission_id": submission_log.id,
            "status": "success",
        }
        
        # problem_statusのdatetimeを文字列に変換
        if problem_status:
            problem_status_dict = problem_status.model_dump(mode='json')
            if problem_status_dict.get("solved_at"):
                # 既にisoformatされている場合は再変換しない
                if not isinstance(problem_status_dict["solved_at"], str):
                    problem_status_dict["solved_at"] = problem_status.solved_at.isoformat() if problem_status.solved_at else None
            result_info["problem_status"] = problem_status_dict
            
        return result_info