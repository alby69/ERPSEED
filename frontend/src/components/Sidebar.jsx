import React from 'react';
import { Menu } from 'antd';
import { Link, useLocation, useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import {
    AppstoreOutlined,
    TeamOutlined,
    ProjectOutlined,
    BuildOutlined,
    BarChartOutlined,
    AuditOutlined,
    LogoutOutlined,
    HomeOutlined,
    DashboardOutlined,
    SettingOutlined,
    ApiOutlined,
    EnvironmentOutlined,
    PhoneOutlined,
    UserOutlined
} from '@ant-design/icons';
import './Sidebar.css';

const Sidebar = ({ projectMenuItems = [] }) => {
    const { user, logout } = useAuth();
    const location = useLocation();
    const navigate = useNavigate();
    const { projectId } = useParams();

    // Static menu items for the administration section
    const adminItems = [
        { key: '/admin/builder', label: 'Builder', icon: <BuildOutlined /> },
        { key: '/admin/workflows', label: 'Workflows', icon: <ApiOutlined /> },
        { key: '/users', label: 'Users', icon: <TeamOutlined /> },
        { key: '/modules', label: 'Modules', icon: <AppstoreOutlined /> },
        { key: '/admin/projects', label: 'Projects Admin', icon: <ProjectOutlined /> },
        { key: '/admin/audit-logs', label: 'Audit Logs', icon: <AuditOutlined /> },
    ];

    // Main application menu items (from enabled modules) - VISION SYSTEM
    const appMenuItems = [
        { key: '/anagrafiche', label: 'Anagrafiche', icon: <UserOutlined /> },
        { key: '/ruoli', label: 'Ruoli', icon: <TeamOutlined /> },
        { key: '/indirizzi', label: 'Indirizzi', icon: <EnvironmentOutlined /> },
        { key: '/contatti', label: 'Contatti', icon: <PhoneOutlined /> },
        { key: '/products', label: 'Prodotti', icon: <AppstoreOutlined /> },
        { key: '/sales', label: 'Vendite', icon: <ProjectOutlined /> },
    ];

    // Dynamically build menu items
    const items = [
        { key: '/projects', label: 'Select Project', icon: <HomeOutlined /> },
    ];

    // Add main application menu
    items.push({ type: 'divider' });
    
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
        <div className="sidebar">
            <div className="sidebar-logo">
                <Link to="/projects">FlaskERP</Link>
            </div>
            <Menu
                theme="dark"
                mode="inline"
                onClick={handleMenuClick}
                selectedKeys={[location.pathname]}
                items={items}
            />
        </div>
    );
};

export default Sidebar;