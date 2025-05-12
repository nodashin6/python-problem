import React, { useEffect } from 'react';
import { TestCaseTable } from '@/components/problem/TestCaseTable';
import { TestResult } from '@/components/problem/TestResultCard';
import { TestResults } from '@/components/problem/TestResults';
import { JudgeStatus } from '@/lib/api';
import type { JudgeResponse } from '@/types/judge';
import TestCaseDetails from '@/components/problem/TestCaseDetails';

interface JudgeResultSectionProps {
  isVisible: boolean;
  testCaseList: string[];
  judgeStatus: JudgeStatus | null;
  submitting: boolean;
  isPolling: boolean;
  testResults?: TestResult[];
  result: JudgeResponse | null;
  selectedTestCase: TestResult | null;
  handleTestCaseSelect: (testCase: TestResult) => void;
  onLoadTestCases: () => void;
}

export const JudgeResultSection: React.FC<JudgeResultSectionProps> = ({
  isVisible,
  testCaseList,
  judgeStatus,
  submitting,
  isPolling,
  testResults,
  result,
  selectedTestCase,
  handleTestCaseSelect,
  onLoadTestCases
}) => {
  // デバッグ用ログ出力
  useEffect(() => {
    console.log('📊 JudgeResultSection レンダリング:', {
      isVisible,
      testCaseListLength: testCaseList?.length,
      hasTestResults: testResults?.length,
      selectedTestCase: selectedTestCase?.id
    });
  }, [isVisible, testCaseList, testResults, selectedTestCase]);
  
  if (!isVisible) return null;
  
  // テストケース行のクリックハンドラのデバッグラッパー
  const handleTestCaseClick = (testCase: TestResult) => {
    console.log('📊 テストケース選択:', testCase.id);
    handleTestCaseSelect(testCase);
  };

  // 表示条件をシンプルに
  const shouldShowTable = submitting || isPolling || testCaseList.length > 0;
  
  return (
    <div className="mt-6 card-modern">
      <div className="card-header">
        <h2 className="text-2xl font-bold text-white flex items-center">
          <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          テスト結果
        </h2>
        
        {/* テスト結果サマリー */}
        {testResults && testResults.length > 0 && (
          <div className="flex items-center ml-auto bg-gray-800 bg-opacity-50 rounded-full px-3 py-1">
            <div className="flex space-x-1">
              <span className="text-green-400 font-medium">
                {testResults.filter(r => r.status === 'AC').length}
              </span>
              <span className="text-white">/</span>
              <span className="text-white font-medium">
                {testResults.length}
              </span>
            </div>
            <span className="ml-2 text-white text-sm">正解</span>
          </div>
        )}
      </div>
      
      <div className="p-4">
        {/* エラー表示 */}
        {result?.error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700">
            <h3 className="font-semibold mb-1">エラー</h3>
            <pre className="text-sm whitespace-pre-wrap">{result.error}</pre>
          </div>
        )}
        
        {/* テストケースがない場合のメッセージ */}
        {testCaseList.length === 0 && !submitting && !isPolling && (
          <div className="text-center p-4">
            <p className="text-gray-500 mb-3">テストケース情報がありません</p>
            <button 
              onClick={() => {
                console.log('📊 テストケース取得ボタンクリック');
                onLoadTestCases();
              }}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              テストケース一覧を取得
            </button>
          </div>
        )}

        {/* テーブル表示の条件をシンプルに */}
        {shouldShowTable && (
          <>
            <p className="text-sm text-gray-500 mb-2">
              {testCaseList.length > 0 
                ? `${testCaseList.length}件のテストケース` 
                : submitting || isPolling 
                  ? "判定実行中..." 
                  : "テストケースがありません"}
            </p>
            
            <TestCaseTable 
              testCaseList={testCaseList} 
              judgeStatus={judgeStatus} 
              submitting={submitting || isPolling}
              allResults={testResults}
              onTestCaseSelect={handleTestCaseClick}
              selectedTestCaseId={selectedTestCase?.id}
            />
          </>
        )}
        
        {/* 選択されたテストケースの詳細表示 */}
        {selectedTestCase && (
          <TestCaseDetails
            testCase={selectedTestCase}
            onClose={() => handleTestCaseSelect(selectedTestCase)}
          />
        )}
        
        {/* 詳細テスト結果 */}
        {testResults && testResults.length > 0 && (
          <div className="mt-6">
            <TestResults 
              results={testResults} 
              error={result?.error || undefined} 
            />
          </div>
        )}
        
        <p className="mt-4 text-sm text-gray-500">
          テストケースをクリックすると、詳細結果を確認できます。
        </p>
      </div>
    </div>
  );
};
