import React from 'react';
import { Menu, theme } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth, useTheme } from '@/context';
import { useNavigation } from './NavigationProvider';
import * as Icons from '@ant-design/icons';
import './Navigation.css';

const ICON_MAP = {
  DashboardOutlined: Icons.DashboardOutlined,
  BuildOutlined: Icons.BuildOutlined,
  SettingOutlined: Icons.SettingOutlined,
  TeamOutlined: Icons.TeamOutlined,
  AppstoreOutlined: Icons.AppstoreOutlined,
  ProjectOutlined: Icons.ProjectOutlined,
  BarChartOutlined: Icons.BarChartOutlined,
  ApiOutlined: Icons.ApiOutlined,
  ShopOutlined: Icons.ShopOutlined,
  LogoutOutlined: Icons.LogoutOutlined,
  HomeOutlined: Icons.HomeOutlined,
  BlockOutlined: Icons.BlockOutlined,
};

const getIcon = (iconName) => {
  const IconComponent = ICON_MAP[iconName];
  return IconComponent ? <IconComponent /> : <Icons.AppstoreOutlined />;
};

// Legacy compatibility wrapper for existing Sidebar
const Sidebar = ({ projectMenuItems = [] }) => {
  const { user, logout } = useAuth();
  const { themeConfig } = useTheme();
  const { token } = theme.useToken();
  const navigate = useNavigate();
  const location = useLocation();
  
  const { getFilteredNavigation } = useNavigation();
  const navigation = getFilteredNavigation(user);

  const handleMenuClick = ({ key }) => {
    if (key === 'logout') {
      logout();
      navigate('/login');
    } else {
      navigate(key);
    }
  };

  // Build items from navigation config
  const items = [];
  
  // Main section
  const mainSection = navigation.main || [];
  const appSection = mainSection.find(item => item.id === 'app-section');
  if (appSection?.children) {
    items.push({
      key: 'app-section',
      label: 'Applicazioni',
      icon: <Icons.AppstoreOutlined />,
      children: appSection.children.map(child => ({
        key: child.path,
        label: child.label,
        icon: child.icon ? getIcon(child.icon) : <Icons.AppstoreOutlined />,
      })),
    });
  }

  // Admin section
  if (user?.role === 'admin') {
    const adminSection = navigation.admin || [];
    if (adminSection.length > 0) {
      items.push({ type: 'divider' });
      items.push({
        key: 'admin-section',
        label: 'Administration',
        icon: <Icons.BarChartOutlined />,
        children: adminSection.map(item => ({
          key: item.path,
          label: item.label,
          icon: item.icon ? getIcon(item.icon) : <Icons.AppstoreOutlined />,
        })),
      });
    }
  }

  items.push({ type: 'divider' });
  items.push({ key: 'logout', label: 'Logout', icon: <Icons.LogoutOutlined />, danger: true });

  return (
    <div 
      className="sidebar" 
      style={{ background: themeConfig.mode === 'dark' ? token.colorBgContainer : '#fff' }}
    >
      <Menu
        theme={themeConfig.mode === 'dark' ? 'dark' : 'light'}
        mode="inline"
        onClick={handleMenuClick}
        selectedKeys={[location.pathname]}
        defaultOpenKeys={['app-section']}
        items={items}
        style={{ borderRight: 0 }}
      />
    </div>
  );
};

// New AppSidebar with more options
const AppSidebar = ({ 
  projectMenuItems = [],
  sections = ['main', 'admin', 'marketplace', 'system'],
  onLogout 
}) => {
  const { user, logout } = useAuth();
  const { themeConfig } = useTheme();
  const { token } = theme.useToken();
  const location = useLocation();
  const navigate = useNavigate();
  
  const { getFilteredNavigation } = useNavigation();
  const navigation = getFilteredNavigation(user);

  const handleMenuClick = ({ key }) => {
    if (key === 'logout') {
      logout();
      if (onLogout) onLogout();
      navigate('/login');
    } else if (key.startsWith('/')) {
      navigate(key);
    }
  };

  // Build menu items from sections
  const buildMenuItems = () => {
    const items = [];
    
    sections.forEach(section => {
      const sectionItems = navigation[section] || [];
      
      if (section === 'system') {
        sectionItems.forEach(item => {
          if (item.action === 'logout') {
            items.push({ type: 'divider', key: 'system-divider' });
          }
          items.push({
            key: item.path || item.action,
            icon: item.icon ? getIcon(item.icon) : null,
            label: item.label,
            danger: item.danger,
          });
        });
      } else if (sectionItems.length > 0) {
        sectionItems.forEach(item => {
          const menuItem = {
            key: item.path || item.id,
            icon: item.icon ? getIcon(item.icon) : null,
            label: item.label,
          };
          
          if (item.children && item.children.length > 0) {
            menuItem.children = item.children.map(child => ({
              key: child.path,
              icon: child.icon ? getIcon(child.icon) : null,
              label: child.label,
            }));
          }
          
          items.push(menuItem);
        });
        
        if (section !== sections[sections.length - 1]) {
          items.push({ type: 'divider', key: `${section}-divider` });
        }
      }
    });

    return items;
  };

  const menuItems = buildMenuItems();
  
  return (
    <div 
      className="app-sidebar" 
      style={{ 
        background: themeConfig.mode === 'dark' ? token.colorBgContainer : '#fff' 
      }}
    >
      <Menu
        theme={themeConfig.mode === 'dark' ? 'dark' : 'light'}
        mode="inline"
        onClick={handleMenuClick}
        selectedKeys={[location.pathname]}
        defaultOpenKeys={['app-section']}
        items={menuItems}
        style={{ borderRight: 0 }}
      />
    </div>
  );
};

export default Sidebar;
export { AppSidebar, getIcon };
