/**
 * AuthNavigation Component
 * 認証ページ間のナビゲーションコンポーネント
 */

'use client';

import React from 'react';

interface AuthNavigationProps {
  text: string;
  linkText: string;
  onLinkClick: () => void;
  className?: string;
}

export function AuthNavigation({ text, linkText, onLinkClick, className = "" }: AuthNavigationProps) {
  return (
    <div className={`text-center mt-8 pt-6 border-t border-gray-200 dark:border-slate-600 ${className}`}>
      <p className="text-sm text-gray-600 dark:text-gray-400">
        {text}{' '}
        <button
          onClick={onLinkClick}
          className="font-semibold text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 
                     transition-colors duration-200 inline-flex items-center space-x-1 hover:underline"
        >
          <span>{linkText}</span>
          {/* <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
          </svg> */}
        </button>
      </p>
    </div>
  );
}

export default AuthNavigation;