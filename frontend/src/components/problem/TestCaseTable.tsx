import React, { useEffect, useState } from 'react';
import { JudgeStatus } from '@/lib/api';
import { TestResult } from './TestResultCard';

type JudgeCaseTableProps = {
  JudgeCaseList: string[];
  judgeStatus: JudgeStatus | null;
  submitting: boolean;
  isPolling: boolean;  // ポーリング状態を追加
  allResults?: TestResult[];
  onJudgeCaseSelect: (JudgeCase: TestResult) => void;
  selectedJudgeCaseId?: string;
};

export const JudgeCaseTable: React.FC<JudgeCaseTableProps> = ({ 
  JudgeCaseList, 
  judgeStatus, 
  submitting, 
  isPolling,
  allResults = [],
  onJudgeCaseSelect,
  selectedJudgeCaseId
}) => {
  // 各テストケースの状態を保持する内部ステート
  const [JudgeCaseState, setJudgeCaseState] = useState<Record<string, unknown>>({});
  // UI表示用のテストケース配列
  const [displayJudgeCases, setDisplayJudgeCases] = useState<unknown[]>([]);
  
  // デバッグ強化: 受け取ったpropsを詳しく表示
  useEffect(() => {
    console.log('🟢 JudgeCaseTable 入力props:', { 
      JudgeCaseListLength: JudgeCaseList?.length,
      judgeStatusId: judgeStatus?.judge_id,
      submitting,
      isPolling,
      allResultsLength: allResults?.length 
    });
    
    if (allResults && allResults.length > 0) {
      console.log('🟢 テスト結果詳細:', allResults);
    }
  }, [JudgeCaseList, judgeStatus, submitting, isPolling, allResults]);

  // 表示用テストケース配列の構築 (allResultsが更新されたときに実行)
  useEffect(() => {
    // テストケースのないテーブルをスキップ
    if (JudgeCaseList.length === 0) {
      setDisplayJudgeCases([]);
      return;
    }

    // 新しいテストケース表示配列を作成
    const newDisplayCases = JudgeCaseList.map(id => {
      // 完了したテスト結果を検索
      const result = allResults?.find(r => r && r.judge_case && r.judge_case.id === id);
      
      if (result) {
        // テスト結果がある場合
        return {
          id,
          name: result.judge_case.name || id,
          status: result.status,
          time: result.metadata?.time_used,
          result
        };
      } else {
        // テスト結果がない場合は状態を参照
        const stateInfo = JudgeCaseState[id];
        if (stateInfo) {
          return {
            id,
            name: id,
            status: (stateInfo as any).status === 'completed'
              ? ((stateInfo as any).result?.status || 'unknown')
              : (stateInfo as any).status,
            time: (stateInfo as any).result?.time_used,
            result: null
          };
        }
        
        // どちらもない場合はデフォルト
        return {
          id,
          name: id,
          status: submitting || isPolling ? 'pending' : 'unknown',
          time: null,
          result: null
        };
      }
    });
    
    console.log('🟢 表示用テストケース更新:', newDisplayCases);
    setDisplayJudgeCases(newDisplayCases);
  }, [JudgeCaseList, allResults, JudgeCaseState, submitting, isPolling]);

  // ポーリング進行状況が更新されたらテストケース状態を更新
  useEffect(() => {
    // TypeScriptエラー修正: progressがundefinedの可能性があるのでちゃんとチェック
    if (judgeStatus && judgeStatus.progress && judgeStatus.progress.JudgeCases) {
      console.log("🔄 テストケースの進行状況更新:", judgeStatus.progress.JudgeCases);
      setJudgeCaseState(prevState => ({
        ...prevState,
        ...judgeStatus.progress.JudgeCases
      }));
    }
  }, [judgeStatus]);

  // 最重要修正: テスト完了後の結果を内部ステートに反映する処理
  useEffect(() => {
    if (allResults && allResults.length > 0) {
      console.log("🔄 テスト結果を反映:", allResults);
      
      // 新しい内部状態オブジェクトを作成
      const newState = { ...JudgeCaseState };
      
      // 結果をループして内部状態に反映
      allResults.forEach(result => {
        if (!result || !result.judge_case || !result.judge_case.id) {
          console.warn("🔄 不正なテスト結果データ:", result);
          return;
        }
        
        const tcId = result.judge_case.id;
        newState[tcId] = {
          status: 'completed',
          result: {
            status: result.status,
            time_used: result.metadata?.time_used || 0,
            errorMessage: result.metadata?.runtime_error || result.metadata?.compile_error || '',
            actualOutput: result.metadata?.output || ''
          }
        };
      });
      
      // 状態を更新
      console.log("🔄 更新するテストケース状態:", newState);
      setJudgeCaseState(newState);
    }
  }, [allResults, JudgeCaseState]); // 明示的に依存関係を指定

  // テストケース行がクリックされたときの処理
  const handleRowClick = (JudgeCaseId: string) => {
    console.log("🔄 テストケース行クリック:", JudgeCaseId);
    
    // 結果が存在するかデバッグ出力
    const result = allResults?.find(r => r.judge_case.id === JudgeCaseId);
    
    if (result) {
      console.log("🔄 クリックされたテストケース結果:", result);
      onJudgeCaseSelect(result);
    } else {
      console.warn('該当するテスト結果が見つかりません:', JudgeCaseId);
    }
  };
  
  // 新規実行が開始されたらテストケース状態をリセット
  useEffect(() => {
    if (submitting) {
      console.log("🔄 テストケース状態をリセット - 実行開始");
      const initialState = JudgeCaseList.reduce((acc, id) => {
        acc[id] = { status: 'pending' };
        return acc;
      }, {} as Record<string, unknown>);
      setJudgeCaseState(initialState);
    }
  }, [submitting, JudgeCaseList]);

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

  // テーブルが空の場合
  if (JudgeCaseList.length === 0 && !submitting) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">テストケース情報がありません</p>
      </div>
    );
  }

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
          {/* ローディング表示 */}
          {(submitting || isPolling) && JudgeCaseList.length === 0 ? (
            <tr>
              <td colSpan={4} className="px-6 py-4 text-center text-sm text-gray-500">
                <div className="flex justify-center items-center space-x-2">
                  <svg className="animate-spin h-5 w-5 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>判定実行中...</span>
                </div>
              </td>
            </tr>
          ) : displayJudgeCases.length > 0 ? (
            // displayJudgeCasesからテーブル行を生成
            displayJudgeCases.map(tc => {
              const { bg, text, icon, label } = getStatusStyles(tc.status);
              const isSelected = selectedJudgeCaseId === tc.id;
              
              return (
                <tr 
                  key={tc.id} 
                  className={`hover:bg-gray-50 transition-colors ${isSelected ? 'bg-blue-50' : ''} ${tc.result ? 'cursor-pointer' : 'cursor-default'}`}
                  onClick={() => tc.result && handleRowClick(tc.id)}
                >
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{tc.name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${bg} ${text}`}>
                      <span className="mr-1">{icon}</span>
                      {label}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {tc.status === 'AC' ? '✅ 正解' : tc.status === 'WA' ? '❌ 不正解' : '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {tc.time != null ? `${tc.time} ms` : '-'}
                  </td>
                </tr>
              );
            })
          ) : (
            // テストケースがない場合
            <tr>
              <td colSpan={4} className="px-6 py-4 text-center text-sm text-gray-500">
                テストケースがありません
              </td>
            </tr>
          )}
        </tbody>
        <tfoot className="bg-gray-50">
          <tr>
            <td colSpan={4} className="px-6 py-3 text-center text-xs text-gray-500">
              {allResults && allResults.length > 0 ? 
                `${allResults.length}件のテスト結果あり` : 
                submitting || isPolling ? "テスト実行中..." : "テスト結果なし"}
            </td>
          </tr>
        </tfoot>
      </table>
      
      {/* 状態一覧をデバッグ表示 */}
      <div className="mt-4 p-2 border border-gray-200 rounded bg-gray-50 text-xs text-gray-600">
        <h4 className="font-bold">デバッグ情報</h4>
        <p>allResults: {allResults?.length || 0}件</p>
        <p>JudgeCaseList: {JudgeCaseList?.length || 0}件</p>
        <p>displayJudgeCases: {displayJudgeCases?.length || 0}件</p>
        <p>状態: {submitting ? '提出中' : isPolling ? 'ポーリング中' : '待機中'}</p>
      </div>
    </div>
  );
};