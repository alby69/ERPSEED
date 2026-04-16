import React, { useState, useEffect } from 'react';
import { apiFetch } from '../utils';
import ChartWidget from '../components/ChartWidget';

const CHART_TYPES = [
  { value: 'bar', label: 'Bar Chart' },
  { value: 'line', label: 'Line Chart' },
  { value: 'pie', label: 'Pie Chart' },
  { value: 'doughnut', label: 'Doughnut Chart' },
  { value: 'area', label: 'Area Chart' },
  { value: 'scatter', label: 'Scatter Chart' },
  { value: 'text', label: 'Text / HTML Widget' },
  { value: 'table', label: 'Table Widget (Last N)' },
];

const AGGREGATIONS = [
  { value: 'sum', label: 'Sum' },
  { value: 'count', label: 'Count' },
  { value: 'avg', label: 'Average' },
  { value: 'min', label: 'Minimum' },
  { value: 'max', label: 'Maximum' },
];

const FILTER_TYPES = [
  { value: 'date_range', label: 'Date Range' },
  { value: 'select', label: 'Dropdown Select' },
  { value: 'multiselect', label: 'Multi-Select' },
  { value: 'text', label: 'Text Input' },
  { value: 'number_range', label: 'Number Range' },
];

function SysChartBuilder() {
  const [charts, setCharts] = useState([]);
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [showFiltersModal, setShowFiltersModal] = useState(false);
  const [editingChart, setEditingChart] = useState(null);

  const [newChart, setNewChart] = useState({
    title: '',
    type: 'bar',
    model_id: '',
    x_axis: '',
    y_axis: '',
    aggregation: 'sum',
    filters: '',
    filters_config: []
  });

  const [modelFields, setModelFields] = useState([]);
  const [tempFilter, setTempFilter] = useState({
    field: '',
    type: 'select',
    label: '',
    options: ''
  });

  const fetchData = async () => {
    try {
      setLoading(true);
      const [chartsRes, modelsRes] = await Promise.all([
        apiFetch('/sys-charts'),
        apiFetch('/sys-models')
      ]);

      if (chartsRes.ok) setCharts(await chartsRes.json());
      if (modelsRes.ok) setModels(await modelsRes.json());
    } catch (error) {
      console.error("Error fetching builder data", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    if (newChart.model_id) {
      apiFetch(`/sys-models/${newChart.model_id}`)
        .then(res => res.json())
        .then(data => setModelFields(data.fields || []))
        .catch(console.error);
    } else {
      setModelFields([]);
    }
  }, [newChart.model_id]);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        ...newChart,
        chart_type: newChart.type,
        filters_config: newChart.filters_config
      };

      const res = await apiFetch('/sys-charts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        setShowModal(false);
        setNewChart({ title: '', type: 'bar', model_id: '', x_axis: '', y_axis: '', aggregation: 'sum', filters: '', filters_config: [] });
        fetchData();
      } else {
        alert("Error creating chart");
      }
    } catch (error) {
      console.error(error);
    }
  };

  const handleEdit = (chart) => {
    setEditingChart(chart);
    setNewChart({
      title: chart.title,
      type: chart.type || chart.chart_type || 'bar',
      model_id: chart.model_id,
      x_axis: chart.x_axis || '',
      y_axis: chart.y_axis || '',
      aggregation: chart.aggregation || 'sum',
      filters: chart.filters || '',
      filters_config: chart.filters_config || []
    });
    setShowModal(true);
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        ...newChart,
        chart_type: newChart.type,
        filters_config: newChart.filters_config
      };

      const res = await apiFetch(`/sys-charts/${editingChart.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        setShowModal(false);
        setEditingChart(null);
        setNewChart({ title: '', type: 'bar', model_id: '', x_axis: '', y_axis: '', aggregation: 'sum', filters: '', filters_config: [] });
        fetchData();
      } else {
        alert("Error updating chart");
      }
    } catch (error) {
      console.error(error);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm("Delete this chart?")) return;
    await apiFetch(`/sys-charts/${id}`, { method: 'DELETE' });
    fetchData();
  };

  const handleLimitChange = (val) => {
    try {
      const currentFilters = newChart.filters ? JSON.parse(newChart.filters) : {};
      currentFilters.limit = parseInt(val);
      setNewChart({ ...newChart, filters: JSON.stringify(currentFilters) });
    } catch (e) {
      setNewChart({ ...newChart, filters: JSON.stringify({ limit: parseInt(val) }) });
    }
  };

  const openFiltersConfig = (chart) => {
    setEditingChart(chart);
    setNewChart({
      title: chart.title,
      type: chart.type || chart.chart_type || 'bar',
      model_id: chart.model_id,
      x_axis: chart.x_axis || '',
      y_axis: chart.y_axis || '',
      aggregation: chart.aggregation || 'sum',
      filters: chart.filters || '',
      filters_config: chart.filters_config || []
    });
    setShowFiltersModal(true);
  };

  const addFilter = () => {
    if (!tempFilter.field || !tempFilter.label) return;

    const newFilter = {
      field: tempFilter.field,
      type: tempFilter.type,
      label: tempFilter.label,
      options: tempFilter.options ? tempFilter.options.split(',').map(o => o.trim()) : []
    };

    setNewChart({
      ...newChart,
      filters_config: [...newChart.filters_config, newFilter]
    });
    setTempFilter({ field: '', type: 'select', label: '', options: '' });
  };

  const removeFilter = (index) => {
    const updated = newChart.filters_config.filter((_, i) => i !== index);
    setNewChart({ ...newChart, filters_config: updated });
  };

  const saveFiltersConfig = async () => {
    try {
      const res = await apiFetch(`/sys-charts/${editingChart.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filters_config: newChart.filters_config })
      });

      if (res.ok) {
        setShowFiltersModal(false);
        fetchData();
      } else {
        alert("Error saving filters");
      }
    } catch (error) {
      console.error(error);
    }
  };

  const currentLimit = (() => { try { return JSON.parse(newChart.filters).limit || 5 } catch { return 5 } })();

  if (loading) return <div className="p-4">Loading...</div>;

  return (
    <div className="container mt-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>BI Builder - Charts</h2>
        <button className="btn btn-primary" onClick={() => { setEditingChart(null); setNewChart({ title: '', type: 'bar', model_id: '', x_axis: '', y_axis: '', aggregation: 'sum', filters: '', filters_config: [] }); setShowModal(true); }}>+ New Chart</button>
      </div>

      <div className="row">
        {charts.map(chart => (
          <div key={chart.id} className="col-md-6 mb-4">
            <div className="card h-100 shadow-sm">
              <div className="card-header d-flex justify-content-between align-items-center">
                <h5 className="mb-0">{chart.title}</h5>
                <div>
                  <button className="btn btn-sm btn-outline-secondary me-1" onClick={() => openFiltersConfig(chart)} title="Configure Filters">
                    <span>⚙️</span>
                  </button>
                  <button className="btn btn-sm btn-outline-primary me-1" onClick={() => handleEdit(chart)}>Edit</button>
                  <button className="btn btn-sm btn-outline-danger" onClick={() => handleDelete(chart.id)}>&times;</button>
                </div>
              </div>
              <div className="card-body" style={{ minHeight: '300px' }}>
                <ChartWidget chartId={chart.id} />
              </div>
              <div className="card-footer text-muted small">
                {chart.type === 'text' ? (
                  <span>Type: Text Widget</span>
                ) : (
                  <span>Type: {chart.type} | Aggregation: {chart.aggregation} of {chart.y_axis} by {chart.x_axis}</span>
                )}
                {chart.filters_config && chart.filters_config.length > 0 && (
                  <span className="ms-2 badge bg-info">{chart.filters_config.length} filter(s)</span>
                )}
              </div>
            </div>
          </div>
        ))}
        {charts.length === 0 && <div className="col-12 text-center text-muted">No charts created yet.</div>}
      </div>

      {showModal && (
        <div className="modal fade show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">{editingChart ? 'Edit' : 'Create'} Chart</h5>
                <button type="button" className="btn-close" onClick={() => setShowModal(false)}></button>
              </div>
              <form onSubmit={editingChart ? handleUpdate : handleCreate}>
                <div className="modal-body">
                  <div className="mb-3">
                    <label className="form-label">Chart Title</label>
                    <input type="text" className="form-control" required value={newChart.title} onChange={e => setNewChart({...newChart, title: e.target.value})} />
                  </div>
                  <div className="row">
                    <div className="col-md-6 mb-3">
                      <label className="form-label">Chart Type</label>
                      <select className="form-select" value={newChart.type} onChange={e => setNewChart({...newChart, type: e.target.value})}>
                        {CHART_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
                      </select>
                    </div>
                    <div className="col-md-6 mb-3">
                      <label className="form-label">Data Source (Model)</label>
                      <select className="form-select" required value={newChart.model_id} onChange={e => setNewChart({...newChart, model_id: e.target.value})}>
                        <option value="">Select Model...</option>
                        {models.map(m => <option key={m.id} value={m.id}>{m.title}</option>)}
                      </select>
                    </div>
                  </div>

                  {newChart.type !== 'text' && newChart.type !== 'table' && (
                    <div className="row">
                      <div className="col-md-6 mb-3">
                        <label className="form-label">X Axis (Category)</label>
                        <select className="form-select" required value={newChart.x_axis} onChange={e => setNewChart({...newChart, x_axis: e.target.value})}>
                          <option value="">Select Field...</option>
                          {modelFields.map(f => <option key={f.name} value={f.name}>{f.title || f.name}</option>)}
                        </select>
                      </div>
                      <div className="col-md-6 mb-3">
                        <label className="form-label">Y Axis (Value)</label>
                        <select className="form-select" required value={newChart.y_axis} onChange={e => setNewChart({...newChart, y_axis: e.target.value})}>
                          <option value="">Select Field...</option>
                          <option value="*">Count All (*)</option>
                          {modelFields.filter(f => ['integer', 'float', 'currency'].includes(f.type)).map(f => <option key={f.name} value={f.name}>{f.title || f.name}</option>)}
                        </select>
                      </div>
                    </div>
                  )}

                  {newChart.type !== 'text' && (
                    <div className="mb-3">
                      <label className="form-label">Aggregation Function</label>
                      <select className="form-select" value={newChart.aggregation} onChange={e => setNewChart({...newChart, aggregation: e.target.value})}>
                        {AGGREGATIONS.map(a => <option key={a.value} value={a.value}>{a.label}</option>)}
                      </select>
                    </div>
                  )}

                  {newChart.type === 'table' && (
                    <div className="mb-3">
                      <label className="form-label">Rows Limit</label>
                      <input type="number" className="form-control" min="1" max="100" value={currentLimit} onChange={e => handleLimitChange(e.target.value)} />
                    </div>
                  )}

                  <div className="mb-3">
                    <label className="form-label">Fixed Filters (JSON)</label>
                    <textarea className="form-control" rows="2" placeholder='e.g. {"status": "confirmed"}' value={newChart.filters} onChange={e => setNewChart({...newChart, filters: e.target.value})}></textarea>
                  </div>
                </div>
                <div className="modal-footer">
                  <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                  <button type="submit" className="btn btn-primary">{editingChart ? 'Update' : 'Create'}</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {showFiltersModal && (
        <div className="modal fade show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Configure Dynamic Filters</h5>
                <button type="button" className="btn-close" onClick={() => setShowFiltersModal(false)}></button>
              </div>
              <div className="modal-body">
                <p className="text-muted small">Add interactive filters that users can apply when viewing the dashboard.</p>

                <div className="border rounded p-3 mb-3">
                  <div className="row g-2">
                    <div className="col-md-4">
                      <input type="text" className="form-control form-control-sm" placeholder="Label" value={tempFilter.label} onChange={e => setTempFilter({...tempFilter, label: e.target.value})} />
                    </div>
                    <div className="col-md-3">
                      <select className="form-select form-select-sm" value={tempFilter.type} onChange={e => setTempFilter({...tempFilter, type: e.target.value})}>
                        {FILTER_TYPES.map(f => <option key={f.value} value={f.value}>{f.label}</option>)}
                      </select>
                    </div>
                    <div className="col-md-3">
                      <select className="form-select form-select-sm" value={tempFilter.field} onChange={e => setTempFilter({...tempFilter, field: e.target.value})}>
                        <option value="">Field...</option>
                        {modelFields.map(f => <option key={f.name} value={f.name}>{f.title || f.name}</option>)}
                      </select>
                    </div>
                    <div className="col-md-2">
                      <button type="button" className="btn btn-sm btn-primary w-100" onClick={addFilter}>Add</button>
                    </div>
                  </div>
                  {tempFilter.type === 'select' || tempFilter.type === 'multiselect' ? (
                    <input type="text" className="form-control form-control-sm mt-2" placeholder="Options (comma separated)" value={tempFilter.options} onChange={e => setTempFilter({...tempFilter, options: e.target.value})} />
                  ) : null}
                </div>

                <div className="list-group">
                  {newChart.filters_config.map((f, i) => (
                    <div key={i} className="list-group-item d-flex justify-content-between align-items-center">
                      <div>
                        <strong>{f.label}</strong>
                        <small className="text-muted ms-2">({f.type}) - {f.field}</small>
                      </div>
                      <button type="button" className="btn btn-sm btn-outline-danger" onClick={() => removeFilter(i)}>&times;</button>
                    </div>
                  ))}
                  {newChart.filters_config.length === 0 && <div className="text-center text-muted p-3">No filters configured</div>}
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowFiltersModal(false)}>Cancel</button>
                <button type="button" className="btn btn-primary" onClick={saveFiltersConfig}>Save Filters</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default SysChartBuilder;
