'use client';

import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';

const themes = [
  {
    id: 'classic',
    name: 'Classic',
    description: '基本的なデザインテーマ',
    color: 'from-indigo-600 to-purple-600'
  }
];

const demoPages = [
  {
    id: 'problem-list',
    name: '問題一覧',
    description: '問題のリスト表示画面',
    icon: '📝'
  },
  {
    id: 'problem-detail',
    name: '問題詳細',
    description: '個別問題の詳細とコードエディタ',
    icon: '📄'
  },
  {
    id: 'judge-result-success',
    name: 'ジャッジ結果（成功）',
    description: 'テスト成功時の結果表示',
    icon: '✅'
  },
  {
    id: 'judge-result-failed',
    name: 'ジャッジ結果（失敗）',
    description: 'テスト失敗時の結果表示',
    icon: '❌'
  },
  {
    id: 'judge-detail',
    name: 'ジャッジ詳細',
    description: '詳細なテスト結果とエラー情報',
    icon: '⚖️'
  }
];

export default function DemoPage() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600 mb-4">
          デザインデモ
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-300">
          様々なページレイアウトとデザインテーマを確認できます
        </p>
      </div>

      {/* Themes Section */}
      <div className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-700 rounded-xl shadow-sm p-8">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">テーマ一覧</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {themes.map((theme) => (
            <motion.div
              key={theme.id}
              className="bg-gray-50 dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-lg p-6 hover:shadow-md transition-all duration-200"
              whileHover={{ y: -5 }}
            >
              <div className={`w-full h-32 bg-gradient-to-r ${theme.color} rounded-lg mb-4 flex items-center justify-center`}>
                <span className="text-white text-2xl font-bold">{theme.name[0]}</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                {theme.name}
              </h3>
              <p className="text-gray-600 dark:text-gray-300 text-sm mb-4">
                {theme.description}
              </p>
              <div className="space-y-2">
                {demoPages.map((page) => (
                  <Link
                    key={page.id}
                    href={`/demo/${theme.id}/${page.id}`}
                    className="block px-3 py-2 text-sm text-gray-700 dark:text-gray-200 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-gray-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
                  >
                    <span className="mr-2">{page.icon}</span>
                    {page.name}
                  </Link>
                ))}
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Pages Overview */}
      <div className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-700 rounded-xl shadow-sm p-8">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">ページ一覧</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {demoPages.map((page, index) => (
            <motion.div
              key={page.id}
              className="bg-gray-50 dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-lg p-6"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
            >
              <div className="text-3xl mb-4">{page.icon}</div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                {page.name}
              </h3>
              <p className="text-gray-600 dark:text-gray-300 text-sm mb-4">
                {page.description}
              </p>
              <div className="space-y-2">
                {themes.map((theme) => (
                  <Link
                    key={theme.id}
                    href={`/demo/${theme.id}/${page.id}`}
                    className={`block px-3 py-2 text-sm text-white bg-gradient-to-r ${theme.color} rounded-lg hover:shadow-lg transition-all duration-200 text-center`}
                  >
                    {theme.name}で表示
                  </Link>
                ))}
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Quick Access */}
      <div className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-700 rounded-xl shadow-sm p-8">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">クイックアクセス</h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {demoPages.map((page) => (
            <Link
              key={page.id}
              href={`/demo/classic/${page.id}`}
              className="flex flex-col items-center p-4 bg-gray-50 dark:bg-slate-800 hover:bg-gray-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
            >
              <div className="text-2xl mb-2">{page.icon}</div>
              <div className="text-sm text-center text-gray-900 dark:text-white font-medium">
                {page.name}
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}