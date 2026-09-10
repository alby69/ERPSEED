import { useNavigate, Link } from 'react-router-dom';
import Sidebar from './Sidebar';
import AppHeader from './AppHeader';
import CommandPalette from './core/CommandPalette';
import useCommandPalette from '../hooks/useCommandPalette';
import { useAuth, useTheme } from '../context';

function Layout({ children, showBackButton = false, breadcrumbs = [] }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { themeConfig } = useTheme();
  const { isOpen, close } = useCommandPalette();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="d-flex flex-column vh-100">
      <AppHeader showBackButton={showBackButton} breadcrumbs={breadcrumbs.length > 0 ? breadcrumbs : undefined} />
      <CommandPalette isOpen={isOpen} onClose={close} />
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