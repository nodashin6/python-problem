/**
 * テストケース情報の型定義
 */
export type JudgeCase = {
  id: string;
  name: string;
  problem: {
    id: string;
    title?: string | null;
    markdown?: string | null;
    level?: number;
    solved?: boolean;
    solved_at?: string | null;
  };
  stdin: {
    id: string;
    name: string;
    content: string;
  };
  stdout: {
    id: string;
    name: string;
    content: string;
  };
};

/**
 * ジャッジ結果の各テストケースの結果
 */
export type JudgeResult = {
  id: string;
  status: 'AC' | 'WA' | 'RE' | 'CE' | 'TLE' | 'MLE' | string;
  judge_case: JudgeCase;
  metadata: {
    time_used?: number | null;
    memory_used?: number | null;
    compile_error?: string | null;
    runtime_error?: string | null;
    output?: string | null;
  };
};

/**
 * 問題のステータス情報
 */
export type ProblemStatus = {
  solved: boolean;
  solved_at: string | null;
  submission_count: number;
};

/**
 * ジャッジレスポンスの型定義
 */
export type JudgeResponse = {
  id: string;
  problem: {
    id: string;
  };
  code: string;
  results: JudgeResult[];
  error: string | null;
  problem_status?: ProblemStatus;
};

/**
 * ジャッジポーリング中のテストケース状態
 */
export type JudgeCasePollingStatus = {
  status: 'pending' | 'running' | 'completed';
  result?: {
    status: string;
    time_used?: number;
    errorMessage?: string;
    actualOutput?: string;
  };
};
