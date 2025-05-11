// バックエンドから返ってくる判定結果の型定義

export type Stdio = {
  id: string;
  name: string;
  content: string;
}

export type TestCase = {
  id: string;
  name: string;
  problem: {
    id: string;
  };
  stdin: Stdio;
  stdout: Stdio;
};


export type JudgeReusltMetadata = {
  memory_used: number | null;
  time_used: number | null;
  compile_error: string | null;
  runtime_error: string | null;
  output: string | null;
};


export type JudgeResult = {
  id: string;
  problem: {
    id: string;
  };
  test_case: TestCase,
  status: string;
  metadata: JudgeReusltMetadata;
};

export type JudgeResponse = {
  id: string;
  problem: {
    id: string;
  };
  code: string;
  results: JudgeResult[];
  error?: string;
  submission_id?: string; // 提出ID
  problem_status?: {
    solved: boolean;
    solved_at: string | null;
    submission_count: number;
  };
};
