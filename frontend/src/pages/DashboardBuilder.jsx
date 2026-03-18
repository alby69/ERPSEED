import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ResponsiveGridLayout, useContainerWidth } from 'react-grid-layout';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';
import { Button, Card, Modal, Form, Input, Select, Space, Table, message, Tooltip, Dropdown, Tag, DatePicker } from 'antd';
import { PlusOutlined, DeleteOutlined, SaveOutlined, ExportOutlined, SettingOutlined, FullscreenOutlined, DownloadOutlined } from '@ant-design/icons';
import { apiFetch } from '../utils';
import { ChartRenderer, getAllAdapters, CHART_LIBRARIES, CHART_LIBRARY_LABELS, CHART_TYPES_BY_LIBRARY } from '../components/charts';
import { exportToImage } from '../utils/exportUtils';

const WIDGET_TYPES = {
  CHART: 'chart',
  KPI: 'kpi',
  TEXT: 'text',
  TABLE: 'table',
};

function DashboardBuilder() {
  const { projectId, dashboardId } = useParams();
  const navigate = useNavigate();
  const dashboardRef = useRef(null);
  const containerRef = useRef(null);
  const { width } = useContainerWidth(containerRef);

  const [dashboards, setDashboards] = useState([]);
  const [charts, setCharts] = useState([]);
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [showChartModal, setShowChartModal] = useState(false);
  const [showKPIModal, setShowKPIModal] = useState(false);
  const [selectedWidget, setSelectedWidget] = useState(null);
  const [isEditing, setIsEditing] = useState(false);

  const [currentDashboard, setCurrentDashboard] = useState(null);
  const [layout, setLayout] = useState({ lg: [] });
  const [widgets, setWidgets] = useState({});

  const [chartForm] = Form.useForm();
  const [kpiForm] = Form.useForm();

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [dashRes, chartsRes, modelsRes] = await Promise.all([
        apiFetch(`/sys-dashboards?page=1&per_page=100`),
        apiFetch(`/sys-charts?page=1&per_page=100`),
        apiFetch(`/sys-models?page=1&per_page=100`),
      ]);

      const [dashData, chartsData, modelsData] = await Promise.all([
        dashRes.json(),
        chartsRes.json(),
        modelsRes.json(),
      ]);

      setDashboards(dashData.items || []);
      setCharts(chartsData.items || []);
      setModels(modelsData.items || []);

      if (dashboardId) {
        const existing = dashData.items?.find(d => d.id === parseInt(dashboardId));
        if (existing) {
          loadDashboard(existing);
        }
      }
    } catch (err) {
      console.error('Error loading data:', err);
    } finally {
      setLoading(false);
    }
  }, [dashboardId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const loadDashboard = (dashboard) => {
    setCurrentDashboard(dashboard);
    const config = dashboard.configuration ? JSON.parse(dashboard.configuration) : { layouts: { lg: [] }, widgets: {} };
    setLayout(config.layouts || { lg: [] });
    setWidgets(config.widgets || {});
  };

  const createNewDashboard = () => {
    setCurrentDashboard({ title: '', description: '' });
    setLayout({ lg: [] });
    setWidgets({});
    setIsEditing(true);
  };

  const saveDashboard = async () => {
    if (!currentDashboard?.title) {
      message.error('Inserisci un titolo per il dashboard');
      return;
    }

    setSaving(true);
    try {
      const config = JSON.stringify({ layouts: layout, widgets });
      const payload = {
        ...currentDashboard,
        configuration: config,
      };

      let url = '/sys-dashboards';
      let method = 'POST';

      if (currentDashboard.id) {
        url = `/sys-dashboards/${currentDashboard.id}`;
        method = 'PUT';
      }

      const res = await apiFetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok) throw new Error('Failed to save dashboard');

      const saved = await res.json();
      setCurrentDashboard(saved);
      message.success('Dashboard salvato!');
      loadData();
      setIsEditing(false);
    } catch (err) {
      message.error('Errore nel salvataggio');
    } finally {
      setSaving(false);
    }
  };

  const addWidget = (type, widgetConfig) => {
    const id = `widget-${Date.now()}`;
    const newWidget = {
      ...widgetConfig,
      type,
      id,
    };

    const newItem = {
      i: id,
      x: (layout.lg.length * 4) % 12,
      y: Infinity,
      w: type === WIDGET_TYPES.CHART ? 6 : 3,
      h: type === WIDGET_TYPES.CHART ? 4 : 2,
      minW: 2,
      minH: 2,
    };

    setLayout(prev => ({
      ...prev,
      lg: [...prev.lg, newItem],
    }));

    setWidgets(prev => ({
      ...prev,
      [id]: newWidget,
    }));
  };

  const removeWidget = (id) => {
    setLayout(prev => ({
      ...prev,
      lg: prev.lg.filter(item => item.i !== id),
    }));
    setWidgets(prev => {
      const newWidgets = { ...prev };
      delete newWidgets[id];
      return newWidgets;
    });
  };

  const handleLayoutChange = (newLayout) => {
    setLayout({ lg: newLayout });
  };

  const handleExport = async (format) => {
    if (!dashboardRef.current) return;
    try {
      await exportToImage(dashboardRef.current, `dashboard-${currentDashboard?.title || 'export'}`, { format });
      message.success(`Export ${format.toUpperCase()} completato!`);
    } catch (err) {
      message.error('Errore durante l\'export');
    }
  };

  const renderWidget = (widget) => {
    if (!widget) return null;

    switch (widget.type) {
      case WIDGET_TYPES.CHART:
        return <ChartWidget widget={widget} />;
      case WIDGET_TYPES.KPI:
        return <KPIWidget widget={widget} />;
      case WIDGET_TYPES.TEXT:
        return <div className="p-3"><h5>{widget.title}</h5><p>{widget.content}</p></div>;
      default:
        return <div>Widget sconosciuto</div>;
    }
  };

  const chartTypesOptions = Object.entries(CHART_TYPES_BY_LIBRARY).flatMap(([lib, types]) =>
    types.map(t => ({ value: t, label: `${t} (${CHART_LIBRARY_LABELS[lib]})` }))
  );

  const exportMenuItems = [
    { key: 'png', label: 'Esporta PNG', icon: <DownloadOutlined />, onClick: () => handleExport('png') },
    { key: 'pdf', label: 'Esporta PDF', icon: <DownloadOutlined />, onClick: () => handleExport('pdf') },
  ];

  return (
    <div className="p-3" style={{ background: '#f5f5f5', minHeight: '100vh' }}>
      <Card
        title={
          <Space>
            <span>Dashboard Builder</span>
            {currentDashboard?.id && <Tag color="blue">#{currentDashboard.id}</Tag>}
          </Space>
        }
        extra={
          <Space>
            {!isEditing && (
              <Button icon={<PlusOutlined />} onClick={createNewDashboard}>
                Nuovo Dashboard
              </Button>
            )}
            {currentDashboard && (
              <>
                {isEditing && (
                  <>
                    <Button icon={<SaveOutlined />} type="primary" loading={saving} onClick={saveDashboard}>
                      Salva
                    </Button>
                    <Button onClick={() => { setIsEditing(false); loadData(); }}>
                      Annulla
                    </Button>
                  </>
                )}
                {!isEditing && (
                  <>
                    <Button icon={<SettingOutlined />} onClick={() => setIsEditing(true)}>
                      Modifica Layout
                    </Button>
                    <Dropdown menu={{ items: exportMenuItems }} placement="bottomRight">
                      <Button icon={<ExportOutlined />}>Esporta</Button>
                    </Dropdown>
                  </>
                )}
              </>
            )}
          </Space>
        }
      >
        {isEditing && (
          <Space direction="vertical" style={{ width: '100%', marginBottom: 16 }}>
            <Form layout="inline">
              <Form.Item label="Titolo">
                <Input
                  style={{ width: 300 }}
                  value={currentDashboard?.title || ''}
                  onChange={(e) => setCurrentDashboard(prev => ({ ...prev, title: e.target.value }))}
                  placeholder="Nome dashboard"
                />
              </Form.Item>
              <Form.Item>
                <Space>
                  <Button icon={<PlusOutlined />} onClick={() => setShowChartModal(true)}>
                    Aggiungi Grafico
                  </Button>
                  <Button icon={<PlusOutlined />} onClick={() => setShowKPIModal(true)}>
                    Aggiungi KPI
                  </Button>
                </Space>
              </Form.Item>
            </Form>
          </Space>
        )}

        {!currentDashboard ? (
          <Table
            dataSource={dashboards}
            rowKey="id"
            loading={loading}
            columns={[
              { title: 'ID', dataIndex: 'id', width: 60 },
              { title: 'Titolo', dataIndex: 'title' },
              { title: 'Creato', dataIndex: 'created_at', render: (v) => v?.slice(0, 10) },
              {
                title: 'Azioni',
                render: (_, record) => (
                  <Space>
                    <Button size="small" onClick={() => navigate(`/dashboard/builder/${record.id}`)}>Apri</Button>
                    <Button size="small" onClick={() => loadDashboard(record)}>Modifica</Button>
                  </Space>
                ),
              },
            ]}
          />
        ) : (
          <div ref={dashboardRef} style={{ background: '#fff', padding: 16, minHeight: 500 }}>
            <div ref={containerRef} style={{ width: '100%', minHeight: 400 }}>
              <ResponsiveGridLayout
                className="layout"
                layouts={layout}
                width={width}
                breakpoints={{ lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 }}
                cols={{ lg: 12, md: 10, sm: 6, xs: 4, xxs: 2 }}
                rowHeight={60}
                onLayoutChange={handleLayoutChange}
                isDraggable={isEditing}
                isResizable={isEditing}
                draggableHandle=".drag-handle"
              >
              {layout.lg.map(item => (
                <div key={item.i} className="bg-white rounded shadow-sm">
                  {isEditing && (
                    <div className="drag-handle p-2 bg-light border-bottom d-flex justify-content-between align-items-center" style={{ cursor: 'move' }}>
                      <span className="fw-bold">{widgets[item.i]?.title || 'Widget'}</span>
                      <Button size="small" type="text" danger icon={<DeleteOutlined />} onClick={() => removeWidget(item.i)} />
                    </div>
                  )}
                  <div style={{ height: isEditing ? 'calc(100% - 40px)' : '100%' }}>
                    {renderWidget(widgets[item.i])}
                  </div>
                </div>
              ))}
              </ResponsiveGridLayout>
            </div>
          </div>
        )}
      </Card>

      <Modal
        title="Aggiungi Grafico"
        open={showChartModal}
        onCancel={() => setShowChartModal(false)}
        footer={null}
      >
        <Form form={chartForm} layout="vertical" onFinish={(values) => {
          addWidget(WIDGET_TYPES.CHART, values);
          chartForm.resetFields();
          setShowChartModal(false);
        }}>
          <Form.Item name="title" label="Titolo" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="chartId" label="Grafico" rules={[{ required: true }]}>
            <Select
              options={charts.map(c => ({ value: c.id, label: c.title }))}
              placeholder="Seleziona un grafico esistente"
            />
          </Form.Item>
          <Form.Item name="library" label="Libreria" initialValue="chartjs">
            <Select options={[
              { value: 'chartjs', label: 'Chart.js' },
              { value: 'apexcharts', label: 'ApexCharts' },
              { value: 'echarts', label: 'ECharts' },
            ]} />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit">Aggiungi</Button>
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="Aggiungi KPI"
        open={showKPIModal}
        onCancel={() => setShowKPIModal(false)}
        footer={null}
      >
        <Form form={kpiForm} layout="vertical" onFinish={(values) => {
          addWidget(WIDGET_TYPES.KPI, values);
          kpiForm.resetFields();
          setShowKPIModal(false);
        }}>
          <Form.Item name="title" label="Label KPI" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="modelId" label="Modello" rules={[{ required: true }]}>
            <Select
              options={models.map(m => ({ value: m.id, label: m.name }))}
              placeholder="Seleziona modello"
            />
          </Form.Item>
          <Form.Item name="aggregation" label="Aggregazione" initialValue="count">
            <Select options={[
              { value: 'count', label: 'Conteggio' },
              { value: 'sum', label: 'Somma' },
              { value: 'avg', label: 'Media' },
            ]} />
          </Form.Item>
          <Form.Item name="field" label="Campo">
            <Input placeholder="Campo da aggregare" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit">Aggiungi</Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

function ChartWidget({ widget }) {
  const [chartConfig, setChartConfig] = useState(null);
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadChart = async () => {
      if (!widget.chartId) return;
      try {
        const [configRes, dataRes] = await Promise.all([
          apiFetch(`/sys-charts/${widget.chartId}`),
          apiFetch(`/analytics/chart-data/${widget.chartId}`),
        ]);

        const [config, data] = await Promise.all([
          configRes.json(),
          dataRes.json(),
        ]);

        setChartConfig(config);
        setChartData(data);
      } catch (err) {
        console.error('Error loading chart:', err);
      } finally {
        setLoading(false);
      }
    };

    loadChart();
  }, [widget.chartId]);

  if (loading) return <div className="text-center p-4">Caricamento...</div>;
  if (!chartConfig) return <div className="p-3 text-muted">Grafico non trovato</div>;

  return (
    <div style={{ width: '100%', height: '100%', padding: 8 }}>
      <ChartRenderer
        library={widget.library || chartConfig.library || 'chartjs'}
        config={chartConfig}
        data={chartData}
      />
    </div>
  );
}

function KPIWidget({ widget }) {
  const [value, setValue] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadKPI = async () => {
      if (!widget.modelId) return;
      try {
        const res = await apiFetch(`/sys-models/${widget.modelId}`);
        const model = await res.json();
        
        const countRes = await apiFetch(`/dynamic/${model.name}/count`);
        const countData = await countRes.json();
        
        setValue(countData.total || 0);
      } catch (err) {
        console.error('Error loading KPI:', err);
        setValue('N/A');
      } finally {
        setLoading(false);
      }
    };

    loadKPI();
  }, [widget.modelId]);

  return (
    <div className="d-flex flex-column justify-content-center align-items-center h-100 p-3">
      <div className="text-muted small">{widget.title}</div>
      <div className="display-4 fw-bold">
        {loading ? '...' : value}
      </div>
    </div>
  );
}

export default DashboardBuilder;
