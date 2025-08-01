'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';

// Mock Problem Data
const mockProblem = {
  id: 1,
  title: "二分探索の実装",
  difficulty: "Medium",
  tags: ["アルゴリズム", "探索", "配列"],
  timeLimit: "1000ms",
  memoryLimit: "128MB",
  solved: 1250,
  acceptance: 78.5,
  description: `
ソートされた配列から特定の値を効率的に見つける二分探索アルゴリズムを実装してください。

## 問題説明

整数の配列 \`nums\` とターゲット値 \`target\` が与えられます。
配列 \`nums\` はソート済みです。
二分探索を使用して \`target\` の位置を見つけて返してください。
\`target\` が配列に存在しない場合は -1 を返してください。

時間計算量は O(log n) である必要があります。

## 制約

- 1 ≤ nums.length ≤ 10^4
- -10^4 ≤ nums[i], target ≤ 10^4
- nums の全ての要素は一意です
- nums は昇順でソートされています

## 入力形式

\`\`\`
nums = [1, 3, 5, 7, 9, 11, 13, 15]
target = 7
\`\`\`

## 出力形式

\`\`\`
3
\`\`\`

## 例

### 例 1
**入力:** nums = [1, 3, 5, 7, 9], target = 7  
**出力:** 3  
**説明:** ターゲット値 7 は配列のインデックス 3 にあります。

### 例 2
**入力:** nums = [1, 3, 5, 7, 9], target = 2  
**出力:** -1  
**説明:** ターゲット値 2 は配列に存在しません。

### 例 3
**入力:** nums = [1], target = 1  
**出力:** 0  
**説明:** ターゲット値 1 は配列のインデックス 0 にあります。
`,
  testCases: [
    {
      id: 1,
      input: "nums = [1, 3, 5, 7, 9]\ntarget = 7",
      expectedOutput: "3",
      explanation: "ターゲット値 7 は配列のインデックス 3 にあります。"
    },
    {
      id: 2,
      input: "nums = [1, 3, 5, 7, 9]\ntarget = 2",
      expectedOutput: "-1",
      explanation: "ターゲット値 2 は配列に存在しません。"
    },
    {
      id: 3,
      input: "nums = [1]\ntarget = 1",
      expectedOutput: "0",
      explanation: "ターゲット値 1 は配列のインデックス 0 にあります。"
    }
  ]
};

const languages = [
  { id: 'python', name: 'Python', template: `def binary_search(nums, target):
    # ここにコードを書いてください
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
    
    return -1` },
  { id: 'javascript', name: 'JavaScript', template: `function binarySearch(nums, target) {
    // ここにコードを書いてください
    let left = 0;
    let right = nums.length - 1;
    
    while (left <= right) {
        let mid = Math.floor((left + right) / 2);
        if (nums[mid] === target) {
            return mid;
        } else if (nums[mid] < target) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }
    
    return -1;
}` },
  { id: 'java', name: 'Java', template: `public class Solution {
    public int binarySearch(int[] nums, int target) {
        // ここにコードを書いてください
        int left = 0;
        int right = nums.length - 1;
        
        while (left <= right) {
            int mid = left + (right - left) / 2;
            if (nums[mid] == target) {
                return mid;
            } else if (nums[mid] < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        
        return -1;
    }
}` }
];

export default function ProblemDetailDemo() {
  const [selectedLanguage, setSelectedLanguage] = useState('python');
  const [code, setCode] = useState(languages[0].template);
  const [activeTab, setActiveTab] = useState('description');

  const handleLanguageChange = (languageId: string) => {
    const language = languages.find(lang => lang.id === languageId);
    if (language) {
      setSelectedLanguage(languageId);
      setCode(language.template);
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'Easy': return 'text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900/30';
      case 'Medium': return 'text-yellow-600 bg-yellow-100 dark:text-yellow-400 dark:bg-yellow-900/30';
      case 'Hard': return 'text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900/30';
      default: return 'text-gray-600 bg-gray-100 dark:text-gray-400 dark:bg-gray-900/30';
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <nav className="flex space-x-2 text-sm text-gray-500 dark:text-gray-400 mb-4">
          <Link href="/demo" className="hover:text-indigo-600 dark:hover:text-indigo-400">デモ</Link>
          <span>/</span>
          <Link href="/demo" className="hover:text-indigo-600 dark:hover:text-indigo-400">Classic</Link>
          <span>/</span>
          <Link href="/demo/classic/problem-list" className="hover:text-indigo-600 dark:hover:text-indigo-400">問題一覧</Link>
          <span>/</span>
          <span className="text-gray-900 dark:text-white">問題詳細</span>
        </nav>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              #{mockProblem.id}. {mockProblem.title}
            </h1>
            <span className={`px-3 py-1 text-sm font-semibold rounded-full ${getDifficultyColor(mockProblem.difficulty)}`}>
              {mockProblem.difficulty}
            </span>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-sm text-gray-600 dark:text-gray-400">
              {mockProblem.solved} 人が解決 • 正答率 {mockProblem.acceptance}%
            </div>
          </div>
        </div>

        {/* Tags and Constraints */}
        <div className="flex items-center justify-between mt-4">
          <div className="flex flex-wrap gap-2">
            {mockProblem.tags.map((tag, index) => (
              <span
                key={index}
                className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400 rounded-full"
              >
                {tag}
              </span>
            ))}
          </div>
          <div className="flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-400">
            <div className="flex items-center space-x-1">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{mockProblem.timeLimit}</span>
            </div>
            <div className="flex items-center space-x-1">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
              </svg>
              <span>{mockProblem.memoryLimit}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Panel - Problem Description */}
        <div className="space-y-6">
          {/* Tab Navigation */}
          <div className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-700 rounded-xl shadow-sm">
            <div className="border-b border-gray-200 dark:border-slate-700">
              <nav className="flex space-x-8 px-6">
                {[
                  { id: 'description', label: '問題説明', icon: '📝' },
                  { id: 'examples', label: 'テストケース', icon: '🧪' },
                  { id: 'submissions', label: '提出履歴', icon: '📊' }
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
              {activeTab === 'description' && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                  className="prose dark:prose-invert max-w-none"
                >
                  <div 
                    className="text-gray-900 dark:text-white leading-relaxed"
                    dangerouslySetInnerHTML={{ 
                      __html: mockProblem.description
                        .replace(/##\s+(.+)/g, '<h3 class="text-lg font-semibold mt-6 mb-3 text-gray-900 dark:text-white">$1</h3>')
                        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
                        .replace(/`([^`]+)`/g, '<code class="px-1 py-0.5 bg-gray-100 dark:bg-slate-800 rounded text-sm font-mono">$1</code>')
                        .replace(/```([^```]+)```/g, '<pre class="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm overflow-x-auto my-4"><code>$1</code></pre>')
                        .replace(/\n/g, '<br>')
                    }}
                  />
                </motion.div>
              )}

              {activeTab === 'examples' && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                  className="space-y-4"
                >
                  {mockProblem.testCases.map((testCase) => (
                    <div key={testCase.id} className="bg-gray-50 dark:bg-slate-800 rounded-lg p-4">
                      <h4 className="font-semibold text-gray-900 dark:text-white mb-3">
                        テストケース {testCase.id}
                      </h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <div className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">入力</div>
                          <pre className="bg-gray-900 text-green-400 p-3 rounded text-sm font-mono overflow-x-auto">
                            <code>{testCase.input}</code>
                          </pre>
                        </div>
                        <div>
                          <div className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">期待される出力</div>
                          <pre className="bg-gray-900 text-green-400 p-3 rounded text-sm font-mono overflow-x-auto">
                            <code>{testCase.expectedOutput}</code>
                          </pre>
                        </div>
                      </div>
                      {testCase.explanation && (
                        <div className="mt-3">
                          <div className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">説明</div>
                          <p className="text-sm text-gray-600 dark:text-gray-400">{testCase.explanation}</p>
                        </div>
                      )}
                    </div>
                  ))}
                </motion.div>
              )}

              {activeTab === 'submissions' && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                  className="text-center py-8"
                >
                  <div className="text-4xl mb-4">📊</div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    提出履歴
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300 mb-4">
                    この問題への提出履歴を確認できます
                  </p>
                  <Link
                    href="/demo/classic/judge-detail"
                    className="inline-flex px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                  >
                    詳細を見る
                  </Link>
                </motion.div>
              )}
            </div>
          </div>
        </div>

        {/* Right Panel - Code Editor */}
        <div className="space-y-6">
          {/* Language Selector */}
          <div className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-700 rounded-xl shadow-sm p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">コードエディタ</h3>
              <select
                value={selectedLanguage}
                onChange={(e) => handleLanguageChange(e.target.value)}
                className="px-3 py-2 border border-gray-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              >
                {languages.map(lang => (
                  <option key={lang.id} value={lang.id}>{lang.name}</option>
                ))}
              </select>
            </div>
            
            <div className="relative">
              <textarea
                value={code}
                onChange={(e) => setCode(e.target.value)}
                className="w-full h-96 p-4 bg-gray-900 text-green-400 font-mono text-sm rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="ここにコードを入力してください..."
              />
              <div className="absolute top-2 right-2 flex space-x-2">
                <button className="px-2 py-1 bg-slate-700 text-white text-xs rounded hover:bg-slate-600 transition-colors">
                  リセット
                </button>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex space-x-4">
            <button className="flex-1 px-6 py-3 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors">
              <div className="flex items-center justify-center space-x-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h.01M15 14h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>実行</span>
              </div>
            </button>
            <Link
              href="/demo/classic/judge-result-success"
              className="flex-1 px-6 py-3 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors"
            >
              <div className="flex items-center justify-center space-x-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
                <span>提出</span>
              </div>
            </Link>
          </div>

          {/* Code Output */}
          <div className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-700 rounded-xl shadow-sm p-4">
            <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">実行結果</h4>
            <div className="bg-gray-900 text-white p-4 rounded-lg font-mono text-sm">
              <div className="text-gray-500 mb-2"># 実行待機中...</div>
              <div className="text-green-400">
                コードを実行するには「実行」ボタンをクリックしてください
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}