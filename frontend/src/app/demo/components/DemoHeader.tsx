'use client';

import React from 'react';
import { ThemeToggle } from '@/components/theme/ThemeToggle';
import { RightTopVerticalBar, RightTopHorizontalBar } from '@/components/layout/bars';
import Link from 'next/link';

interface DemoHeaderProps {
  onToggleSidebar?: () => void;
}

export function DemoHeader({ onToggleSidebar }: DemoHeaderProps) {
  // Items for RightTopVerticalBar
  const rightTopVerticalItems = [
    // Settings/Config button
    <button key="settings" className="p-2 text-gray-600 dark:text-gray-400 hover:text-purple-600 dark:hover:text-purple-400 transition-colors">
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
    </button>,
    // Notification button
    <button key="notifications" className="p-2 text-gray-600 dark:text-gray-400 hover:text-purple-600 dark:hover:text-purple-400 transition-colors relative">
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-5 5v-5zM6 7l5-5v5H6z" />
      </svg>
      <div className="absolute -top-1 -right-1 w-3 h-3 bg-purple-500 rounded-full animate-pulse"></div>
    </button>,
  ];

  // Items for RightTopHorizontalBar
  const rightTopHorizontalItems = [
    // Mobile menu button (only show on mobile)
    onToggleSidebar ? (
      <button
        key="mobile-menu"
        onClick={onToggleSidebar}
        className="lg:hidden p-2 text-gray-600 dark:text-gray-300 hover:text-purple-600 dark:hover:text-purple-400 transition-colors"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>
    ) : null,
    // Theme Toggle
    <div key="theme-toggle" className="scale-90">
      <ThemeToggle />
    </div>,
    // User Profile
    <div key="user-profile" className="w-10 h-10 bg-gradient-to-br from-purple-500 to-indigo-500 rounded-full flex items-center justify-center shadow-lg hover:shadow-xl transition-shadow cursor-pointer">
      <span className="text-white text-sm font-bold">D</span>
    </div>,
  ].filter(Boolean);

  return (
    <>
      {/* Simplified header for mobile/small screens */}
      <header className="lg:hidden bg-white/90 dark:bg-slate-900/90 backdrop-blur-sm border border-gray-200 dark:border-slate-700 rounded-lg shadow-sm h-12 mb-4">
        <div className="px-3 py-2 flex items-center justify-between h-full">
          {/* Left - Logo/Title */}
          <div className="flex items-center space-x-2">
            <div className="w-6 h-6 bg-gradient-to-br from-purple-500 to-indigo-500 rounded-lg flex items-center justify-center">
              <span className="text-white text-xs font-bold">PD</span>
            </div>
            <h1 className="text-sm font-bold text-gray-900 dark:text-white">Demo</h1>
          </div>

          {/* Right - Mobile controls */}
          <div className="flex items-center space-x-2">
            {onToggleSidebar && (
              <button
                onClick={onToggleSidebar}
                className="p-1 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-slate-800 rounded"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
            )}
            
            <div className="scale-75">
              <ThemeToggle />
            </div>
            
            <div className="w-6 h-6 bg-gradient-to-br from-purple-500 to-indigo-500 rounded-full flex items-center justify-center">
              <span className="text-white text-xs font-bold">D</span>
            </div>
          </div>
        </div>
      </header>

      {/* Logo/Title for large screens - positioned at top-left */}
      <div className="hidden lg:block fixed top-4 left-4 z-50">
        <div className="flex items-center space-x-3 bg-white/90 dark:bg-slate-900/90 backdrop-blur-sm border border-gray-200 dark:border-slate-700 rounded-2xl shadow-lg p-3">
          <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-indigo-500 rounded-xl flex items-center justify-center">
            <span className="text-white text-sm font-bold">PD</span>
          </div>
          <h1 className="text-lg font-bold text-gray-900 dark:text-white">Demo Platform</h1>
        </div>
      </div>

      {/* Right Top Bar Components for large screens */}
      <div className="hidden lg:block">
        <RightTopHorizontalBar items={rightTopHorizontalItems} />
        <RightTopVerticalBar items={rightTopVerticalItems} />
      </div>
    </>
  );
}

export default DemoHeader;