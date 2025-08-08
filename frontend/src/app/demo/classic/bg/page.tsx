'use client';

import React from 'react';
import { motion } from 'framer-motion';

export default function BackgroundDemoPage() {
  return (
    <div className="min-h-screen p-8">
      {/* Header */}
      <div className="mb-8">
        <motion.h1 
          className="text-4xl font-bold text-gray-900 dark:text-white mb-4"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          背景アニメーション デモ
        </motion.h1>
        <motion.p 
          className="text-lg text-gray-600 dark:text-gray-300 mb-6"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          エレガントで動的な背景アニメーションのテストページです。
        </motion.p>
      </div>

      {/* Content Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <motion.div 
          className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-3">
            グラデーション球体
          </h2>
          <p className="text-gray-600 dark:text-gray-300">
            紫からインディゴ、青へと変化する美しいグラデーション球体が滑らかに浮遊しています。
          </p>
        </motion.div>

        <motion.div 
          className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-3">
            流れる線
          </h2>
          <p className="text-gray-600 dark:text-gray-300">
            SVGパスアニメーションによる波状の線が画面を横切って流れ、動的な印象を演出します。
          </p>
        </motion.div>

        <motion.div 
          className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.5 }}
        >
          <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-3">
            微細なパーティクル
          </h2>
          <p className="text-gray-600 dark:text-gray-300">
            小さなパーティクルがランダムに移動し、フェードイン/アウトしながら空間に深みを与えます。
          </p>
        </motion.div>
      </div>

      {/* Visual Test Area */}
      <motion.div 
        className="bg-transparent border-2 border-dashed border-purple-300/50 dark:border-purple-400/30 rounded-3xl p-8 mb-8 min-h-[200px]"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.6 }}
      >
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4 text-center">
          🎨 背景アニメーション表示エリア
        </h2>
        <p className="text-center text-gray-600 dark:text-gray-300 mb-4">
          この透明エリアで背景アニメーションが確認できます
        </p>
        <div className="text-center text-sm text-gray-500 dark:text-gray-400">
          動く球体、流れる線、パーティクルが見えるはずです
        </div>
      </motion.div>

      {/* Background Info */}
      <motion.div 
        className="bg-gradient-to-r from-purple-500/20 via-indigo-500/20 to-blue-500/20 backdrop-blur-sm rounded-3xl p-8 mb-8"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.7 }}
      >
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
          背景アニメーションの特徴
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-2">
              同系色パレット
            </h3>
            <ul className="text-gray-600 dark:text-gray-300 space-y-1">
              <li>• Purple (#9333ea) - メインアクセント</li>
              <li>• Indigo (#4f46e5) - 中間色</li>
              <li>• Blue (#3b82f6) - 涼しい色調</li>
            </ul>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-2">
              パフォーマンス最適化
            </h3>
            <ul className="text-gray-600 dark:text-gray-300 space-y-1">
              <li>• GPU加速対応のCSS Transform</li>
              <li>• 適切な透明度で軽量化</li>
              <li>• Framer Motionによるスムーズなアニメーション</li>
            </ul>
          </div>
        </div>
      </motion.div>

      {/* Interactive Elements */}
      <div className="space-y-4">
        <motion.h2 
          className="text-2xl font-bold text-gray-900 dark:text-white"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.7 }}
        >
          インタラクティブ要素
        </motion.h2>
        
        <div className="flex flex-wrap gap-4">
          <motion.button
            className="px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-xl font-semibold shadow-lg hover:shadow-xl"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.8 }}
          >
            アニメーション確認
          </motion.button>
          
          <motion.button
            className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-blue-600 text-white rounded-xl font-semibold shadow-lg hover:shadow-xl"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.9 }}
          >
            パフォーマンステスト
          </motion.button>
          
          <motion.button
            className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-semibold shadow-lg hover:shadow-xl"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 1.0 }}
          >
            色彩調和テスト
          </motion.button>
        </div>
      </div>

      {/* Technical Details */}
      <motion.div 
        className="mt-12 bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm rounded-2xl p-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 1.1 }}
      >
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
          技術的詳細
        </h2>
        <div className="text-sm text-gray-600 dark:text-gray-300 space-y-2">
          <p><strong>フレームワーク:</strong> Framer Motion + React</p>
          <p><strong>アニメーション:</strong> CSS Transform, SVG Path Animation</p>
          <p><strong>レスポンシブ:</strong> Tailwind CSS Breakpoints</p>
          <p><strong>パフォーマンス:</strong> Hardware Acceleration, Optimized Opacity</p>
          <p><strong>互換性:</strong> Light/Dark Mode Support</p>
        </div>
      </motion.div>
    </div>
  );
}