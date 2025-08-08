'use client';

import React from 'react';
import {
  LeftBottomVerticalBar,
  LeftBottomHorizontalBar,
  RightTopVerticalBar,
  RightTopHorizontalBar,
  RightBottomVerticalBar
} from './index';

export function BarExample() {
  const sampleItems = [
    <button key="1" className="w-6 h-6 text-indigo-600">
      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z" />
      </svg>
    </button>,
    <button key="2" className="w-6 h-6 text-purple-600">
      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    </button>,
    <button key="3" className="w-6 h-6 text-green-600">
      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
    </button>
  ];

  return (
    <div className="relative w-full h-screen bg-gray-50 dark:bg-slate-800">
      {/* Example usage of all bar components */}
      
      {/* Left Bottom Corner - Horizontal has priority */}
      <LeftBottomHorizontalBar items={sampleItems.slice(0, 2)} />
      {/* Left Bottom Corner - Vertical with bottom margin */}
      <LeftBottomVerticalBar items={sampleItems.slice(2, 4)} />
      
      {/* Right Top Corner - Horizontal has priority */}
      <RightTopHorizontalBar items={sampleItems.slice(0, 2)} />
      {/* Right Top Corner - Vertical with top margin */}
      <RightTopVerticalBar items={sampleItems.slice(2, 4)} />
      
      {/* Right Bottom Corner - Vertical with bottom margin */}
      <RightBottomVerticalBar items={sampleItems} />

      {/* Content area */}
      <div className="flex items-center justify-center h-full">
        <div className="text-center space-y-4 p-8 bg-white dark:bg-slate-900 rounded-2xl shadow-lg border border-gray-200 dark:border-slate-700">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Bar Components Example
          </h2>
          <p className="text-gray-600 dark:text-gray-400 max-w-md">
            This demonstrates the usage of the new bar components positioned at different corners of the screen.
            Each bar can hold interactive elements and adapts to the theme.
          </p>
        </div>
      </div>
    </div>
  );
}

export default BarExample;