'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

interface Category {
  id: string;
  label: string;
  icon: React.ReactNode;
  href?: string;
  subcategories: {
    label: string;
    href: string;
    description: string;
  }[];
}

interface MegaMenuButtonProps {
  category: Category;
  position: 'horizontal' | 'vertical';
  onClose: () => void;
}

export function MegaMenuButton({ category, position, onClose }: MegaMenuButtonProps) {
  const pathname = usePathname();
  const [hoveredCategory, setHoveredCategory] = useState<string | null>(null);
  
  const isActive = category.href && pathname === category.href;
  const hasSubcategories = category.subcategories && category.subcategories.length > 0;

  const getMenuPosition = () => {
    if (position === 'horizontal') {
      return 'absolute bottom-full left-0 mb-2';
    }
    return 'absolute left-full top-0 ml-2';
  };

  const getHoverBridge = () => {
    if (position === 'horizontal') {
      return 'absolute bottom-12 left-0 h-6 w-12 z-40';
    }
    return 'absolute left-12 top-0 w-6 h-12 z-40';
  };

  return (
    <div
      className="relative group/item hover:z-60"
      onMouseEnter={() => setHoveredCategory(category.id)}
      onMouseLeave={() => setTimeout(() => setHoveredCategory(null), 150)}
    >
      {/* Invisible hover bridge */}
      <div className={getHoverBridge()}></div>

      {/* Main Category Icon */}
      <div
        className={`
          flex items-center justify-center w-12 h-12 rounded-lg transition-all duration-300 relative cursor-pointer
          ${isActive
            ? 'bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 border-2 border-purple-300 dark:border-purple-600'
            : 'text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-slate-800 hover:text-purple-600 dark:hover:text-purple-400 hover:scale-105'
          }
        `}
      >
        <div className={`${isActive ? 'text-purple-600 dark:text-purple-400' : 'text-gray-400 group-hover/item:text-purple-500'} transition-colors duration-200`}>
          {category.icon}
        </div>

        {/* Category indicator for subcategories */}
        {hasSubcategories && (
          <div className="absolute -top-1 -right-1 w-3 h-3 bg-purple-500 rounded-full flex items-center justify-center">
            <div className="w-1 h-1 bg-white rounded-full"></div>
          </div>
        )}
      </div>

      {/* MegaBar Expandable Menu */}
      <div
        className={`${getMenuPosition()} transition-opacity duration-200 z-50 ${
          hoveredCategory === category.id
            ? 'opacity-100 pointer-events-auto'
            : 'opacity-0 pointer-events-none'
        }`}
        onMouseEnter={() => setHoveredCategory(category.id)}
        onMouseLeave={() => setTimeout(() => setHoveredCategory(null), 100)}
      >
        <div className="bg-white dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-lg shadow-xl backdrop-blur-sm min-w-80 max-w-96">
          {/* Category Header */}
          <div className="px-4 py-3 border-b border-gray-100 dark:border-slate-700">
            <div className="flex items-center space-x-3">
              <div className="text-purple-600 dark:text-purple-400">
                {category.icon}
              </div>
              <h3 className="font-semibold text-gray-900 dark:text-white text-sm">
                {category.label}
              </h3>
            </div>
          </div>

          {/* Subcategories */}
          {hasSubcategories && (
            <div className="py-2">
              {category.subcategories.map((subcategory, index) => {
                const isSubActive = pathname === subcategory.href;

                return (
                  <Link
                    key={index}
                    href={subcategory.href as any}
                    onClick={() => onClose()}
                    className={`
                      flex flex-col px-4 py-3 hover:bg-gray-50 dark:hover:bg-slate-700/50 transition-colors duration-200 cursor-pointer
                      ${isSubActive ? 'bg-purple-50 dark:bg-purple-900/20 border-l-2 border-purple-500' : ''}
                    `}
                  >
                    <div className={`font-medium text-sm ${isSubActive ? 'text-purple-600 dark:text-purple-400' : 'text-gray-900 dark:text-white'}`}>
                      {subcategory.label}
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      {subcategory.description}
                    </div>
                  </Link>
                );
              })}
            </div>
          )}

          {/* Direct link for categories with href */}
          {category.href && (
            <div className="py-2 border-t border-gray-100 dark:border-slate-700">
              <Link
                href={category.href as any}
                onClick={() => onClose()}
                className="flex items-center justify-center px-4 py-2 text-purple-600 dark:text-purple-400 hover:bg-purple-50 dark:hover:bg-purple-900/20 transition-colors duration-200 text-sm font-medium"
              >
                Go to {category.label}
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default MegaMenuButton;