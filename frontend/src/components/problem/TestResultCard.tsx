import React from 'react';
import { motion } from 'framer-motion';

export interface TestResult {
  id: string;
  status: string;
  judge_case: {
    id: string; // idフィールドを追加
    name: string;
    stdin: {
      content: string;
    };
    stdout: {
      content: string;
    };
  };
  metadata: {
    output?: string;
    runtime_error?: string;
    compile_error?: string;
    time_used?: number; // numberに変更
  };
}

interface TestResultCardProps {
  testResult: TestResult;
}

export const TestResultCard: React.FC<TestResultCardProps> = ({ testResult }) => {
  const isPassed = testResult.status === 'AC';
  
  return (
    <div className="bg-white rounded-xl shadow-md overflow-hidden">
      <div className={`py-3 px-5 font-medium text-white ${
        isPassed 
          ? 'bg-gradient-to-r from-green-500 to-emerald-600' 
          : 'bg-gradient-to-r from-red-500 to-rose-600'
      }`}>
        <div className="flex items-center justify-between">
          <h4 className="font-bold">テストケース {testResult.judge_case.name}</h4>
          <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm ${
            isPassed 
              ? 'bg-green-100 text-green-800' 
              : 'bg-red-100 text-red-800'
          }`}>
            {isPassed ? '✓ 正解' : '✗ 不正解'}
          </span>
        </div>
      </div>

      <div className="p-5">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div className="test-result-box">
            <p className="text-sm font-medium text-gray-600 mb-2">入力:</p>
            <pre className="whitespace-pre-wrap text-sm bg-white p-3 rounded-lg border border-gray-200 overflow-auto max-h-40">
              {testResult.judge_case.stdin.content || '(入力なし)'}
            </pre>
          </div>
          <div className="test-result-box">
            <p className="text-sm font-medium text-gray-600 mb-2">期待される出力:</p>
            <pre className="whitespace-pre-wrap text-sm bg-white p-3 rounded-lg border border-gray-200 overflow-auto max-h-40">
              {testResult.judge_case.stdout.content}
            </pre>
          </div>
        </div>

        <div className="mt-4 test-result-box">
          <p className="text-sm font-medium text-gray-600 mb-2">あなたの出力:</p>
          <pre className={`whitespace-pre-wrap text-sm p-3 rounded-lg border overflow-auto max-h-40
            ${isPassed
              ? 'bg-green-50 border-green-200' 
              : 'bg-red-50 border-red-200'
            }`}>
            {testResult.metadata.output || '(出力なし)'}
          </pre>
        </div>

        {testResult.metadata.runtime_error && (
          <div className="mt-4 test-result-box !bg-red-50">
            <p className="text-sm font-medium text-red-600 mb-2">実行時エラー:</p>
            <pre className="whitespace-pre-wrap text-sm bg-white p-3 rounded-lg border border-red-200 text-red-800 overflow-auto max-h-40">
              {testResult.metadata.runtime_error}
            </pre>
          </div>
        )}

        {testResult.metadata.compile_error && (
          <div className="mt-4 test-result-box !bg-red-50">
            <p className="text-sm font-medium text-red-600 mb-2">コンパイルエラー:</p>
            <pre className="whitespace-pre-wrap text-sm bg-white p-3 rounded-lg border border-red-200 text-red-800 overflow-auto max-h-40">
              {testResult.metadata.compile_error}
            </pre>
          </div>
        )}

        {testResult.metadata.time_used && (
          <div className="flex items-center mt-3">
            <svg className="w-4 h-4 text-indigo-500 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="text-xs text-indigo-600 font-medium">
              実行時間: {testResult.metadata.time_used}ms
            </p>
          </div>
        )}
      </div>
    </div>
  );
};