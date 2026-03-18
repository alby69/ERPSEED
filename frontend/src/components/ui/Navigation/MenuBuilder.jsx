import React from 'react';
import { Menu } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  DashboardOutlined,
  BuildOutlined,
  SettingOutlined,
  TeamOutlined,
  AppstoreOutlined,
  ProjectOutlined,
  BarChartOutlined,
  ApiOutlined,
  ShopOutlined,
  LogoutOutlined,
  HomeOutlined,
  InboxOutlined,
  DollarOutlined,
  UserOutlined,
  ExperimentOutlined,
  AuditOutlined,
  BlockOutlined,
  DatabaseOutlined,
  UploadOutlined,
  SearchOutlined,
  ShoppingCartOutlined,
} from '@ant-design/icons';
import { hasPermission } from './constants';

// Icon mapping
const ICON_MAP = {
  DashboardOutlined,
  BuildOutlined,
  SettingOutlined,
  TeamOutlined,
  AppstoreOutlined,
  ProjectOutlined,
  BarChartOutlined,
  ApiOutlined,
  ShopOutlined,
  LogoutOutlined,
  HomeOutlined,
  InboxOutlined,
  DollarOutlined,
  UserOutlined,
  ExperimentOutlined,
  AuditOutlined,
  BlockOutlined,
  DatabaseOutlined,
  UploadOutlined,
  SearchOutlined,
  ShoppingCartOutlined,
};

const getIcon = (iconName) => {
  const IconComponent = ICON_MAP[iconName];
  return IconComponent ? <IconComponent /> : <AppstoreOutlined />;
};

const MenuBuilder = ({ 
  items = [], 
  mode = 'inline', 
  onItemClick,
  user,
  theme = 'light',
  selectedKeys = [],
  defaultOpenKeys = [],
}) => {
  const navigate = useNavigate();
  const location = useLocation();

  // Filter items based on permissions
  const filterItems = (menuItems) => {
    return menuItems
      .filter(item => hasPermission(item, user))
      .map(item => {
        // Process children recursively
        const processedItem = { ...item };
        
        if (item.children && item.children.length > 0) {
          processedItem.children = filterItems(item.children);
          // Remove parent if all children are filtered out
          if (processedItem.children.length === 0) {
            return null;
          }
        }

        // Convert to Ant Design Menu format
        if (item.type === 'divider') {
          return { type: 'divider', key: item.id };
        }

        const menuItem = {
          key: item.path || item.action || item.id,
          icon: item.icon ? getIcon(item.icon) : null,
          label: item.label,
          danger: item.danger,
          disabled: item.disabled,
        };

        return menuItem;
      })
      .filter(Boolean);
  };

  const processedItems = filterItems(items);

  const handleClick = ({ key }) => {
    const item = findItemByKey(items, key);
    
    if (item?.action === 'logout') {
      if (onItemClick) {
        onItemClick({ action: 'logout', key });
      }
      return;
    }

    if (item?.path) {
      navigate(item.path);
    }
    
    if (onItemClick) {
      onItemClick({ ...item, key });
    }
  };

  // Find item by key
  const findItemByKey = (menuItems, key) => {
    for (const item of menuItems) {
      if ((item.path || item.action || item.id) === key) {
        return item;
      }
      if (item.children) {
        const found = findItemByKey(item.children, key);
        if (found) return found;
      }
    }
    return null;
  };

  // Auto-select current path
  const currentSelectedKeys = selectedKeys?.length > 0 
    ? selectedKeys 
    : [location.pathname];

  // Auto-expand submenus based on current path
  const currentDefaultOpenKeys = defaultOpenKeys?.length > 0 
    ? defaultOpenKeys 
    : items
        .filter(item => item.children?.some(child => 
          location.pathname.startsWith(child.path || '')
        ))
        .map(item => item.id);

  return (
    <Menu
      theme={theme}
      mode={mode}
      onClick={handleClick}
      selectedKeys={currentSelectedKeys}
      defaultOpenKeys={currentDefaultOpenKeys}
      items={processedItems}
      style={{ borderRight: 0 }}
    />
  );
};

export default MenuBuilder;
