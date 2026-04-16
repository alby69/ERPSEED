import React, { useState, useEffect } from 'react';
import { apiFetch } from '../utils';
import GridLayout from 'react-grid-layout';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';
import ChartWidget from '../components/ChartWidget';

const GRID_COLS = 12;
const ROW_HEIGHT = 80;

function SysDashboardBuilder() {
  const [dashboards, setDashboards] = useState([]);
  const [charts, setCharts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingDashboard, setEditingDashboard] = useState(null);
  const [viewMode, setViewMode] = useState('list');

  const [formData, setFormData] = useState({
    title: '',
    selectedCharts: []
  });

  const [layout, setLayout] = useState([]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [dashboardsRes, chartsRes] = await Promise.all([
        apiFetch('/sys-dashboards'),
        apiFetch('/sys-charts')
      ]);

      if (dashboardsRes.ok) setDashboards(await dashboardsRes.json());
      if (chartsRes.ok) setCharts(await chartsRes.json());
    } catch (error) {
      console.error("Error fetching builder data", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const openModal = (dashboard = null) => {
    if (dashboard) {
      setEditingDashboard(dashboard);
      let selectedCharts = [];
      let savedLayout = [];
      try {
        const parsed = JSON.parse(dashboard.layout || '{}');
        selectedCharts = parsed.charts || [];
        savedLayout = parsed.layout || [];
      } catch (e) {}
      setFormData({ title: dashboard.title, selectedCharts });
      setLayout(savedLayout.length > 0 ? savedLayout : generateDefaultLayout(selectedCharts));
    } else {
      setEditingDashboard(null);
      setFormData({ title: '', selectedCharts: [] });
      setLayout([]);
    }
    setShowModal(true);
  };

  const generateDefaultLayout = (chartIds) => {
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

  const handleChartSelection = (chartId) => {
    setFormData(prev => {
      let newSelected;
      if (prev.selectedCharts.includes(chartId)) {
        newSelected = prev.selectedCharts.filter(id => id !== chartId);
      } else {
        newSelected = [...prev.selectedCharts, chartId];
      }
      setLayout(generateDefaultLayout(newSelected));
      return { ...prev, selectedCharts: newSelected };
    });
  };

  const handleLayoutChange = (newLayout) => {
    setLayout(newLayout);
  };

  const handleSave = async (e) => {
    e.preventDefault();
    const layoutData = JSON.stringify({
      charts: formData.selectedCharts,
      layout: layout
    });
    const payload = { title: formData.title, layout: layoutData };

    const url = editingDashboard ? `/sys-dashboards/${editingDashboard.id}` : '/sys-dashboards';
    const method = editingDashboard ? 'PUT' : 'POST';

    try {
      const res = await apiFetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        setShowModal(false);
        fetchData();
      } else {
        alert("Error saving dashboard");
      }
    } catch (error) {
      console.error(error);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm("Delete this dashboard?")) return;
    await apiFetch(`/sys-dashboards/${id}`, { method: 'DELETE' });
    fetchData();
  };

  const renderDashboardPreview = (dashboard) => {
    let chartIds = [];
    let dashboardLayout = [];
    try {
      const parsed = JSON.parse(dashboard.layout || '{}');
      chartIds = parsed.charts || [];
      dashboardLayout = parsed.layout || generateDefaultLayout(chartIds);
    } catch (e) {
      chartIds = [];
      dashboardLayout = [];
    }

    return (
      <div key={dashboard.id} className="col-md-6 mb-4">
        <div className="card h-100 shadow-sm">
          <div className="card-header d-flex justify-content-between align-items-center">
            <h5 className="mb-0">{dashboard.title}</h5>
            <div>
              <button className="btn btn-sm btn-outline-primary me-2" onClick={() => openModal(dashboard)}>Edit</button>
              <button className="btn btn-sm btn-outline-danger" onClick={() => handleDelete(dashboard.id)}>Delete</button>
            </div>
          </div>
          <div className="card-body" style={{ minHeight: '300px' }}>
            {chartIds.length > 0 ? (
              <GridLayout
                className="layout"
                layout={dashboardLayout}
                cols={GRID_COLS}
                rowHeight={ROW_HEIGHT}
                width={500}
                isDraggable={false}
                isResizable={false}
                margin={[10, 10]}
              >
                {chartIds.map(chartId => (
                  <div key={String(chartId)}>
                    <ChartWidget chartId={chartId} />
                  </div>
                ))}
              </GridLayout>
            ) : (
              <div className="text-center text-muted p-4">No charts in this dashboard</div>
            )}
          </div>
        </div>
      </div>
    );
  };

  if (loading) return <div className="p-4">Loading...</div>;

  return (
    <div className="container mt-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>BI Builder - Dashboards</h2>
        <button className="btn btn-primary" onClick={() => openModal()}>+ New Dashboard</button>
      </div>

      {dashboards.length > 0 ? (
        <div className="row">
          {dashboards.map(d => renderDashboardPreview(d))}
        </div>
      ) : (
        <div className="text-center text-muted p-4 border rounded">No dashboards created yet.</div>
      )}

      {showModal && (
        <div className="modal fade show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog modal-xl" style={{ maxWidth: '90vw' }}>
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">{editingDashboard ? 'Edit' : 'Create'} Dashboard</h5>
                <button type="button" className="btn-close" onClick={() => setShowModal(false)}></button>
              </div>
              <form onSubmit={handleSave}>
                <div className="modal-body">
                  <div className="mb-3">
                    <label className="form-label">Dashboard Title</label>
                    <input type="text" className="form-control" required value={formData.title} onChange={e => setFormData({...formData, title: e.target.value})} />
                  </div>

                  <div className="row">
                    <div className="col-md-4">
                      <label className="form-label">Available Charts</label>
                      <div className="border rounded p-2 bg-light" style={{maxHeight: '400px', overflowY: 'auto'}}>
                        {charts.map(chart => (
                          <div key={chart.id} className="form-check mb-2">
                            <input
                              className="form-check-input"
                              type="checkbox"
                              id={`chart-${chart.id}`}
                              checked={formData.selectedCharts.includes(chart.id)}
                              onChange={() => handleChartSelection(chart.id)}
                            />
                            <label className="form-check-label" htmlFor={`chart-${chart.id}`}>
                              {chart.title} <small className="text-muted">({chart.type})</small>
                            </label>
                          </div>
                        ))}
                        {charts.length === 0 && <div className="text-muted small">No charts available</div>}
                      </div>
                    </div>

                    <div className="col-md-8">
                      <label className="form-label">
                        Dashboard Layout (Drag to Position & Resize)
                        <span className="ms-2 badge bg-secondary">Preview</span>
                      </label>
                      <div className="border rounded p-2 bg-light" style={{minHeight: '400px'}}>
                        {formData.selectedCharts.length > 0 ? (
                          <GridLayout
                            className="layout"
                            layout={layout}
                            cols={GRID_COLS}
                            rowHeight={ROW_HEIGHT}
                            width={700}
                            onLayoutChange={handleLayoutChange}
                            margin={[10, 10]}
                            draggableHandle=".drag-handle"
                          >
                            {formData.selectedCharts.map(chartId => {
                              const chart = charts.find(c => c.id === chartId);
                              if (!chart) return null;
                              return (
                                <div key={String(chartId)} className="bg-white border rounded shadow-sm" style={{ overflow: 'hidden' }}>
                                  <div className="drag-handle p-1 bg-light border-bottom d-flex justify-content-between align-items-center" style={{ cursor: 'move', fontSize: '11px' }}>
                                    <span className="text-truncate">{chart.title}</span>
                                    <button
                                      type="button"
                                      className="btn-close btn-sm"
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        handleChartSelection(chartId);
                                      }}
                                    />
                                  </div>
                                  <div className="p-1" style={{ height: 'calc(100% - 28px)' }}>
                                    <ChartWidget chartId={chartId} />
                                  </div>
                                </div>
                              );
                            })}
                          </GridLayout>
                        ) : (
                          <div className="text-center text-muted mt-4">Select charts to build your dashboard</div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
                <div className="modal-footer">
                  <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                  <button type="submit" className="btn btn-primary">Save Dashboard</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default SysDashboardBuilder;
