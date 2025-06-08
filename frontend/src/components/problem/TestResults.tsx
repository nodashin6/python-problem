import React from 'react';
import { motion } from 'framer-motion';
import { TestResult, TestResultCard } from './TestResultCard';

interface TestResultsProps {
  results: TestResult[];
  error?: string;
}

export const TestResults: React.FC<TestResultsProps> = ({ results, error }) => {
  const isAllPassed = !error && results.every(r => r.status === 'AC');

  if (!results?.length && !error) {
    return null;
  }

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }} 
      animate={{ opacity: 1, y: 0 }} 
      transition={{ duration: 0.5 }}
      className="mt-12"
    >
      <h3 className="text-xl font-bold text-indigo-800 mb-4 flex items-center">
        <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
        </svg>
        実行結果
      </h3>
      <div className="rounded-xl overflow-hidden shadow-lg border-2">
        {error ? (
          <div className="p-6 bg-red-50 border-b-2 border-red-200">
            <div className="font-bold text-red-700 text-lg flex items-center">
              <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              エラーが発生しました
            </div>
            <div className="mt-3 text-red-600 bg-red-100 p-4 rounded-lg">{error}</div>
          </div>
        ) : (
          <div className={`p-6 ${isAllPassed ? 'bg-green-50 border-b-2 border-green-200' : 'bg-red-50 border-b-2 border-red-200'}`}>
            <div className={`font-bold text-lg flex items-center ${isAllPassed ? 'text-green-700' : 'text-red-700'}`}>
              {isAllPassed ? (
                <>
                  <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  テスト通過！おめでとう！
                </>
              ) : (
                <>
                  <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  テスト失敗...もう一度チャレンジ！
                </>
              )}
            </div>

            <div className="mt-6 space-y-6">
              {results.map((testResult) => (
                <TestResultCard key={testResult.id} testResult={testResult} />
              ))}
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
};