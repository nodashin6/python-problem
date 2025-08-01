import { useState, useCallback } from 'react';

export interface JudgeCase {
  id: string;
  name: string;
  input?: string;
  expected_output?: string;
}

export interface TestResult {
  judge_case: JudgeCase;
  status: 'AC' | 'WA' | 'TLE' | 'RE' | 'CE' | 'PE' | 'PENDING';
  output?: string;
  error_message?: string;
  execution_time?: number;
  memory_usage?: number;
}

export const convertToTestResult = (result: unknown): TestResult => {
  const r = result as {
    judge_case_id?: string;
    id?: string;
    judge_case_name?: string;
    name?: string;
    input?: string;
    expected_output?: string;
    status?: string;
    output?: string;
    error_message?: string;
    execution_time?: number;
    memory_usage?: number;
  };
  
  return {
    judge_case: {
      id: r.judge_case_id || r.id || '',
      name: r.judge_case_name || r.name || `Test Case ${r.id}`,
      input: r.input,
      expected_output: r.expected_output,
    },
    status: (r.status as TestResult['status']) || 'PENDING',
    output: r.output,
    error_message: r.error_message,
    execution_time: r.execution_time,
    memory_usage: r.memory_usage,
  };
};

export const useJudgeCases = (problemId: string) => {
  const [availableJudgeCases, setAvailableJudgeCases] = useState<string[]>([]);
  const [selectedJudgeCase, setSelectedJudgeCase] = useState<string | null>(null);

  const handleJudgeCaseSelect = useCallback((judgeCaseId: string) => {
    setSelectedJudgeCase(judgeCaseId);
  }, []);

  const loadJudgeCases = useCallback(async () => {
    try {
      // TODO: 実際のAPIエンドポイントに置き換える
      const response = await fetch(`/api/problems/${problemId}/judge-cases`);
      if (response.ok) {
        const data = await response.json();
        const caseIds = (data as { judge_cases?: { id: string }[] }).judge_cases?.map(c => c.id) || [];
        setAvailableJudgeCases(caseIds);
      }
    } catch (error) {
      console.error('Failed to load judge cases:', error);
      // フォールバック用のダミーデータ
      setAvailableJudgeCases(['case1', 'case2', 'case3']);
    }
  }, [problemId]);

  return {
    availableJudgeCases,
    selectedJudgeCase,
    handleJudgeCaseSelect,
    loadJudgeCases,
  };
};