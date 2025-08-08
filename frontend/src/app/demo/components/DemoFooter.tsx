'use client';

import React from 'react';

export function DemoFooter() {
  return (
    <footer className="bg-white/90 dark:bg-slate-900/90 backdrop-blur-sm border border-gray-200 dark:border-slate-700 rounded-lg shadow-sm">
      <div className="px-4 py-3">
        <div className="flex items-center justify-between text-xs text-gray-600 dark:text-gray-400">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse"></div>
            <span>Demo</span>
          </div>
          <span>© 2024</span>
        </div>
      </div>
    </footer>
  );
}

export default DemoFooter;