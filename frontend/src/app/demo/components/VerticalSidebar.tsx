'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MenuItemType, MenuLayout, SidebarEventHandler } from './MenuConfig';
import { MenuFactory } from './MenuFactory';
import { usePathname } from 'next/navigation';

interface VerticalSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  layout: MenuLayout;
  cornerButton?: React.ReactNode;
  onEvent: SidebarEventHandler;
}

export function VerticalSidebar({ isOpen, onClose, layout, cornerButton, onEvent }: VerticalSidebarProps) {
  const [isLargeScreen, setIsLargeScreen] = useState(false);
  const pathname = usePathname();

  useEffect(() => {
    const checkScreenSize = () => {
      setIsLargeScreen(window.innerWidth >= 1024);
    };

    checkScreenSize();
    window.addEventListener('resize', checkScreenSize);
    return () => window.removeEventListener('resize', checkScreenSize);
  }, []);

  const handleEvent: SidebarEventHandler = (event) => {
    if (event.type === 'SIDEBAR_CLOSE') {
      onClose();
    }
    onEvent(event);
  };

  // 全てのメニューアイテムを縦に配置
  const allItems = [...layout.horizontal, ...layout.vertical];

  return (
    <>
      {/* Overlay */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 lg:hidden"
          />
        )}
      </AnimatePresence>

      {/* Vertical Sidebar */}
      <motion.aside
        initial={false}
        animate={{
          x: isLargeScreen ? 0 : (isOpen ? 0 : -80),
        }}
        transition={{ type: "spring", damping: 25, stiffness: 200 }}
        className="fixed bottom-0 left-0 z-50 lg:relative lg:z-auto flex-shrink-0 overflow-visible"
      >
        <div className="bg-white/90 dark:bg-slate-900/90 backdrop-blur-sm border border-gray-200 dark:border-slate-700 rounded-lg shadow-sm flex flex-col w-16 min-h-96">
          {/* Corner button at top */}
          <div className="flex items-center justify-center p-2 border-b border-gray-200 dark:border-slate-700">
            {cornerButton}
            
            {/* Close button for mobile */}
            <button
              onClick={() => handleEvent({ type: 'SIDEBAR_CLOSE', payload: {} })}
              className="lg:hidden absolute top-1 right-1 p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded text-xs"
            >
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          {/* Menu items */}
          <div className="flex-1 flex flex-col py-4">
            <nav className="flex flex-col space-y-2 px-2">
              {allItems.map(itemType => 
                MenuFactory.createMenuButton(itemType, 'vertical', handleEvent, pathname)
              )}
            </nav>
          </div>
          
          {/* Bottom indicator */}
          <div className="flex justify-center p-2">
            <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse"></div>
          </div>
        </div>
      </motion.aside>
    </>
  );
}

export default VerticalSidebar;