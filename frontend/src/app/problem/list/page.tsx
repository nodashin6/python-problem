'use client';

import { useEffect, useState } from 'react';
import { fetchProblemList, Problem, extractTitle, extractContent } from '@/lib/api';
import { motion } from 'framer-motion';
import { ProblemCard } from '@/components/problem/ProblemCard';

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
    return (
      <div className="flex justify-center items-center min-h-screen page-gradient">
        <div className="p-8 rounded-xl bg-white shadow-lg flex items-center space-x-4">
          <div className="loading-spinner"></div>
          <p className="text-lg text-indigo-700 font-medium">読み込み中...</p>
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
          <div className="mb-10">
            <h1 className="text-4xl font-bold text-indigo-800 mb-3">Python プログラミング問題集</h1>
            <p className="text-gray-600">実際にプログラムを書いて、あなたのPythonスキルを試してみよう！</p>
          </div>
          
          {problems.length === 0 ? (
            <div className="card-modern">
              <div className="card-body text-center py-12">
                <svg className="mx-auto h-16 w-16 text-indigo-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p className="text-xl text-gray-600">問題が見つかりませんでした</p>
              </div>
            </div>
          ) : (
            <div className="grid gap-6 md:grid-cols-2">
              {problems.map((problem) => {
                // タイトルを取得（title属性があればそれを使うか、マークダウンからタイトルを抽出）
                const title = problem.title || 
                  (problem.markdown ? extractTitle(problem.markdown) : `問題 ${problem.id}`);
                
                // 説明を取得（マークダウンからコンテンツを抽出）
                const content = problem.markdown ? extractContent(problem.markdown) : "問題文がありません";
                
                return (
                  <motion.div
                    key={problem.id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.5, delay: parseInt(problem.id) * 0.1 }}
                  >
                    <ProblemCard
                      id={problem.id}
                      title={title}
                      description={content}
                      isListItem={true}
                    />
                  </motion.div>
                );
              })}
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
}