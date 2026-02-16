import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '@/context';
import { Login, Dashboard, ForgotPassword, ResetPassword, Profile, Users, Parties, Products, ProjectSelectionPage, ProjectMembersPage, ProjectSettingsPage } from './pages';
import Sales from './pages/Sales';
import SalesOrderDetail from './pages/SalesOrderDetail';
import SysModelDetail from './pages/SysModelDetail';
import SysModelList from './pages/SysModelList';
import ProjectLayout from './ProjectLayout'; // Path corretto
import DynamicModelPage from './pages/DynamicModelPage';
import AuditLogs from './pages/AuditLogs';
import WorkflowsPage from './pages/WorkflowsPage';


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
        <Route path="/projects/:projectId" element={<ProtectedRoute><ProjectLayout /></ProtectedRoute>}>
            {/* A default page for a project, e.g. a dashboard */}
            <Route index element={<Dashboard />} /> 
            {/* Member management page */}
            <Route path="members" element={<ProjectMembersPage />} />
            {/* Project settings page */}
            <Route path="settings" element={<ProjectSettingsPage />} />
            {/* The route for dynamic models, now nested */}
            <Route path="data/:modelName" element={<DynamicModelPage />} /> 
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
              <Parties />
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
          path="/admin/workflows" 
          element={
            <ProtectedRoute roles={['admin']}>
              <WorkflowsPage />
            </ProtectedRoute>
          } 
        />
        {/* Redirect everything to the dashboard; if not logged in, ProtectedRoute will send to login */}
        <Route path="*" element={<Navigate to="/projects" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;