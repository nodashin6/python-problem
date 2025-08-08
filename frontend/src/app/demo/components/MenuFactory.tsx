'use client';

import React from 'react';
import { MenuItemType, SidebarEvent, SidebarEventHandler } from './MenuConfig';

interface MenuItem {
  type: MenuItemType;
  label: string;
  icon: React.ReactNode;
  href?: string;
  subcategories: {
    label: string;
    href: string;
    description: string;
  }[];
}

const MENU_DEFINITIONS: Record<MenuItemType, MenuItem> = {
  [MenuItemType.DASHBOARD]: {
    type: MenuItemType.DASHBOARD,
    label: 'Dashboard',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 5a2 2 0 012-2h4a2 2 0 012 2v3H8V5z" />
      </svg>
    ),
    href: '/demo',
    subcategories: [
      { label: 'Overview', href: '/demo', description: 'Main dashboard overview' },
      { label: 'Analytics', href: '/demo/analytics', description: 'Performance analytics' }
    ]
  },
  [MenuItemType.PROBLEMS]: {
    type: MenuItemType.PROBLEMS,
    label: 'Problems',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    ),
    subcategories: [
      { label: 'Problem List', href: '/demo/classic/problem-list', description: 'Browse all available problems' },
      { label: 'Problem Detail', href: '/demo/classic/problem-detail', description: 'View detailed problem information' }
    ]
  },
  [MenuItemType.JUDGE]: {
    type: MenuItemType.JUDGE,
    label: 'Judge',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    subcategories: [
      { label: 'Judge Success', href: '/demo/classic/judge-result-success', description: 'Successful submission result' },
      { label: 'Judge Failed', href: '/demo/classic/judge-result-failed', description: 'Failed submission result' }
    ]
  },
  [MenuItemType.SUBMIT]: {
    type: MenuItemType.SUBMIT,
    label: 'Submit',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
    ),
    subcategories: [
      { label: 'Submit Animation', href: '/demo/classic/submit-animation', description: 'Advanced submission with animations' }
    ]
  },
  [MenuItemType.SETTINGS]: {
    type: MenuItemType.SETTINGS,
    label: 'Settings',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
    ),
    subcategories: [
      { label: 'General Settings', href: '/demo/settings', description: 'General configuration' }
    ]
  },
  [MenuItemType.WORKSPACE]: {
    type: MenuItemType.WORKSPACE,
    label: 'Workspace',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
      </svg>
    ),
    href: '/demo/workspace',
    subcategories: [
      { label: 'Projects', href: '/demo/projects', description: 'Manage your projects' },
      { label: 'Code Editor', href: '/demo/editor', description: 'Online code editor' }
    ]
  },
  [MenuItemType.ALGORITHMS]: {
    type: MenuItemType.ALGORITHMS,
    label: 'Algorithms',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
      </svg>
    ),
    subcategories: [
      { label: 'Sorting', href: '/demo/algorithms/sorting', description: 'Sorting algorithms' },
      { label: 'Graph Theory', href: '/demo/algorithms/graph', description: 'Graph algorithms' }
    ]
  },
  [MenuItemType.CONTESTS]: {
    type: MenuItemType.CONTESTS,
    label: 'Contests',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
      </svg>
    ),
    subcategories: [
      { label: 'Active Contests', href: '/demo/contests/active', description: 'Currently active contests' },
      { label: 'Contest History', href: '/demo/contests/history', description: 'Past contest results' }
    ]
  },
  [MenuItemType.LEADERBOARD]: {
    type: MenuItemType.LEADERBOARD,
    label: 'Leaderboard',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
    ),
    subcategories: [
      { label: 'Global Ranking', href: '/demo/leaderboard/global', description: 'Global user rankings' }
    ]
  },
  [MenuItemType.COMMUNITY]: {
    type: MenuItemType.COMMUNITY,
    label: 'Community',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
      </svg>
    ),
    subcategories: [
      { label: 'Discussion Forum', href: '/demo/community/forum', description: 'Community discussions' }
    ]
  },
  [MenuItemType.LEARNING]: {
    type: MenuItemType.LEARNING,
    label: 'Learning',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
      </svg>
    ),
    href: '/demo/learning',
    subcategories: [
      { label: 'Tutorials', href: '/demo/learning/tutorials', description: 'Programming tutorials' },
      { label: 'Practice Sets', href: '/demo/learning/practice', description: 'Curated practice problems' }
    ]
  },
  [MenuItemType.COURSES]: {
    type: MenuItemType.COURSES,
    label: 'Courses',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
      </svg>
    ),
    subcategories: [
      { label: 'Data Structures', href: '/demo/courses/data-structures', description: 'Learn data structures' },
      { label: 'Algorithms', href: '/demo/courses/algorithms', description: 'Algorithm fundamentals' }
    ]
  },
  [MenuItemType.ACHIEVEMENTS]: {
    type: MenuItemType.ACHIEVEMENTS,
    label: 'Achievements',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
      </svg>
    ),
    subcategories: [
      { label: 'Badges', href: '/demo/achievements/badges', description: 'Your earned badges' },
      { label: 'Progress', href: '/demo/achievements/progress', description: 'Learning progress' }
    ]
  },
  [MenuItemType.RESOURCES]: {
    type: MenuItemType.RESOURCES,
    label: 'Resources',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 14v3m4-3v3m4-3v3M3 21h18M3 10h18M3 7l9-4 9 4M4 10h16v11H4V10z" />
      </svg>
    ),
    subcategories: [
      { label: 'Documentation', href: '/demo/resources/docs', description: 'Programming documentation' },
      { label: 'Cheat Sheets', href: '/demo/resources/cheatsheets', description: 'Quick reference guides' }
    ]
  },
  [MenuItemType.PROFILE]: {
    type: MenuItemType.PROFILE,
    label: 'Profile',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
      </svg>
    ),
    subcategories: [
      { label: 'My Profile', href: '/demo/profile', description: 'View and edit profile' }
    ]
  }
};

export class MenuFactory {
  static createMenuButton(
    itemType: MenuItemType,
    position: 'horizontal' | 'vertical',
    onEvent: SidebarEventHandler,
    currentPath: string
  ): React.ReactNode {
    const menuItem = MENU_DEFINITIONS[itemType];
    if (!menuItem) {
      console.warn(`Menu item not found: ${itemType}`);
      return null;
    }

    const handleMenuClick = (href?: string) => {
      onEvent({
        type: 'MENU_CLICK',
        payload: { itemType, href }
      });
    };

    const handleSubmenuClick = (href: string) => {
      onEvent({
        type: 'SUBMENU_CLICK', 
        payload: { itemType, href }
      });
    };

    return (
      <MenuButton
        key={itemType}
        menuItem={menuItem}
        position={position}
        currentPath={currentPath}
        onMenuClick={handleMenuClick}
        onSubmenuClick={handleSubmenuClick}
      />
    );
  }

  static getMenuItem(itemType: MenuItemType): MenuItem | undefined {
    return MENU_DEFINITIONS[itemType];
  }
}

interface MenuButtonProps {
  menuItem: MenuItem;
  position: 'horizontal' | 'vertical';
  currentPath: string;
  onMenuClick: (href?: string) => void;
  onSubmenuClick: (href: string) => void;
}

function MenuButton({ menuItem, position, currentPath, onMenuClick, onSubmenuClick }: MenuButtonProps) {
  // MegaMenuButtonの実装をここに移植する予定
  return (
    <div className="w-12 h-12 bg-gray-200 rounded flex items-center justify-center">
      {menuItem.icon}
    </div>
  );
}