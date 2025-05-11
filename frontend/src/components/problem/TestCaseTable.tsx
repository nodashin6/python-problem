import { useEffect, useState } from 'react';
import { JudgeStatus } from '@/lib/api';
import { TestResult } from './TestResultCard';
import { TestResultDrawer } from './TestResultDrawer';
import { JudgeResult } from '@/types/judge';

type TestCaseTableProps = {
  testCaseList: string[];
  judgeStatus: JudgeStatus | null;
  submitting: boolean;
  allResults?: TestResult[]; // 実行完了した全テストケースの結果
};

export const TestCaseTable = ({ testCaseList, judgeStatus, submitting, allResults = [] }: TestCaseTableProps) => {
  // ドロワーの状態管理
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selectedResult, setSelectedResult] = useState<TestResult | null>(null);
  // 各テストケースの状態を保持する内部ステート
  const [testcaseState, setTestcaseState] = useState<Record<string, any>>({});
  
  // judgeStatusが変更されたら内部ステートを更新
  useEffect(() => {
    if (judgeStatus?.progress?.testcases) {
      console.log("テストケース状態の更新:", judgeStatus.progress.testcases);
      setTestcaseState(prevState => ({
        ...prevState,
        ...judgeStatus.progress.testcases
      }));
    }
  }, [judgeStatus]);

  // allResultsが変更されたら内部ステートを更新（完了後の結果反映）
  useEffect(() => {
    if (allResults && allResults.length > 0) {
      console.log("テスト完了後の結果を反映:", allResults);
      
      // 既存のテストケース状態をコピー
      const updatedState = { ...testcaseState };
      
      // allResultsの結果を反映
      allResults.forEach(result => {
        const testcaseId = result.test_case.id;
        if (testcaseId) {
          // そのテストケースのステータスを「完了」にして結果を設定
          updatedState[testcaseId] = {
            status: 'completed',
            result: {
              status: result.status,
              time_used: result.metadata.time_used || 0,
              errorMessage: result.output?.error || '',
              actualOutput: result.output?.actual || ''
            }
          };
        }
      });
      
      // 更新された状態を設定
      setTestcaseState(updatedState);
    }
  }, [allResults]);
  
  // テストケース行がクリックされたときの処理
  const handleRowClick = (testcaseId: string) => {
    // 実行完了している結果から選択されたテストケースを探す
    const result = allResults?.find(r => r.test_case.id === testcaseId);
    
    if (result) {
      setSelectedResult(result);
      setDrawerOpen(true);
    } else {
      // まだ結果がない場合はドロワーを開かない
      console.log('このテストケースの結果はまだありません');
    }
  };
  
  // 新規実行が開始されたらテストケース状態をリセット
  useEffect(() => {
    if (submitting) {
      const initialState = testCaseList.reduce((acc, id) => {
        acc[id] = { status: 'pending' };
        return acc;
      }, {} as Record<string, any>);
      setTestcaseState(initialState);
    }
  }, [submitting, testCaseList]);
  
  return (
    <>
      <div className="overflow-x-auto mt-4">
        <table className="min-w-full bg-white rounded-lg overflow-hidden">
          <thead className="bg-gray-100">
            <tr>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">テストケース</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状態</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">結果</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">実行時間</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {testCaseList.map((testcaseId) => {
              const testcase = testcaseState[testcaseId] || { status: 'pending' };
              
              // 状態に応じたスタイルとテキスト
              let statusStyle = 'bg-gray-100 text-gray-500'; // デフォルト（pending）
              let statusText = '待機中';
              
              // 完了したテストケース結果をallResultsから探す
              const fullResult = allResults?.find(r => r.test_case.id === testcaseId);
              
              // 状態の表示を決定
              if (testcase.status === 'processing') {
                statusStyle = 'bg-blue-100 text-blue-600';
                statusText = '実行中';
              } else if (testcase.status === 'completed' || fullResult) {
                statusText = '完了';
                statusStyle = 'bg-green-100 text-green-600';
              }
              
              // 結果のスタイルと表示
              let resultDisplay = '-';
              let resultStyle = '';
              
              // 結果表示を決定（allResultsの情報を優先）
              if (fullResult) {
                resultDisplay = fullResult.status;
                if (fullResult.status === 'AC') {
                  resultStyle = 'text-green-600 font-medium';
                  resultDisplay = '正解';
                } else if (fullResult.status === 'WA') {
                  resultStyle = 'text-red-600 font-medium';
                  resultDisplay = '不正解';
                } else if (fullResult.status === 'TLE') {
                  resultStyle = 'text-yellow-600 font-medium';
                  resultDisplay = '時間超過';
                } else if (fullResult.status === 'RE') {
                  resultStyle = 'text-orange-600 font-medium';
                  resultDisplay = '実行エラー';
                } else {
                  resultStyle = 'text-yellow-600 font-medium';
                }
              } else if (testcase.result) {
                resultDisplay = testcase.result.status;
                if (testcase.result.status === 'AC') {
                  resultStyle = 'text-green-600 font-medium';
                  resultDisplay = '正解';
                } else if (testcase.result.status === 'WA') {
                  resultStyle = 'text-red-600 font-medium';
                  resultDisplay = '不正解';
                } else if (testcase.result.status === 'TLE') {
                  resultStyle = 'text-yellow-600 font-medium';
                  resultDisplay = '時間超過';
                } else if (testcase.result.status === 'RE') {
                  resultStyle = 'text-orange-600 font-medium';
                  resultDisplay = '実行エラー';
                } else {
                  resultStyle = 'text-yellow-600 font-medium';
                }
              }

              // 実行時間の表示（allResultsの情報を優先）
              const timeUsed = fullResult?.metadata.time_used || testcase.result?.time_used;
              
              // 詳細結果があるかどうかを確認
              const hasDetailResult = fullResult || testcase.status === 'completed';
              
              return (
                <tr 
                  key={testcaseId} 
                  className={`hover:bg-gray-50 ${hasDetailResult ? 'cursor-pointer' : ''}`}
                  onClick={hasDetailResult ? () => handleRowClick(testcaseId) : undefined}
                >
                  <td className="px-4 py-2 whitespace-nowrap text-sm font-medium text-gray-900">
                    {testcaseId}
                  </td>
                  <td className="px-4 py-2 whitespace-nowrap text-sm">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium ${statusStyle}`}>
                      {testcase.status === 'processing' && (
                        <svg className="animate-spin -ml-1 mr-2 h-3 w-3" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                      )}
                      {statusText}
                    </span>
                  </td>
                  <td className="px-4 py-2 whitespace-nowrap text-sm">
                    <span className={resultStyle}>{resultDisplay}</span>
                  </td>
                  <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-500">
                    {timeUsed ? `${timeUsed} ms` : '-'}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* テスト結果を表示するドロワー */}
      <TestResultDrawer 
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        result={selectedResult}
      />
    </>
  );
};