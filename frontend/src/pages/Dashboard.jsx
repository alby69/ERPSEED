import { useEffect, useState } from 'react';
import { Layout } from '../components';
import { apiFetch } from '../utils';
import { useAuth } from '../context';

function Dashboard() {
  const { user } = useAuth();
  const [usersList, setUsersList] = useState([]);

  useEffect(() => {
    if (user?.role === 'admin') {
      loadUsersList();
    }
  }, [user]);

  const loadUsersList = () => {
    apiFetch('/users')
    .then(res => res.json())
    .then(data => setUsersList(data));
  };

  if (!user) return null; // Layout will handle loading/redirect

  return (
    <Layout>
      <h2>Dashboard</h2>
      <p className="text-muted">Ruolo: <span className="badge bg-secondary">{user.role}</span></p>
      <hr />

      {user.role === 'admin' && (
        <div className="mt-4">
          <h4>Gestione Utenti (Area Admin)</h4>
          <ul className="list-group mt-3">
            {usersList.map(u => (
              <li key={u.id} className="list-group-item d-flex justify-content-between align-items-center">
                {u.email} <span className="badge bg-primary rounded-pill">{u.role}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </Layout>
  );
}

export default Dashboard;