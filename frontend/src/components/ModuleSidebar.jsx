/**
 * ModuleSidebar - Sidebar dinamica basata sui moduli abilitati
 */
import React from 'react';
import { Menu } from 'antd';
import { Link, useLocation, useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { useMenu } from '@/hooks/useModules';
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
    ShoppingCartOutlined,
    UserOutlined,
    FileTextOutlined,
    SettingOutlined as SettingsIcon,
} from '@ant-design/icons';
import './Sidebar.css';

// Mappa icone per categorie standard
const ICON_MAP = {
    'users': <UserOutlined />,
    'shopping-cart': <ShoppingCartOutlined />,
    'package': <AppstoreOutlined />,
    'truck': <TeamOutlined />,
    'calculator': <BarChartOutlined />,
    'warehouse': <AppstoreOutlined />,
    'folder': <ProjectOutlined />,
    'heart': <TeamOutlined />,
    'factory': <BuildOutlined />,
    'file-text': <FileTextOutlined />,
    'default': <AppstoreOutlined />
};

// Funzione per ottenere icona dal nome
const getIcon = (iconName) => {
    return ICON_MAP[iconName] || ICON_MAP['default'];
};

const ModuleSidebar = ({ projectMenuItems = [] }) => {
    const { user, logout } = useAuth();
    const location = useLocation();
    const navigate = useNavigate();
    const { projectId } = useParams();
    const { menu: moduleMenu, loading } = useMenu();

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
        { key: '/admin/projects', label: 'Projects Admin', icon: <ProjectOutlined /> },
        { key: '/admin/audit-logs', label: 'Audit Logs', icon: <AuditOutlined /> },
    ];

    // Dynamically build menu items
    const items = [
        { key: '/projects', label: 'Select Project', icon: <HomeOutlined /> },
    ];

    if (projectId) {
        items.push({ key: `/projects/${projectId}`, label: 'Project Dashboard', icon: <DashboardOutlined /> });
        items.push({ key: `/projects/${projectId}/members`, label: 'Team Members', icon: <TeamOutlined /> });
        items.push({ key: `/projects/${projectId}/settings`, label: 'Settings', icon: <SettingOutlined /> });
    }

    // Add the applications of the current project, if present
    if (projectMenuItems.length > 0) {
        items.push({
            key: 'project-apps',
            label: 'Applications',
            icon: <AppstoreOutlined />,
            children: projectMenuItems.map(item => ({
                key: item.path,
                label: item.label,
            }))
        });
    }

    // Aggiungi menu dinamico dai moduli
    if (moduleMenu && moduleMenu.length > 0) {
        const moduleMenuItems = moduleMenu.map(section => {
            const item = {
                key: section.id,
                label: section.label,
                icon: getIcon(section.icon),
            };

            // Aggiungi figli se presenti
            if (section.children && section.children.length > 0) {
                item.children = section.children.map(child => ({
                    key: child.path,
                    label: child.label,
                    icon: getIcon(child.icon)
                }));
            }

            return item;
        });

        items.push({ type: 'divider' });
        items.push(...moduleMenuItems);
    }

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

    if (loading) {
        return (
            <div className="sidebar">
                <div className="sidebar-logo">
                    <Link to="/projects">ERPSeed</Link>
                </div>
                <div style={{ padding: '20px', color: '#888' }}>Caricamento menu...</div>
            </div>
        );
    }

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

export default ModuleSidebar;
