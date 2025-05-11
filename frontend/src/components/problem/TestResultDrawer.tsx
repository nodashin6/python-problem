import { useEffect, useRef } from 'react';
import { TestResult } from './TestResultCard';

type TestResultDrawerProps = {
  isOpen: boolean;
  onClose: () => void;
  result?: TestResult | null;
};

export const TestResultDrawer = ({ isOpen, onClose, result }: TestResultDrawerProps) => {
  const drawerRef = useRef<HTMLDivElement>(null);

  // 外側クリックでドロワーを閉じる
  useEffect(() => {
    const handleOutsideClick = (event: MouseEvent) => {
      if (drawerRef.current && !drawerRef.current.contains(event.target as Node)) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleOutsideClick);
    }

    return () => {
      document.removeEventListener('mousedown', handleOutsideClick);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  // ステータスに基づいたスタイルを設定
  let statusColor = 'bg-gray-100';
  let statusText = '未実行';
  let statusBadge = 'text-gray-600 bg-gray-100';

  if (result) {
    if (result.status === 'AC') {
      statusColor = 'bg-green-50';
      statusText = '正解';
      statusBadge = 'text-green-700 bg-green-100';
    } else if (result.status === 'WA') {
      statusColor = 'bg-red-50';
      statusText = '不正解';
      statusBadge = 'text-red-700 bg-red-100';
    } else if (result.status === 'RE') {
      statusColor = 'bg-orange-50';
      statusText = '実行エラー';
      statusBadge = 'text-orange-700 bg-orange-100';
    } else if (result.status === 'TLE') {
      statusColor = 'bg-yellow-50';
      statusText = '時間超過';
      statusBadge = 'text-yellow-700 bg-yellow-100';
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-30 z-50 flex justify-end">
      <div 
        ref={drawerRef}
        className={`w-full max-w-md ${statusColor} h-full shadow-xl p-6 overflow-auto transform transition-transform duration-300 ease-in-out`}
        style={{ transform: isOpen ? 'translateX(0)' : 'translateX(100%)' }}
      >
        {/* ヘッダー */}
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-xl font-bold">
            テストケース{result?.test_case.id ? ` ${result.test_case.id}` : ''}の結果
          </h3>
          <button 
            onClick={onClose}
            className="p-2 rounded-full hover:bg-gray-200 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {result ? (
          <div className="space-y-6">
            {/* ステータスバッジ */}
            <div className="flex items-center space-x-2">
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${statusBadge}`}>
                {statusText}
              </span>
              {result.metadata.time_used && (
                <span className="text-gray-500 text-sm">
                  実行時間: {result.metadata.time_used} ms
                </span>
              )}
            </div>
            
            {/* 入力 */}
            <div>
              <h4 className="font-semibold text-gray-700 mb-1">入力:</h4>
              <pre className="bg-gray-800 text-green-400 p-3 rounded overflow-x-auto">
                {result.test_case.stdin.content}
              </pre>
            </div>
            
            {/* 期待される出力 */}
            <div>
              <h4 className="font-semibold text-gray-700 mb-1">期待される出力:</h4>
              <pre className="bg-gray-800 text-green-400 p-3 rounded overflow-x-auto">
                {result.test_case.stdout.content}
              </pre>
            </div>
            
            {/* 実際の出力 */}
            <div>
              <h4 className="font-semibold text-gray-700 mb-1">あなたの出力:</h4>
              <pre className="bg-gray-800 text-amber-400 p-3 rounded overflow-x-auto">
                {result.metadata.output || '(出力なし)'}
              </pre>
            </div>
            
            {/* エラーメッセージ(存在する場合) */}
            {(result.metadata.runtime_error || result.metadata.compile_error) && (
              <div>
                <h4 className="font-semibold text-red-600 mb-1">エラー:</h4>
                <pre className="bg-red-50 text-red-700 p-3 rounded overflow-x-auto border border-red-200">
                  {result.metadata.runtime_error || result.metadata.compile_error}
                </pre>
              </div>
            )}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-64">
            <svg className="w-16 h-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M12 14h.01M17 21H7a2 2 0 01-2-2V5a2 2 0 012-2h10a2 2 0 012 2v14a2 2 0 01-2 2z" />
            </svg>
            <p className="text-gray-500 mt-4">テストケースが選択されていません</p>
          </div>
        )}
      </div>
    </div>
  );
};