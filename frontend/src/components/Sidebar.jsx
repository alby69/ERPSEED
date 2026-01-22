import { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import { apiFetch } from '../utils';

function Sidebar({ user }) {
  // Correzione: controlla se l'utente ha il ruolo 'admin' nell'array dei ruoli.
  // L'API /me restituisce i ruoli come un array di oggetti (es. [{name: 'admin'}]).
  const isAdmin = user?.role === 'admin' || user?.roles?.some(role => role.name === 'admin');
  const [dynamicModels, setDynamicModels] = useState([]);

  useEffect(() => {
    if (user) {
      // Carica i modelli dinamici per il menu
      apiFetch('/sys-models')
        .then(res => {
          if (res.ok) return res.json();
          return [];
        })
        .then(data => setDynamicModels(data))
        .catch(err => console.error("Failed to load dynamic models", err));
    }
  }, [user]);

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
              <li className="nav-item mb-2">
                <NavLink 
                  to="/admin/builder" 
                  className={({ isActive }) => `nav-link rounded ${isActive ? 'active bg-light text-primary' : 'text-dark'}`}
                >
                  Builder (Admin)
                </NavLink>
              </li>
              <li className="nav-item mb-2">
                <NavLink 
                  to="/admin/bi-builder" 
                  className={({ isActive }) => `nav-link rounded ${isActive ? 'active bg-light text-primary' : 'text-dark'}`}
                >
                  BI Builder
                </NavLink>
              </li>
              <li className="nav-item mb-2">
                <NavLink 
                  to="/admin/audit-logs" 
                  className={({ isActive }) => `nav-link rounded ${isActive ? 'active bg-light text-primary' : 'text-dark'}`}
                >
                  Audit Logs
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

        {/* Sezione Dinamica per i Modelli Creati */}
        {dynamicModels.length > 0 && (
          <>
            <h6 className="text-uppercase text-muted small fw-bold mt-4">Applicazioni</h6>
            <ul className="nav flex-column">
              {dynamicModels.map(model => (
                <li className="nav-item mb-2" key={model.id}>
                  <NavLink 
                    to={`/data/${model.name}`} 
                    className={({ isActive }) => `nav-link rounded ${isActive ? 'active bg-light text-primary' : 'text-dark'}`}
                  >
                    {model.title}
                  </NavLink>
                </li>
              ))}
            </ul>
          </>
        )}
      </div>
    </div>
  );
}

export default Sidebar;