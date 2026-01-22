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

function SysChartBuilder() {
  const [charts, setCharts] = useState([]);
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  
  // Form State
  const [newChart, setNewChart] = useState({
    title: '',
    type: 'bar',
    model_id: '',
    x_axis: '',
    y_axis: '',
    aggregation: 'sum',
    filters: '',
    content: ''
  });
  
  // Fields of the selected model for dropdowns
  const [modelFields, setModelFields] = useState([]);

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

  // Load fields when model is selected
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
      const res = await apiFetch('/sys-charts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newChart)
      });
      
      if (res.ok) {
        setShowModal(false);
        setNewChart({ title: '', type: 'bar', model_id: '', x_axis: '', y_axis: '', aggregation: 'sum', filters: '', content: '' });
        fetchData();
      } else {
        alert("Error creating chart");
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

  // Helper per gestire il limite nel JSON filters
  const handleLimitChange = (val) => {
    try {
      const currentFilters = newChart.filters ? JSON.parse(newChart.filters) : {};
      currentFilters.limit = parseInt(val);
      setNewChart({ ...newChart, filters: JSON.stringify(currentFilters) });
    } catch (e) {
      // Se il JSON non è valido, sovrascriviamo o gestiamo l'errore. 
      // Qui facciamo un reset semplice per usabilità.
      setNewChart({ ...newChart, filters: JSON.stringify({ limit: parseInt(val) }) });
    }
  };

  const currentLimit = (() => { try { return JSON.parse(newChart.filters).limit || 5 } catch { return 5 } })();

  if (loading) return <div className="p-4">Loading...</div>;

  return (
    <div className="container mt-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>BI Builder - Charts</h2>
        <button className="btn btn-primary" onClick={() => setShowModal(true)}>+ New Chart</button>
      </div>

      <div className="row">
        {charts.map(chart => (
          <div key={chart.id} className="col-md-6 mb-4">
            <div className="card h-100 shadow-sm">
              <div className="card-header d-flex justify-content-between align-items-center">
                <h5 className="mb-0">{chart.title}</h5>
                <button className="btn btn-sm btn-outline-danger" onClick={() => handleDelete(chart.id)}>&times;</button>
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
                <h5 className="modal-title">Create New Chart</h5>
                <button type="button" className="btn-close" onClick={() => setShowModal(false)}></button>
              </div>
              <form onSubmit={handleCreate}>
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

                  <div className="mb-3">
                    <label className="form-label">Aggregation Function</label>
                    <select className="form-select" value={newChart.aggregation} onChange={e => setNewChart({...newChart, aggregation: e.target.value})}>
                      {AGGREGATIONS.map(a => <option key={a.value} value={a.value}>{a.label}</option>)}
                    </select>
                  </div>

                  <div className="mb-3">
                    <label className="form-label">Filters (JSON)</label>
                    <textarea className="form-control" rows="2" placeholder='e.g. {"status": "confirmed"}' value={newChart.filters} onChange={e => setNewChart({...newChart, filters: e.target.value})}></textarea>
                  </div>
                </div>
                <div className="modal-footer">
                  <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                  <button type="submit" className="btn btn-primary">Create Chart</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default SysChartBuilder;