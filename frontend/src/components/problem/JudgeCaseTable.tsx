import React from 'react';
import { JudgeStatus } from '@/lib/api';

interface TestResult {
  judge_case: {
    id: string;
    name: string;
  };
  status: 'AC' | 'WA' | 'TLE' | 'RE' | 'CE' | 'PE' | 'PENDING';
  execution_time?: number;
  memory_usage?: number;
}

interface JudgeCaseTableProps {
  JudgeCaseList: string[];
  judgeStatus: JudgeStatus | null;
  submitting: boolean;
  isPolling: boolean;
  allResults: TestResult[];
  onJudgeCaseSelect: (result: TestResult) => void;
  selectedJudgeCaseId?: string;
}

const getStatusDisplay = (status: string) => {
  const statusMap = {
    'AC': { text: 'AC', color: 'text-green-600 bg-green-100' },
    'WA': { text: 'WA', color: 'text-red-600 bg-red-100' },
    'TLE': { text: 'TLE', color: 'text-yellow-600 bg-yellow-100' },
    'RE': { text: 'RE', color: 'text-orange-600 bg-orange-100' },
    'CE': { text: 'CE', color: 'text-purple-600 bg-purple-100' },
    'PE': { text: 'PE', color: 'text-blue-600 bg-blue-100' },
    'PENDING': { text: '実行中', color: 'text-gray-600 bg-gray-100' },
  };
  
  return statusMap[status as keyof typeof statusMap] || statusMap['PENDING'];
};

export const JudgeCaseTable: React.FC<JudgeCaseTableProps> = ({
  JudgeCaseList,
  submitting,
  isPolling,
  allResults,
  onJudgeCaseSelect,
  selectedJudgeCaseId
}) => {
  const getResultForCase = (caseId: string): TestResult | null => {
    return allResults.find(result => result.judge_case.id === caseId) || null;
  };

  const getStatusForCase = (caseId: string): string => {
    const result = getResultForCase(caseId);
    if (result) {
      return result.status;
    }
    
    // ジャッジ実行中の場合
    if (submitting || isPolling) {
      return 'PENDING';
    }
    
    return 'PENDING';
  };

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse border border-gray-300">
        <thead>
          <tr className="bg-gray-50">
            <th className="border border-gray-300 px-4 py-2 text-left">テストケース</th>
            <th className="border border-gray-300 px-4 py-2 text-center">ステータス</th>
            <th className="border border-gray-300 px-4 py-2 text-center">実行時間</th>
            <th className="border border-gray-300 px-4 py-2 text-center">メモリ使用量</th>
          </tr>
        </thead>
        <tbody>
          {JudgeCaseList.map((caseId, index) => {
            const result = getResultForCase(caseId);
            const status = getStatusForCase(caseId);
            const statusDisplay = getStatusDisplay(status);
            const isSelected = selectedJudgeCaseId === caseId;
            
            return (
              <tr 
                key={caseId}
                className={`
                  border-b hover:bg-gray-50 cursor-pointer transition-colors
                  ${isSelected ? 'bg-blue-50 border-blue-200' : ''}
                `}
                onClick={() => {
                  if (result) {
                    onJudgeCaseSelect(result);
                  }
                }}
              >
                <td className="border border-gray-300 px-4 py-2">
                  <div className="flex items-center">
                    <span className="font-medium">
                      テストケース {index + 1}
                    </span>
                    {isSelected && (
                      <span className="ml-2 text-blue-600 text-sm">(選択中)</span>
                    )}
                  </div>
                </td>
                <td className="border border-gray-300 px-4 py-2 text-center">
                  <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${statusDisplay.color}`}>
                    {statusDisplay.text}
                  </span>
                </td>
                <td className="border border-gray-300 px-4 py-2 text-center">
                  {result?.execution_time ? `${result.execution_time}ms` : '-'}
                </td>
                <td className="border border-gray-300 px-4 py-2 text-center">
                  {result?.memory_usage ? `${result.memory_usage}KB` : '-'}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
      
      {JudgeCaseList.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          テストケースがありません
        </div>
      )}
    </div>
  );
};