import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Layout } from '../components';
import DashboardWidgets from '../components/DashboardWidgets';
import ChartWidget from '../components/ChartWidget';
import { apiFetch } from '../utils';
import { useAuth } from '../context';

function Dashboard() {
  const { projectId } = useParams();
  const { user } = useAuth();
  const [usersList, setUsersList] = useState([]);
  const [dashboards, setDashboards] = useState([]);
  const [selectedDashboard, setSelectedDashboard] = useState(null);
  const [dashboardCharts, setDashboardCharts] = useState([]);
  const [dateFilters, setDateFilters] = useState({ from: '', to: '' });

  useEffect(() => {
    if (user?.role === 'admin') {
      loadUsersList();
    }
    loadDashboards();
  }, [user]);

  const loadDashboards = () => {
    apiFetch('/sys-dashboards').then(res => res.json()).then(data => {
      setDashboards(data);
      // Seleziona la prima dashboard di default
      if (data.length > 0) {
        handleDashboardChange(data[0].id);
      }
    }).catch(console.error);
  };

  const handleDashboardChange = (dashboardId) => {
    if (!dashboardId) {
      setSelectedDashboard(null);
      setDashboardCharts([]);
      return;
    }
    // Carica il layout della dashboard specifica
    apiFetch(`/sys-dashboards/${dashboardId}`).then(res => res.json()).then(dashboard => {
      setSelectedDashboard(dashboard);
      try {
        const layout = JSON.parse(dashboard.layout || '{}');
        setDashboardCharts(layout.charts || []);
      } catch (e) {
        setDashboardCharts([]);
      }
    }).catch(console.error);
  };

  const loadUsersList = () => {
    apiFetch('/users')
    .then(res => res.json())
    .then(data => setUsersList(data));
  };

  if (!user) return null; // Layout will handle loading/redirect

  return (
    <Layout>
      <div className="d-flex justify-content-between align-items-center">
        <h2>Dashboard</h2>
        <div className="d-flex gap-2 align-items-center">
          <span className="text-muted small">Periodo:</span>
          <input type="date" className="form-control form-control-sm" value={dateFilters.from} onChange={e => setDateFilters({...dateFilters, from: e.target.value})} />
          <span className="text-muted">-</span>
          <input type="date" className="form-control form-control-sm" value={dateFilters.to} onChange={e => setDateFilters({...dateFilters, to: e.target.value})} />
        </div>
      </div>
      
      <p className="text-muted">Ruolo: <span className="badge bg-secondary">{user.role}</span></p>
      <hr />

      {/* Widget Dinamici dal Builder (Modello: dashboard_kpi) */}
      <DashboardWidgets modelName="dashboard_kpi" projectId={projectId} />

      {/* Selettore Dashboard */}
      {dashboards.length > 0 && (
        <div className="mb-4">
          <label htmlFor="dashboard-selector" className="form-label fw-bold">Visualizza Dashboard</label>
          <select 
            id="dashboard-selector" 
            className="form-select" 
            value={selectedDashboard?.id || ''}
            onChange={(e) => handleDashboardChange(e.target.value)}
          >
            {dashboards.map(d => <option key={d.id} value={d.id}>{d.title}</option>)}
          </select>
        </div>
      )}

      {/* Grafici Dinamici dal BI Builder */}
      {dashboardCharts.length > 0 && (
        <div className="row mb-4">
          {dashboardCharts.map(chartId => (
            <div key={chartId} className="col-md-6 mb-4">
              <ChartWidget chartId={chartId} dateFilters={dateFilters} />
            </div>
          ))}
        </div>
      )}
      {selectedDashboard && dashboardCharts.length === 0 && (
        <div className="text-center text-muted p-4 border rounded bg-light">Questa dashboard non ha ancora grafici.</div>
      )}

      {user.role === 'admin' && (
        <div className="mt-4">
          <div className="d-flex justify-content-between align-items-center">
            <h4>Gestione Utenti (Area Admin)</h4>
            <Link to="/users" className="btn btn-sm btn-outline-primary">Gestisci Utenti</Link>
          </div>
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