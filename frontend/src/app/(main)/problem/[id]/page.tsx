'use client';

import { useEffect, useRef, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';

// カスタムフック
import { useProblem } from '@/hooks/useProblem';
import { useSubmission } from '@/hooks/useSubmission';
import { useJudgeCases, convertToTestResult } from '@/hooks/useJudgeCases';

// コンポーネント
import { ProblemCard } from '@/components/problem/ProblemCard';
import { CodeSubmissionForm } from '@/components/problem/CodeSubmissionForm';
import { JudgeResultSection } from '@/components/problem/JudgeResultSection';

export default function ProblemPage() {
  const params = useParams();
  const problemId = params.id as string;
  
  // トースト通知済みのジャッジIDを追跡するためのRef
  const notifiedJudgeIdsRef = useRef<Set<string>>(new Set());
  
  // カスタムフックで状態管理
  const { problem, loading, title } = useProblem(problemId);
  const { 
    isSubmitting: submitting, 
    judgeId, 
    error: submitError, 
    submit, 
    result, 
    judgeStatus, 
    isPolling, 
    code, 
    setCode 
  } = useSubmission(problemId);
  
  const {
    availableJudgeCases,
    selectedJudgeCase,
    handleJudgeCaseSelect,
    loadJudgeCases
  } = useJudgeCases(problemId);

  // TestResult型に変換された結果
  const testResults = result?.results ? result.results.map(convertToTestResult) : undefined;

  // 進行中のテストケース情報と完了したテストケースIDの取得
  const pendingJudgeCaseIds = judgeStatus?.progress?.testcases 
    ? Object.keys(judgeStatus.progress.testcases) 
    : [];
  
  // 結果が返ってきた場合は結果からテストケースIDを取得
  const completedJudgeCaseIds = testResults ? testResults.map(r => r.judge_case.id) : [];
  
  // テストケースリスト管理
  const [activeJudgeCaseIds, setActiveJudgeCaseIds] = useState<string[]>([]);
  
  // テストケースリストを更新
  useEffect(() => {
    // ジャッジ実行中か結果がある場合は、完了 or 進行中のテストケースを表示
    if (submitting || isPolling || result) {
      const newJudgeCaseIds = completedJudgeCaseIds.length > 0 
        ? completedJudgeCaseIds 
        : pendingJudgeCaseIds;
      
      if (newJudgeCaseIds.length > 0) {
        setActiveJudgeCaseIds(newJudgeCaseIds);
      }
    }
  }, [submitting, isPolling, result, completedJudgeCaseIds, pendingJudgeCaseIds]);

  // テスト結果表示フラグ
  const showJudgeCases = submitting || isPolling || result !== null;
  
  // トースト通知の処理 - 一度だけ表示
  useEffect(() => {
    if (!result?.results || !judgeId || notifiedJudgeIdsRef.current.has(judgeId)) return;
    
    notifiedJudgeIdsRef.current.add(judgeId);
    
    setTimeout(() => {
      const passCount = result.results.filter(r => r.status === 'AC').length || 0;
      const totalCount = result.results.length || 0;
      
      if (passCount === totalCount && totalCount > 0) {
        toast.success(`正解数: ${passCount}/${totalCount} `, { 
          duration: 5000, icon: '🎉' 
        });
      } else if (passCount > 0) {
        toast(`正解数: ${passCount}/${totalCount}`, { icon: '📊' });
      } else if (totalCount > 0) {
        toast.error(`正解数: 0/${totalCount}`, { icon: '💪' });
      }
    }, 100);
  }, [result, judgeId]);

  // 問題解決の通知とステート更新
  useEffect(() => {
    if (!result?.problem_status?.solved || !problem || problem.solved) return;
      
    setTimeout(() => {
      toast.success('🏆 この問題を初めて解けました！おめでとう！', {
        duration: 5000,
        icon: '🏆'
      });
    }, 600);
  }, [result, problem]);

  // フォーム送信処理
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!code.trim()) {
      toast.error('コードを入力してください');
      return;
    }
    
    // 送信時にテストケースを取得 (初回のみ) 
    if (availableJudgeCases.length === 0 && activeJudgeCaseIds.length === 0) {
      await loadJudgeCases();
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
      <div className="flex flex-col gap-6">
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
          <div className="card-modern">
            <div className="card-header">
              <h2 className="text-2xl font-bold text-white flex items-center">
                <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                </svg>
                解答
              </h2>
            </div>
            <div className="p-4">
              <CodeSubmissionForm 
                code={code} 
                onCodeChange={setCode}
                onSubmit={handleSubmit} 
                submitting={submitting || isPolling} 
              />
            </div>
          </div>

          {/* テストケース実行結果 - 統合されたUIコンポーネント */}
          <JudgeResultSection
            isVisible={showJudgeCases}
            JudgeCaseList={activeJudgeCaseIds.length > 0 ? activeJudgeCaseIds : availableJudgeCases}
            judgeStatus={judgeStatus}
            submitting={submitting}
            isPolling={isPolling}
            testResults={testResults as never}
            result={result}
            selectedJudgeCase={selectedJudgeCase as never}
            handleJudgeCaseSelect={handleJudgeCaseSelect as never}
            onLoadJudgeCases={loadJudgeCases}
          />
        </div>
      </div>
    </motion.div>
  );
}