import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useParams } from 'react-router-dom';
import { useAuth, ThemeProvider, useTheme } from '@/context';
import { Login, Dashboard, ForgotPassword, ResetPassword, Profile, Users, SoggettiPage, RuoliPage, IndirizziPage, ComuniPage, ContattiPage, Products, ProjectSelectionPage, ProjectMembersPage, ProjectSettingsPage, ModulesPage } from './pages';
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
            <ProtectedRoute roles={['admin']}>
              <Users />
            </ProtectedRoute>
          }
        />
        <Route
          path="/anagrafiche"
          element={
            <ProtectedRoute roles={['admin']}>
              <SoggettiPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/ruoli"
          element={
            <ProtectedRoute roles={['admin']}>
              <RuoliPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/indirizzi"
          element={
            <ProtectedRoute roles={['admin']}>
              <IndirizziPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/comuni"
          element={
            <ProtectedRoute roles={['admin']}>
              <ComuniPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/contatti"
          element={
            <ProtectedRoute roles={['admin']}>
              <ContattiPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/products"
          element={
            <ProtectedRoute roles={['admin']}>
              <Products />
            </ProtectedRoute>
          }
        />
        <Route
          path="/modules"
          element={
            <ProtectedRoute roles={['admin']}>
              <ModulesPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/test-runner"
          element={
            <ProtectedRoute roles={['admin']}>
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
            <ProtectedRoute roles={['admin']}>
              <SysModelDetail />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/builder"
          element={
            <ProtectedRoute roles={['admin']}>
              <SysModelList />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/custom-modules"
          element={
            <ProtectedRoute roles={['admin']}>
              <CustomModulesPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/project-import-export"
          element={
            <ProtectedRoute roles={['admin']}>
              <ProjectImportExportPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/bi-builder"
          element={
            <ProtectedRoute roles={['admin']}>
              <div className="p-5 text-center"><h2>BI Builder</h2><p>Module coming soon...</p></div>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/audit-logs"
          element={
            <ProtectedRoute roles={['admin']}>
              <AuditLogs />
            </ProtectedRoute>
          }
        />
        <Route
          path="/ai-assistant"
          element={
            <ProtectedRoute roles={['admin']}>
              <AIAssistantPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/workflows"
          element={
            <ProtectedRoute roles={['admin']}>
              <WorkflowsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/projects/:projectId/business-rules"
          element={
            <ProtectedRoute roles={['admin']}>
              <BusinessRulesPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/projects/:projectId/workflow-builder"
          element={
            <ProtectedRoute roles={['admin']}>
              <WorkflowBuilder />
            </ProtectedRoute>
          }
        />
        <Route
          path="/projects/:projectId/workflow-builder/:workflowId"
          element={
            <ProtectedRoute roles={['admin']}>
              <WorkflowBuilder />
            </ProtectedRoute>
          }
        />
        {/* Redirect everything to the dashboard; if not logged in, ProtectedRoute will send to login */}
        <Route path="*" element={<Navigate to="/projects" replace />} />
      </Routes>
      </ThemeProvider>
    </BrowserRouter>
  );
}

export default App;