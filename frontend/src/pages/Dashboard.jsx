import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { Button, Card, Flex, List, Select, Space, Tag, Typography } from 'antd';
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

const { Title, Text } = Typography;

const GRID_COLS = 12;
const ROW_HEIGHT = 80;

function Dashboard() {
  const { projectId } = useParams();
  const { user } = useAuth();
  const { t } = useTranslation();
  const navigate = useNavigate();
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

  const isInProject = !!projectId;

  const dashboardContent = (
    <div style={{ padding: isInProject ? 0 : 24 }}>
      <Flex justify="space-between" align="center" style={{ marginBottom: 12 }}>
        <Title level={2} style={{ margin: 0 }}>{t('dashboard.title')}</Title>
        <Flex gap={8} align="center">
          <DateRangePicker
            value={[dateFilters.from, dateFilters.to]}
            onChange={(dates) => setDateFilters({ from: dates[0], to: dates[1] })}
          />
        </Flex>
      </Flex>

      <Text type="secondary">
        {t('dashboard.roleLabel')}: <Tag color="blue">{user.role}</Tag>
      </Text>

      <div style={{ margin: '16px 0', borderBottom: '1px solid #f0f0f0' }} />

      {/* Dynamic KPI Widgets */}
      <DashboardWidgets modelName="dashboard_kpi" projectId={kpiProjectId} />

      {/* Dashboard Selector */}
      {dashboards.length > 0 && (
        <div style={{ marginBottom: 16 }}>
          <Text strong style={{ display: 'block', marginBottom: 6 }}>{t('dashboard.selectorLabel')}</Text>
          <Select
            style={{ width: '100%', maxWidth: 300 }}
            value={selectedDashboard?.id || ''}
            onChange={(val) => handleDashboardChange(val)}
            options={dashboards.map(d => ({ value: d.id, label: d.title }))}
          />
        </div>
      )}

      {/* Dynamic BI Builder Charts */}
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
        <Card style={{ textAlign: 'center', marginTop: 16 }}>
          <Text type="secondary">{t('dashboard.emptyCharts')}</Text>
        </Card>
      )}

      {user.role && ['admin', 'owner'].includes(user.role) && (
        <div style={{ marginTop: 24 }}>
          <Flex justify="space-between" align="center" style={{ marginBottom: 12 }}>
            <Title level={4} style={{ margin: 0 }}>{t('dashboard.adminUsersTitle')}</Title>
            <Button size="small" type="default" onClick={() => navigate('/users')}>
              {t('dashboard.manageUsers')}
            </Button>
          </Flex>
          <List
            bordered
            dataSource={usersList}
            renderItem={(u) => (
              <List.Item key={u.id}>
                <Flex justify="space-between" align="center" style={{ width: '100%' }}>
                  <Text>{u.email}</Text>
                  <Tag color="blue">{u.role}</Tag>
                </Flex>
              </List.Item>
            )}
          />
        </div>
      )}
    </div>
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
