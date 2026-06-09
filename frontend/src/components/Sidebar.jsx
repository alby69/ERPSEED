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
    AuditOutlined,
    ShoppingCartOutlined,
    InboxOutlined,
    DollarOutlined,
    ToolOutlined,
    TagsOutlined,
    PercentageOutlined,
    LineHeightOutlined,
    BookOutlined,
    FileTextOutlined,
    FileDoneOutlined,
    CarOutlined,
    RollbackOutlined,
    HeartOutlined,
    FileProtectOutlined,
    SwapOutlined,
    ProfileOutlined,
    BarcodeOutlined,
    CalendarOutlined,
    ApartmentOutlined,
    NodeIndexOutlined,
    BellOutlined,
    ClockCircleOutlined,
    FieldTimeOutlined,
    FundOutlined,
    FileSearchOutlined,
    RobotOutlined,
} from '@ant-design/icons';
import './Sidebar.css';

const Sidebar = ({ projectMenuItems = [] }) => {
    const { user, logout } = useAuth();
    const { themeConfig } = useTheme();
    const { token } = theme.useToken();
    const location = useLocation();
    const navigate = useNavigate();
    const { projectId } = useParams();

    // Main application menu items organized by Area
    const appMenuItems = [
        {
            key: 'area-anagrafiche',
            label: 'Anagrafiche',
            icon: <UserOutlined />,
            children: [
                { key: '/anagrafiche', label: 'Soggetti', icon: <UserOutlined /> },
                { key: '/ruoli', label: 'Ruoli', icon: <TeamOutlined /> },
                { key: '/indirizzi', label: 'Indirizzi', icon: <EnvironmentOutlined /> },
                { key: '/contatti', label: 'Contatti', icon: <PhoneOutlined /> },
                { key: '/products', label: 'Prodotti', icon: <AppstoreOutlined /> },
                { key: '/product-categories', label: 'Categorie Prodotto', icon: <TagsOutlined /> },
                { key: '/tax-rates', label: 'Aliquote IVA', icon: <PercentageOutlined /> },
                { key: '/units-of-measure', label: 'Unità di Misura', icon: <LineHeightOutlined /> },
                { key: '/price-lists', label: 'Listini Prezzo', icon: <DollarOutlined /> },
                { key: '/chart-of-accounts', label: 'Piano dei Conti', icon: <BookOutlined /> },
            ],
        },
        {
            key: 'area-geografia',
            label: 'Geografia',
            icon: <GlobalOutlined />,
            children: [
                { key: '/geografia/nazioni', label: 'Nazioni', icon: <GlobalOutlined /> },
                { key: '/geografia/regioni', label: 'Regioni', icon: <GlobalOutlined /> },
                { key: '/geografia/province', label: 'Province', icon: <GlobalOutlined /> },
                { key: '/geografia/comuni', label: 'Comuni', icon: <GlobalOutlined /> },
            ],
        },
        {
            key: 'area-acquisti',
            label: 'Acquisti',
            icon: <ShoppingCartOutlined />,
            children: [
                { key: '/purchase-orders', label: 'Ordini Acquisto', icon: <ShoppingCartOutlined /> },
                { key: '/purchase-requests', label: 'Richieste d\'Acquisto', icon: <FileTextOutlined /> },
                { key: '/goods-receipts', label: 'DDT Entrata Merci', icon: <CarOutlined /> },
                { key: '/purchase-returns', label: 'Resi Acquisti', icon: <RollbackOutlined /> },
            ],
        },
        {
            key: 'area-vendite',
            label: 'Vendite',
            icon: <ShoppingCartOutlined />,
            children: [
                { key: '/sales', label: 'Ordini Vendita', icon: <ShoppingCartOutlined /> },
                { key: '/quotations', label: 'Preventivi', icon: <FileTextOutlined /> },
                { key: '/delivery-notes', label: 'DDT Vendita', icon: <CarOutlined /> },
                { key: '/invoices', label: 'Fatture', icon: <FileDoneOutlined /> },
                { key: '/sales-returns', label: 'Resi Vendita', icon: <RollbackOutlined /> },
                { key: '/crm', label: 'CRM', icon: <HeartOutlined /> },
                { key: '/contracts', label: 'Contratti', icon: <FileProtectOutlined /> },
            ],
        },
        {
            key: 'area-magazzino',
            label: 'Magazzino',
            icon: <InboxOutlined />,
            children: [
                { key: '/stock-levels', label: 'Giacenze', icon: <InboxOutlined /> },
                { key: '/stock-movements', label: 'Movimenti', icon: <SwapOutlined /> },
                { key: '/inventory-counts', label: 'Inventari', icon: <ProfileOutlined /> },
                { key: '/lots', label: 'Lotti e Seriali', icon: <BarcodeOutlined /> },
            ],
        },
        {
            key: 'area-contabilita',
            label: 'Contabilità',
            icon: <DollarOutlined />,
            children: [
                { key: '/journal', label: 'Prima Nota', icon: <BookOutlined /> },
                { key: '/maturities', label: 'Scadenzario', icon: <CalendarOutlined /> },
                { key: '/vat-registers', label: 'Registri IVA', icon: <PercentageOutlined /> },
                { key: '/intrastat', label: 'Intrastat', icon: <GlobalOutlined /> },
            ],
        },
        {
            key: 'area-produzione',
            label: 'Produzione',
            icon: <ToolOutlined />,
            children: [
                { key: '/bom', label: 'Distinte Base', icon: <ApartmentOutlined /> },
                { key: '/work-cycles', label: 'Cicli di Lavoro', icon: <NodeIndexOutlined /> },
                { key: '/production-orders', label: 'Ordini Produzione', icon: <BellOutlined /> },
            ],
        },
        {
            key: 'area-hr',
            label: 'Risorse Umane',
            icon: <TeamOutlined />,
            children: [
                { key: '/employees', label: 'Dipendenti', icon: <TeamOutlined /> },
                { key: '/departments', label: 'Reparti', icon: <ApartmentOutlined /> },
                { key: '/attendance', label: 'Presenze', icon: <ClockCircleOutlined /> },
                { key: '/leave-requests', label: 'Ferie e Permessi', icon: <CalendarOutlined /> },
            ],
        },
        {
            key: 'area-progetti',
            label: 'Progetti',
            icon: <ProjectOutlined />,
            children: [
                { key: '/projects', label: 'Progetti', icon: <ProjectOutlined /> },
                { key: '/timesheet', label: 'Timesheet', icon: <FieldTimeOutlined /> },
                { key: '/project-budgets', label: 'Budget Commessa', icon: <FundOutlined /> },
            ],
        },
        {
            key: 'area-analytics',
            label: 'Analytics',
            icon: <BarChartOutlined />,
            children: [
                { key: '/dashboard', label: 'Dashboard', icon: <DashboardOutlined /> },
                { key: '/dashboard/builder', label: 'Dashboard Builder', icon: <BuildOutlined /> },
                { key: '/builder/blocks', label: 'Chart Builder', icon: <BarChartOutlined /> },
                { key: '/reports', label: 'Report Designer', icon: <FileSearchOutlined /> },
            ],
        },
    ];

    // Static menu items for the administration section
    const adminItems = [
        {
            key: 'builder-sub',
            label: 'Builder',
            icon: <BuildOutlined />,
            children: [
                { key: '/admin/builder', label: 'Modelli (SysModel)' },
                { key: '/admin/blocks', label: 'Blocchi (Block)' },
                { key: '/builder/relationships', label: 'Relationship Manager', icon: <ApartmentOutlined /> },
            ]
        },
        {
            key: 'modules-section',
            label: 'Moduli',
            icon: <AppstoreOutlined />,
            children: [
                { key: '/admin/custom-modules', label: 'Tutti i Moduli' },
                { key: '/modules', label: 'System Modules' },
            ]
        },
        { key: `/projects/${projectId}/business-rules`, label: 'Business Rules', icon: <SettingOutlined /> },
        { key: '/users', label: 'Users', icon: <TeamOutlined /> },
        { key: '/test-runner', label: 'Test Runner', icon: <ExperimentOutlined /> },
        { key: '/admin/projects', label: 'Projects Admin', icon: <ProjectOutlined /> },
        { key: '/admin/audit-logs', label: 'Audit Logs', icon: <AuditOutlined /> },
        { key: '/ai-assistant', label: 'AI Assistant', icon: <RobotOutlined /> },
    ];

    // Build the full menu items array
    const items = [];

    // Clone appMenuItems and merge with projectMenuItems
    const allAppItems = appMenuItems.map(area => ({ ...area, children: [...area.children] }));

    if (projectMenuItems.length > 0) {
        // Add project-specific items to the "Progetti" area
        const progettiArea = allAppItems.find(a => a.key === 'area-progetti');
        projectMenuItems.forEach(item => {
            if (item.children) {
                progettiArea.children.push({
                    key: item.key,
                    label: item.label,
                    icon: <ProjectOutlined />,
                    children: item.children.map(child => ({
                        key: child.path,
                        label: child.label,
                    }))
                });
            } else {
                if (!progettiArea.children.find(i => i.key === item.path)) {
                    progettiArea.children.push({
                        key: item.path,
                        label: item.label,
                        icon: <AppstoreOutlined />
                    });
                }
            }
        });
    }

    items.push({
        key: 'app-section',
        label: 'Applicazioni',
        icon: <AppstoreOutlined />,
        children: allAppItems,
    });

    // Add the administration section if the user is an admin/owner
    if (user?.role && ['admin', 'owner'].includes(user.role)) {
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
        <div className="sidebar" style={{ background: themeConfig.mode === 'dark' ? token.colorBgContainer : themeConfig.surface }}>
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
