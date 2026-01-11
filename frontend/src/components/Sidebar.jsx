import { NavLink } from 'react-router-dom';

function Sidebar({ user }) {
  const isAdmin = user?.role === 'admin';

  return (
    <div className="bg-white border-end" style={{ width: '250px', minHeight: '100%' }}>
      <div className="p-3">
        <h6 className="text-uppercase text-muted small fw-bold">Menu</h6>
        <ul className="nav flex-column">
          <li className="nav-item mb-2">
            <NavLink 
              to="/dashboard" 
              className={({ isActive }) => `nav-link rounded ${isActive ? 'active bg-light text-primary' : 'text-dark'}`}
            >
              Dashboard
            </NavLink>
          </li>
          {isAdmin && (
            <>
              <li className="nav-item mb-2">
                <NavLink 
                  to="/users" 
                  className={({ isActive }) => `nav-link rounded ${isActive ? 'active bg-light text-primary' : 'text-dark'}`}
                >
                  Utenti
                </NavLink>
              </li>
              <li className="nav-item mb-2">
                <NavLink 
                  to="/anagrafiche" 
                  className={({ isActive }) => `nav-link rounded ${isActive ? 'active bg-light text-primary' : 'text-dark'}`}
                >
                  Anagrafiche
                </NavLink>
              </li>
              <li className="nav-item mb-2">
                <NavLink 
                  to="/products" 
                  className={({ isActive }) => `nav-link rounded ${isActive ? 'active bg-light text-primary' : 'text-dark'}`}
                >
                  Prodotti
                </NavLink>
              </li>
            </>
          )}
          <li className="nav-item mb-2">
            <NavLink 
              to="/sales" 
              className={({ isActive }) => `nav-link rounded ${isActive ? 'active bg-light text-primary' : 'text-dark'}`}
            >
              Vendite
            </NavLink>
          </li>
        </ul>
      </div>
    </div>
  );
}

export default Sidebar;