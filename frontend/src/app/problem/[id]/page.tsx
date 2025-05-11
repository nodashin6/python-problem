'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { fetchProblemById, judgeCode, Problem, extractTitle } from '@/lib/api';
import Link from 'next/link';
import { motion } from 'framer-motion';

// 新しく作成したコンポーネントをインポート
import { ProblemCard } from '@/components/problem/ProblemCard';
import { CodeSubmissionForm } from '@/components/problem/CodeSubmissionForm';
import { TestResults } from '@/components/problem/TestResults';
import { TestResult } from '@/components/problem/TestResultCard';

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

  // タイトルをマークダウンから取得するか、titleがあればそれを使用
  const title = problem?.title || 
    (problem?.markdown ? extractTitle(problem.markdown) : `問題 ${problemId}`);

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen page-gradient">
        <div className="p-8 rounded-xl bg-white shadow-lg flex items-center space-x-4">
          <div className="loading-spinner"></div>
          <p className="text-lg text-indigo-700 font-medium">読み込み中...</p>
        </div>
      </div>
    );
  }

  if (!problem) {
    return (
      <div className="page-gradient flex items-center justify-center">
        <div className="card-modern p-10 max-w-md w-full">
          <h1 className="text-3xl font-bold mb-6 text-indigo-800 text-center">問題が見つかりませんでした</h1>
          <Link href="/problem/list" className="block text-center py-3 px-6 btn-primary">
            問題一覧に戻る
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="page-gradient">
      <div className="max-w-5xl mx-auto">
        <motion.div 
          initial={{ opacity: 0, y: 20 }} 
          animate={{ opacity: 1, y: 0 }} 
          transition={{ duration: 0.5 }}
        >
          <Link href="/problem/list" className="link-primary mb-6">
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            問題一覧に戻る
          </Link>
          
          {/* 問題カードコンポーネント */}
          <ProblemCard title={title} markdownContent={problem.markdown} />
          
          {/* 解答入力フォームコンポーネント */}
          <div className="card-modern">
            <div className="card-header">
              <h2 className="text-2xl font-bold text-white flex items-center">
                <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                </svg>
                解答
              </h2>
            </div>
            
            <div className="card-body">
              <CodeSubmissionForm 
                code={code}
                onCodeChange={setCode}
                onSubmit={handleSubmit}
                submitting={submitting}
              />
              
              {/* テスト結果コンポーネント */}
              {result && (
                <TestResults 
                  results={result.results as unknown as TestResult[]}
                  error={result.error}
                />
              )}
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}