import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context';
import { Login, Dashboard, ForgotPassword, ResetPassword, Profile, Users, Parties, Products, Sales } from './pages';

function App() {
  // Componente per proteggere le rotte in base all'autenticazione e al ruolo
  const ProtectedRoute = ({ children, roles }) => {
    const { user, isLoading } = useAuth();

    if (isLoading) {
      return <div className="p-5 text-center">Caricamento...</div>;
    }

    if (!user) {
      return <Navigate to="/login" replace />;
    }

    if (roles && !roles.includes(user.role)) {
      return <Navigate to="/dashboard" replace />; // Redirect to a safe page
    }

    return children;
  };

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
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
        <Route path="*" element={<Navigate to="/login" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;