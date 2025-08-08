export enum MenuItemType {
  DASHBOARD = 'dashboard',
  PROBLEMS = 'problems',
  JUDGE = 'judge',
  SUBMIT = 'submit',
  SETTINGS = 'settings',
  WORKSPACE = 'workspace',
  ALGORITHMS = 'algorithms',
  CONTESTS = 'contests',
  LEADERBOARD = 'leaderboard',
  COMMUNITY = 'community',
  LEARNING = 'learning',
  COURSES = 'courses',
  ACHIEVEMENTS = 'achievements',
  RESOURCES = 'resources',
  PROFILE = 'profile'
}

export enum CornerMode {
  RED = 'red',
  BLUE = 'blue',
  GREEN = 'green'
}

export interface MenuLayout {
  mode: CornerMode;
  horizontal: MenuItemType[];
  vertical: MenuItemType[];
}

export const SIDEBAR_LAYOUTS: Record<CornerMode, MenuLayout> = {
  [CornerMode.RED]: {
    mode: CornerMode.RED,
    horizontal: [MenuItemType.DASHBOARD, MenuItemType.PROBLEMS, MenuItemType.JUDGE, MenuItemType.SUBMIT],
    vertical: [MenuItemType.SETTINGS]
  },
  [CornerMode.BLUE]: {
    mode: CornerMode.BLUE,
    horizontal: [MenuItemType.WORKSPACE, MenuItemType.ALGORITHMS, MenuItemType.CONTESTS, MenuItemType.LEADERBOARD],
    vertical: [MenuItemType.COMMUNITY]
  },
  [CornerMode.GREEN]: {
    mode: CornerMode.GREEN,
    horizontal: [MenuItemType.LEARNING, MenuItemType.COURSES, MenuItemType.ACHIEVEMENTS, MenuItemType.RESOURCES],
    vertical: [MenuItemType.PROFILE]
  }
};

export interface SidebarEvent {
  type: 'MENU_CLICK' | 'SUBMENU_CLICK' | 'MODE_CHANGE' | 'SIDEBAR_CLOSE';
  payload: {
    itemType?: MenuItemType;
    href?: string;
    newMode?: CornerMode;
  };
}

export type SidebarEventHandler = (event: SidebarEvent) => void;