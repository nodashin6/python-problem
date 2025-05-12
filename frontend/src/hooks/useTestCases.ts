import { useState, useCallback } from 'react';
import { fetchTestCases } from '@/lib/api';
import { TestResult } from '@/components/problem/TestResultCard';
import type { JudgeResult } from '@/types/judge';

/**
 * JudgeResultをTestResultに変換するアダプタ関数
 */
export const convertToTestResult = (judgeResult: JudgeResult): TestResult => {
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
export const useTestCases = (problemId: string) => {
  const [availableTestCases, setAvailableTestCases] = useState<string[]>([]);
  const [isLoadingTestCases, setIsLoadingTestCases] = useState(false);
  const [selectedTestCase, setSelectedTestCase] = useState<TestResult | null>(null);

  // テストケース選択ハンドラー
  const handleTestCaseSelect = useCallback((testCase: TestResult) => {
    setSelectedTestCase(prev => prev?.id === testCase.id ? null : testCase);
  }, []);
  
  // テストケースをロードする - 必要なときだけ呼び出す
  const loadTestCases = useCallback(async () => {
    if (!problemId || isLoadingTestCases) return;
    
    setIsLoadingTestCases(true);
    try {
      const testCases = await fetchTestCases(problemId);
      setAvailableTestCases(testCases);
      console.log('📌 テストケース一覧を取得しました:', testCases);
    } catch (error) {
      console.error('テストケース一覧の取得に失敗しました', error);
    } finally {
      setIsLoadingTestCases(false);
    }
  }, [problemId, isLoadingTestCases]);

  return {
    availableTestCases,
    isLoadingTestCases,
    selectedTestCase,
    setSelectedTestCase,
    handleTestCaseSelect,
    loadTestCases
  };
};
