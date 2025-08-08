'use client';

import React from 'react';
import { motion } from 'framer-motion';

interface LeftBottomHorizontalBarProps {
  items?: React.ReactNode[];
  className?: string;
}

export function LeftBottomHorizontalBar({ items = [], className = '' }: LeftBottomHorizontalBarProps) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
      className={`fixed bottom-0 left-0 z-40 flex items-center bg-white/95 dark:bg-slate-900/95 backdrop-blur-md rounded-tr-3xl shadow-xl shadow-black/10 dark:shadow-black/30 p-2 space-x-1 ring-1 ring-white/20 dark:ring-white/10 ${className}`}
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

export default LeftBottomHorizontalBar;