'use client';

import { useEffect, useState, useRef, useCallback } from 'react';
import { useParams } from 'next/navigation';
import { fetchProblemById, judgeCode, fetchJudgeStatus, Problem, extractTitle, JudgeStatus } from '@/lib/api';
import Link from 'next/link';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';

// コンポーネントをインポート
import { ProblemCard } from '@/components/problem/ProblemCard';
import { CodeSubmissionForm } from '@/components/problem/CodeSubmissionForm';
import { TestResults } from '@/components/problem/TestResults';
import { TestResult } from '@/components/problem/TestResultCard';
import { TestCaseTable } from '@/components/problem/TestCaseTable';
import type { JudgeResponse, JudgeResult } from '@/types/judge';

// JudgeResultをTestResultに変換するアダプタ関数
const convertToTestResult = (judgeResult: JudgeResult): TestResult => {
  return {
    id: judgeResult.id,
    status: judgeResult.status,
    test_case: {
      id: judgeResult.test_case.id,
      name: judgeResult.test_case.name,
      stdin: {
        content: judgeResult.test_case.stdin.content
      },
      stdout: {
        content: judgeResult.test_case.stdout.content 
      }
    },
    metadata: {
      output: judgeResult.metadata.output ?? undefined,  // nullをundefinedに変換
      runtime_error: judgeResult.metadata.runtime_error ?? undefined,
      compile_error: judgeResult.metadata.compile_error ?? undefined,
      time_used: judgeResult.metadata.time_used ?? undefined
    }
  };
};

const useSubmission = (problemId: string) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [judgeId, setJudgeId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const submit = async (code: string) => {
    if (!code.trim()) {
      setError('コードを入力してください');
      return null;
    }
    
    try {
      setIsSubmitting(true);
      setError(null);

      // ジャッジリクエストを送信して、ジャッジIDを取得
      const response = await judgeCode(problemId, code);
      setJudgeId(response.judge_id);
      return response.judge_id;
    } catch (err) {
      console.error('ジャッジリクエストに失敗しました', err);
      setError('ジャッジリクエストの送信に失敗しました');
      return null;
    }
    // finallyブロックを削除（リセットはuseResultの完了時に行う）
  };

  // 提出状態をリセットするメソッドを追加
  const resetSubmitting = useCallback(() => {
    setIsSubmitting(false);
    console.log('📌 提出状態をリセットしました');
  }, []);

  return { isSubmitting, judgeId, error, submit, resetSubmitting };
};

const useResult = (judgeId: string | null, code: string, problemId: string, onComplete?: () => void) => {
  const [result, setResult] = useState<JudgeResponse | null>(null);
  const [status, setStatus] = useState<JudgeStatus | null>(null);
  const [isPolling, setIsPolling] = useState(false);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const isFetchingRef = useRef<boolean>(false);
  const fetchErrorCountRef = useRef<number>(0);
  const MAX_RETRY_COUNT = 5;
  const POLLING_INTERVAL = 2000;
  const resultReceivedRef = useRef<boolean>(false);
  const processedJudgeIdsRef = useRef<Set<string>>(new Set());

  // ジャッジの状態を取得する
  const fetchStatus = useCallback(async () => {
    if (!judgeId || isFetchingRef.current || resultReceivedRef.current) return;
    
    try {
      isFetchingRef.current = true;
      const status = await fetchJudgeStatus(judgeId);
      setStatus(status);
      
      // 完了またはエラーの場合
      if (status.status === 'completed' || status.status === 'error') {
        // ポーリングを停止
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
        
        setIsPolling(false);
        resultReceivedRef.current = true;
        // このジャッジIDを処理済みとしてマーク
        processedJudgeIdsRef.current.add(judgeId);
        
        // 結果が含まれている場合、結果を設定
        if (status.results) {
          setResult(status.results);
        } else if (status.error) {
          setResult({ 
            id: 'error', 
            problem: { id: problemId }, 
            code: code, 
            results: [],
            error: status.error
          });
        }
        
        // 完了コールバックを実行
        onComplete?.();
        console.log('📌 ジャッジ完了: ポーリングを停止しました', judgeId);
      }
      
      // エラーカウントをリセット
      fetchErrorCountRef.current = 0;
    } catch (error) {
      console.error('ジャッジ状態の取得に失敗しました', error);
      
      // エラーカウントを増やす
      fetchErrorCountRef.current += 1;
      
      // エラー回数が閾値を超えたらポーリング停止
      if (fetchErrorCountRef.current >= MAX_RETRY_COUNT) {
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
        
        setIsPolling(false);
        resultReceivedRef.current = true;
        // このジャッジIDを処理済みとしてマーク
        processedJudgeIdsRef.current.add(judgeId);
        
        setResult({ 
          id: 'error', 
          problem: { id: problemId }, 
          code: code, 
          results: [],
          error: `リクエスト失敗が${MAX_RETRY_COUNT}回連続しました。処理を中止します。`
        });
        
        onComplete?.();
        console.log('📌 エラー上限到達: ポーリングを停止しました', judgeId);
      }
    } finally {
      isFetchingRef.current = false;
    }
  }, [judgeId, code, problemId, onComplete]);

  // judgeIdが変更されたらポーリングを開始
  useEffect(() => {
    // judgeIdがnullか、すでに処理済みのIDならポーリングしない
    if (!judgeId || processedJudgeIdsRef.current.has(judgeId)) {
      console.log('📌 ポーリングスキップ: ID既処理済み =', judgeId);
      return;
    }
    
    // 既存のポーリングを停止
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    
    // 状態をリセット
    setIsPolling(true);
    setResult(null);
    fetchErrorCountRef.current = 0;
    isFetchingRef.current = false;
    resultReceivedRef.current = false;
    
    // 初回実行
    fetchStatus();
    
    // 定期的にポーリングを実行
    intervalRef.current = setInterval(fetchStatus, POLLING_INTERVAL);
    console.log('📌 ポーリング開始: ID =', judgeId);
    
    // クリーンアップ関数
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
        console.log('📌 クリーンアップ: ポーリングを停止しました', judgeId);
      }
      setIsPolling(false);
    };
  }, [judgeId, fetchStatus]);

  return { result, status, isPolling };
};

// useTestCasesフックを追加して、テストケース関連の処理を分離
const useTestCases = (problemId: string) => {
  const [testCaseList, setTestCaseList] = useState<string[]>([]);

  const fetchTestCases = async () => {
    try {
      const response = await fetch(`http://localhost:8901/api/v1/testcases/${problemId}`);
      if (response.ok) {
        const testcases = await response.json();
        setTestCaseList(testcases);
      } else {
        // APIがなければ推測
        const dummyTestcases = Array.from({ length: 3 }, (_, i) => 
          `${String(i + 1).padStart(2, '0')}`
        );
        setTestCaseList(dummyTestcases);
      }
    } catch (e) {
      // APIがエラーになれば推測
      const dummyTestcases = Array.from({ length: 3 }, (_, i) => 
        `${String(i + 1).padStart(2, '0')}`
      );
      setTestCaseList(dummyTestcases);
    }
  };

  useEffect(() => {
    fetchTestCases();
  }, [problemId]);

  return { testCaseList, fetchTestCases };
};

// ポーリング間隔を定数として定義（既存の定数は削除）
const POLLING_INTERVAL = 2000;

export default function ProblemPage() {
  const params = useParams();
  const problemId = params.id as string;
  
  const [problem, setProblem] = useState<Problem | null>(null);
  const [loading, setLoading] = useState(true);
  const [code, setCode] = useState('');

  // テストケース管理用カスタムフック
  const { testCaseList } = useTestCases(problemId);
  
  // 提出管理用カスタムフック
  const { isSubmitting: submitting, judgeId, error: submitError, submit, resetSubmitting } = useSubmission(problemId);
  
  // 結果管理用カスタムフック
  const { result, status: judgeStatus, isPolling } = useResult(judgeId, code, problemId, () => {
    // ロードトーストを終了
    toast.dismiss('judge-status');
    
    // 提出状態をリセット (これが重要なポイント！)
    resetSubmitting();
    
    setTimeout(() => {
      // 結果に基づくサマリー通知
      if (result?.results) {
        const passCount = result.results.filter(r => r.status === 'AC').length || 0;
        const totalCount = result.results.length || 0;
        
        if (passCount === totalCount && totalCount > 0) {
          // 全問正解
          toast.success(`🎉 全テストケース ${passCount}/${totalCount} に正解しました！`, {
            duration: 5000,
            icon: '🎉'
          });
        } else if (passCount > 0) {
          // 一部正解
          toast(`${passCount}/${totalCount} のテストケースに正解しました`, {
            icon: '📊'
          });
        } else if (totalCount > 0) {
          // 全問不正解
          toast.error(`0/${totalCount} のテストケースが不合格でした`, {
            icon: '💪'
          });
        }
        
        // 問題が解けたとき
        if (result.problem_status?.solved && problem && !problem.solved) {
          setTimeout(() => {
            toast.success('🏆 この問題を初めて解けました！おめでとう！', {
              duration: 5000,
              icon: '🏆'
            });
          }, 500);
          
          // 問題ステータスの更新
          setProblem({
            ...problem,
            solved: result.problem_status.solved,
            solved_at: result.problem_status.solved_at,
            submission_count: result.problem_status.submission_count
          });
        }
      }
    }, 100); // 少し遅延させてtoast.dismissの後に表示
  });

  // TestResult型に変換された結果
  const testResults = result?.results ? result.results.map(convertToTestResult) : undefined;

  // 問題読み込み
  useEffect(() => {
    async function loadProblem() {
      try {
        const data = await fetchProblemById(problemId);
        setProblem(data);
      } catch (error) {
        console.error('問題の取得に失敗しました', error);
      } finally {
        setLoading(false);
      }
    }

    loadProblem();
  }, [problemId]);

  // フォーム送信処理
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!code.trim()) {
      toast.error('コードを入力してください');
      return;
    }
    
    toast.loading('ジャッジを開始します...', { id: 'judge-status' });
    
    // コード提出
    const newJudgeId = await submit(code);
    
    if (newJudgeId) {
      toast.loading('ジャッジ実行中...', { id: 'judge-status' });
    } else {
      toast.error(submitError || 'ジャッジリクエストの送信に失敗しました', { id: 'judge-status' });
    }
  };

  // 読み込み中表示
  if (loading) {
    return (
      <div className="min-h-screen p-4 bg-gray-50 flex flex-col items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-gray-900"></div>
        <p className="mt-4 text-gray-700">問題を読み込み中...</p>
      </div>
    );
  }

  // 問題が見つからない場合
  if (!problem) {
    return (
      <div className="min-h-screen p-4 bg-gray-50 flex flex-col items-center justify-center">
        <h1 className="text-2xl font-bold text-red-600">問題が見つかりませんでした</h1>
        <p className="mt-2 text-gray-700">指定された問題ID「{problemId}」は存在しないか、アクセス権限がありません。</p>
        <Link href="/problem/list" className="mt-6 text-blue-500 hover:underline">
          問題一覧へ戻る
        </Link>
      </div>
    );
  }

  // タイトルをマークダウンから取得するか、titleがあればそれを使用
  const title = problem?.title || 
    (problem?.markdown ? extractTitle(problem.markdown) : `問題 ${problemId}`);

  // メインのUI
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="container mx-auto p-4 max-w-7xl"
    >
      {/* 問題一覧へのリンク */}
      <div className="mb-4">
        <Link href="/problem/list" className="text-blue-500 hover:underline inline-flex items-center">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          問題一覧へ戻る
        </Link>
      </div>

      {/* 問題と提出フォームのグリッドレイアウト */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 左側：問題文 */}
        <div>
          <ProblemCard
            title={title} 
            markdownContent={problem.markdown} 
            level={problem.level}
            solved={problem.solved}
            submission_count={problem.submission_count}
          />
        </div>

        {/* 右側：コードエディタと提出ボタン */}
        <div className="flex flex-col">
          <h2 className="text-xl font-semibold mb-4">解答を提出</h2>
          
          <CodeSubmissionForm 
            code={code} 
            onCodeChange={setCode}
            onSubmit={handleSubmit} 
            submitting={submitting || isPolling} 
          />

          {/* テストケースの表示 */}
          {testCaseList.length > 0 && (
            <div className="mt-6">
              <h3 className="text-lg font-semibold mb-2">テストケース実行状況</h3>
              <TestCaseTable 
                testCaseList={testCaseList} 
                judgeStatus={judgeStatus} 
                submitting={submitting || isPolling}
                allResults={testResults}
              />
            </div>
          )}
          
          {/* テスト結果の表示 */}
          {result && (
            <div className="mt-6">
              <h3 className="text-lg font-semibold mb-2">テスト結果</h3>
              <TestResults 
                results={testResults || []} 
                error={result.error} 
              />
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}