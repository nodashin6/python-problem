'use client';

import Link from "next/link";
import { motion } from "framer-motion";
import { useAuth } from "@/hooks/useAuth";
import { memo, useMemo } from "react";

const features = [
  {
    icon: "🚀",
    title: "実践的な問題",
    description: "初心者から上級者まで対応した段階的な問題セット"
  },
  {
    icon: "⚡",
    title: "リアルタイム判定",
    description: "コードを提出すると即座に正誤判定とフィードバック"
  },
  {
    icon: "📊",
    title: "進捗管理",
    description: "解いた問題数や正答率を可視化して学習をサポート"
  },
  {
    icon: "🎯",
    title: "数学問題対応",
    description: "数式表示に対応した高度なプログラミング問題"
  }
];

const FeatureCard = memo(({ feature, index }: { feature: typeof features[0], index: number }) => (
  <motion.div
    className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-700 rounded-xl shadow-sm hover:shadow-md hover:border-gray-300 dark:hover:border-slate-600 transition-all duration-200 text-center p-8"
    role="listitem"
    initial={{ opacity: 0, y: 30 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.6, delay: 1.0 + index * 0.1 }}
    whileHover={{ 
      y: -10,
      transition: { duration: 0.3 }
    }}
  >
    <div className="text-4xl mb-6" role="img" aria-label={`${feature.title}のアイコン`}>
      {feature.icon}
    </div>
    <h3 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">
      {feature.title}
    </h3>
    <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
      {feature.description}
    </p>
  </motion.div>
));

FeatureCard.displayName = 'FeatureCard';

export default function Home() {
  const { isAuthenticated, user } = useAuth();

  const heroVariants = useMemo(() => ({
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0 }
  }), []);

  const featuresVariants = useMemo(() => ({
    hidden: { opacity: 0 },
    visible: { opacity: 1 }
  }), []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-16" role="banner" aria-label="プログラミング学習プラットフォーム">
      {/* Hero Section */}
      <motion.div 
        className="text-center py-16"
        initial="hidden"
        animate="visible"
        variants={heroVariants}
        transition={{ duration: 0.8 }}
      >
        <motion.h1 
          className="text-4xl md:text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600 mb-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          Python Programming
          <br />
          Challenge Platform
        </motion.h1>
        
        <motion.p 
          className="text-xl text-gray-600 dark:text-gray-300 mb-10 max-w-3xl mx-auto leading-relaxed"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
        >
          プログラミングスキルを実践的に学べる、最新のオンライン学習プラットフォーム。
          <br />
          段階的な問題設計で、確実にスキルアップを実現します。
        </motion.p>

        <motion.div 
          className="flex flex-col sm:flex-row gap-4 justify-center items-center"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
        >
          {isAuthenticated ? (
            <>
              <Link 
                href="/problem/list" 
                className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-medium shadow-lg hover:from-indigo-700 hover:to-purple-700 hover:shadow-xl transform hover:scale-105 transition-all duration-200"
                aria-label="プログラミング問題一覧ページに移動"
              >
                問題を解く
                <svg className="w-5 h-5 ml-2 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </Link>
              <div className="text-gray-600 dark:text-gray-300">
                ようこそ、<span className="font-semibold text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600">{user?.display_name}</span>さん！
              </div>
            </>
          ) : (
            <>
              <Link 
                href={"/auth/login" as never} 
                className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-medium shadow-lg hover:from-indigo-700 hover:to-purple-700 hover:shadow-xl transform hover:scale-105 transition-all duration-200"
                aria-label="ログインページに移動してアカウントにサインイン"
              >
                今すぐ始める
                <svg className="w-5 h-5 ml-2 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </Link>
              <Link 
                href="/problem/list" 
                className="px-6 py-3 text-indigo-600 dark:text-indigo-400 bg-white dark:bg-slate-800 border border-indigo-200 dark:border-indigo-600 rounded-lg font-medium hover:bg-indigo-50 dark:hover:bg-slate-700 transition-all duration-200"
                aria-label="プログラミング問題一覧を閲覧"
              >
                問題を見る
              </Link>
            </>
          )}
        </motion.div>
      </motion.div>

      {/* Features Section */}
      <motion.div 
        className="py-16"
        initial="hidden"
        animate="visible"
        variants={featuresVariants}
        transition={{ duration: 0.8, delay: 0.8 }}
      >
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4" id="features-heading">
            なぜこのプラットフォームなのか？
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-300">
            効率的な学習のために設計された特徴をご紹介します
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8" role="list" aria-labelledby="features-heading">
          {features.map((feature, index) => (
            <FeatureCard key={feature.title} feature={feature} index={index} />
          ))}
        </div>
      </motion.div>

      {/* CTA Section */}
      <motion.div 
        className="py-16"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8, delay: 1.4 }}
      >
        <div className="max-w-4xl mx-auto">
          <div className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-700 rounded-xl shadow-sm text-center p-12 bg-gradient-to-r from-indigo-600 to-purple-600">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              今すぐ始めましょう
            </h2>
            <p className="text-indigo-100 text-lg mb-8">
              アカウント作成は無料です。すぐにプログラミング学習を開始できます。
            </p>
            {!isAuthenticated && (
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link 
                  href={"/auth/register" as never} 
                  className="px-8 py-4 bg-white text-indigo-600 rounded-lg font-medium hover:bg-gray-50 transition-all duration-200 shadow-lg hover:shadow-xl"
                  aria-label="新規アカウント作成ページに移動"
                >
                  無料でアカウント作成
                </Link>
                <Link 
                  href={"/auth/login" as never} 
                  className="px-8 py-4 border-2 border-white text-white rounded-lg font-medium hover:bg-white hover:text-indigo-600 transition-all duration-200"
                  aria-label="ログインページに移動"
                >
                  ログイン
                </Link>
              </div>
            )}
            <div className="mt-8 text-indigo-100">
              <p className="flex flex-col sm:flex-row sm:justify-center gap-4 text-sm">
                <span>✓ 無料で利用可能</span>
                <span>✓ 即座に開始</span>
                <span>✓ 豊富な問題セット</span>
              </p>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
