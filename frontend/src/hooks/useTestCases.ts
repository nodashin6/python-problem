import { useState, useCallback } from 'react';
import { fetchJudgeCases } from '@/lib/api';
import { TestResult } from '@/components/problem/TestResultCard';
import type { JudgeResult } from '@/types/judge';

/**
 * JudgeResultをTestResultに変換するアダプタ関数
 */
export const convertToTestResult = (judgeResult: JudgeResult): TestResult => {
  return {
    id: judgeResult.id,
    status: judgeResult.status,
    judge_case: {
      id: judgeResult.judge_case.id,
      name: judgeResult.judge_case.name,
      stdin: {
        content: judgeResult.judge_case.stdin.content
      },
      stdout: {
        content: judgeResult.judge_case.stdout.content 
      }
    },
    metadata: {
      output: judgeResult.metadata.output ?? undefined,
      runtime_error: judgeResult.metadata.runtime_error ?? undefined,
      compile_error: judgeResult.metadata.compile_error ?? undefined,
      time_used: judgeResult.metadata.time_used ?? undefined
    }
  };
};

/**
 * テストケース管理用カスタムフック
 */
export const useJudgeCases = (problemId: string) => {
  const [availableJudgeCases, setAvailableJudgeCases] = useState<string[]>([]);
  const [isLoadingJudgeCases, setIsLoadingJudgeCases] = useState(false);
  const [selectedJudgeCase, setSelectedJudgeCase] = useState<TestResult | null>(null);

  // テストケース選択ハンドラー
  const handleJudgeCaseSelect = useCallback((JudgeCase: TestResult) => {
    setSelectedJudgeCase(prev => prev?.id === JudgeCase.id ? null : JudgeCase);
  }, []);
  
  // テストケースをロードする - 必要なときだけ呼び出す
  const loadJudgeCases = useCallback(async () => {
    if (!problemId || isLoadingJudgeCases) return;
    
    setIsLoadingJudgeCases(true);
    try {
      const JudgeCases = await fetchJudgeCases(problemId);
      setAvailableJudgeCases(JudgeCases);
      console.log('📌 テストケース一覧を取得しました:', JudgeCases);
    } catch (error) {
      console.error('テストケース一覧の取得に失敗しました', error);
    } finally {
      setIsLoadingJudgeCases(false);
    }
  }, [problemId, isLoadingJudgeCases]);

  return {
    availableJudgeCases,
    isLoadingJudgeCases,
    selectedJudgeCase,
    setSelectedJudgeCase,
    handleJudgeCaseSelect,
    loadJudgeCases
  };
};
