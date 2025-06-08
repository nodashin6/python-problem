import React from 'react';
import { TestResult } from './TestResultCard';

interface JudgeCaseDetailsProps {
  JudgeCase: TestResult;
  onClose: () => void;
}

const JudgeCaseDetails: React.FC<JudgeCaseDetailsProps> = ({ JudgeCase, onClose }) => {
  return (
    <div className="mt-4 p-4 bg-gray-50 border border-gray-200 rounded-lg animate-fadeIn">
      <div className="flex justify-between items-center mb-3">
        <h3 className="font-semibold text-lg">テストケース詳細: {JudgeCase.judge_case.name}</h3>
        <button 
          onClick={onClose}
          className="text-gray-500 hover:text-gray-700"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <h4 className="font-medium text-gray-700 mb-1">入力</h4>
          <pre className="bg-gray-100 p-3 rounded text-sm overflow-auto max-h-40">
            {JudgeCase.judge_case.stdin.content}
          </pre>
        </div>
        <div>
          <h4 className="font-medium text-gray-700 mb-1">期待される出力</h4>
          <pre className="bg-gray-100 p-3 rounded text-sm overflow-auto max-h-40">
            {JudgeCase.judge_case.stdout.content}
          </pre>
        </div>
        {JudgeCase.metadata.output && (
          <div className="md:col-span-2">
            <h4 className="font-medium text-gray-700 mb-1">あなたの出力</h4>
            <pre className={`p-3 rounded text-sm overflow-auto max-h-40 ${
              JudgeCase.status === 'AC' 
                ? 'bg-green-50 border border-green-100' 
                : 'bg-red-50 border border-red-100'
            }`}>
              {JudgeCase.metadata.output}
            </pre>
          </div>
        )}
        {JudgeCase.metadata.runtime_error && (
          <div className="md:col-span-2">
            <h4 className="font-medium text-red-700 mb-1">実行時エラー</h4>
            <pre className="bg-red-50 p-3 border border-red-100 rounded text-sm text-red-700 overflow-auto max-h-40">
              {JudgeCase.metadata.runtime_error}
            </pre>
          </div>
        )}
        {JudgeCase.metadata.compile_error && (
          <div className="md:col-span-2">
            <h4 className="font-medium text-red-700 mb-1">コンパイルエラー</h4>
            <pre className="bg-red-50 p-3 border border-red-100 rounded text-sm text-red-700 overflow-auto max-h-40">
              {JudgeCase.metadata.compile_error}
            </pre>
          </div>
        )}
        {JudgeCase.metadata.time_used && (
          <div className="md:col-span-2">
            <p className="text-sm text-gray-600">
              実行時間: {JudgeCase.metadata.time_used} ms
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default JudgeCaseDetails;
