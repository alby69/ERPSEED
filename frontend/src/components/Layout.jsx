import { useNavigate, Link } from 'react-router-dom';
import Sidebar from './Sidebar';
import AppHeader from './AppHeader';
import { useAuth, useTheme } from '../context';

function Layout({ children, showBackButton = false, breadcrumbs = [] }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { themeConfig } = useTheme();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="d-flex flex-column vh-100">
      <AppHeader showBackButton={showBackButton} breadcrumbs={breadcrumbs.length > 0 ? breadcrumbs : undefined} />
      <div className="d-flex flex-grow-1">
        <Sidebar user={user} />
        <div className="flex-grow-1 p-4 bg-light overflow-auto">
          {children}
        </div>
      </div>
    </div>
  );
}

export default Layout;