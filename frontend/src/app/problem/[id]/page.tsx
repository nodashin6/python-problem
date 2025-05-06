'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { fetchProblemById, judgeCode, Problem, extractTitle } from '@/lib/api';
import Link from 'next/link';
import ReactMarkdown from 'react-markdown';

// バックエンドから返ってくる判定結果の型定義
type JudgeResult = {
  id: string;
  problem: {
    id: string;
  };
  test_case: {
    id: string;
    name: string;
    problem: {
      id: string;
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
  status: string;
  metadata: {
    memory_used: number | null;
    time_used: number | null;
    compile_error: string | null;
    runtime_error: string | null;
    output: string | null;
  };
};

type JudgeResponse = {
  id: string;
  problem: {
    id: string;
  };
  code: string;
  results: JudgeResult[];
  error?: string;
};

export default function ProblemPage() {
  const params = useParams();
  const problemId = params.id as string;
  
  const [problem, setProblem] = useState<Problem | null>(null);
  const [loading, setLoading] = useState(true);
  const [code, setCode] = useState('');
  const [result, setResult] = useState<JudgeResponse | null>(null);
  const [submitting, setSubmitting] = useState(false);

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

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    
    if (!code.trim()) {
      alert('コードを入力してください');
      return;
    }
    
    try {
      setSubmitting(true);
      setResult(null);
      
      const judgeResult = await judgeCode(problemId, code);
      setResult(judgeResult);
    } catch (error) {
      console.error('ジャッジに失敗しました', error);
      setResult({ 
        id: 'error', 
        problem: { id: problemId }, 
        code: code, 
        results: [],
        error: '処理中にエラーが発生しました'
      });
    } finally {
      setSubmitting(false);
    }
  }

  // 全テストケースがACかどうかをチェック
  const isAllPassed = result?.results?.every(r => r.status === 'AC') ?? false;

  // タイトルをマークダウンから取得するか、titleがあればそれを使用
  const title = problem?.title || 
    (problem?.markdown ? extractTitle(problem.markdown) : `問題 ${problemId}`);

  if (loading) {
    return <div className="flex justify-center items-center min-h-screen">読み込み中...</div>;
  }

  if (!problem) {
    return (
      <div className="container mx-auto px-4 py-16 text-center">
        <h1 className="text-3xl font-bold mb-6">問題が見つかりませんでした</h1>
        <Link href="/problem/list" className="text-blue-600 hover:underline">
          問題一覧に戻る
        </Link>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <Link href="/problem/list" className="text-blue-600 hover:underline mb-6 inline-block">
        ← 問題一覧に戻る
      </Link>
      
      <h1 className="text-3xl font-bold mb-4">{title}</h1>
      
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 mb-8">
        <h2 className="text-xl font-semibold mb-4">問題文</h2>
        <div className="prose max-w-none">
          {problem.markdown ? (
            <ReactMarkdown>{problem.markdown}</ReactMarkdown>
          ) : (
            <p>問題文がありません</p>
          )}
        </div>
      </div>
      
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <h2 className="text-xl font-semibold mb-4">解答</h2>
        
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label htmlFor="code" className="block text-sm font-medium text-gray-700 mb-2">
              コード
            </label>
            <textarea
              id="code"
              className="w-full h-64 p-3 border border-gray-300 rounded-md font-mono text-sm"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="Pythonコードを入力してください"
            />
          </div>
          
          <button
            type="submit"
            disabled={submitting}
            className={`px-6 py-2 rounded-md text-white font-medium 
              ${submitting ? 'bg-gray-400' : 'bg-blue-600 hover:bg-blue-700'}`}
          >
            {submitting ? '判定中...' : '提出する'}
          </button>
        </form>
        
        {result && (
          <div className="mt-8">
            <h3 className="text-lg font-medium mb-2">実行結果</h3>
            <div className="border rounded-md overflow-hidden">
              {result.error ? (
                <div className="p-4 bg-red-100">
                  <div className="font-medium">❌ エラーが発生しました</div>
                  <div className="mt-2 text-red-600">{result.error}</div>
                </div>
              ) : (
                <div className={`p-4 ${isAllPassed ? 'bg-green-100' : 'bg-red-100'}`}>
                  <div className="font-medium">
                    {isAllPassed ? '✅ テスト通過' : '❌ テスト失敗'}
                  </div>
                  <div className="mt-4">
                    {result.results.map((testResult) => (
                      <div key={testResult.id} className="mb-4 border-t pt-3">
                        <h4 className="font-medium">テストケース {testResult.test_case.name}</h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
                          <div>
                            <p className="text-sm text-gray-600">入力:</p>
                            <pre className="whitespace-pre-wrap text-sm bg-gray-50 p-2 rounded border mt-1">
                              {testResult.test_case.stdin.content || '(入力なし)'}
                            </pre>
                          </div>
                          <div>
                            <p className="text-sm text-gray-600">期待される出力:</p>
                            <pre className="whitespace-pre-wrap text-sm bg-gray-50 p-2 rounded border mt-1">
                              {testResult.test_case.stdout.content}
                            </pre>
                          </div>
                        </div>
                        <div className="mt-2">
                          <p className="text-sm text-gray-600">あなたの出力:</p>
                          <pre className="whitespace-pre-wrap text-sm bg-gray-50 p-2 rounded border mt-1">
                            {testResult.metadata.output || '(出力なし)'}
                          </pre>
                        </div>
                        <div className="mt-2">
                          <span 
                            className={`inline-block px-2 py-1 rounded text-sm ${
                              testResult.status === 'AC' 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-red-100 text-red-800'
                            }`}
                          >
                            {testResult.status === 'AC' ? '✓ 正解' : '✗ 不正解'}
                          </span>
                          {testResult.metadata.runtime_error && (
                            <div className="mt-2">
                              <p className="text-sm text-red-600">実行時エラー:</p>
                              <pre className="whitespace-pre-wrap text-sm bg-red-50 p-2 rounded border mt-1 text-red-800">
                                {testResult.metadata.runtime_error}
                              </pre>
                            </div>
                          )}
                          {testResult.metadata.compile_error && (
                            <div className="mt-2">
                              <p className="text-sm text-red-600">コンパイルエラー:</p>
                              <pre className="whitespace-pre-wrap text-sm bg-red-50 p-2 rounded border mt-1 text-red-800">
                                {testResult.metadata.compile_error}
                              </pre>
                            </div>
                          )}
                          {testResult.metadata.time_used && (
                            <p className="text-xs text-gray-500 mt-1">
                              実行時間: {testResult.metadata.time_used}ms
                            </p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}