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
      label: 'Chiaro',
      icon: <SunOutlined />,
      onClick: () => updateTheme({ mode: 'light' })
    },
    {
      key: 'dark',
      label: 'Scuro',
      icon: <MoonOutlined />,
      onClick: () => updateTheme({ mode: 'dark' })
    },
    { type: 'divider' },
    {
      key: 'blue',
      label: 'Blu',
      icon: <span className="color-dot" style={{ background: '#1890ff', display: 'inline-block', width: 12, height: 12, borderRadius: '50%' }} />,
      onClick: () => updateTheme({ primaryColor: '#1890ff', mode: 'light' })
    },
    {
      key: 'green',
      label: 'Verde',
      icon: <span className="color-dot" style={{ background: '#52c41a', display: 'inline-block', width: 12, height: 12, borderRadius: '50%' }} />,
      onClick: () => updateTheme({ primaryColor: '#52c41a', mode: 'light' })
    },
    {
      key: 'purple',
      label: 'Viola',
      icon: <span className="color-dot" style={{ background: '#722ed1', display: 'inline-block', width: 12, height: 12, borderRadius: '50%' }} />,
      onClick: () => updateTheme({ primaryColor: '#722ed1', mode: 'light' })
    },
    {
      key: 'red',
      label: 'Rosso',
      icon: <span className="color-dot" style={{ background: '#ff4d4f', display: 'inline-block', width: 12, height: 12, borderRadius: '50%' }} />,
      onClick: () => updateTheme({ primaryColor: '#ff4d4f', mode: 'light' })
    },
    {
      key: 'orange',
      label: 'Arancione',
      icon: <span className="color-dot" style={{ background: '#fa8c16', display: 'inline-block', width: 12, height: 12, borderRadius: '50%' }} />,
      onClick: () => updateTheme({ primaryColor: '#fa8c16', mode: 'light' })
    }
  ];

  const userMenuItems = [
    {
      key: 'profile',
      label: 'Profilo',
      icon: <UserOutlined />,
      onClick: () => navigate('/profile')
    },
    {
      key: 'settings',
      label: 'Impostazioni',
      icon: <SettingOutlined />,
      onClick: () => navigate('/users')
    },
    { type: 'divider' },
    {
      key: 'logout',
      label: 'Logout',
      icon: <LogoutOutlined />,
      danger: true,
      onClick: handleLogout
    }
  ];

  const buildBreadcrumbs = () => {
    const paths = location.pathname.split('/').filter(Boolean);
    const crumbs = [{ title: <Link to="/projects"><HomeOutlined /></Link> }];

    let currentPath = '';
    paths.forEach((path, index) => {
      currentPath += `/${path}`;
      const isLast = index === paths.length - 1;

      let label = path;
      if (path === 'projects') label = 'Progetti';
      else if (path === 'data') label = 'Dati';
      else if (path === 'admin') label = 'Admin';
      else if (path === 'settings') label = 'Impostazioni';
      else if (path === 'members') label = 'Membri';
      else if (path === 'builder') label = 'Builder';
      else if (path === 'custom-modules') label = 'Moduli Personalizzati';
      else if (path === 'workflows') label = 'Workflows';
      else if (path === 'audit-logs') label = 'Audit Logs';
      else if (path === 'bi-builder') label = 'BI Builder';
      else if (path === 'project-import-export') label = 'Import/Export';
      else if (path === 'system') label = 'Sistema';
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
      background: themeConfig.mode === 'dark' ? '#1f1f1f' : '#e6e6e6',
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
