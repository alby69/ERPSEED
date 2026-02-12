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
    SettingOutlined
} from '@ant-design/icons';
import './Sidebar.css';

const Sidebar = ({ projectMenuItems = [] }) => {
    const { user, logout } = useAuth();
    const location = useLocation();
    const navigate = useNavigate();
    const { projectId } = useParams();

    // Voci di menu statiche per la sezione di amministrazione
    const adminItems = [
        { key: '/admin/builder', label: 'Builder', icon: <BuildOutlined /> },
        { key: '/users', label: 'Users', icon: <TeamOutlined /> },
        { key: '/admin/projects', label: 'Projects Admin', icon: <ProjectOutlined /> },
        { key: '/admin/audit-logs', label: 'Audit Logs', icon: <AuditOutlined /> },
    ];

    // Costruisce dinamicamente le voci del menu
    const items = [
        { key: '/projects', label: 'Seleziona Progetto', icon: <HomeOutlined /> },
    ];

    if (projectId) {
        items.push({ key: `/projects/${projectId}`, label: 'Dashboard Progetto', icon: <DashboardOutlined /> });
        items.push({ key: `/projects/${projectId}/members`, label: 'Membri del Team', icon: <TeamOutlined /> });
        items.push({ key: `/projects/${projectId}/settings`, label: 'Impostazioni', icon: <SettingOutlined /> });
    }

    // Aggiunge le applicazioni del progetto corrente, se presenti
    if (projectMenuItems.length > 0) {
        items.push({
            key: 'project-apps',
            label: 'Applicazioni',
            icon: <AppstoreOutlined />,
            children: projectMenuItems.map(item => ({
                key: item.path,
                label: item.label,
            }))
        });
    }

    // Aggiunge la sezione di amministrazione se l'utente è un admin
    if (user?.role === 'admin') {
        items.push({ type: 'divider' });
        items.push({
            key: 'admin-section',
            label: 'Amministrazione',
            icon: <BarChartOutlined />,
            children: adminItems,
        });
    }

    // Aggiunge il pulsante di logout in fondo
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