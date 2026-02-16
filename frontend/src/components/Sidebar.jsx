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
    ApiOutlined
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