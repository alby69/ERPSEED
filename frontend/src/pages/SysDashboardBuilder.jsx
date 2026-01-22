import React, { useState, useEffect } from 'react';
import { apiFetch } from '../utils';
import { DndContext, closestCenter, KeyboardSensor, PointerSensor, useSensor, useSensors } from '@dnd-kit/core';
import { arrayMove, SortableContext, sortableKeyboardCoordinates, verticalListSortingStrategy, useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

function SortableChartItem({ id, title, onRemove }) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
  } = useSortable({ id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  return (
    <div ref={setNodeRef} style={style} {...attributes} {...listeners} className="list-group-item d-flex justify-content-between align-items-center bg-white mb-1 border rounded shadow-sm">
      <div className="d-flex align-items-center text-truncate">
        <span className="me-2 text-muted" style={{cursor: 'grab'}}>☰</span>
        {title}
      </div>
      <button 
        type="button" 
        className="btn-close btn-sm" 
        aria-label="Remove"
        onClick={(e) => {
          e.stopPropagation(); // Evita che il click inizi il drag
          onRemove(id);
        }}
      ></button>
    </div>
  );
}

function SysDashboardBuilder() {
  const [dashboards, setDashboards] = useState([]);
  const [charts, setCharts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingDashboard, setEditingDashboard] = useState(null);
  
  const [formData, setFormData] = useState({
    title: '',
    selectedCharts: []
  });

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

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
      try {
        selectedCharts = JSON.parse(dashboard.layout || '{}').charts || [];
      } catch (e) {}
      setFormData({ title: dashboard.title, selectedCharts });
    } else {
      setEditingDashboard(null);
      setFormData({ title: '', selectedCharts: [] });
    }
    setShowModal(true);
  };

  const handleChartSelection = (chartId) => {
    setFormData(prev => {
      if (prev.selectedCharts.includes(chartId)) {
        // Rimozione: filtra l'array esistente
        return { ...prev, selectedCharts: prev.selectedCharts.filter(id => id !== chartId) };
      } else {
        // Aggiunta: appendi alla fine
        return { ...prev, selectedCharts: [...prev.selectedCharts, chartId] };
      }
    });
  };

  const handleDragEnd = (event) => {
    const { active, over } = event;

    if (active.id !== over.id) {
      setFormData((prev) => {
        const oldIndex = prev.selectedCharts.indexOf(active.id);
        const newIndex = prev.selectedCharts.indexOf(over.id);
        return {
          ...prev,
          selectedCharts: arrayMove(prev.selectedCharts, oldIndex, newIndex),
        };
      });
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    const layout = JSON.stringify({ charts: formData.selectedCharts });
    const payload = { title: formData.title, layout };
    
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

  if (loading) return <div className="p-4">Loading...</div>;

  return (
    <div className="container mt-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>BI Builder - Dashboards</h2>
        <button className="btn btn-primary" onClick={() => openModal()}>+ New Dashboard</button>
      </div>

      <ul className="list-group">
        {dashboards.map(d => (
          <li key={d.id} className="list-group-item d-flex justify-content-between align-items-center">
            {d.title}
            <div>
              <button className="btn btn-sm btn-outline-primary me-2" onClick={() => openModal(d)}>Edit</button>
              <button className="btn btn-sm btn-outline-danger" onClick={() => handleDelete(d.id)}>Delete</button>
            </div>
          </li>
        ))}
      </ul>

      {showModal && (
        <div className="modal fade show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog modal-xl">
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
                    {/* Colonna Sinistra: Selezione Grafici */}
                    <div className="col-md-6">
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
                        {charts.length === 0 && <div className="text-muted small">No charts available. Create one first.</div>}
                      </div>
                    </div>

                    {/* Colonna Destra: Ordinamento */}
                    <div className="col-md-6">
                      <label className="form-label">Selected Charts (Drag to Reorder)</label>
                      <div className="border rounded p-2 bg-light" style={{maxHeight: '400px', overflowY: 'auto', minHeight: '100px'}}>
                        <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
                          <SortableContext items={formData.selectedCharts} strategy={verticalListSortingStrategy}>
                            {formData.selectedCharts.map(chartId => {
                              const chart = charts.find(c => c.id === chartId);
                              if (!chart) return null;
                              return <SortableChartItem key={chart.id} id={chart.id} title={chart.title} onRemove={handleChartSelection} />;
                            })}
                          </SortableContext>
                        </DndContext>
                        {formData.selectedCharts.length === 0 && <div className="text-center text-muted mt-4">Select charts from the left to add them here.</div>}
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