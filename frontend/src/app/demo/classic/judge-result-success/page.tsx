'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';

// Mock Data
const mockJudgeResult = {
  submissionId: "SUB123456789",
  problemId: 1,
  problemTitle: "二分探索の実装",
  status: "Accepted",
  totalScore: 100,
  maxScore: 100,
  runtime: "45ms",
  memory: "12.8MB",
  language: "Python",
  submittedAt: "2024-01-15 14:30:25",
  testCasesTotal: 8,
  testCasesPassed: 8,
  code: `def binary_search(nums, target):
    left = 0
    right = len(nums) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1

# テスト用のコード
if __name__ == "__main__":
    nums = [1, 3, 5, 7, 9, 11, 13, 15]
    target = 7
    result = binary_search(nums, target)
    print(f"Target {target} found at index: {result}")`,
  testCases: [
    {
      id: 1,
      status: "Passed",
      input: "nums = [1, 3, 5, 7, 9]\ntarget = 7",
      expectedOutput: "3",
      actualOutput: "3",
      runtime: "12ms",
      memory: "11.2MB"
    },
    {
      id: 2,
      status: "Passed",
      input: "nums = [1, 3, 5, 7, 9]\ntarget = 2",
      expectedOutput: "-1",
      actualOutput: "-1",
      runtime: "8ms",
      memory: "11.0MB"
    },
    {
      id: 3,
      status: "Passed",
      input: "nums = [1]\ntarget = 1",
      expectedOutput: "0",
      actualOutput: "0",
      runtime: "5ms",
      memory: "10.8MB"
    },
    {
      id: 4,
      status: "Passed",
      input: "nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]\ntarget = 5",
      expectedOutput: "4",
      actualOutput: "4",
      runtime: "15ms",
      memory: "12.1MB"
    },
    {
      id: 5,
      status: "Passed",
      input: "nums = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]\ntarget = 14",
      expectedOutput: "6",
      actualOutput: "6",
      runtime: "18ms",
      memory: "12.3MB"
    },
    {
      id: 6,
      status: "Passed",
      input: "nums = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]\ntarget = 25",
      expectedOutput: "-1",
      actualOutput: "-1",
      runtime: "20ms",
      memory: "12.5MB"
    },
    {
      id: 7,
      status: "Passed",
      input: "nums = [10, 20, 30, 40, 50]\ntarget = 30",
      expectedOutput: "2",
      actualOutput: "2",
      runtime: "10ms",
      memory: "11.5MB"
    },
    {
      id: 8,
      status: "Passed",
      input: "nums = [100]\ntarget = 50",
      expectedOutput: "-1",
      actualOutput: "-1",
      runtime: "3ms",
      memory: "10.5MB"
    }
  ]
};

export default function JudgeResultSuccessDemo() {
  const [activeTab, setActiveTab] = useState('summary');
  const [selectedTestCase, setSelectedTestCase] = useState<number | null>(null);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Accepted':
      case 'Passed':
        return 'text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900/30';
      default:
        return 'text-gray-600 bg-gray-100 dark:text-gray-400 dark:bg-gray-900/30';
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="text-center">
        <nav className="flex justify-center space-x-2 text-sm text-gray-500 dark:text-gray-400 mb-4">
          <Link href="/demo" className="hover:text-indigo-600 dark:hover:text-indigo-400">デモ</Link>
          <span>/</span>
          <Link href="/demo" className="hover:text-indigo-600 dark:hover:text-indigo-400">Classic</Link>
          <span>/</span>
          <span className="text-gray-900 dark:text-white">ジャッジ結果（成功）</span>
        </nav>
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <div className="w-20 h-20 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-10 h-10 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            提出成功！
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300">
            すべてのテストケースが通過しました
          </p>
        </motion.div>
      </div>

      {/* Result Summary */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-700 rounded-xl shadow-sm p-8"
      >
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            #{mockJudgeResult.problemId}. {mockJudgeResult.problemTitle}
          </h2>
          <div className="flex items-center justify-center space-x-4">
            <span className={`px-4 py-2 text-lg font-semibold rounded-full ${getStatusColor(mockJudgeResult.status)}`}>
              {mockJudgeResult.status}
            </span>
            <span className="text-2xl font-bold text-green-600">
              {mockJudgeResult.totalScore}/{mockJudgeResult.maxScore} 点
            </span>
          </div>
        </div>

        {/* Performance Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
          <div className="text-center">
            <div className="text-3xl font-bold text-indigo-600 mb-1">{mockJudgeResult.runtime}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">実行時間</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-600 mb-1">{mockJudgeResult.memory}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">メモリ使用量</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600 mb-1">
              {mockJudgeResult.testCasesPassed}/{mockJudgeResult.testCasesTotal}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">テストケース通過</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600 mb-1">{mockJudgeResult.language}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">使用言語</div>
          </div>
        </div>

        {/* Submission Info */}
        <div className="border-t border-gray-200 dark:border-slate-700 pt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">提出ID:</span>
              <span className="text-gray-900 dark:text-white font-mono">{mockJudgeResult.submissionId}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">提出日時:</span>
              <span className="text-gray-900 dark:text-white">{mockJudgeResult.submittedAt}</span>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Detailed Results */}
      <div className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-700 rounded-xl shadow-sm">
        <div className="border-b border-gray-200 dark:border-slate-700">
          <nav className="flex space-x-8 px-6">
            {[
              { id: 'summary', label: '概要', icon: '📊' },
              { id: 'testcases', label: 'テストケース', icon: '🧪' },
              { id: 'code', label: '提出コード', icon: '💻' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  flex items-center py-4 px-1 border-b-2 font-medium text-sm transition-colors
                  ${activeTab === tab.id
                    ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
                  }
                `}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'summary' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              <div className="text-center">
                <div className="text-6xl mb-4">🎉</div>
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                  完璧な解答です！
                </h3>
                <p className="text-gray-600 dark:text-gray-300 mb-6">
                  すべてのテストケースが正常に通過しました。効率的なアルゴリズムの実装ができています。
                </p>
              </div>

              <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-6">
                <h4 className="text-lg font-semibold text-green-800 dark:text-green-400 mb-3">
                  パフォーマンス分析
                </h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-green-700 dark:text-green-300">時間計算量:</span>
                    <span className="text-green-800 dark:text-green-400 font-mono">O(log n)</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-green-700 dark:text-green-300">空間計算量:</span>
                    <span className="text-green-800 dark:text-green-400 font-mono">O(1)</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-green-700 dark:text-green-300">実行時間:</span>
                    <span className="text-green-800 dark:text-green-400">平均 12.6ms (優秀)</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-green-700 dark:text-green-300">メモリ効率:</span>
                    <span className="text-green-800 dark:text-green-400">11.4MB (最適)</span>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Link
                  href="/demo/classic/problem-list"
                  className="flex items-center justify-center px-4 py-3 bg-gray-100 dark:bg-slate-800 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-200 dark:hover:bg-slate-700 transition-colors"
                >
                  <span className="mr-2">📝</span>
                  他の問題を解く
                </Link>
                <Link
                  href="/demo/classic/judge-detail"
                  className="flex items-center justify-center px-4 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                >
                  <span className="mr-2">📊</span>
                  詳細結果を見る
                </Link>
                <button className="flex items-center justify-center px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
                  <span className="mr-2">🔄</span>
                  再提出する
                </button>
              </div>
            </motion.div>
          )}

          {activeTab === 'testcases' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className="space-y-4"
            >
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                {mockJudgeResult.testCases.map((testCase) => (
                  <button
                    key={testCase.id}
                    onClick={() => setSelectedTestCase(testCase.id)}
                    className={`p-4 rounded-lg border-2 transition-all ${
                      selectedTestCase === testCase.id
                        ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20'
                        : 'border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-900/20 hover:border-green-300 dark:hover:border-green-700'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-900 dark:text-white">
                        Test {testCase.id}
                      </span>
                      <svg className="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                    <div className="text-xs text-gray-600 dark:text-gray-400">
                      {testCase.runtime} • {testCase.memory}
                    </div>
                  </button>
                ))}
              </div>

              {selectedTestCase && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2 }}
                  className="bg-gray-50 dark:bg-slate-800 rounded-lg p-6"
                >
                  {(() => {
                    const testCase = mockJudgeResult.testCases.find(tc => tc.id === selectedTestCase);
                    if (!testCase) return null;
                    
                    return (
                      <>
                        <div className="flex items-center justify-between mb-4">
                          <h4 className="text-lg font-semibold text-gray-900 dark:text-white">
                            テストケース {testCase.id}
                          </h4>
                          <span className={`px-3 py-1 text-sm font-semibold rounded-full ${getStatusColor(testCase.status)}`}>
                            {testCase.status}
                          </span>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          <div>
                            <div className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">入力</div>
                            <pre className="bg-gray-900 text-green-400 p-3 rounded text-xs font-mono overflow-x-auto">
                              <code>{testCase.input}</code>
                            </pre>
                          </div>
                          <div>
                            <div className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">期待される出力</div>
                            <pre className="bg-gray-900 text-green-400 p-3 rounded text-xs font-mono overflow-x-auto">
                              <code>{testCase.expectedOutput}</code>
                            </pre>
                          </div>
                          <div>
                            <div className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">実際の出力</div>
                            <pre className="bg-gray-900 text-green-400 p-3 rounded text-xs font-mono overflow-x-auto">
                              <code>{testCase.actualOutput}</code>
                            </pre>
                          </div>
                        </div>
                        <div className="mt-4 flex justify-between text-sm text-gray-600 dark:text-gray-400">
                          <span>実行時間: {testCase.runtime}</span>
                          <span>メモリ使用量: {testCase.memory}</span>
                        </div>
                      </>
                    );
                  })()}
                </motion.div>
              )}
            </motion.div>
          )}

          {activeTab === 'code' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              <div className="mb-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  提出されたコード ({mockJudgeResult.language})
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  提出日時: {mockJudgeResult.submittedAt}
                </p>
              </div>
              <div className="bg-gray-900 text-green-400 p-6 rounded-lg font-mono text-sm overflow-x-auto">
                <pre><code>{mockJudgeResult.code}</code></pre>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}