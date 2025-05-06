'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { fetchProblemList, Problem, extractTitle, extractContent } from '@/lib/api';

export default function ProblemListPage() {
  const [problems, setProblems] = useState<Problem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadProblems() {
      try {
        const data = await fetchProblemList();
        setProblems(data);
      } catch (error) {
        console.error('問題の取得に失敗しました', error);
      } finally {
        setLoading(false);
      }
    }

    loadProblems();
  }, []);

  if (loading) {
    return <div className="flex justify-center items-center min-h-screen">読み込み中...</div>;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">問題一覧</h1>
      
      {problems.length === 0 ? (
        <div className="text-center py-10">
          <p>問題が見つかりませんでした</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {problems.map((problem) => {
            // タイトルを取得（title属性があればそれを使うか、マークダウンからタイトルを抽出）
            const title = problem.title || 
              (problem.markdown ? extractTitle(problem.markdown) : `問題 ${problem.id}`);
            
            // 説明を取得（マークダウンからコンテンツを抽出）
            const content = problem.markdown ? extractContent(problem.markdown) : "問題文がありません";
            
            return (
              <Link 
                key={problem.id}
                href={`/problem/${problem.id}`}
                className="block p-6 bg-white hover:bg-gray-50 border border-gray-200 rounded-lg shadow-sm transition"
              >
                <h2 className="text-xl font-semibold">{title}</h2>
                <p className="mt-2 text-gray-600 line-clamp-2">{content}</p>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}