'use client';

import React from 'react';
import { VerticalSidebar } from './VerticalSidebar';
import { CornerMode, SIDEBAR_LAYOUTS, SidebarEvent } from './MenuConfig';
import { LeftBottomHorizontalBar, LeftBottomVerticalBar } from '@/components/layout/bars';
import { MenuFactory } from './MenuFactory';
import { useState } from 'react';
import Link from 'next/link';

interface DemoSidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export function DemoSidebar({ isOpen, onClose }: DemoSidebarProps) {
  const [cornerMode, setCornerMode] = useState<CornerMode>(CornerMode.RED);

  const toggleCornerMode = () => {
    setCornerMode(current => {
      switch (current) {
        case CornerMode.RED: return CornerMode.BLUE;
        case CornerMode.BLUE: return CornerMode.GREEN;
        case CornerMode.GREEN: return CornerMode.RED;
        default: return CornerMode.RED;
      }
    });
  };

  const getCornerButtonColors = () => {
    switch (cornerMode) {
      case CornerMode.RED:
        return {
          bg: 'bg-gradient-to-br from-red-500 to-red-600',
          hover: 'hover:from-red-600 hover:to-red-700',
          text: 'R'
        };
      case CornerMode.BLUE:
        return {
          bg: 'bg-gradient-to-br from-blue-500 to-blue-600',
          hover: 'hover:from-blue-600 hover:to-blue-700',
          text: 'B'
        };
      case CornerMode.GREEN:
        return {
          bg: 'bg-gradient-to-br from-green-500 to-green-600',
          hover: 'hover:from-green-600 hover:to-green-700',
          text: 'G'
        };
    }
  };

  const handleEvent = (event: SidebarEvent) => {
    switch (event.type) {
      case 'MODE_CHANGE':
        if (event.payload.newMode) {
          setCornerMode(event.payload.newMode);
        }
        break;
      case 'MENU_CLICK':
        console.log('Menu clicked:', event.payload);
        if (event.payload.href) {
          window.location.href = event.payload.href;
        }
        break;
      case 'SUBMENU_CLICK':
        console.log('Submenu clicked:', event.payload);
        if (event.payload.href) {
          window.location.href = event.payload.href;
        }
        break;
      case 'SIDEBAR_CLOSE':
        onClose();
        break;
    }
  };

  const cornerButton = (
    <button
      onClick={toggleCornerMode}
      className={`w-10 h-10 ${getCornerButtonColors().bg} ${getCornerButtonColors().hover} rounded-lg flex items-center justify-center transition-all duration-300 hover:scale-105 active:scale-95 shadow-lg`}
    >
      <span className="text-white text-sm font-bold">{getCornerButtonColors().text}</span>
    </button>
  );

  // Create menu items for Left Bottom Horizontal Bar
  const horizontalMenuItems = SIDEBAR_LAYOUTS[cornerMode].horizontal.slice(0, 3).map((itemType) => {
    const menuItem = MenuFactory.getMenuItem(itemType);
    if (!menuItem) return null;

    return (
      <Link
        key={itemType}
        href={(menuItem.subcategories[0]?.href || '/demo') as never}
        className="p-2 text-gray-600 dark:text-gray-400 hover:text-purple-600 dark:hover:text-purple-400 transition-colors"
        onClick={() => handleEvent({ type: 'MENU_CLICK', payload: { itemType, href: menuItem.subcategories[0]?.href || '/demo' }})}
      >
        {menuItem.icon}
      </Link>
    );
  }).filter(Boolean);

  // Create menu items for Left Bottom Vertical Bar
  const verticalMenuItems = SIDEBAR_LAYOUTS[cornerMode].vertical.map((itemType) => {
    const menuItem = MenuFactory.getMenuItem(itemType);
    if (!menuItem) return null;

    return (
      <Link
        key={itemType}
        href={(menuItem.subcategories[0]?.href || '/demo') as never}
        className="p-2 text-gray-600 dark:text-gray-400 hover:text-purple-600 dark:hover:text-purple-400 transition-colors"
        onClick={() => handleEvent({ type: 'MENU_CLICK', payload: { itemType, href: menuItem.subcategories[0]?.href || '/demo' }})}
      >
        {menuItem.icon}
      </Link>
    );
  }).filter(Boolean);

  // Add corner mode toggle button to horizontal bar
  const horizontalItemsWithCorner = [
    cornerButton,
    ...horizontalMenuItems
  ];

  return (
    <>
      {/* Mobile version - keep the original VerticalSidebar */}
      <div className="lg:hidden">
        <VerticalSidebar 
          isOpen={isOpen} 
          onClose={onClose} 
          layout={SIDEBAR_LAYOUTS[cornerMode]}
          cornerButton={cornerButton}
          onEvent={handleEvent}
        />
      </div>

      {/* Desktop version - use Left Bottom Bar components */}
      <div className="hidden lg:block">
        <LeftBottomHorizontalBar items={horizontalItemsWithCorner} />
        <LeftBottomVerticalBar items={verticalMenuItems} />
      </div>
    </>
  );
}

export default DemoSidebar;