import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth, useTheme } from '../context';
import LanguageSelector from './LanguageSelector';
import { useTranslation } from 'react-i18next';
import { Dropdown, Breadcrumb } from 'antd';
import {
  SunOutlined,
  MoonOutlined,
  HomeOutlined,
  LeftOutlined,
  UserOutlined,
  LogoutOutlined,
  SettingOutlined
} from '@ant-design/icons';

function AppHeader({ showBackButton = true, breadcrumbs = [] }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const { t } = useTranslation();
  const { themeConfig, updateTheme } = useTheme();

  const canGoBack = showBackButton && location.pathname !== '/projects' &&
    location.pathname !== '/' &&
    !['/login', '/forgot-password', '/reset-password'].includes(location.pathname);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const themeItems = [
    {
      key: 'light',
      label: t('theme.light', 'Light'),
      icon: <SunOutlined />,
      onClick: () => updateTheme({ mode: 'light' })
    },
    {
      key: 'dark',
      label: t('theme.dark', 'Dark'),
      icon: <MoonOutlined />,
      onClick: () => updateTheme({ mode: 'dark' })
    },
    { type: 'divider' },
    {
      key: 'blue',
      label: t('theme.colors.blue', 'Blue'),
      icon: <span className="color-dot" style={{ background: '#1890ff', display: 'inline-block', width: 12, height: 12, borderRadius: '50%' }} />,
      onClick: () => updateTheme({ primaryColor: '#1890ff', mode: 'light' })
    },
    {
      key: 'green',
      label: t('theme.colors.green', 'Green'),
      icon: <span className="color-dot" style={{ background: '#52c41a', display: 'inline-block', width: 12, height: 12, borderRadius: '50%' }} />,
      onClick: () => updateTheme({ primaryColor: '#52c41a', mode: 'light' })
    },
    {
      key: 'purple',
      label: t('theme.colors.purple', 'Purple'),
      icon: <span className="color-dot" style={{ background: '#722ed1', display: 'inline-block', width: 12, height: 12, borderRadius: '50%' }} />,
      onClick: () => updateTheme({ primaryColor: '#722ed1', mode: 'light' })
    },
    {
      key: 'red',
      label: t('theme.colors.red', 'Red'),
      icon: <span className="color-dot" style={{ background: '#ff4d4f', display: 'inline-block', width: 12, height: 12, borderRadius: '50%' }} />,
      onClick: () => updateTheme({ primaryColor: '#ff4d4f', mode: 'light' })
    },
    {
      key: 'orange',
      label: t('theme.colors.orange', 'Orange'),
      icon: <span className="color-dot" style={{ background: '#fa8c16', display: 'inline-block', width: 12, height: 12, borderRadius: '50%' }} />,
      onClick: () => updateTheme({ primaryColor: '#fa8c16', mode: 'light' })
    }
  ];

  const userMenuItems = [
    {
      key: 'profile',
      label: t('profile.userProfile'),
      icon: <UserOutlined />,
      onClick: () => navigate('/profile')
    },
    {
      key: 'settings',
      label: t('common.settings'),
      icon: <SettingOutlined />,
      onClick: () => navigate('/users')
    },
    { type: 'divider' },
    {
      key: 'logout',
      label: t('auth.logout'),
      icon: <LogoutOutlined />,
      danger: true,
      onClick: handleLogout
    }
  ];

  const buildBreadcrumbs = () => {
    const paths = location.pathname.split('/').filter(Boolean);
    const crumbs = [{ title: <Link to="/projects"><HomeOutlined /></Link> }];
    
    // Mappa della gerarchia per iniettare i livelli applicativi
    const hierarchyMap = {
      'anagrafiche': ['Applicazioni', 'Anagrafiche'],
      'ruoli': ['Applicazioni', 'Anagrafiche'],
      'indirizzi': ['Applicazioni', 'Anagrafiche'],
      'contatti': ['Applicazioni', 'Anagrafiche'],
      'products': ['Applicazioni', 'Anagrafiche'],
      'product-categories': ['Applicazioni', 'Anagrafiche'],
      'tax-rates': ['Applicazioni', 'Anagrafiche'],
      'units-of-measure': ['Applicazioni', 'Anagrafiche'],
      'price-lists': ['Applicazioni', 'Anagrafiche'],
      'sales': ['Applicazioni', 'Vendite'],
      'quotations': ['Applicazioni', 'Vendite'],
      'delivery-notes': ['Applicazioni', 'Vendite'],
      'invoices': ['Applicazioni', 'Vendite'],
      'purchase-orders': ['Applicazioni', 'Acquisti'],
      'purchase-requests': ['Applicazioni', 'Acquisti'],
      'goods-receipts': ['Applicazioni', 'Acquisti'],
      'stock-levels': ['Applicazioni', 'Magazzino'],
      'stock-movements': ['Applicazioni', 'Magazzino'],
      'lots': ['Applicazioni', 'Magazzino'],
      'journal': ['Applicazioni', 'Contabilità'],
      'maturities': ['Applicazioni', 'Contabilità'],
      'vat-registers': ['Applicazioni', 'Contabilità'],
      'intrastat': ['Applicazioni', 'Contabilità'],
      'bom': ['Applicazioni', 'Produzione'],
      'work-cycles': ['Applicazioni', 'Produzione'],
      'production-orders': ['Applicazioni', 'Produzione'],
      'employees': ['Applicazioni', 'Risorse Umane'],
      'departments': ['Applicazioni', 'Risorse Umane'],
      'attendance': ['Applicazioni', 'Risorse Umane'],
      'leave-requests': ['Applicazioni', 'Risorse Umane'],
    };

    const firstPath = paths[0];
    if (hierarchyMap[firstPath]) {
      hierarchyMap[firstPath].forEach(label => {
        crumbs.push({ title: label });
      });
    }

    let currentPath = '';
    paths.forEach((path, index) => {
      currentPath += `/${path}`;
      const isLast = index === paths.length - 1;

      let label = path;
      if (path === 'projects') label = t('menu.areas.progetti');
      else if (path === 'data') label = t('common.data', 'Data');
      else if (path === 'anagrafiche') label = t('menu.blocks.soggetti');
      else if (path === 'ruoli') label = t('menu.blocks.ruoli');
      else if (path === 'indirizzi') label = t('menu.blocks.indirizzi');
      else if (path === 'contatti') label = t('menu.blocks.contatti');
      else if (path === 'products') label = t('menu.blocks.products', 'Products');
      else if (path === 'product-categories') label = t('menu.blocks.categorie');
      else if (path === 'tax-rates') label = t('menu.blocks.aliquoteIva');
      else if (path === 'units-of-measure') label = t('menu.blocks.unitaMisura');
      else if (path === 'price-lists') label = t('menu.blocks.listiniPrezzo');
      else if (path === 'sales') label = t('menu.blocks.ordiniVendita');
      else if (path === 'quotations') label = t('menu.blocks.preventivi');
      else if (path === 'invoices') label = t('menu.blocks.fatture');
      else if (path === 'journal') label = t('menu.blocks.primaNota');
      else if (path === 'stock-levels') label = t('menu.blocks.giacenze');
      else if (path === 'stock-movements') label = t('menu.blocks.movimenti');
      else if (path === 'admin') label = t('menu.admin.adminArea', 'Admin');
      else if (path === 'settings') label = t('common.settings');
      else if (path === 'members') label = t('common.members', 'Members');
      else if (path === 'builder') label = t('menu.admin.builderSection');
      else if (path === 'custom-modules') label = t('menu.admin.customModules');
      else if (path === 'workflows') label = t('menu.blocks.workflows', 'Workflows');
      else if (path === 'audit-logs') label = t('menu.admin.auditLogs');
      else if (path === 'bi-builder') label = t('menu.blocks.dashboardBuilder');
      else if (path === 'project-import-export') label = t('menu.admin.importExport');
      else if (path === 'system') label = t('menu.blocks.system', 'System');
      else if (path === 'sales-returns') label = t('menu.blocks.resiVendita');
      else if (path === 'purchase-returns') label = t('menu.blocks.resiAcquisto');
      else if (path === 'inventory-counts') label = t('menu.blocks.inventari');
      else if (path === 'bom') label = t('menu.blocks.bom');
      else if (path === 'work-cycles') label = t('menu.blocks.cicliLavoro');
      else if (path === 'production-orders') label = t('menu.blocks.ordiniProduzione');
      else if (path === 'employees') label = t('menu.blocks.dipendenti');
      else if (path === 'departments') label = t('menu.blocks.reparti');
      else if (path === 'attendance') label = t('menu.blocks.presenze');
      else if (path === 'leave-requests') label = t('menu.blocks.feriePermessi');
      else if (path === 'timesheet') label = t('menu.blocks.timesheet');
      else if (path === 'project-budgets') label = t('menu.blocks.budgetCommessa');
      else if (path === 'reports') label = t('menu.blocks.reportDesigner');
      else if (path === 'gdo-reconciliation') label = t('menu.blocks.gdoReconciliation', 'GDO Reconciliation');
      else if (path === 'test-runner') label = t('menu.admin.testRunner');
      else if (path === 'relationship-manager') label = t('menu.admin.relationshipManager');
      else if (path === 'audit-logs') label = t('menu.admin.auditLogs');
      else if (path === 'distance-calculator') label = t('menu.blocks.calcoloDistanze');
      else if (!isNaN(path)) label = `#${path}`;

      crumbs.push({
        title: isLast ? label : <Link to={currentPath}>{label}</Link>
      });
    });

    return crumbs;
  };

  return (
    <div className="app-header" style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '8px 24px',
      background: themeConfig.mode === 'dark' ? '#1f1f1f' : '#fff',
      borderBottom: `3px solid ${themeConfig.primaryColor}`,
      minHeight: 56,
      marginBottom: 0,
      position: 'relative',
      zIndex: 100,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 16, flex: 1 }}>
        {canGoBack && (
          <LeftOutlined
            onClick={() => navigate(-1)}
            style={{ fontSize: 18, cursor: 'pointer', color: themeConfig.primaryColor }}
            title="Torna indietro"
          />
        )}
        <Link to="/projects" style={{
          color: themeConfig.primaryColor,
          fontWeight: 'bold',
          fontSize: 20,
          textDecoration: 'none',
          whiteSpace: 'nowrap',
        }}>
          ERPSeed
        </Link>
        <Breadcrumb
          items={breadcrumbs.length > 0 ? breadcrumbs : buildBreadcrumbs()}
          style={{ marginLeft: 16, flex: 1 }}
        />
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 16, flexShrink: 0 }}>
        <LanguageSelector />

        <Dropdown menu={{ items: themeItems }} trigger={['click']}>
          <a style={{ color: themeConfig.mode === 'dark' ? '#fff' : '#000', fontSize: 18 }}>
            {themeConfig.mode === 'dark' ? <MoonOutlined /> : <SunOutlined />}
          </a>
        </Dropdown>

        {user ? (
          <Dropdown menu={{ items: userMenuItems }} trigger={['click']}>
            <a style={{ color: themeConfig.mode === 'dark' ? '#fff' : '#000' }}>
              <img
                src={user.avatar ? `http://localhost:5000/uploads/${user.avatar}` : `https://ui-avatars.com/api/?name=${user.first_name || 'U'}${user.last_name || 'ser'}&background=random`}
                alt="Avatar"
                className="rounded-circle"
                style={{
                  width: 32,
                  height: 32,
                  objectFit: 'cover',
                  border: `2px solid ${themeConfig.primaryColor}`,
                  verticalAlign: 'middle'
                }}
              />
            </a>
          </Dropdown>
        ) : (
          <span style={{ color: themeConfig.mode === 'dark' ? '#fff' : '#000' }}>Guest</span>
        )}
      </div>
    </div>
  );
}

export default AppHeader;
