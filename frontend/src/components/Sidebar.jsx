import React from 'react';
import { Menu, theme } from 'antd';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { useAuth, useTheme } from '@/context';
import {
    AppstoreOutlined,
    TeamOutlined,
    ProjectOutlined,
    BuildOutlined,
    BarChartOutlined,
    LogoutOutlined,
    HomeOutlined,
    DashboardOutlined,
    SettingOutlined,
    ApiOutlined,
    EnvironmentOutlined,
    PhoneOutlined,
    UserOutlined,
    GlobalOutlined,
    ExperimentOutlined,
    AuditOutlined
} from '@ant-design/icons';
import './Sidebar.css';

const Sidebar = ({ projectMenuItems = [] }) => {
    const { user, logout } = useAuth();
    const { themeConfig } = useTheme();
    const { token } = theme.useToken();
    const location = useLocation();
    const navigate = useNavigate();
    const { projectId } = useParams();

    // Static menu items for the administration section
    const adminItems = [
        { key: '/admin/builder', label: 'Builder', icon: <BuildOutlined /> },
        { 
            key: 'modules-section', 
            label: 'Moduli', 
            icon: <AppstoreOutlined />,
            children: [
                { key: '/admin/custom-modules', label: 'Tutti i Moduli' },
                { key: '/modules', label: 'System Modules' },
            ]
        },
        { key: '/admin/workflows', label: 'Workflows', icon: <ApiOutlined /> },
        { key: '/users', label: 'Users', icon: <TeamOutlined /> },
        { key: '/test-runner', label: 'Test Runner', icon: <ExperimentOutlined /> },
        { key: '/admin/projects', label: 'Projects Admin', icon: <ProjectOutlined /> },
        { key: '/admin/audit-logs', label: 'Audit Logs', icon: <AuditOutlined /> },
        { key: '/ai-assistant', label: 'AI Assistant', icon: <SettingOutlined /> },
    ];

    // Main application menu items (from enabled modules) - VISION SYSTEM
    const appMenuItems = [
        { key: '/anagrafiche', label: 'Anagrafiche', icon: <UserOutlined /> },
        { key: '/ruoli', label: 'Ruoli', icon: <TeamOutlined /> },
        { key: '/indirizzi', label: 'Indirizzi', icon: <EnvironmentOutlined /> },
        { key: '/comuni', label: 'Comuni', icon: <GlobalOutlined /> },
        { key: '/contatti', label: 'Contatti', icon: <PhoneOutlined /> },
        { key: '/products', label: 'Prodotti', icon: <AppstoreOutlined /> },
        { key: '/sales', label: 'Vendite', icon: <ProjectOutlined /> },
    ];

    // Dynamically build menu items - no need for "Select Project" since it's in the header now
    
    // Add main application menu
    const items = [];
    
    // Combine static app items with dynamic project menu items
    const allAppItems = [...appMenuItems];
    if (projectMenuItems.length > 0) {
        projectMenuItems.forEach(item => {
            // Avoid duplicates
            if (!allAppItems.find(i => i.key === item.path)) {
                allAppItems.push({
                    key: item.path,
                    label: item.label,
                    icon: <AppstoreOutlined />
                });
            }
        });
    }
    
    items.push({
        key: 'app-section',
        label: 'Applicazioni',
        icon: <AppstoreOutlined />,
        children: allAppItems,
    });

    // Add the administration section if the user is an admin
    if (user?.role === 'admin') {
        items.push({ type: 'divider' });
        items.push({
            key: 'admin-section',
            label: 'Administration',
            icon: <BarChartOutlined />,
            children: adminItems,
        });
    }

    // Add the logout button at the bottom
    items.push({ type: 'divider' });
    items.push({ key: 'logout', label: 'Logout', icon: <LogoutOutlined />, danger: true });

    const handleMenuClick = (e) => {
        if (e.key === 'logout') {
            logout();
        } else {
            navigate(e.key);
        }
    };

    return (
        <div className="sidebar" style={{ background: themeConfig.mode === 'dark' ? token.colorBgContainer : '#fff' }}>
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

export default Sidebar;
