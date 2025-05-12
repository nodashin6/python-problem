import React, { useEffect, useState } from 'react';
import { JudgeStatus } from '@/lib/api';
import { TestResult } from './TestResultCard';

type TestCaseTableProps = {
  testCaseList: string[];
  judgeStatus: JudgeStatus | null;
  submitting: boolean;
  allResults?: TestResult[];
  onTestCaseSelect: (testCase: TestResult) => void;
  selectedTestCaseId?: string;
};

export const TestCaseTable: React.FC<TestCaseTableProps> = ({ 
  testCaseList, 
  judgeStatus, 
  submitting, 
  allResults = [],
  onTestCaseSelect,
  selectedTestCaseId
}) => {
  // 各テストケースの状態を保持する内部ステート
  const [testcaseState, setTestcaseState] = useState<Record<string, any>>({});
  
  // judgeStatusが変更されたら内部ステートを更新
  useEffect(() => {
    // ここで?を追加して、progressがundefinedの場合に対応
    if (judgeStatus?.progress?.testcases) {
      console.log("テストケース状態の更新:", judgeStatus?.progress?.testcases);
      setTestcaseState(prevState => ({
        ...prevState,
        ...judgeStatus?.progress?.testcases
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
              // TestResultにはoutputがなく、代わりにmetadataにエラー情報がある
              errorMessage: result.metadata.runtime_error || result.metadata.compile_error || '',
              actualOutput: result.metadata.output || ''
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
      onTestCaseSelect(result);
    } else {
      console.log('該当するテスト結果が見つかりません:', testcaseId, allResults);
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
  
  // テストケースリストが空であれば、プレースホルダー行を表示
  if (testCaseList.length === 0 && !submitting) {
    return (
      <table className="min-w-full divide-y divide-gray-200 border-b border-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">テストケース</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状態</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">結果</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">実行時間</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          <tr>
            <td colSpan={4} className="px-6 py-4 text-center text-sm text-gray-500">
              テストケースがありません
            </td>
          </tr>
        </tbody>
      </table>
    );
  }

  // 各テストケースの実行状態とテスト結果を対応付ける
  const getTestCaseData = (testCaseId: string) => {
    // テスト結果が既に存在する場合
    const result = allResults?.find(r => r.test_case.id === testCaseId);
    if (result) {
      return {
        name: result.test_case.name || testCaseId,
        status: result.status,
        time: result.metadata.time_used,
        result
      };
    }

    // 実行中のテストケース情報
    const progressInfo = judgeStatus?.progress?.testcases?.[testCaseId];
    if (progressInfo) {
      return {
        name: testCaseId,
        status: 'running',
        time: null,
        result: null
      };
    }

    // 情報がないテストケース（まだ実行されていない）
    return {
      name: testCaseId,
      status: submitting ? 'pending' : 'unknown',
      time: null,
      result: null
    };
  };
  
  // 状態に応じたスタイルとアイコン
  const getStatusStyles = (status: string) => {
    switch (status) {
      case 'AC':
        return {
          bg: 'bg-green-100',
          text: 'text-green-800',
          icon: '✓',
          label: '正解'
        };
      case 'WA':
        return {
          bg: 'bg-red-100',
          text: 'text-red-800',
          icon: '✗',
          label: '不正解'
        };
      case 'RE':
        return {
          bg: 'bg-orange-100',
          text: 'text-orange-800',
          icon: '!',
          label: '実行時エラー'
        };
      case 'CE':
        return {
          bg: 'bg-yellow-100',
          text: 'text-yellow-800',
          icon: '!',
          label: 'コンパイルエラー'
        };
      case 'TLE':
        return {
          bg: 'bg-purple-100',
          text: 'text-purple-800',
          icon: '⏱',
          label: 'タイムアウト'
        };
      case 'running':
        return {
          bg: 'bg-blue-100',
          text: 'text-blue-800',
          icon: '⟳',
          label: '実行中'
        };
      case 'pending':
        return {
          bg: 'bg-gray-100',
          text: 'text-gray-800',
          icon: '⏳',
          label: '待機中'
        };
      default:
        return {
          bg: 'bg-gray-50',
          text: 'text-gray-500',
          icon: '-',
          label: '未実行'
        };
    }
  };

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200 border-b border-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">テストケース</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状態</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">結果</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">実行時間</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {submitting && testCaseList.length === 0 ? (
            <tr>
              <td colSpan={4} className="px-6 py-4 text-center text-sm text-gray-500">
                <div className="flex justify-center items-center space-x-2">
                  <svg className="animate-spin h-5 w-5 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>判定準備中...</span>
                </div>
              </td>
            </tr>
          ) : (
            // 各テストケースを表示
            testCaseList.map(testCaseId => {
              const { name, status, time, result } = getTestCaseData(testCaseId);
              const { bg, text, icon, label } = getStatusStyles(status);
              const isSelected = result && result.id === selectedTestCaseId;
              
              return (
                <tr 
                  key={testCaseId} 
                  className={`hover:bg-gray-50 transition-colors cursor-pointer ${isSelected ? 'bg-blue-50' : ''}`}
                  onClick={() => result && handleRowClick(testCaseId)}
                >
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${bg} ${text}`}>
                      <span className="mr-1">{icon}</span>
                      {label}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {status === 'AC' ? '✅ 正解' : status === 'WA' ? '❌ 不正解' : '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {time != null ? `${time} ms` : '-'}
                  </td>
                </tr>
              );
            })
          )}
        </tbody>
      </table>
    </div>
  );
};