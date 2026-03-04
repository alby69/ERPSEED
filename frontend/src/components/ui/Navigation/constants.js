// Navigation System - Constants and Types
// This file defines the navigation configuration schema

// Navigation Item Types
export const NAV_ITEM_TYPES = {
  LINK: 'link',
  SUBMENU: 'submenu',
  DIVIDER: 'divider',
  ACTION: 'action',
};

// Default icon mapping (Ant Design icons)
export const DEFAULT_ICONS = {
  dashboard: 'DashboardOutlined',
  builder: 'BuildOutlined',
  settings: 'SettingOutlined',
  users: 'TeamOutlined',
  modules: 'AppstoreOutlined',
  projects: 'ProjectOutlined',
  charts: 'BarChartOutlined',
  workflow: 'ApiOutlined',
  marketplace: 'ShopOutlined',
  logout: 'LogoutOutlined',
  home: 'HomeOutlined',
  products: 'AppstoreOutlined',
  sales: 'ShoppingCartOutlined',
  inventory: 'InboxOutlined',
  accounting: 'DollarOutlined',
  hr: 'UserOutlined',
  test: 'ExperimentOutlined',
  audit: 'AuditOutlined',
  blocks: 'BlockOutlined',
  components: 'AppstoreOutlined',
  schema: 'DatabaseOutlined',
  publish: 'UploadOutlined',
  browse: 'SearchOutlined',
  ai: 'RobotOutlined',
  importExport: 'SwapOutlined',
};

// Permission levels
export const PERMISSION_LEVELS = {
  PUBLIC: 'public',
  AUTHENTICATED: 'authenticated',
  USER: 'user',
  EDITOR: 'editor',
  ADMIN: 'admin',
  OWNER: 'owner',
};

// Check if user has permission to see navigation item
export const hasPermission = (item, user) => {
  if (!item.permission || item.permission === PERMISSION_LEVELS.PUBLIC) {
    return true;
  }

  if (!user) {
    return item.permission === PERMISSION_LEVELS.PUBLIC;
  }

  const roleHierarchy = {
    [PERMISSION_LEVELS.OWNER]: 5,
    [PERMISSION_LEVELS.ADMIN]: 4,
    [PERMISSION_LEVELS.EDITOR]: 3,
    [PERMISSION_LEVELS.USER]: 2,
    [PERMISSION_LEVELS.AUTHENTICATED]: 1,
  };

  const userLevel = roleHierarchy[user.role] || 0;
  const requiredLevel = roleHierarchy[item.permission] || 0;

  return userLevel >= requiredLevel;
};

// Default navigation configurations
export const DEFAULT_NAVIGATIONS = {
  // Main application navigation
  main: [
    {
      id: 'dashboard',
      label: 'Dashboard',
      path: '/dashboard',
      icon: DEFAULT_ICONS.dashboard,
      permission: PERMISSION_LEVELS.AUTHENTICATED,
    },
    {
      id: 'app-section',
      label: 'Applications',
      icon: DEFAULT_ICONS.modules,
      permission: PERMISSION_LEVELS.AUTHENTICATED,
      children: [
        { id: 'anagrafiche', label: 'Anagrafiche', path: '/anagrafiche', icon: DEFAULT_ICONS.users },
        { id: 'ruoli', label: 'Ruoli', path: '/ruoli', icon: DEFAULT_ICONS.users },
        { id: 'indirizzi', label: 'Indirizzi', path: '/indirizzi', icon: DEFAULT_ICONS.home },
        { id: 'comuni', label: 'Comuni', path: '/comuni', icon: DEFAULT_ICONS.home },
        { id: 'contatti', label: 'Contatti', path: '/contatti', icon: DEFAULT_ICONS.users },
        { id: 'products', label: 'Prodotti', path: '/products', icon: DEFAULT_ICONS.products },
        { id: 'sales', label: 'Vendite', path: '/sales', icon: DEFAULT_ICONS.sales },
      ],
    },
  ],

  // Admin section
  admin: [
    {
      id: 'builder',
      label: 'Builder',
      path: '/admin/builder',
      icon: DEFAULT_ICONS.builder,
      permission: PERMISSION_LEVELS.ADMIN,
    },
    {
      id: 'blocks',
      label: 'Blocks',
      path: '/admin/blocks',
      icon: DEFAULT_ICONS.blocks,
      permission: PERMISSION_LEVELS.ADMIN,
    },
    {
      id: 'workflows',
      label: 'Workflows',
      path: '/admin/workflows',
      icon: DEFAULT_ICONS.workflow,
      permission: PERMISSION_LEVELS.ADMIN,
    },
    {
      id: 'business-rules',
      label: 'Business Rules',
      path: '/projects/{projectId}/business-rules',
      icon: DEFAULT_ICONS.workflow,
      permission: PERMISSION_LEVELS.ADMIN,
    },
    {
      id: 'modules',
      label: 'Modules',
      path: '/admin/custom-modules',
      icon: DEFAULT_ICONS.modules,
      permission: PERMISSION_LEVELS.ADMIN,
    },
    {
      id: 'project-import-export',
      label: 'Import/Export',
      path: '/admin/project-import-export',
      icon: DEFAULT_ICONS.importExport,
      permission: PERMISSION_LEVELS.ADMIN,
    },
    {
      id: 'test-runner',
      label: 'Test Runner',
      path: '/test-runner',
      icon: DEFAULT_ICONS.test,
      permission: PERMISSION_LEVELS.ADMIN,
    },
    {
      id: 'projects-admin',
      label: 'Projects',
      path: '/admin/projects',
      icon: DEFAULT_ICONS.projects,
      permission: PERMISSION_LEVELS.ADMIN,
    },
    {
      id: 'audit-logs',
      label: 'Audit Logs',
      path: '/admin/audit-logs',
      icon: DEFAULT_ICONS.audit,
      permission: PERMISSION_LEVELS.ADMIN,
    },
    {
      id: 'ai-assistant',
      label: 'AI Assistant',
      path: '/ai-assistant',
      icon: DEFAULT_ICONS.ai,
      permission: PERMISSION_LEVELS.ADMIN,
    },
  ],

  // Marketplace
  marketplace: [
    {
      id: 'marketplace-browse',
      label: 'Browse',
      path: '/marketplace',
      icon: DEFAULT_ICONS.browse,
      permission: PERMISSION_LEVELS.AUTHENTICATED,
    },
    {
      id: 'marketplace-publish',
      label: 'Publish Block',
      path: '/marketplace/publish',
      icon: DEFAULT_ICONS.publish,
      permission: PERMISSION_LEVELS.ADMIN,
    },
    {
      id: 'marketplace-my',
      label: 'My Blocks',
      path: '/marketplace/my-blocks',
      icon: DEFAULT_ICONS.blocks,
      permission: PERMISSION_LEVELS.AUTHENTICATED,
    },
  ],

  // System (footer items)
  system: [
    {
      id: 'logout',
      label: 'Logout',
      action: 'logout',
      icon: DEFAULT_ICONS.logout,
      danger: true,
    },
  ],
};

export default {
  NAV_ITEM_TYPES,
  DEFAULT_ICONS,
  PERMISSION_LEVELS,
  hasPermission,
  DEFAULT_NAVIGATIONS,
};
