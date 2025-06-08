import { useState, useEffect } from 'react';
import { fetchProblemById, Problem, extractTitle } from '@/lib/api';

/**
 * 問題データを取得するカスタムフック
 */
export const useProblem = (problemId: string) => {
  const [problem, setProblem] = useState<Problem | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // 問題読み込み
  useEffect(() => {
    async function loadProblem() {
      if (!problemId) {
        setLoading(false);
        return;
      }
      
      try {
        const data = await fetchProblemById(problemId);
        setProblem(data);
      } catch (err) {
        console.error('問題の取得に失敗しました', err);
        setError('問題の取得に失敗しました');
      } finally {
        setLoading(false);
      }
    }

    loadProblem();
  }, [problemId]);

  // 問題のステータスを更新
  const updateProblemStatus = (status: Partial<Problem>) => {
    if (!problem) return;
    
    setProblem({
      ...problem,
      ...status
    });
  };
  
  // タイトルを取得
  const title = problem?.title || 
    (problem?.markdown ? extractTitle(problem.markdown) : `問題 ${problemId}`);

  return {
    problem,
    loading,
    error,
    title,
    updateProblemStatus
  };
};
