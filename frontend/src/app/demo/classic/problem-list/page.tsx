'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';

// Mock Data
const mockProblems = [
  {
    id: 1,
    title: "二分探索の実装",
    difficulty: "Medium",
    tags: ["アルゴリズム", "探索", "配列"],
    solved: 1250,
    acceptance: 78.5,
    description: "ソートされた配列から特定の値を効率的に見つける二分探索アルゴリズムを実装してください。時間計算量O(log n)で解くことが求められます。",
    timeLimit: "1000ms",
    memoryLimit: "128MB"
  },
  {
    id: 2,
    title: "動的プログラミング：フィボナッチ数列",
    difficulty: "Easy",
    tags: ["動的プログラミング", "数学", "再帰"],
    solved: 2100,
    acceptance: 85.2,
    description: "フィボナッチ数列のn番目の値を効率的に求めるプログラムを作成してください。メモ化を使用して効率的に計算することが重要です。",
    timeLimit: "500ms",
    memoryLimit: "64MB"
  },
  {
    id: 3,
    title: "グラフの最短経路問題",
    difficulty: "Hard",
    tags: ["グラフ", "最短経路", "Dijkstra", "アルゴリズム"],
    solved: 680,
    acceptance: 62.3,
    description: "重み付きグラフにおいて、2つのノード間の最短経路を求めるアルゴリズムを実装してください。ダイクストラ法を使用することを推奨します。",
    timeLimit: "2000ms",
    memoryLimit: "256MB"
  },
  {
    id: 4,
    title: "文字列パターンマッチング",
    difficulty: "Medium",
    tags: ["文字列", "パターンマッチング", "KMP"],
    solved: 890,
    acceptance: 71.8,
    description: "文字列内で特定のパターンを効率的に検索するアルゴリズムを実装してください。KMP法やRabin-Karp法の使用を検討してください。",
    timeLimit: "1500ms",
    memoryLimit: "128MB"
  },
  {
    id: 5,
    title: "ソートアルゴリズムの比較",
    difficulty: "Easy",
    tags: ["ソート", "アルゴリズム", "比較"],
    solved: 1850,
    acceptance: 89.3,
    description: "異なるソートアルゴリズム（バブルソート、選択ソート、挿入ソート）を実装し、それぞれの性能を比較してください。",
    timeLimit: "3000ms",
    memoryLimit: "128MB"
  },
  {
    id: 6,
    title: "木の走査アルゴリズム",
    difficulty: "Medium",
    tags: ["木", "走査", "再帰", "データ構造"],
    solved: 1120,
    acceptance: 76.4,
    description: "二分木に対して前順、中順、後順走査を実装してください。再帰的解法と反復的解法の両方を考慮してください。",
    timeLimit: "1000ms",
    memoryLimit: "128MB"
  },
  {
    id: 7,
    title: "動的配列の実装",
    difficulty: "Hard",
    tags: ["データ構造", "配列", "メモリ管理"],
    solved: 420,
    acceptance: 58.7,
    description: "サイズが動的に変更される配列データ構造を実装してください。要素の追加、削除、アクセスを効率的に行えるようにしてください。",
    timeLimit: "2000ms",
    memoryLimit: "256MB"
  },
  {
    id: 8,
    title: "ハッシュテーブルの実装",
    difficulty: "Hard",
    tags: ["ハッシュテーブル", "データ構造", "衝突処理"],
    solved: 365,
    acceptance: 54.2,
    description: "ハッシュテーブルを実装し、チェイン法またはオープンアドレス法で衝突を処理してください。動的リサイズも実装してください。",
    timeLimit: "2500ms",
    memoryLimit: "256MB"
  }
];

const difficultyStats = {
  Easy: { count: 2, color: 'text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900/30' },
  Medium: { count: 3, color: 'text-yellow-600 bg-yellow-100 dark:text-yellow-400 dark:bg-yellow-900/30' },
  Hard: { count: 3, color: 'text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900/30' }
};

export default function ProblemListDemo() {
  const [selectedDifficulty, setSelectedDifficulty] = useState('');
  const [selectedTag, setSelectedTag] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  const getDifficultyColor = (difficulty: string) => {
    return difficultyStats[difficulty as keyof typeof difficultyStats]?.color || 'text-gray-600 bg-gray-100 dark:text-gray-400 dark:bg-gray-900/30';
  };

  const filteredProblems = mockProblems.filter(problem => {
    const matchesDifficulty = !selectedDifficulty || problem.difficulty === selectedDifficulty;
    const matchesTag = !selectedTag || problem.tags.includes(selectedTag);
    const matchesSearch = !searchQuery || 
      problem.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      problem.description.toLowerCase().includes(searchQuery.toLowerCase());
    
    return matchesDifficulty && matchesTag && matchesSearch;
  });

  const allTags = Array.from(new Set(mockProblems.flatMap(p => p.tags))).sort();

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <nav className="flex space-x-2 text-sm text-gray-500 dark:text-gray-400 mb-2">
            <Link href="/demo" className="hover:text-indigo-600 dark:hover:text-indigo-400">デモ</Link>
            <span>/</span>
            <Link href="/demo" className="hover:text-indigo-600 dark:hover:text-indigo-400">Classic</Link>
            <span>/</span>
            <span className="text-gray-900 dark:text-white">問題一覧</span>
          </nav>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            問題一覧
          </h1>
          <p className="text-gray-600 dark:text-gray-300 mt-2">
            プログラミング問題を解いてスキルアップしましょう
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="text-sm text-gray-600 dark:text-gray-400">
            {filteredProblems.length} / {mockProblems.length} 問題
          </div>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-700 rounded-xl shadow-sm p-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">難易度別統計</h2>
        <div className="grid grid-cols-3 gap-4">
          {Object.entries(difficultyStats).map(([difficulty, stats]) => (
            <div key={difficulty} className="text-center">
              <div className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full ${stats.color} mb-2`}>
                {difficulty}
              </div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">{stats.count}</div>
              <div className="text-xs text-gray-600 dark:text-gray-400">問題</div>
            </div>
          ))}
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-700 rounded-xl shadow-sm p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              検索
            </label>
            <input
              type="text"
              placeholder="問題を検索..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              難易度
            </label>
            <select
              value={selectedDifficulty}
              onChange={(e) => setSelectedDifficulty(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option value="">すべての難易度</option>
              <option value="Easy">Easy</option>
              <option value="Medium">Medium</option>
              <option value="Hard">Hard</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              タグ
            </label>
            <select
              value={selectedTag}
              onChange={(e) => setSelectedTag(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option value="">すべてのタグ</option>
              {allTags.map(tag => (
                <option key={tag} value={tag}>{tag}</option>
              ))}
            </select>
          </div>
          <div className="flex items-end">
            <button
              onClick={() => {
                setSelectedDifficulty('');
                setSelectedTag('');
                setSearchQuery('');
              }}
              className="w-full px-4 py-2 text-gray-700 dark:text-gray-200 bg-gray-100 dark:bg-slate-800 hover:bg-gray-200 dark:hover:bg-slate-700 rounded-lg transition-colors"
            >
              リセット
            </button>
          </div>
        </div>
      </div>

      {/* Problems List */}
      <div className="space-y-4">
        {filteredProblems.map((problem, index) => (
          <motion.div
            key={problem.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
            className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-700 rounded-xl shadow-sm hover:shadow-md transition-shadow p-6"
          >
            <div className="flex justify-between items-start mb-4">
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-2">
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                    #{problem.id}. {problem.title}
                  </h3>
                  <span className={`px-3 py-1 text-xs font-semibold rounded-full ${getDifficultyColor(problem.difficulty)}`}>
                    {problem.difficulty}
                  </span>
                </div>
                <p className="text-gray-600 dark:text-gray-300 mb-3 leading-relaxed">
                  {problem.description}
                </p>
                <div className="flex flex-wrap gap-2 mb-3">
                  {problem.tags.map((tag, tagIndex) => (
                    <span
                      key={tagIndex}
                      className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400 rounded-full"
                    >
                      {tag}      
                    </span>
                  ))}
                </div>
                <div className="flex items-center space-x-6 text-sm text-gray-600 dark:text-gray-400">
                  <div className="flex items-center space-x-1">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span>制限時間: {problem.timeLimit}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                    </svg>
                    <span>メモリ制限: {problem.memoryLimit}</span>
                  </div>
                </div>
              </div>
              <div className="flex flex-col items-end space-y-3 ml-6">
                <div className="text-right text-sm">
                  <div className="text-gray-900 dark:text-white font-semibold">
                    {problem.solved} 人が解決
                  </div>
                  <div className="text-gray-600 dark:text-gray-400">
                    正答率: {problem.acceptance}%
                  </div>
                </div>
                <Link
                  href={`/demo/classic/problem-detail?id=${problem.id}`}
                  className="px-6 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-medium hover:from-indigo-700 hover:to-purple-700 hover:shadow-lg transform hover:scale-105 transition-all duration-200"
                >
                  挑戦する
                </Link>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Empty State */}
      {filteredProblems.length === 0 && (
        <div className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-700 rounded-xl shadow-sm p-12 text-center">
          <div className="text-6xl mb-4">🔍</div>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            検索条件に一致する問題が見つかりません
          </h3>
          <p className="text-gray-600 dark:text-gray-300 mb-4">
            検索条件を変更するか、フィルターをリセットしてください
          </p>
          <button
            onClick={() => {
              setSelectedDifficulty('');
              setSelectedTag('');
              setSearchQuery('');
            }}
            className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            フィルターをリセット
          </button>
        </div>
      )}
    </div>
  );
}