/**
 * AuthLayout Component
 * 認証ページ共通のレイアウトコンポーネント
 */

'use client';

import React from 'react';
import { motion } from 'framer-motion';

interface AuthLayoutProps {
  children: React.ReactNode;
  title: string;
  subtitle?: string;
  footerText?: string;
}

export function AuthLayout({ children, title, subtitle, footerText }: AuthLayoutProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 dark:from-slate-900 dark:via-slate-800 dark:to-purple-900">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-center min-h-screen py-8 sm:py-12">
          <div className="w-full max-w-md sm:max-w-lg">
            <motion.div 
              className="text-center mb-8"
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              <div className="w-16 h-16 sm:w-20 sm:h-20 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-xl">
                <span className="text-white font-bold text-lg sm:text-xl">PP</span>
              </div>
              <h1 className="text-3xl sm:text-4xl font-bold mb-3 bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                {title}
              </h1>
              {subtitle && (
                <p className="text-base sm:text-lg text-gray-600 dark:text-gray-300">
                  {subtitle}
                </p>
              )}
            </motion.div>
            
            {children}
            
            {footerText && (
              <motion.div 
                className="text-center mt-8"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.3 }}
              >
                <p className="text-sm sm:text-base text-gray-500 dark:text-gray-400">
                  {footerText}
                </p>
              </motion.div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default AuthLayout;