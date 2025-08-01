/**
 * LoadingButton Component
 * ローディング状態付きボタンコンポーネント
 */

'use client';

import React from 'react';
import { motion } from 'framer-motion';

interface LoadingButtonProps {
  type?: "button" | "submit" | "reset";
  isLoading: boolean;
  disabled?: boolean;
  children: React.ReactNode;
  loadingText?: string;
  onClick?: () => void;
  className?: string;
}

export function LoadingButton({
  type = "button",
  isLoading,
  disabled = false,
  children,
  loadingText = "処理中...",
  onClick,
  className = "",
}: LoadingButtonProps) {
  return (
    <motion.button
      type={type}
      disabled={isLoading || disabled}
      onClick={onClick}
      className={`w-full py-4 px-6 text-base font-semibold text-white bg-gradient-to-r from-indigo-600 to-purple-600 
                 rounded-2xl shadow-lg hover:shadow-xl hover:from-indigo-700 hover:to-purple-700 
                 focus:outline-none focus:ring-4 focus:ring-indigo-100 dark:focus:ring-indigo-900 
                 disabled:opacity-70 disabled:cursor-not-allowed transition-all duration-300
                 transform hover:-translate-y-0.5 active:translate-y-0 ${className}`}
      whileHover={{ scale: isLoading || disabled ? 1 : 1.02 }}
      whileTap={{ scale: isLoading || disabled ? 1 : 0.98 }}
    >
      {isLoading ? (
        <div className="flex items-center justify-center space-x-3">
          <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
          <span>{loadingText}</span>
        </div>
      ) : (
        children
      )}
    </motion.button>
  );
}

export default LoadingButton;