import React from 'react';

interface TestResult {
  judge_case: {
    id: string;
    name: string;
    input?: string;
    expected_output?: string;
  };
  status: 'AC' | 'WA' | 'TLE' | 'RE' | 'CE' | 'PE' | 'PENDING';
  output?: string;
  error_message?: string;
  execution_time?: number;
  memory_usage?: number;
}

interface JudgeCaseDetailsProps {
  JudgeCase: TestResult;
  onClose: () => void;
}

const JudgeCaseDetails: React.FC<JudgeCaseDetailsProps> = ({ JudgeCase, onClose }) => {
  const getStatusColor = (status: string) => {
    const statusMap = {
      'AC': 'text-green-600 bg-green-100',
      'WA': 'text-red-600 bg-red-100',
      'TLE': 'text-yellow-600 bg-yellow-100',
      'RE': 'text-orange-600 bg-orange-100',
      'CE': 'text-purple-600 bg-purple-100',
      'PE': 'text-blue-600 bg-blue-100',
      'PENDING': 'text-gray-600 bg-gray-100',
    };
    return statusMap[status as keyof typeof statusMap] || statusMap['PENDING'];
  };

  return (
    <div className="mt-6 border rounded-lg bg-white shadow-sm">
      <div className="flex items-center justify-between p-4 border-b bg-gray-50">
        <h3 className="text-lg font-semibold">
          {JudgeCase.judge_case.name || `テストケース ${JudgeCase.judge_case.id}`}
        </h3>
        <div className="flex items-center space-x-3">
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(JudgeCase.status)}`}>
            {JudgeCase.status}
          </span>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 p-1"
            aria-label="閉じる"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <div className="p-4 space-y-4">
        {/* 実行情報 */}
        {(JudgeCase.execution_time || JudgeCase.memory_usage) && (
          <div className="grid grid-cols-2 gap-4">
            {JudgeCase.execution_time && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  実行時間
                </label>
                <div className="text-sm text-gray-900 bg-gray-50 px-3 py-2 rounded">
                  {JudgeCase.execution_time}ms
                </div>
              </div>
            )}
            {JudgeCase.memory_usage && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  メモリ使用量
                </label>
                <div className="text-sm text-gray-900 bg-gray-50 px-3 py-2 rounded">
                  {JudgeCase.memory_usage}KB
                </div>
              </div>
            )}
          </div>
        )}

        {/* 入力データ */}
        {JudgeCase.judge_case.input && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              入力
            </label>
            <pre className="text-sm bg-gray-50 border p-3 rounded-md overflow-x-auto">
              {JudgeCase.judge_case.input}
            </pre>
          </div>
        )}

        {/* 期待される出力 */}
        {JudgeCase.judge_case.expected_output && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              期待される出力
            </label>
            <pre className="text-sm bg-gray-50 border p-3 rounded-md overflow-x-auto">
              {JudgeCase.judge_case.expected_output}
            </pre>
          </div>
        )}

        {/* 実際の出力 */}
        {JudgeCase.output && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              実際の出力
            </label>
            <pre className={`text-sm border p-3 rounded-md overflow-x-auto ${
              JudgeCase.status === 'AC' ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
            }`}>
              {JudgeCase.output}
            </pre>
          </div>
        )}

        {/* エラーメッセージ */}
        {JudgeCase.error_message && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              エラーメッセージ
            </label>
            <pre className="text-sm bg-red-50 border border-red-200 text-red-700 p-3 rounded-md overflow-x-auto">
              {JudgeCase.error_message}
            </pre>
          </div>
        )}

        {/* 結果が不明な場合 */}
        {JudgeCase.status === 'PENDING' && (
          <div className="text-center py-4">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
            <p className="mt-2 text-sm text-gray-600">実行中...</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default JudgeCaseDetails;