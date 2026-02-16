import { useNavigate, Link } from 'react-router-dom';
import Sidebar from './Sidebar';
import { useAuth } from '../context';
import LanguageSelector from './LanguageSelector';
import { useTranslation } from 'react-i18next';

function Layout({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { t } = useTranslation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="d-flex flex-column vh-100">
      <nav className="navbar navbar-dark bg-dark px-4">
        <span className="navbar-brand mb-0 h1">FlaskERP</span>
        <div className="d-flex align-items-center gap-3">
          <LanguageSelector />
          {user && (
            <div className="d-flex align-items-center gap-2">
              <img 
                src={user.avatar ? `http://localhost:5000/uploads/${user.avatar}` : `https://ui-avatars.com/api/?name=${user.first_name}+${user.last_name}&background=random`} 
                alt="Avatar" 
                className="rounded-circle border border-light"
                style={{ width: '32px', height: '32px', objectFit: 'cover' }}
              />
              <span className="text-light small">
                Hi, <Link to="/profile" className="text-light text-decoration-none fw-bold">{user.first_name || user.email}</Link>
              </span>
            </div>
          )}
          <button onClick={handleLogout} className="btn btn-outline-light btn-sm">{t('auth.logout')}</button>
        </div>
      </nav>

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