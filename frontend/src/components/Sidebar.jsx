import React from 'react';
import { Menu, theme } from 'antd';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
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
    ShopOutlined,
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
    const { t } = useTranslation();
    const location = useLocation();
    const navigate = useNavigate();
    const { projectId } = useParams();

    // Main application menu items organized by Area
    const appMenuItems = [
        {
            key: 'area-anagrafiche',
            label: t('menu.areas.anagrafiche'),
            icon: <UserOutlined />,
            children: [
                { key: '/anagrafiche', label: t('menu.blocks.soggetti'), icon: <UserOutlined /> },
                { key: '/ruoli', label: t('menu.blocks.ruoli'), icon: <TeamOutlined /> },
                { key: '/indirizzi', label: t('menu.blocks.indirizzi'), icon: <EnvironmentOutlined /> },
                { key: '/contatti', label: t('menu.blocks.contatti'), icon: <PhoneOutlined /> },
                { key: '/products', label: t('menu.blocks.prodotti'), icon: <AppstoreOutlined /> },
                { key: '/product-categories', label: t('menu.blocks.categorie'), icon: <TagsOutlined /> },
                { key: '/tax-rates', label: t('menu.blocks.aliquoteIva'), icon: <PercentageOutlined /> },
                { key: '/units-of-measure', label: t('menu.blocks.unitaMisura'), icon: <LineHeightOutlined /> },
                { key: '/price-lists', label: t('menu.blocks.listini'), icon: <DollarOutlined /> },
                { key: '/chart-of-accounts', label: t('menu.blocks.pianoConti'), icon: <BookOutlined /> },
            ],
        },
        {
            key: 'area-geografia',
            label: t('menu.areas.geografia'),
            icon: <GlobalOutlined />,
            children: [
                { key: '/geografia/nazioni', label: t('menu.blocks.nazioni'), icon: <GlobalOutlined /> },
                { key: '/geografia/regioni', label: t('menu.blocks.regioni'), icon: <GlobalOutlined /> },
                { key: '/geografia/province', label: t('menu.blocks.province'), icon: <GlobalOutlined /> },
                { key: '/geografia/comuni', label: t('menu.blocks.comuni'), icon: <GlobalOutlined /> },
                { type: 'divider' },
                { key: '/logistics/distances', label: t('menu.blocks.calcoloDistanze'), icon: <CarOutlined /> },
            ],
        },
        {
            key: 'area-acquisti',
            label: t('menu.areas.acquisti'),
            icon: <ShoppingCartOutlined />,
            children: [
                { key: '/purchase-orders', label: t('menu.blocks.ordiniAcquisto'), icon: <ShoppingCartOutlined /> },
                { key: '/purchase-requests', label: t('menu.blocks.richiesteAcquisto'), icon: <FileTextOutlined /> },
                { key: '/goods-receipts', label: t('menu.blocks.ddtEntrata'), icon: <CarOutlined /> },
                { key: '/purchase-returns', label: t('menu.blocks.resiAcquisto'), icon: <RollbackOutlined /> },
            ],
        },
        {
            key: 'area-vendite',
            label: t('menu.areas.vendite'),
            icon: <ShoppingCartOutlined />,
            children: [
                { key: '/sales', label: t('menu.blocks.ordiniVendita'), icon: <ShoppingCartOutlined /> },
                { key: '/quotations', label: t('menu.blocks.preventivi'), icon: <FileTextOutlined /> },
                { key: '/delivery-notes', label: t('menu.blocks.ddtVendita'), icon: <CarOutlined /> },
                { key: '/invoices', label: t('menu.blocks.fatture'), icon: <FileDoneOutlined /> },
                { key: '/sales-returns', label: t('menu.blocks.resiVendita'), icon: <RollbackOutlined /> },
                { key: '/crm', label: t('menu.blocks.crm'), icon: <HeartOutlined /> },
                { key: '/contracts', label: t('menu.blocks.contratti'), icon: <FileProtectOutlined /> },
            ],
        },
        {
            key: 'area-magazzino',
            label: t('menu.areas.magazzino'),
            icon: <InboxOutlined />,
            children: [
                { key: '/stock-levels', label: t('menu.blocks.giacenze'), icon: <InboxOutlined /> },
                { key: '/stock-movements', label: t('menu.blocks.movimenti'), icon: <SwapOutlined /> },
                { key: '/inventory-counts', label: t('menu.blocks.inventari'), icon: <ProfileOutlined /> },
                { key: '/lots', label: t('menu.blocks.lotti'), icon: <BarcodeOutlined /> },
            ],
        },
        {
            key: 'area-contabilita',
            label: t('menu.areas.contabilita'),
            icon: <DollarOutlined />,
            children: [
                { key: '/journal', label: t('menu.blocks.primaNota'), icon: <BookOutlined /> },
                { key: '/maturities', label: t('menu.blocks.scadenzario'), icon: <CalendarOutlined /> },
                { key: '/trial-balance', label: t('menu.blocks.bilancioVerifica'), icon: <DollarOutlined /> },
                { key: '/vat-registers', label: t('menu.blocks.registriIva'), icon: <PercentageOutlined /> },
                { key: '/intrastat', label: t('menu.blocks.intrastat'), icon: <GlobalOutlined /> },
            ],
        },
        {
            key: 'area-produzione',
            label: t('menu.areas.produzione'),
            icon: <ToolOutlined />,
            children: [
                { key: '/bom', label: t('menu.blocks.bom'), icon: <ApartmentOutlined /> },
                { key: '/work-cycles', label: t('menu.blocks.cicliLavoro'), icon: <NodeIndexOutlined /> },
                { key: '/production-orders', label: t('menu.blocks.ordiniProduzione'), icon: <BellOutlined /> },
            ],
        },
        {
            key: 'area-hr',
            label: t('menu.areas.hr'),
            icon: <TeamOutlined />,
            children: [
                { key: '/employees', label: t('menu.blocks.dipendenti'), icon: <TeamOutlined /> },
                { key: '/departments', label: t('menu.blocks.reparti'), icon: <ApartmentOutlined /> },
                { key: '/attendance', label: t('menu.blocks.presenze'), icon: <ClockCircleOutlined /> },
                { key: '/leave-requests', label: t('menu.blocks.feriePermessi'), icon: <CalendarOutlined /> },
            ],
        },
        {
            key: 'area-progetti',
            label: t('menu.areas.progetti'),
            icon: <ProjectOutlined />,
            children: [
                { key: '/projects', label: t('menu.blocks.progetti'), icon: <ProjectOutlined /> },
                { key: '/timesheet', label: t('menu.blocks.timesheet'), icon: <FieldTimeOutlined /> },
                { key: '/project-budgets', label: t('menu.blocks.budgetCommessa'), icon: <FundOutlined /> },
            ],
        },
        {
            key: 'area-analytics',
            label: t('menu.areas.analytics'),
            icon: <BarChartOutlined />,
            children: [
                { key: '/dashboard', label: t('menu.blocks.dashboard'), icon: <DashboardOutlined /> },
                { key: '/dashboard/builder', label: t('menu.blocks.dashboardBuilder'), icon: <BuildOutlined /> },
                { key: '/builder/blocks', label: t('menu.blocks.chartBuilder'), icon: <BarChartOutlined /> },
                { key: '/reports', label: t('menu.blocks.reportDesigner'), icon: <FileSearchOutlined /> },
            ],
        },
    ];

    // Static menu items for the administration section
    const adminItems = [
        {
            key: 'builder-sub',
            label: t('menu.admin.builderSection'),
            icon: <BuildOutlined />,
            children: [
                { key: '/admin/builder', label: t('menu.admin.sysModels') },
                { key: '/admin/blocks', label: t('menu.admin.blocks') },
                { key: '/builder/relationships', label: t('menu.admin.relationshipManager'), icon: <ApartmentOutlined /> },
            ]
        },
        {
            key: 'modules-section',
            label: t('menu.admin.modulesSection'),
            icon: <AppstoreOutlined />,
            children: [
                { key: '/admin/custom-modules', label: t('menu.admin.customModules') },
                { key: '/modules', label: t('menu.admin.systemModules') },
            ]
        },
        { key: `/projects/${projectId}/business-rules`, label: t('menu.admin.businessRules'), icon: <SettingOutlined /> },
        { key: '/users', label: t('menu.admin.users'), icon: <TeamOutlined /> },
        { key: '/test-runner', label: t('menu.admin.testRunner'), icon: <ExperimentOutlined /> },
        { key: '/admin/projects', label: t('menu.admin.projectsAdmin'), icon: <ProjectOutlined /> },
        { key: '/admin/audit-logs', label: t('menu.admin.auditLogs'), icon: <AuditOutlined /> },
        { key: '/ai-assistant', label: t('menu.admin.aiAssistant'), icon: <RobotOutlined /> },
        { key: '/marketplace', label: t('menu.admin.marketplace'), icon: <ShopOutlined /> },
        { key: '/admin/project-import-export', label: t('menu.admin.importExport'), icon: <SwapOutlined /> },
        { key: '/swagger-ui', label: t('menu.admin.apiDocs'), icon: <FileSearchOutlined /> },
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
        label: t('menu.applications'),
        icon: <AppstoreOutlined />,
        children: allAppItems,
    });

    // Add the administration section if the user is an admin/owner
    if (user?.role && ['admin', 'owner'].includes(user.role)) {
        items.push({ type: 'divider' });
        items.push({
            key: 'admin-section',
            label: t('menu.administration'),
            icon: <BarChartOutlined />,
            children: adminItems,
        });
    }

    // Add the logout button at the bottom
    items.push({ type: 'divider' });
    items.push({ key: 'logout', label: t('menu.logout'), icon: <LogoutOutlined />, danger: true });

    const handleMenuClick = (e) => {
        if (e.key === 'logout') {
            logout();
        } else if (e.key === '/swagger-ui') {
            // Open Swagger UI in a new tab
            window.open('/swagger-ui', '_blank');
        }
        else {
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
