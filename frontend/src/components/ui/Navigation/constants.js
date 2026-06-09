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
  purchases: 'ShoppingCartOutlined',
  inventory: 'InboxOutlined',
  accounting: 'DollarOutlined',
  hr: 'TeamOutlined',
  manufacturing: 'ToolOutlined',
  analytics: 'BarChartOutlined',
  anagrafiche: 'UserOutlined',
  test: 'ExperimentOutlined',
  audit: 'AuditOutlined',
  blocks: 'BlockOutlined',
  components: 'AppstoreOutlined',
  schema: 'DatabaseOutlined',
  publish: 'UploadOutlined',
  browse: 'SearchOutlined',
  ai: 'RobotOutlined',
  importExport: 'SwapOutlined',
  contacts: 'PhoneOutlined',
  addresses: 'EnvironmentOutlined',
  cities: 'GlobalOutlined',
  roles: 'TeamOutlined',
  categories: 'TagsOutlined',
  tax: 'PercentageOutlined',
  uom: 'RulerOutlined',
  pricelists: 'DollarOutlined',
  coa: 'BookOutlined',
  quotations: 'FileTextOutlined',
  invoices: 'FileDoneOutlined',
  deliveryNotes: 'CarOutlined',
  returns: 'RollbackOutlined',
  crm: 'HeartOutlined',
  contracts: 'FileProtectOutlined',
  stock: 'InboxOutlined',
  movements: 'SwapOutlined',
  inventoryCounts: 'ClipboardOutlined',
  lots: 'BarcodeOutlined',
  journal: 'BookOutlined',
  maturities: 'CalendarOutlined',
  vatRegisters: 'PercentageOutlined',
  intrastat: 'GlobalOutlined',
  bom: 'ApartmentOutlined',
  workCycles: 'NodeIndexOutlined',
  productionOrders: 'BellOutlined',
  employees: 'TeamOutlined',
  departments: 'ApartmentOutlined',
  attendance: 'ClockCircleOutlined',
  leave: 'CalendarOutlined',
  timesheet: 'FieldTimeOutlined',
  budget: 'FundOutlined',
  reports: 'FileSearchOutlined',
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
        // Area: Anagrafiche e Dati Base
        {
          id: 'area-anagrafiche',
          label: 'Anagrafiche',
          icon: DEFAULT_ICONS.anagrafiche,
          children: [
            { id: 'soggetti', label: 'Soggetti', path: '/anagrafiche', icon: DEFAULT_ICONS.users },
            { id: 'ruoli', label: 'Ruoli', path: '/ruoli', icon: DEFAULT_ICONS.roles },
            { id: 'indirizzi', label: 'Indirizzi', path: '/indirizzi', icon: DEFAULT_ICONS.addresses },
            { id: 'comuni', label: 'Comuni', path: '/comuni', icon: DEFAULT_ICONS.cities },
            { id: 'contatti', label: 'Contatti', path: '/contatti', icon: DEFAULT_ICONS.contacts },
            { id: 'products', label: 'Prodotti', path: '/products', icon: DEFAULT_ICONS.products },
            { id: 'product-categories', label: 'Categorie Prodotto', path: '/product-categories', icon: DEFAULT_ICONS.categories },
            { id: 'tax-rates', label: 'Aliquote IVA', path: '/tax-rates', icon: DEFAULT_ICONS.tax },
            { id: 'units-of-measure', label: 'Unità di Misura', path: '/units-of-measure', icon: DEFAULT_ICONS.uom },
            { id: 'price-lists', label: 'Listini Prezzo', path: '/price-lists', icon: DEFAULT_ICONS.pricelists },
            { id: 'chart-of-accounts', label: 'Piano dei Conti', path: '/chart-of-accounts', icon: DEFAULT_ICONS.coa },
          ],
        },
        // Area: Logistica e Acquisti
        {
          id: 'area-acquisti',
          label: 'Acquisti',
          icon: DEFAULT_ICONS.purchases,
          children: [
            { id: 'purchase-orders', label: 'Ordini Acquisto', path: '/purchase-orders', icon: DEFAULT_ICONS.purchases },
            { id: 'purchase-requests', label: 'Richieste d\'Acquisto', path: '/purchase-requests', icon: DEFAULT_ICONS.purchases },
            { id: 'goods-receipts', label: 'DDT Entrata Merci', path: '/goods-receipts', icon: DEFAULT_ICONS.deliveryNotes },
            { id: 'purchase-returns', label: 'Resi Acquisti', path: '/purchase-returns', icon: DEFAULT_ICONS.returns },
          ],
        },
        // Area: Vendite e CRM
        {
          id: 'area-vendite',
          label: 'Vendite',
          icon: DEFAULT_ICONS.sales,
          children: [
            { id: 'sales-orders', label: 'Ordini Vendita', path: '/sales', icon: DEFAULT_ICONS.sales },
            { id: 'quotations', label: 'Preventivi', path: '/quotations', icon: DEFAULT_ICONS.quotations },
            { id: 'delivery-notes', label: 'DDT Vendita', path: '/delivery-notes', icon: DEFAULT_ICONS.deliveryNotes },
            { id: 'invoices', label: 'Fatture', path: '/invoices', icon: DEFAULT_ICONS.invoices },
            { id: 'sales-returns', label: 'Resi Vendita', path: '/sales-returns', icon: DEFAULT_ICONS.returns },
            { id: 'crm', label: 'CRM', path: '/crm', icon: DEFAULT_ICONS.crm },
            { id: 'contracts', label: 'Contratti', path: '/contracts', icon: DEFAULT_ICONS.contracts },
          ],
        },
        // Area: Magazzino e Inventory
        {
          id: 'area-magazzino',
          label: 'Magazzino',
          icon: DEFAULT_ICONS.inventory,
          children: [
            { id: 'stock-levels', label: 'Giacenze', path: '/stock-levels', icon: DEFAULT_ICONS.stock },
            { id: 'stock-movements', label: 'Movimenti', path: '/stock-movements', icon: DEFAULT_ICONS.movements },
            { id: 'inventory-counts', label: 'Inventari', path: '/inventory-counts', icon: DEFAULT_ICONS.inventoryCounts },
            { id: 'lots', label: 'Lotti e Seriali', path: '/lots', icon: DEFAULT_ICONS.lots },
          ],
        },
        // Area: Contabilità e Finanza
        {
          id: 'area-contabilita',
          label: 'Contabilità',
          icon: DEFAULT_ICONS.accounting,
          children: [
            { id: 'journal', label: 'Prima Nota', path: '/journal', icon: DEFAULT_ICONS.journal },
            { id: 'maturities', label: 'Scadenzario', path: '/maturities', icon: DEFAULT_ICONS.maturities },
            { id: 'vat-registers', label: 'Registri IVA', path: '/vat-registers', icon: DEFAULT_ICONS.vatRegisters },
            { id: 'intrastat', label: 'Intrastat', path: '/intrastat', icon: DEFAULT_ICONS.intrastat },
          ],
        },
        // Area: Produzione
        {
          id: 'area-produzione',
          label: 'Produzione',
          icon: DEFAULT_ICONS.manufacturing,
          children: [
            { id: 'bom', label: 'Distinte Base', path: '/bom', icon: DEFAULT_ICONS.bom },
            { id: 'work-cycles', label: 'Cicli di Lavoro', path: '/work-cycles', icon: DEFAULT_ICONS.workCycles },
            { id: 'production-orders', label: 'Ordini Produzione', path: '/production-orders', icon: DEFAULT_ICONS.productionOrders },
          ],
        },
        // Area: HR e Payroll
        {
          id: 'area-hr',
          label: 'Risorse Umane',
          icon: DEFAULT_ICONS.hr,
          children: [
            { id: 'employees', label: 'Dipendenti', path: '/employees', icon: DEFAULT_ICONS.employees },
            { id: 'departments', label: 'Reparti', path: '/departments', icon: DEFAULT_ICONS.departments },
            { id: 'attendance', label: 'Presenze', path: '/attendance', icon: DEFAULT_ICONS.attendance },
            { id: 'leave-requests', label: 'Ferie e Permessi', path: '/leave-requests', icon: DEFAULT_ICONS.leave },
          ],
        },
        // Area: Project Management
        {
          id: 'area-progetti',
          label: 'Progetti',
          icon: DEFAULT_ICONS.projects,
          children: [
            { id: 'projects', label: 'Progetti', path: '/projects', icon: DEFAULT_ICONS.projects },
            { id: 'timesheet', label: 'Timesheet', path: '/timesheet', icon: DEFAULT_ICONS.timesheet },
            { id: 'project-budgets', label: 'Budget Commessa', path: '/project-budgets', icon: DEFAULT_ICONS.budget },
          ],
        },
        // Area: BI e Analytics
        {
          id: 'area-analytics',
          label: 'Analytics',
          icon: DEFAULT_ICONS.analytics,
          children: [
            { id: 'dashboard', label: 'Dashboard', path: '/dashboard', icon: DEFAULT_ICONS.dashboard },
            { id: 'dashboard-builder', label: 'Dashboard Builder', path: '/dashboard/builder', icon: DEFAULT_ICONS.builder },
            { id: 'chart-builder', label: 'Chart Builder', path: '/builder/blocks', icon: DEFAULT_ICONS.charts },
            { id: 'reports', label: 'Report Designer', path: '/reports', icon: DEFAULT_ICONS.reports },
          ],
        },
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
