import React, { useEffect } from 'react';
import { JudgeCaseTable } from '@/components/problem/JudgeCaseTable';
import { TestResult } from '@/components/problem/TestResultCard';
import { TestResults } from '@/components/problem/TestResults';
import { JudgeStatus } from '@/lib/api';
import type { JudgeResponse, JudgeResult } from '@/types/judge';
import JudgeCaseDetails from '@/components/problem/JudgeCaseDetails';

interface JudgeResultSectionProps {
  isVisible: boolean;
  JudgeCaseList: string[];
  judgeStatus: JudgeStatus | null;
  submitting: boolean;
  isPolling: boolean;
  testResults?: TestResult[];
  result: JudgeResponse | null;
  selectedJudgeCase: TestResult | null;
  handleJudgeCaseSelect: (JudgeCase: TestResult) => void;
  onLoadJudgeCases: () => void;
}

export const JudgeResultSection: React.FC<JudgeResultSectionProps> = ({
  isVisible,
  JudgeCaseList,
  judgeStatus,
  submitting,
  isPolling,
  testResults,
  result,
  selectedJudgeCase,
  handleJudgeCaseSelect,
  onLoadJudgeCases
}) => {
  // 修正: APIのデータ構造変化に対応するためのデバッグ用ロガー
  useEffect(() => {
    if (result) {
      console.log('🌟 JudgeResultSection - result詳細:', {
        hasError: !!result.error,
        resultsType: typeof result.results,
        resultsIsArray: Array.isArray(result.results),
        resultsLength: Array.isArray(result.results) ? result.results.length : 'N/A'
      });
      
      if (result.results && Array.isArray(result.results)) {
        result.results.forEach((item, idx) => {
          console.log(`🌟 結果項目 ${idx}:`, {
            id: item.id,
            hasJudgeCase: !!item.judge_case,
            JudgeCaseId: item.judge_case?.id,
            status: item.status
          });
        });
      }
    }
  }, [result]);

  // 修正: テスト結果を適切に処理
  useEffect(() => {
    if (testResults && testResults.length > 0) {
      console.log('🌟 処理済みテスト結果:', testResults);
    }
  }, [testResults]);

  if (!isVisible) return null;
  
  // 本当にテスト結果があるか確認
  const hasTestResults = testResults && testResults.length > 0;
  
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
        
        {/* テスト結果がない場合に原因を表示 */}
        {judgeStatus?.status === 'completed' && (!testResults || testResults.length === 0) && !result?.error && (
          <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-yellow-700">
            <h3 className="font-semibold mb-1">注意</h3>
            <p className="text-sm">
              ジャッジは完了しましたが、テスト結果が取得できませんでした。APIの応答形式が想定と異なる可能性があります。
            </p>
            <div className="mt-2 text-xs bg-gray-50 p-2 rounded">
              <p className="font-bold">応答情報:</p>
              <p>JudgeStatus: {judgeStatus?.status}</p>
              <p>結果型: {result ? typeof result.results : 'なし'}</p>
              <p>エラー: {result?.error || 'なし'}</p>
            </div>
          </div>
        )}
        
        {/* テストケースがない場合のメッセージ */}
        {JudgeCaseList.length === 0 && !submitting && !isPolling && (
          <div className="text-center p-4">
            <p className="text-gray-500 mb-3">テストケース情報がありません</p>
            <button 
              onClick={() => {
                console.log('📊 テストケース取得ボタンクリック');
                onLoadJudgeCases();
              }}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              テストケース一覧を取得
            </button>
          </div>
        )}

        {/* テスト結果の状態をより詳細に表示 */}
        <div className="mb-4 p-3 bg-blue-50 border border-blue-100 rounded-lg text-blue-800">
          <h3 className="font-semibold mb-1">デバッグ情報</h3>
          <div className="text-xs">
            <p>テストケース数: {JudgeCaseList.length}</p>
            <p>提出中: {submitting ? 'はい' : 'いいえ'}</p>
            <p>ポーリング中: {isPolling ? 'はい' : 'いいえ'}</p>
            <p>テスト結果: {hasTestResults ? `${testResults?.length}件` : 'なし'}</p>
            <p>ジャッジステータス: {judgeStatus?.status || '不明'}</p>
          </div>
        </div>

        {/* テーブル表示の条件をシンプルに */}
        {(submitting || isPolling || JudgeCaseList.length > 0) && (
          <>
            <p className="text-sm text-gray-500 mb-2">
              {JudgeCaseList.length > 0 
                ? `${JudgeCaseList.length}件のテストケース` 
                : submitting || isPolling 
                  ? "判定実行中..." 
                  : "テストケースがありません"}
            </p>
            
            {/* テストケース一覧テーブル - 重要な修正 */}
            <JudgeCaseTable 
              JudgeCaseList={JudgeCaseList} 
              judgeStatus={judgeStatus} 
              submitting={submitting}  
              isPolling={isPolling}
              allResults={hasTestResults ? testResults : []}
              onJudgeCaseSelect={handleJudgeCaseSelect}
              selectedJudgeCaseId={selectedJudgeCase?.id}
            />
          </>
        )}
        
        {/* 選択されたテストケースの詳細表示 */}
        {selectedJudgeCase && (
          <JudgeCaseDetails
            JudgeCase={selectedJudgeCase}
            onClose={() => handleJudgeCaseSelect(selectedJudgeCase)}
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
