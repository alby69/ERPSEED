import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { apiFetch } from '../utils';
import { Layout, message } from 'antd';
import ImportExportToolbar from '../components/ui/ImportExportToolbar';
import ImportExportContextMenu from '../components/ui/ImportExportContextMenu';

function SysModelList() {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newModel, setNewModel] = useState({ name: '', title: '', description: '' });
  const [dateFilters, setDateFilters] = useState({ from: '', to: '' });

  const projectId = localStorage.getItem('currentProjectId') || 1;

  const fetchModels = async () => {
    try {
      const params = new URLSearchParams();
      if (dateFilters.from) params.append('date_from', dateFilters.from);
      if (dateFilters.to) params.append('date_to', dateFilters.to);

      const response = await apiFetch(`/sys-models?${params.toString()}`);
      if (response.ok) {
        const data = await response.json();
        setModels(data);
      } else {
        throw new Error('Failed to fetch models');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchModels();
  }, [dateFilters]);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      const modelData = {
        ...newModel,
        project_id: parseInt(projectId)
      };
      const response = await apiFetch('/sys-models', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(modelData)
      });
      if (response.ok) {
        setShowCreateModal(false);
        setNewModel({ name: '', title: '', description: '' });
        fetchModels();
        // Ricarica la pagina per aggiornare anche la sidebar
        window.location.reload();
      } else {
        const data = await response.json();
        alert(data.message || 'Error creating model');
      }
    } catch (err) {
      alert(err.message);
    }
  };

  const handleClone = async (model) => {
    const newName = prompt("Nome interno per il clone (snake_case):", `${model.name}_copy`);
    if (!newName) return;
    const newTitle = prompt("Titolo visualizzato per il clone:", `${model.title} (Copia)`);
    if (!newTitle) return;

    try {
      const response = await apiFetch(`/sys-models/${model.id}/clone`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newName, title: newTitle })
      });

      if (response.ok) {
alert('Model cloned successfully! Remember to generate the table in the DB.');
        window.location.reload();
      } else {
        const data = await response.json();
        alert(data.message || 'Error during cloning');
      }
    } catch (err) {
      alert(err.message);
    }
  };

  if (loading) return <Layout><div>Loading...</div></Layout>;

  return (
    <Layout>
      <div className="container-fluid p-4">
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h2>System Models (Builder)</h2>
          <div className="d-flex gap-2">
            <div className="d-flex gap-1">
              <input
                type="date"
                className="form-control"
                value={dateFilters.from}
                onChange={e => setDateFilters(prev => ({ ...prev, from: e.target.value }))}
                title="Data Inizio"
              />
              <input
                type="date"
                className="form-control"
                value={dateFilters.to}
                onChange={e => setDateFilters(prev => ({ ...prev, to: e.target.value }))}
                title="Data Fine"
              />
            </div>

            {/* Import/Export Toolbar */}
            <ImportExportToolbar
              type="sysmodels_project"
              projectId={localStorage.getItem('currentProjectId') || 1}
              onImportComplete={() => fetchModels()}
              exportConfigLabel="Esporta Tutti i Modelli"
              showExport={true}
              showImport={true}
            />

            <button className="btn btn-primary" onClick={() => setShowCreateModal(true)}>Create New Model</button>
          </div>
        </div>

        {error && <div className="alert alert-danger">{error}</div>}

        <div className="row">
          {models.map(model => (
            <div key={model.id} className="col-md-4 mb-3">
              <ImportExportContextMenu
                type="sysmodel"
                entityId={model.id}
                entityName={model.name}
                projectId={localStorage.getItem('currentProjectId') || 1}
                onImportComplete={() => fetchModels()}
                showExportConfig={true}
                showExportData={true}
              >
                <div className="card h-100 shadow-sm">
                  <div className="card-body">
                    <h5 className="card-title">{model.title}</h5>
                    <h6 className="card-subtitle mb-2 text-muted"><code>{model.name}</code></h6>
                    <p className="card-text">{model.description || 'No description provided.'}</p>
                    <div className="d-flex gap-2 mt-3">
                      <Link to={`/admin/builder/${model.id}`} className="btn btn-outline-primary flex-grow-1">Manage</Link>
                      <button className="btn btn-outline-secondary" onClick={() => handleClone(model)}>Clone</button>
                    </div>
                  </div>
                </div>
              </ImportExportContextMenu>
            </div>
          ))}
        </div>

        {showCreateModal && (
          <div className="modal fade show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
            <div className="modal-dialog">
              <div className="modal-content">
                <form onSubmit={handleCreate}>
                  <div className="modal-header">
                    <h5 className="modal-title">Create New Model</h5>
                    <button type="button" className="btn-close" onClick={() => setShowCreateModal(false)}></button>
                  </div>
                  <div className="modal-body">
                    <div className="mb-3">
                      <label className="form-label">Internal Name (snake_case)</label>
                      <input
                        type="text"
                        className="form-control"
                        value={newModel.name}
                        onChange={e => setNewModel({...newModel, name: e.target.value})}
                        required
                        pattern="[a-z0-9_]+"
                        title="Solo lettere minuscole, numeri e underscore"
                        placeholder="e.g. sales_orders"
                      />
                    </div>
                    <div className="mb-3">
                      <label className="form-label">Display Title</label>
                      <input
                        type="text"
                        className="form-control"
                        value={newModel.title}
                        onChange={e => setNewModel({...newModel, title: e.target.value})}
                        required
                        placeholder="e.g. Sales Orders"
                      />
                    </div>
                    <div className="mb-3">
                      <label className="form-label">Description</label>
                      <textarea
                        className="form-control"
                        value={newModel.description}
                        onChange={e => setNewModel({...newModel, description: e.target.value})}
                      />
                    </div>
                  </div>
                  <div className="modal-footer">
                    <button type="button" className="btn btn-secondary" onClick={() => setShowCreateModal(false)}>Cancel</button>
                    <button type="submit" className="btn btn-primary">Create</button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}

export default SysModelList;