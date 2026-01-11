import { useNavigate, Link } from 'react-router-dom';
import Sidebar from './Sidebar';
import { useAuth } from '../context';

function Layout({ children }) {
  const { user } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    sessionStorage.removeItem('access_token');
    sessionStorage.removeItem('refresh_token');
    navigate('/login');
  };

  return (
    <div className="d-flex flex-column vh-100">
      <nav className="navbar navbar-dark bg-dark px-4">
        <span className="navbar-brand mb-0 h1">FlaskERP</span>
        <div className="d-flex align-items-center gap-3">
          {user && (
            <span className="text-light small">
              Ciao, <Link to="/profile" className="text-light text-decoration-none fw-bold">{user.email}</Link>
            </span>
          )}
          <button onClick={handleLogout} className="btn btn-outline-light btn-sm">Logout</button>
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