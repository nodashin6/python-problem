'use client';

import React from 'react';
import { motion } from 'framer-motion';

interface RightTopVerticalBarProps {
  items?: React.ReactNode[];
  className?: string;
}

export function RightTopVerticalBar({ items = [], className = '' }: RightTopVerticalBarProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`fixed top-0 right-0 z-40 flex flex-col items-center bg-white/95 dark:bg-slate-900/95 backdrop-blur-md rounded-bl-3xl shadow-xl shadow-black/10 dark:shadow-black/30 p-2 space-y-1 mt-12 ring-1 ring-white/20 dark:ring-white/10 ${className}`}
    >
      {items.map((item, index) => (
        <div
          key={index}
          className="w-11 h-11 flex items-center justify-center rounded-xl hover:bg-gray-100/80 dark:hover:bg-slate-800/80 transition-all duration-300 hover:scale-110 active:scale-95 backdrop-blur-sm"
        >
          {item}
        </div>
      ))}
    </motion.div>
  );
}

export default RightTopVerticalBar;