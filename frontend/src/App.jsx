import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useParams } from 'react-router-dom';
import { useAuth, ThemeProvider, useTheme } from '@/context';
import { Login, Dashboard, ForgotPassword, ResetPassword, Profile, Users, SoggettiPage, RuoliPage, IndirizziPage, ComuniPage, ContattiPage, NazioniPage, RegioniPage, ProvincePage, Products, ProductDetail, ProjectSelectionPage, ProjectMembersPage, ProjectSettingsPage, ModulesPage } from './pages';
import Sales from './pages/Sales';
import SalesOrderDetail from './pages/SalesOrderDetail';
import SysModelDetail from './pages/SysModelDetail';
import SysModelList from './pages/SysModelList';
import ProjectLayout from './ProjectLayout';
import DynamicModelPage from './pages/DynamicModelPage';
import AuditLogs from './pages/AuditLogs';
import WorkflowsPage from './pages/WorkflowsPage';
import WorkflowBuilder from './pages/WorkflowBuilder';
import BusinessRulesPage from './pages/BusinessRulesPage';
import TestRunnerPage from './pages/TestRunnerPage';
import DashboardBuilder from './pages/DashboardBuilder';
import BlockBuilder from './pages/BlockBuilder';
import MarketplaceBrowse from './pages/MarketplaceBrowse';
import CustomModulesPage from './pages/CustomModulesPage';
import AIAssistantPage from './pages/AIAssistantPage';
import ModuleAppPage from './pages/ModuleAppPage';
import ProjectImportExportPage from './pages/ProjectImportExportPage';
import GDOReconciliationTool from './pages/GDOReconciliationTool';
import PagePlaceholder from './pages/PagePlaceholder';
import RelationshipManagerPage from './pages/RelationshipManagerPage';
import DistanceCalculator from './pages/DistanceCalculator';
import TaxRates from './pages/TaxRates';
import ProductCategories from './pages/ProductCategories';
import UnitsOfMeasure from './pages/UnitsOfMeasure';
import PriceLists from './pages/PriceLists';
import ChartOfAccounts from './pages/ChartOfAccounts';
import Invoices from './pages/Invoices';
import StockMovements from './pages/StockMovements';
import StockLevels from './pages/StockLevels';
import PurchaseOrders from './pages/PurchaseOrders';
import Journal from './pages/Journal';
import GoodsReceipts from './pages/GoodsReceipts';
import Maturities from './pages/Maturities';
import CRMPage from './pages/CRM';
import Quotations from './pages/Quotations';
import DeliveryNotes from './pages/DeliveryNotes';
import HR from './pages/HR';
import Contracts from './pages/Contracts';
import Manufacturing from './pages/Manufacturing';
import ProjectManagement from './pages/ProjectManagement';
import ReportDesigner from './pages/ReportDesigner';
import TrialBalance from './pages/TrialBalance';
import VatRegisters from './pages/VatRegisters';
import IntrastatPage from './pages/Intrastat';
import RiBaPage from './pages/RiBaPage';
import LotsPage from './pages/LotsPage';
import PurchaseRequests from './pages/PurchaseRequests';
import MRPPage from './pages/MRPPage';


// Helper component to load project theme
const ProjectThemeLoader = ({ children }) => {
    const { projectId } = useParams();
    const { fetchTheme, resetTheme } = useTheme();

    useEffect(() => {
        if (projectId) {
            fetchTheme(projectId);
        } else {
            resetTheme();
        }
    }, [projectId, fetchTheme, resetTheme]);

    return children;
};

function App() {
  // Component for public routes (e.g., Login)
  // If the user is already authenticated, redirect to the dashboard
  const PublicRoute = ({ children }) => {
    const { user, isLoading } = useAuth();

    if (isLoading) {
      return <div className="p-5 text-center">Loading...</div>;
    }

    if (user) {
      return <Navigate to="/projects" replace />;
    }

    return children;
  };

  // Component to protect routes based on authentication and role
  const ProtectedRoute = ({ children, roles }) => {
    const { user, isLoading } = useAuth();

    if (isLoading) {
      return <div className="p-5 text-center">Loading...</div>;
    }

    if (!user) {
      return <Navigate to="/login" replace />;
    }

    // Fix: Support both user.role (string) and user.roles (array of objects)
    const hasRole = !roles || roles.includes(user.role) || user.roles?.some(r => roles.includes(r.name));
    if (!hasRole) {
      return <Navigate to="/dashboard" replace />; // Redirect to a safe page
    }

    return children;
  };

return (
    <BrowserRouter>
      <ThemeProvider>
      <Routes>
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route
          path="/login"
          element={
            <PublicRoute>
              <Login />
            </PublicRoute>
          }
        />

        {/* Project Selection and Project-specific routes */}
        <Route path="/projects" element={<ProtectedRoute><ProjectSelectionPage /></ProtectedRoute>} />
        <Route path="/projects/:projectId" element={<ProtectedRoute><ProjectThemeLoader><ProjectLayout /></ProjectThemeLoader></ProtectedRoute>}>
            {/* A default page for a project, e.g. a dashboard */}
            <Route index element={<Dashboard />} />
            {/* Member management page */}
            <Route path="members" element={<ProjectMembersPage />} />
            {/* Project settings page */}
            <Route path="settings" element={<ProjectSettingsPage />} />
            {/* The route for dynamic models, now nested */}
            <Route path="data/:modelName" element={<DynamicModelPage />} />
            <Route path="gdo-reconciliation" element={<GDOReconciliationTool />} />
            {/* Module App Dashboard - App-like experience */}
            <Route path="app/:moduleName" element={<ModuleAppPage />} />
            <Route path="workflows" element={<WorkflowsPage />} />
            {/* You can add more project-specific routes here */}
        </Route>

        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/dashboard/builder"
          element={
            <ProtectedRoute>
              <DashboardBuilder />
            </ProtectedRoute>
          }
        />
        <Route
          path="/dashboard/builder/:dashboardId"
          element={
            <ProtectedRoute>
              <DashboardBuilder />
            </ProtectedRoute>
          }
        />
        <Route
          path="/builder/blocks"
          element={
            <ProtectedRoute>
              <BlockBuilder />
            </ProtectedRoute>
          }
        />
        <Route
          path="/builder/blocks/:blockId"
          element={
            <ProtectedRoute>
              <BlockBuilder />
            </ProtectedRoute>
          }
        />
        <Route
          path="/builder/relationships"
          element={
            <ProtectedRoute roles={['admin', 'owner']}>
              <RelationshipManagerPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/marketplace"
          element={
            <ProtectedRoute>
              <MarketplaceBrowse />
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          }
        />
        <Route
          path="/users"
          element={
            <ProtectedRoute roles={['admin', 'owner']}>
              <Users />
            </ProtectedRoute>
          }
        />
        <Route
          path="/anagrafiche"
          element={
            <ProtectedRoute roles={['admin', 'owner']}>
              <SoggettiPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/ruoli"
          element={
            <ProtectedRoute roles={['admin', 'owner']}>
              <RuoliPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/indirizzi"
          element={
            <ProtectedRoute roles={['admin', 'owner']}>
              <IndirizziPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/comuni"
          element={<Navigate to="/geografia/comuni" replace />}
        />
        <Route
          path="/geografia/comuni"
          element={
            <ProtectedRoute roles={['admin', 'owner']}>
              <ComuniPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/geografia/nazioni"
          element={
            <ProtectedRoute roles={['admin', 'owner']}>
              <NazioniPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/geografia/regioni"
          element={
            <ProtectedRoute roles={['admin', 'owner']}>
              <RegioniPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/geografia/province"
          element={
            <ProtectedRoute roles={['admin', 'owner']}>
              <ProvincePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/contatti"
          element={
            <ProtectedRoute roles={['admin', 'owner']}>
              <ContattiPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/products"
          element={
            <ProtectedRoute roles={['admin', 'owner']}>
              <Products />
            </ProtectedRoute>
          }
        />
        <Route
          path="/products/new"
          element={
            <ProtectedRoute roles={['admin', 'owner']}>
              <ProductDetail />
            </ProtectedRoute>
          }
        />
        <Route
          path="/products/:id"
          element={
            <ProtectedRoute roles={['admin', 'owner']}>
              <ProductDetail />
            </ProtectedRoute>
          }
        />
        <Route
          path="/modules"
          element={
            <ProtectedRoute roles={['admin', 'owner']}>
              <ModulesPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/test-runner"
          element={
            <ProtectedRoute roles={['admin', 'owner']}>
              <TestRunnerPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/sales"
          element={
            <ProtectedRoute>
              <Sales />
            </ProtectedRoute>
          }
        />
        <Route
          path="/sales/new"
          element={
            <ProtectedRoute>
              <SalesOrderDetail />
            </ProtectedRoute>
          }
        />
        <Route
          path="/sales/:orderId"
          element={
            <ProtectedRoute>
              <SalesOrderDetail />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/builder/:modelId"
          element={
            <ProtectedRoute roles={['admin', 'owner']}>
              <SysModelDetail />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/builder"
          element={
            <ProtectedRoute roles={['admin', 'owner']}>
              <SysModelList />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/blocks"
          element={
            <ProtectedRoute roles={['admin', 'owner']}>
              <BlockBuilder />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/custom-modules"
          element={
            <ProtectedRoute roles={['admin', 'owner']}>
              <CustomModulesPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/project-import-export"
          element={
            <ProtectedRoute roles={['admin', 'owner']}>
              <ProjectImportExportPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/bi-builder"
          element={
            <ProtectedRoute roles={['admin', 'owner']}>
              <div className="p-5 text-center"><h2>BI Builder</h2><p>Module coming soon...</p></div>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/audit-logs"
          element={
            <ProtectedRoute roles={['admin', 'owner']}>
              <AuditLogs />
            </ProtectedRoute>
          }
        />
        <Route
          path="/ai-assistant"
          element={
            <ProtectedRoute roles={['admin', 'owner']}>
              <AIAssistantPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/projects/:projectId/business-rules"
          element={
            <ProtectedRoute roles={['admin', 'owner']}>
              <BusinessRulesPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/projects/:projectId/workflow-builder"
          element={
            <ProtectedRoute roles={['admin', 'owner']}>
              <WorkflowBuilder />
            </ProtectedRoute>
          }
        />
        <Route
          path="/projects/:projectId/workflow-builder/:workflowId"
          element={
            <ProtectedRoute roles={['admin', 'owner']}>
              <WorkflowBuilder />
            </ProtectedRoute>
          }
        />
        {/* === Anagrafiche e Dati Base - Nuovi Blocchi === */}
        <Route path="/product-categories" element={<ProtectedRoute roles={['admin', 'owner']}><ProductCategories /></ProtectedRoute>} />
        <Route path="/tax-rates" element={<ProtectedRoute roles={['admin', 'owner']}><TaxRates /></ProtectedRoute>} />
        <Route path="/units-of-measure" element={<ProtectedRoute roles={['admin', 'owner']}><UnitsOfMeasure /></ProtectedRoute>} />
        <Route path="/price-lists" element={<ProtectedRoute roles={['admin', 'owner']}><PriceLists /></ProtectedRoute>} />
        <Route path="/chart-of-accounts" element={<ProtectedRoute roles={['admin', 'owner']}><ChartOfAccounts /></ProtectedRoute>} />

        {/* === Acquisti === */}
        <Route path="/purchase-orders" element={<ProtectedRoute roles={['admin', 'owner']}><PurchaseOrders /></ProtectedRoute>} />
        <Route path="/purchase-requests" element={<ProtectedRoute roles={['admin', 'owner']}><PurchaseRequests /></ProtectedRoute>} />
        <Route path="/goods-receipts" element={<ProtectedRoute roles={['admin', 'owner']}><GoodsReceipts /></ProtectedRoute>} />
        <Route path="/purchase-returns" element={<ProtectedRoute roles={['admin', 'owner']}><PagePlaceholder title="Resi Acquisti" priority="P2" /></ProtectedRoute>} />

        {/* === Vendite === */}
        <Route path="/quotations" element={<ProtectedRoute roles={['admin', 'owner']}><Quotations /></ProtectedRoute>} />
        <Route path="/delivery-notes" element={<ProtectedRoute roles={['admin', 'owner']}><DeliveryNotes /></ProtectedRoute>} />
        <Route path="/invoices" element={<ProtectedRoute roles={['admin', 'owner']}><Invoices /></ProtectedRoute>} />
        <Route path="/sales-returns" element={<ProtectedRoute roles={['admin', 'owner']}><PagePlaceholder title="Resi Vendita" priority="P2" /></ProtectedRoute>} />
        <Route path="/crm" element={<ProtectedRoute roles={['admin', 'owner']}><CRMPage /></ProtectedRoute>} />
        <Route path="/contracts" element={<ProtectedRoute roles={['admin', 'owner']}><Contracts /></ProtectedRoute>} />

        {/* === Magazzino === */}
        <Route path="/stock-levels" element={<ProtectedRoute roles={['admin', 'owner']}><StockLevels /></ProtectedRoute>} />
        <Route path="/stock-movements" element={<ProtectedRoute roles={['admin', 'owner']}><StockMovements /></ProtectedRoute>} />
        <Route path="/inventory-counts" element={<ProtectedRoute roles={['admin', 'owner']}><PagePlaceholder title="Inventari Fisici" priority="P2" /></ProtectedRoute>} />
        <Route path="/lots" element={<ProtectedRoute roles={['admin', 'owner']}><LotsPage /></ProtectedRoute>} />

        {/* === Contabilità === */}
        <Route path="/journal" element={<ProtectedRoute roles={['admin', 'owner']}><Journal /></ProtectedRoute>} />
        <Route path="/maturities" element={<ProtectedRoute roles={['admin', 'owner']}><Maturities /></ProtectedRoute>} />
        <Route path="/trial-balance" element={<ProtectedRoute roles={['admin', 'owner']}><TrialBalance /></ProtectedRoute>} />
        <Route path="/vat-registers" element={<ProtectedRoute roles={['admin', 'owner']}><VatRegisters /></ProtectedRoute>} />
        <Route path="/intrastat" element={<ProtectedRoute roles={['admin', 'owner']}><IntrastatPage /></ProtectedRoute>} />
        <Route path="/riba" element={<ProtectedRoute roles={['admin', 'owner']}><RiBaPage /></ProtectedRoute>} />

        {/* === Produzione === */}
        <Route path="/production" element={<ProtectedRoute roles={['admin', 'owner']}><Manufacturing /></ProtectedRoute>} />
        <Route path="/mrp" element={<ProtectedRoute roles={['admin', 'owner']}><MRPPage /></ProtectedRoute>} />

        {/* === HR === */}
        <Route path="/employees" element={<ProtectedRoute roles={['admin', 'owner']}><HR /></ProtectedRoute>} />
        <Route path="/departments" element={<ProtectedRoute roles={['admin', 'owner']}><PagePlaceholder title="Reparti" priority="P2" /></ProtectedRoute>} />
        <Route path="/attendance" element={<ProtectedRoute roles={['admin', 'owner']}><HR /></ProtectedRoute>} />
        <Route path="/leave-requests" element={<ProtectedRoute roles={['admin', 'owner']}><HR /></ProtectedRoute>} />

        {/* === Progetti === */}
        <Route path="/project-management" element={<ProtectedRoute roles={['admin', 'owner']}><ProjectManagement /></ProtectedRoute>} />
        <Route path="/timesheet" element={<ProtectedRoute roles={['admin', 'owner']}><ProjectManagement /></ProtectedRoute>} />
        <Route path="/project-budgets" element={<ProtectedRoute roles={['admin', 'owner']}><ProjectManagement /></ProtectedRoute>} />

        {/* === Logistica === */}
        <Route path="/logistics/distances" element={<ProtectedRoute roles={['admin', 'owner']}><DistanceCalculator /></ProtectedRoute>} />

        {/* === Analytics === */}
        <Route path="/reports" element={<ProtectedRoute roles={['admin', 'owner']}><ReportDesigner /></ProtectedRoute>} />

        {/* Redirect everything to the dashboard; if not logged in, ProtectedRoute will send to login */}
        <Route path="*" element={<Navigate to="/projects" replace />} />
      </Routes>
      </ThemeProvider>
    </BrowserRouter>
  );
}

export default App;