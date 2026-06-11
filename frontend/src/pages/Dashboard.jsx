import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Layout } from '../components';
import DashboardWidgets from '../components/DashboardWidgets';
import ChartWidget from '../components/ChartWidget';
import { apiFetch } from '../utils';
import { useAuth } from '../context';
import { useTranslation } from 'react-i18next';
import DateRangePicker from '@/components/DateRangePicker';
import GridLayout from 'react-grid-layout';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';

const GRID_COLS = 12;
const ROW_HEIGHT = 80;

function Dashboard() {
  const { projectId } = useParams();
  const { user } = useAuth();
  const { t } = useTranslation();
  const [usersList, setUsersList] = useState([]);
  const [dashboards, setDashboards] = useState([]);
  const [selectedDashboard, setSelectedDashboard] = useState(null);
  const [dashboardCharts, setDashboardCharts] = useState([]);
  const [dashboardLayout, setDashboardLayout] = useState([]);
  const [dateFilters, setDateFilters] = useState({ from: '', to: '' });
  const [kpiProjectId, setKpiProjectId] = useState(null);

  useEffect(() => {
    if (!projectId) return;
    apiFetch(`/api/v1/system/resolve-model/dashboard_kpi`).then(r => r.json()).then(data => {
      if (data.found) setKpiProjectId(data.projectId);
    });
  }, [projectId]);

  function handleDashboardChange(dashboardId) {
    if (!dashboardId) {
      setSelectedDashboard(null);
      setDashboardCharts([]);
      setDashboardLayout([]);
      return;
    }
    apiFetch(`/analytics/sys-dashboards/${dashboardId}`).then(res => res.json()).then(dashboard => {
      setSelectedDashboard(dashboard);
      try {
        const layoutData = JSON.parse(dashboard.layout || '{}');
        setDashboardCharts(layoutData.charts || []);
        setDashboardLayout(layoutData.layout || generateDefaultLayout(layoutData.charts || []));
      } catch {
        setDashboardCharts([]);
        setDashboardLayout([]);
      }
    }).catch(console.error);
  }

  const generateDefaultLayout = (chartIds) => {
    if (!chartIds) return [];
    return chartIds.map((id, index) => ({
      i: String(id),
      x: (index % 2) * 6,
      y: Math.floor(index / 2),
      w: 6,
      h: 4,
      minW: 3,
      minH: 3
    }));
  };

  useEffect(() => {
    const loadInitialData = async () => {
      if (user?.role && ['admin', 'owner'].includes(user.role)) {
        const usersResponse = await apiFetch('/users');
        const usersData = await usersResponse.json();
        setUsersList(usersData);
      }

      const dashboardsResponse = await apiFetch('/analytics/sys-dashboards');
      const dashboardsData = await dashboardsResponse.json();
      setDashboards(dashboardsData);
      if (dashboardsData.length > 0) {
        const dashboard = dashboardsData[0];
        setSelectedDashboard(dashboard);
        try {
          const layoutData = JSON.parse(dashboard.layout || '{}');
          setDashboardCharts(layoutData.charts || []);
          setDashboardLayout(layoutData.layout || generateDefaultLayout(layoutData.charts || []));
        } catch {
          setDashboardCharts([]);
          setDashboardLayout([]);
        }
      }
    };

    void loadInitialData();
  }, [user]);

  if (!user) return null;

  // Se siamo dentro un progetto, non usare il Layout principale (già incluso in ProjectLayout)
  const isInProject = !!projectId;

  const dashboardContent = (
    <>
      <div className="d-flex justify-content-between align-items-center">
        <h2>{t('dashboard.title')}</h2>
        <div className="d-flex gap-2 align-items-center">
          <DateRangePicker
            value={[dateFilters.from, dateFilters.to]}
            onChange={(dates) => setDateFilters({ from: dates[0], to: dates[1] })}
          />
        </div>
      </div>

      <p className="text-muted">{t('dashboard.roleLabel')}: <span className="badge bg-secondary">{user.role}</span></p>
      <hr />

      {/* Widget Dinamici dal Builder (Modello: dashboard_kpi) */}
      <DashboardWidgets modelName="dashboard_kpi" projectId={kpiProjectId} />

      {/* Selettore Dashboard */}
      {dashboards.length > 0 && (
        <div className="mb-4">
          <label htmlFor="dashboard-selector" className="form-label fw-bold">{t('dashboard.selectorLabel')}</label>
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
        <GridLayout
          className="layout"
          layout={dashboardLayout}
          cols={GRID_COLS}
          rowHeight={ROW_HEIGHT}
          width={1100}
          margin={[16, 16]}
          isDraggable={false}
          isResizable={false}
        >
          {dashboardCharts.map(chartId => (
            <div key={String(chartId)} style={{ overflow: 'hidden' }}>
              <ChartWidget chartId={chartId} dateFilters={dateFilters} />
            </div>
          ))}
        </GridLayout>
      )}
      {selectedDashboard && dashboardCharts.length === 0 && (
        <div className="text-center text-muted p-4 border rounded bg-light">{t('dashboard.emptyCharts')}</div>
      )}

      {user.role && ['admin', 'owner'].includes(user.role) && (
        <div className="mt-4">
          <div className="d-flex justify-content-between align-items-center">
            <h4>{t('dashboard.adminUsersTitle')}</h4>
            <Link to="/users" className="btn btn-sm btn-outline-primary">{t('dashboard.manageUsers')}</Link>
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
    </>
  );

  if (isInProject) {
    return dashboardContent;
  }

  return (
    <Layout>
      {dashboardContent}
    </Layout>
  );
}

export default Dashboard;