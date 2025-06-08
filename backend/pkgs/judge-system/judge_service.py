import logging
import traceback
import uuid
from datetime import datetime
from typing import Any

from src.const import DEFAULT_PROBLEM_SET
from src.domain import models
from src.infra.repositories.judge_repository import JudgeResultRepository
from src.usecase.judge_use_case import (
    JudgeCaseLoader,
    JudgeUserCode,
)
from src.usecase.submission_log import SubmissionLogger
from src.usecase.user_status import UserStatusManager


class JudgeResultStatus:
    """ジャッジ結果のステータス定数"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"
    NOT_FOUND = "not_found"


class JudgeTestStatus:
    """テストケース結果のステータス定数"""

    ACCEPTED = "AC"  # 正解
    WRONG_ANSWER = "WA"  # 不正解
    RUNTIME_ERROR = "RE"  # 実行時エラー
    TIME_LIMIT_EXCEEDED = "TLE"  # 時間超過
    MEMORY_LIMIT_EXCEEDED = "MLE"  # メモリ超過
    COMPILATION_ERROR = "CE"  # コンパイルエラー
    INTERNAL_ERROR = "IE"  # 内部エラー


class JudgeService:
    """
    ジャッジのワークフローを管理するサービス
    """

    def __init__(self, repository: JudgeResultRepository | None = None):
        """
        Args:
            repository: ジャッジ結果を保存するリポジトリ。省略時は標準のものを使用
        """
        self.repository = repository or JudgeResultRepository()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.judge_executor = JudgeUserCode()
        self.submission_logger = SubmissionLogger()
        self.user_status_manager = None  # ユーザーIDに基づいて後で初期化

    def start_judge(
        self, problem_id: str, code: str, problem_set: str = DEFAULT_PROBLEM_SET
    ) -> str:
        """
        ジャッジプロセスを開始する

        Args:
            problem_id: 問題ID
            code: ユーザーのコード
            problem_set: 問題セット

        Returns:
            生成されたジャッジID

        Raises:
            Exception: ジャッジ開始中にエラーが発生した場合
        """
        # ユニークなジャッジIDを生成
        judge_id = str(uuid.uuid4())

        try:
            # 初期状態を保存
            self.repository.save(
                judge_id,
                {
                    "status": JudgeResultStatus.RUNNING,
                    "problem_id": problem_id,
                    "problem_set": problem_set,
                    "code": code,
                    "results": [],
                    "created_at": datetime.now().isoformat(),
                },
            )

            self.logger.info(
                f"ジャッジ開始: ID={judge_id}, 問題ID={problem_id}, 問題セット={problem_set}"
            )
            return judge_id

        except Exception as e:
            self.logger.error(f"ジャッジ開始エラー: {e!s}")
            self.logger.debug(traceback.format_exc())
            raise

    def process_judge_results(
        self,
        judge_id: str,
        problem_id: str,
        code: str,
        problem_set: str = DEFAULT_PROBLEM_SET,
    ) -> None:
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
            case_loader = JudgeCaseLoader(problem, problem_set)
            case_names = case_loader.load_judge_case_names()
            total_cases = len(case_names)
            processed_cases = 0

            results = []
            overall_status = JudgeTestStatus.ACCEPTED  # 初期値は成功
            max_execution_time_ms = 0
            max_memory_usage_kb = 0

            # 各テストケースを処理
            for judge_case in case_loader:
                # テストケース処理中の状態を報告
                progress_status = {
                    "status": JudgeResultStatus.RUNNING,
                    "current": processed_cases + 1,
                    "total": total_cases,
                    "case_id": judge_case.id,
                }
                self.repository.update(judge_id, progress_status)

                # 単一テストケースを実行
                result = self.judge_executor.judge_case(code, judge_case)

                # ステータスを決定
                status = self.judge_executor.determine_status(result)

                # 最悪のステータスを全体のステータスとして採用する
                # 優先度: CE > MLE > TLE > RE > WA > AC
                if status == JudgeTestStatus.COMPILATION_ERROR:
                    overall_status = JudgeTestStatus.COMPILATION_ERROR
                elif (
                    status == JudgeTestStatus.MEMORY_LIMIT_EXCEEDED
                    and overall_status != JudgeTestStatus.COMPILATION_ERROR
                ):
                    overall_status = JudgeTestStatus.MEMORY_LIMIT_EXCEEDED
                elif (
                    status == JudgeTestStatus.TIME_LIMIT_EXCEEDED
                    and overall_status
                    not in [
                        JudgeTestStatus.COMPILATION_ERROR,
                        JudgeTestStatus.MEMORY_LIMIT_EXCEEDED,
                    ]
                ):
                    overall_status = JudgeTestStatus.TIME_LIMIT_EXCEEDED
                elif status == JudgeTestStatus.RUNTIME_ERROR and overall_status not in [
                    JudgeTestStatus.COMPILATION_ERROR,
                    JudgeTestStatus.MEMORY_LIMIT_EXCEEDED,
                    JudgeTestStatus.TIME_LIMIT_EXCEEDED,
                ]:
                    overall_status = JudgeTestStatus.RUNTIME_ERROR
                elif (
                    status == JudgeTestStatus.WRONG_ANSWER
                    and overall_status == JudgeTestStatus.ACCEPTED
                ):
                    overall_status = JudgeTestStatus.WRONG_ANSWER

                # パフォーマンス指標を更新
                if (
                    result.metadata.time_used_ms is not None
                    and result.metadata.time_used_ms > max_execution_time_ms
                ):
                    max_execution_time_ms = result.metadata.time_used_ms

                if (
                    result.metadata.memory_used_kb is not None
                    and result.metadata.memory_used_kb > max_memory_usage_kb
                ):
                    max_memory_usage_kb = result.metadata.memory_used_kb

                # 結果オブジェクトを作成
                case_result = models.JudgeCaseResult(
                    id=str(uuid.uuid4()),
                    judge_process_id=judge_id,
                    judge_case_id=judge_case.id,
                    status=status,
                    result=status,
                    processing_time_ms=result.metadata.time_used_ms,
                    memory_usage_kb=result.metadata.memory_used_kb,
                    error=result.metadata.runtime_error
                    or result.metadata.compile_error,
                    warning=None,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    judge_case=judge_case,
                    metadata=models.JudgeCaseResultMetadata(
                        memory_used_kb=result.metadata.memory_used_kb,
                        time_used_ms=result.metadata.time_used_ms,
                        compile_error=result.metadata.compile_error,
                        runtime_error=result.metadata.runtime_error,
                        output=result.metadata.output,
                    ),
                )

                results.append(case_result)
                processed_cases += 1

                # テストケース処理完了の状態を報告
                completion_status = {
                    "status": "case_completed",
                    "current": processed_cases,
                    "total": total_cases,
                    "case_id": judge_case.id,
                    "test_result": {
                        "status": status,
                        "time_used_ms": result.metadata.time_used_ms,
                        "memory_used_kb": result.metadata.memory_used_kb,
                    },
                }
                self.repository.update(judge_id, completion_status)

                # コンパイルエラーなら、残りのテストケースは実行しない
                if status == JudgeTestStatus.COMPILATION_ERROR:
                    break

            # 結果を保存
            result_dicts = [result.model_dump(mode="json") for result in results]

            # ジャッジプロセス全体の結果を更新
            judge_process_result = {
                "status": JudgeResultStatus.COMPLETED,
                "problem_id": problem_id,
                "problem_set": problem_set,
                "code": code,
                "results": result_dicts,
                "execution_time_ms": max_execution_time_ms,
                "memory_usage_kb": max_memory_usage_kb,
                "overall_status": overall_status,
                "completed_at": datetime.now().isoformat(),
            }

            self.repository.save(judge_id, judge_process_result)
            self.logger.info(
                f"ジャッジ完了: ID={judge_id}, 問題ID={problem_id}, 結果={overall_status}"
            )

        except Exception as e:
            self.logger.error(f"ジャッジ処理エラー: ID={judge_id}, エラー={e!s}")
            self.logger.debug(traceback.format_exc())
            # エラー状態を保存
            self.repository.save(
                judge_id,
                {
                    "status": JudgeResultStatus.ERROR,
                    "problem_id": problem_id,
                    "problem_set": problem_set,
                    "error_message": str(e),
                    "error_traceback": traceback.format_exc(),
                    "completed_at": datetime.now().isoformat(),
                },
            )
        finally:
            # 完了状態を記録
            self.repository.finalize(judge_id)

    def get_judge_status(self, judge_id: str) -> dict[str, Any]:
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
            return {
                "status": JudgeResultStatus.NOT_FOUND,
                "message": f"ジャッジID {judge_id} が見つかりません",
            }

        return result

    def save_submission_result(
        self, judge_id: str, user_id: str, problem_set: str = DEFAULT_PROBLEM_SET
    ) -> dict[str, Any]:
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

        if judge_data["status"] != JudgeResultStatus.COMPLETED:
            self.logger.warning(
                f"ジャッジID {judge_id} が完了していません: {judge_data['status']}"
            )
            return {"status": "error", "message": "ジャッジが完了していません"}

        try:
            # 結果からレスポンスモデルを構築
            problem_id = judge_data.get("problem_id")
            problem = models.Problem(
                id=problem_id,
                title="",
                description="",
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )

            results = self._build_judge_case_results(judge_data, problem)

            # ジャッジプロセスを作成
            judge_process = models.JudgeProcess(
                id=judge_id,
                submission_id=judge_id,  # 仮のIDを設定
                status=self._map_status_to_enum(
                    judge_data.get("overall_status", "completed")
                ),
                result=judge_data.get("overall_status"),
                execution_time_ms=judge_data.get("execution_time_ms"),
                memory_usage_kb=judge_data.get("memory_usage_kb"),
                created_at=datetime.fromisoformat(
                    judge_data.get("created_at", datetime.now().isoformat())
                ),
                updated_at=datetime.fromisoformat(
                    judge_data.get("completed_at", datetime.now().isoformat())
                ),
                results=results,
            )

            # 提出ログとユーザーステータスを更新
            result_info = self._update_logs_and_status(
                judge_process, user_id, problem_set
            )

            self.logger.info(
                f"提出結果保存成功: ジャッジID={judge_id}, ユーザーID={user_id}, 提出ID={result_info.get('submission_id')}"
            )
            return result_info

        except Exception as e:
            self.logger.error(
                f"提出結果保存エラー: ジャッジID={judge_id}, エラー={e!s}"
            )
            self.logger.debug(traceback.format_exc())
            return {
                "status": "error",
                "message": f"提出記録の保存に失敗しました: {e!s}",
            }

    def _map_status_to_enum(self, status: str) -> models.JudgeStatus:
        """文字列のステータスをJudgeStatusに変換する"""
        status_mapping = {
            "pending": models.JudgeStatus.PENDING,
            "running": models.JudgeStatus.RUNNING,
            "completed": models.JudgeStatus.SUCCEEDED,
            "succeeded": models.JudgeStatus.SUCCEEDED,
            "failed": models.JudgeStatus.FAILED,
            "error": models.JudgeStatus.ERROR,
            JudgeTestStatus.ACCEPTED: models.JudgeStatus.SUCCEEDED,
            JudgeTestStatus.WRONG_ANSWER: models.JudgeStatus.FAILED,
            JudgeTestStatus.RUNTIME_ERROR: models.JudgeStatus.FAILED,
            JudgeTestStatus.TIME_LIMIT_EXCEEDED: models.JudgeStatus.FAILED,
            JudgeTestStatus.MEMORY_LIMIT_EXCEEDED: models.JudgeStatus.FAILED,
            JudgeTestStatus.COMPILATION_ERROR: models.JudgeStatus.FAILED,
            JudgeTestStatus.INTERNAL_ERROR: models.JudgeStatus.ERROR,
        }
        return status_mapping.get(status.lower(), models.JudgeStatus.OTHER)

    def _build_judge_case_results(
        self, judge_data: dict[str, Any], problem: models.Problem
    ) -> list[models.JudgeCaseResult]:
        """ジャッジケース結果オブジェクトのリストを構築"""
        results = []
        for result_dict in judge_data.get("results", []):
            # テストケース情報がない場合はスキップ
            if "judge_case" not in result_dict and "judge_case_id" not in result_dict:
                continue

            # テストケース情報を復元
            if "judge_case" in result_dict:
                judge_case = models.JudgeCase(
                    id=result_dict["judge_case"]["id"],
                    problem_id=problem.id,
                    input_id=result_dict.get("input_id", str(uuid.uuid4())),
                    output_id=result_dict.get("output_id", str(uuid.uuid4())),
                    is_sample=result_dict.get("is_sample", False),
                    display_order=int(result_dict.get("display_order", 0)),
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    problem=problem,
                )
            else:
                # judge_case_idだけ存在する場合は最小限の情報でオブジェクトを作成
                judge_case = models.JudgeCase(
                    id=result_dict["judge_case_id"],
                    problem_id=problem.id,
                    input_id=str(uuid.uuid4()),
                    output_id=str(uuid.uuid4()),
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    problem=problem,
                )

            # メタデータ情報を復元
            metadata = None
            if "metadata" in result_dict:
                metadata = models.JudgeCaseResultMetadata(
                    memory_used_kb=result_dict["metadata"].get("memory_used_kb"),
                    time_used_ms=result_dict["metadata"].get("time_used_ms"),
                    compile_error=result_dict["metadata"].get("compile_error"),
                    runtime_error=result_dict["metadata"].get("runtime_error"),
                    output=result_dict["metadata"].get("output"),
                )

            # 結果オブジェクトを作成
            judge_result = models.JudgeCaseResult(
                id=result_dict.get("id", str(uuid.uuid4())),
                judge_process_id=judge_data.get("id", str(uuid.uuid4())),
                judge_case_id=judge_case.id,
                status=result_dict["status"],
                result=result_dict.get("result", result_dict["status"]),
                error=result_dict.get("error"),
                warning=result_dict.get("warning"),
                processing_time_ms=result_dict.get("processing_time_ms"),
                memory_usage_kb=result_dict.get("memory_usage_kb"),
                created_at=datetime.now(),
                updated_at=datetime.now(),
                judge_case=judge_case,
                metadata=metadata,
            )

            results.append(judge_result)

        return results

    def _update_logs_and_status(
        self, judge_process: models.JudgeProcess, user_id: str, problem_set: str
    ) -> dict[str, Any]:
        """
        提出ログとユーザーステータスを更新する

        Args:
            judge_process: ジャッジプロセス
            user_id: ユーザーID
            problem_set: 問題セット

        Returns:
            更新結果情報
        """
        # 提出ログを保存
        submission_log = self.submission_logger.save_submission(
            judge_process, problem_set
        )

        # ユーザーの解決状態を更新 (ユーザーIDが変わる場合は初期化)
        if not self.user_status_manager or self.user_status_manager.user_id != user_id:
            self.user_status_manager = UserStatusManager(user_id)

        problem_status = self.user_status_manager.update_problem_status(
            judge_process, submission_log.id, problem_set
        )

        # 結果に提出IDと解決状態を追加
        result_info = {
            "submission_id": submission_log.id,
            "status": "success",
            "execution_time_ms": judge_process.execution_time_ms,
            "memory_usage_kb": judge_process.memory_usage_kb,
            "overall_result": judge_process.result,
        }

        # problem_statusのdatetimeを文字列に変換
        if problem_status:
            problem_status_dict = problem_status.model_dump(mode="json")
            result_info["problem_status"] = problem_status_dict

        return result_info
