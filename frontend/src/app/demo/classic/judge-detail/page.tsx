'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';

// Mock Data
const mockSubmissions = [
  {
    id: "SUB123456789",
    problemId: 1,
    problemTitle: "二分探索の実装",
    status: "Accepted",
    score: 100,
    runtime: "45ms",
    memory: "12.8MB",
    language: "Python",
    submittedAt: "2024-01-15 14:30:25",
    testCasesPassed: 8,
    testCasesTotal: 8
  },
  {
    id: "SUB123456790",
    problemId: 1,
    problemTitle: "二分探索の実装",
    status: "Wrong Answer",
    score: 37,
    runtime: "38ms",
    memory: "13.2MB",
    language: "Python",
    submittedAt: "2024-01-15 13:45:12",
    testCasesPassed: 3,
    testCasesTotal: 8
  },
  {
    id: "SUB123456788",
    problemId: 1,
    problemTitle: "二分探索の実装",
    status: "Time Limit Exceeded",
    score: 25,
    runtime: "> 2000ms",
    memory: "15.1MB",
    language: "Python",
    submittedAt: "2024-01-15 13:15:45",
    testCasesPassed: 2,
    testCasesTotal: 8
  },
  {
    id: "SUB123456787",
    problemId: 1,
    problemTitle: "二分探索の実装",
    status: "Runtime Error",
    score: 0,
    runtime: "-",
    memory: "-",
    language: "Python",
    submittedAt: "2024-01-15 12:58:33",
    testCasesPassed: 0,
    testCasesTotal: 8
  },
  {
    id: "SUB123456786",
    problemId: 1,
    problemTitle: "二分探索の実装",
    status: "Wrong Answer",
    score: 12,
    runtime: "52ms",
    memory: "14.3MB",
    language: "Python",
    submittedAt: "2024-01-15 12:30:15",
    testCasesPassed: 1,
    testCasesTotal: 8
  }
];

const mockStats = {
  totalSubmissions: 15,
  acceptedSubmissions: 1,
  acceptanceRate: 6.7,
  bestRuntime: "45ms",
  averageRuntime: "267ms",
  firstSolvedAt: "2024-01-15 14:30:25",
  attempts: 15,
  timeSpent: "2h 15m"
};

const mockTestCaseDetails = {
  submissionId: "SUB123456789",
  testCases: [
    { id: 1, status: "Passed", runtime: "12ms", memory: "11.2MB", input: "nums = [1, 3, 5, 7, 9], target = 7", expectedOutput: "3", actualOutput: "3" },
    { id: 2, status: "Passed", runtime: "8ms", memory: "11.0MB", input: "nums = [1, 3, 5, 7, 9], target = 2", expectedOutput: "-1", actualOutput: "-1" },
    { id: 3, status: "Passed", runtime: "15ms", memory: "12.1MB", input: "nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], target = 5", expectedOutput: "4", actualOutput: "4" },
    { id: 4, status: "Passed", runtime: "18ms", memory: "12.3MB", input: "nums = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20], target = 14", expectedOutput: "6", actualOutput: "6" },
    { id: 5, status: "Passed", runtime: "20ms", memory: "12.5MB", input: "nums = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19], target = 25", expectedOutput: "-1", actualOutput: "-1" },
    { id: 6, status: "Passed", runtime: "10ms", memory: "11.5MB", input: "nums = [10, 20, 30, 40, 50], target = 30", expectedOutput: "2", actualOutput: "2" },
    { id: 7, status: "Passed", runtime: "5ms", memory: "10.8MB", input: "nums = [1], target = 1", expectedOutput: "0", actualOutput: "0" },
    { id: 8, status: "Passed", runtime: "3ms", memory: "10.5MB", input: "nums = [100], target = 50", expectedOutput: "-1", actualOutput: "-1" }
  ]
};

export default function JudgeDetailDemo() {
  const [activeTab, setActiveTab] = useState('submissions');
  // const [selectedSubmission, setSelectedSubmission] = useState<string | null>(null);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Accepted':
        return 'text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900/30';
      case 'Wrong Answer':
        return 'text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900/30';
      case 'Time Limit Exceeded':
        return 'text-orange-600 bg-orange-100 dark:text-orange-400 dark:bg-orange-900/30';
      case 'Runtime Error':
        return 'text-purple-600 bg-purple-100 dark:text-purple-400 dark:bg-purple-900/30';
      case 'Passed':
        return 'text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900/30';
      default:
        return 'text-gray-600 bg-gray-100 dark:text-gray-400 dark:bg-gray-900/30';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'Accepted':
      case 'Passed':
        return (
          <svg className="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        );
      case 'Wrong Answer':
        return (
          <svg className="w-5 h-5 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        );
      case 'Time Limit Exceeded':
        return (
          <svg className="w-5 h-5 text-orange-600 dark:text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      case 'Runtime Error':
        return (
          <svg className="w-5 h-5 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      default:
        return (
          <svg className="w-5 h-5 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div>
        <nav className="flex space-x-2 text-sm text-gray-500 dark:text-gray-400 mb-4">
          <Link href="/demo" className="hover:text-indigo-600 dark:hover:text-indigo-400">デモ</Link>
          <span>/</span>
          <Link href="/demo" className="hover:text-indigo-600 dark:hover:text-indigo-400">Classic</Link>
          <span>/</span>
          <span className="text-gray-900 dark:text-white">ジャッジ詳細</span>
        </nav>
        
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              提出履歴と詳細分析
            </h1>
            <p className="text-gray-600 dark:text-gray-300">
              #{mockSubmissions[0].problemId}. {mockSubmissions[0].problemTitle}
            </p>
          </div>
          <Link
            href="/demo/classic/problem-detail"
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            問題に戻る
          </Link>
        </div>
      </div>

      {/* Stats Overview */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-700 rounded-xl shadow-sm p-8"
      >
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6">統計情報</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600 mb-1">{mockStats.totalSubmissions}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">合計提出回数</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600 mb-1">{mockStats.acceptedSubmissions}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">正解数</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-600 mb-1">{mockStats.acceptanceRate}%</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">正答率</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-indigo-600 mb-1">{mockStats.bestRuntime}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">最高実行時間</div>
          </div>
        </div>
        <div className="mt-6 pt-6 border-t border-gray-200 dark:border-slate-700">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600 dark:text-gray-400">初回正解:</span>
              <span className="text-gray-900 dark:text-white">{mockStats.firstSolvedAt}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600 dark:text-gray-400">挑戦回数:</span>
              <span className="text-gray-900 dark:text-white">{mockStats.attempts} 回</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600 dark:text-gray-400">所要時間:</span>
              <span className="text-gray-900 dark:text-white">{mockStats.timeSpent}</span>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Detailed Results */}
      <div className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-700 rounded-xl shadow-sm">
        <div className="border-b border-gray-200 dark:border-slate-700">
          <nav className="flex space-x-8 px-6">
            {[
              { id: 'submissions', label: '提出履歴', icon: '📊' },
              { id: 'analysis', label: 'パフォーマンス分析', icon: '📈' },
              { id: 'testcases', label: 'テストケース詳細', icon: '🧪' }
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
          {activeTab === 'submissions' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-slate-700">
                  <thead className="bg-gray-50 dark:bg-slate-800">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        提出ID
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        ステータス
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        スコア
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        実行時間
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        メモリ
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        テストケース
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        提出日時
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        操作
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-slate-900 divide-y divide-gray-200 dark:divide-slate-700">
                    {mockSubmissions.map((submission, index) => (
                      <motion.tr
                        key={submission.id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.2, delay: index * 0.05 }}
                        className="hover:bg-gray-50 dark:hover:bg-slate-800"
                      >
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900 dark:text-white">
                          {submission.id.slice(-6)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center space-x-2">
                            {getStatusIcon(submission.status)}
                            <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(submission.status)}`}>
                              {submission.status}
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <span className={`font-semibold ${
                            submission.score === 100 ? 'text-green-600' : 
                            submission.score >= 50 ? 'text-yellow-600' : 'text-red-600'
                          }`}>
                            {submission.score}/100
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white font-mono">
                          {submission.runtime}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white font-mono">
                          {submission.memory}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                          {submission.testCasesPassed}/{submission.testCasesTotal}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                          {submission.submittedAt}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <div className="flex space-x-2">
                            <Link
                              href={submission.status === 'Accepted' 
                                ? '/demo/classic/judge-result-success' 
                                : '/demo/classic/judge-result-failed'
                              }
                              className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-900 dark:hover:text-indigo-300"
                            >
                              詳細
                            </Link>
                          </div>
                        </td>
                      </motion.tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </motion.div>
          )}

          {activeTab === 'analysis' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className="space-y-8"
            >
              {/* Performance Chart Mock */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">実行時間の推移</h3>
                <div className="bg-gray-50 dark:bg-slate-800 rounded-lg p-6">
                  <div className="flex items-end space-x-2 h-40">
                    {mockSubmissions.reverse().map((submission, index) => {
                      const height = submission.status === 'Runtime Error' ? 5 : 
                        submission.runtime === '> 2000ms' ? 160 :
                        Math.max(10, parseInt(submission.runtime) / 2);
                      
                      return (
                        <div key={submission.id} className="flex flex-col items-center">
                          <div
                            className={`w-8 rounded-t ${
                              submission.status === 'Accepted' ? 'bg-green-500' :
                              submission.status === 'Wrong Answer' ? 'bg-red-500' :
                              submission.status === 'Time Limit Exceeded' ? 'bg-orange-500' :
                              'bg-purple-500'
                            }`}
                            style={{ height: `${height}px` }}
                          />
                          <div className="text-xs text-gray-600 dark:text-gray-400 mt-2 transform -rotate-45">
                            #{index + 1}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                  <div className="mt-4 flex justify-center space-x-4 text-sm">
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-green-500 rounded"></div>
                      <span className="text-gray-600 dark:text-gray-400">正解</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-red-500 rounded"></div>
                      <span className="text-gray-600 dark:text-gray-400">不正解</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-orange-500 rounded"></div>
                      <span className="text-gray-600 dark:text-gray-400">時間制限</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-purple-500 rounded"></div>
                      <span className="text-gray-600 dark:text-gray-400">実行エラー</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Success Rate */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">学習の進歩</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-gray-50 dark:bg-slate-800 rounded-lg p-6">
                    <h4 className="font-semibold text-gray-900 dark:text-white mb-3">エラーパターン分析</h4>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600 dark:text-gray-400">Wrong Answer</span>
                        <span className="text-sm font-semibold text-red-600">40%</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600 dark:text-gray-400">Time Limit Exceeded</span>
                        <span className="text-sm font-semibold text-orange-600">20%</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600 dark:text-gray-400">Runtime Error</span>
                        <span className="text-sm font-semibold text-purple-600">13%</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600 dark:text-gray-400">Accepted</span>
                        <span className="text-sm font-semibold text-green-600">27%</span>
                      </div>
                    </div>
                  </div>
                  <div className="bg-gray-50 dark:bg-slate-800 rounded-lg p-6">
                    <h4 className="font-semibold text-gray-900 dark:text-white mb-3">改善ポイント</h4>
                    <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                      <li>• 境界条件の処理を見直す</li>
                      <li>• アルゴリズムの時間計算量を最適化</li>
                      <li>• エッジケースでのテストを強化</li>
                      <li>• コードレビューの実施</li>
                    </ul>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 'testcases' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              <div className="mb-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  テストケース詳細 (最新の正解提出: {mockTestCaseDetails.submissionId})
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  すべてのテストケースが正常に通過しました
                </p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {mockTestCaseDetails.testCases.map((testCase, index) => (
                  <motion.div
                    key={testCase.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.2, delay: index * 0.05 }}
                    className="bg-gray-50 dark:bg-slate-800 rounded-lg p-4"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="text-sm font-semibold text-gray-900 dark:text-white">
                        テストケース {testCase.id}
                      </h4>
                      <div className="flex items-center space-x-2">
                        <svg className="w-4 h-4 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        <span className="text-xs text-green-600 dark:text-green-400 font-semibold">PASSED</span>
                      </div>
                    </div>
                    
                    <div className="space-y-3">
                      <div>
                        <div className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">入力</div>
                        <pre className="bg-gray-900 text-green-400 p-2 rounded text-xs font-mono overflow-x-auto">
                          <code>{testCase.input}</code>
                        </pre>
                      </div>
                      <div className="grid grid-cols-2 gap-2">
                        <div>
                          <div className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">期待値</div>
                          <pre className="bg-gray-900 text-green-400 p-2 rounded text-xs font-mono">
                            <code>{testCase.expectedOutput}</code>
                          </pre>
                        </div>
                        <div>
                          <div className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">出力</div>
                          <pre className="bg-gray-900 text-green-400 p-2 rounded text-xs font-mono">
                            <code>{testCase.actualOutput}</code>
                          </pre>
                        </div>
                      </div>
                      <div className="flex justify-between text-xs text-gray-600 dark:text-gray-400">
                        <span>実行時間: {testCase.runtime}</span>
                        <span>メモリ: {testCase.memory}</span>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}