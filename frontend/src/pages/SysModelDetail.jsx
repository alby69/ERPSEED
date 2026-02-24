import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { apiFetch } from '../utils';
import { Layout } from '../components';
import SysFieldModal from '../components/SysFieldModal';
import ResetTableButton from '../components/ResetTableButton';
import { DndContext, closestCenter, KeyboardSensor, PointerSensor, useSensor, useSensors } from '@dnd-kit/core';
import { arrayMove, SortableContext, sortableKeyboardCoordinates, verticalListSortingStrategy, useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

const AVAILABLE_ROLES = ['user', 'admin', 'manager'];

function SysModelDetail() {
  const { modelId } = useParams();
  const [model, setModel] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showFieldModal, setShowFieldModal] = useState(false);
  const [showEditModelModal, setShowEditModelModal] = useState(false);
  const [modelForm, setModelForm] = useState({ name: '', title: '', description: '', permissions: { read: [], write: [] } });
  const [editingField, setEditingField] = useState(null);

  // Sensori per il Drag & Drop
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  );

  // Componente riga ordinabile
  const SortableRow = ({ field, onEdit, onDelete }) => {
    const { attributes, listeners, setNodeRef, transform, transition } = useSortable({ id: field.id });
    const style = { transform: CSS.Transform.toString(transform), transition };

    return (
      <tr ref={setNodeRef} style={style} {...attributes}>
        <td {...listeners} style={{ cursor: 'grab' }}>
          <i className="bi bi-grip-vertical text-muted me-2"></i>
          <code>{field.name}</code>
        </td>
        <td>{field.title}</td>
        <td><span className="badge bg-info">{field.type}</span></td>
        <td>{field.required ? 'Yes' : 'No'}</td>
        <td>{field.is_unique ? 'Yes' : 'No'}</td>
        <td>{field.default_value}</td>
        <td>
          <button className="btn btn-sm btn-outline-primary me-2" onClick={() => onEdit(field)}>Edit</button>
          <button className="btn btn-sm btn-outline-danger" onClick={() => onDelete(field.id)}>Delete</button>
        </td>
      </tr>
    );
  };

  const fetchModel = async () => {
    try {
      const response = await apiFetch(`/sys-models/${modelId}`);
      if (!response.ok) {
        throw new Error('Failed to fetch model details');
      }
      const data = await response.json();
      // Ordina i campi per 'order' se presente, altrimenti per ID
      if (data.fields) data.fields.sort((a, b) => (a.order || 0) - (b.order || 0));
      setModel(data);
    } catch (err) {
      setError(err.message);
    }
  };

  useEffect(() => {
    const initialFetch = async () => {
      setLoading(true);
      await fetchModel();
      setLoading(false);
    };
    initialFetch();
  }, [modelId]);

  const handleGenerateTable = async () => {
    if (!window.confirm("Are you sure you want to generate/update the database table? This can be a destructive operation if the table already exists and is not perfectly aligned.")) {
      return;
    }
    try {
      const response = await apiFetch(`/sys-models/${modelId}/generate-table`, { method: 'POST' });
      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.message || 'Failed to generate table');
      }
      alert('Table generated successfully!');
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  const handleSaveField = async (fieldData) => {
    const url = editingField ? `/sys-fields/${editingField.id}` : '/sys-fields';
    const method = editingField ? 'PUT' : 'POST';

    try {
      const response = await apiFetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...fieldData, model_id: parseInt(modelId) })
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.message || 'Failed to save field');
      }

      // Ricarica i dati del modello per vedere il nuovo campo
      await fetchModel();
      setShowFieldModal(false);
      setEditingField(null);

    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  const handleDeleteField = async (fieldId) => {
    if (!window.confirm("Are you sure you want to delete this field? This might require a database migration if the table has already been generated.")) {
      return;
    }
    try {
      const response = await apiFetch(`/sys-fields/${fieldId}`, { method: 'DELETE' });
      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.message || 'Failed to delete field');
      }
      // Refresh model data to show updated field list
      await fetchModel();
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  const openAddFieldModal = () => {
    setEditingField(null);
    setShowFieldModal(true);
  };

  const openEditFieldModal = (field) => {
    setEditingField(field);
    setShowFieldModal(true);
  };

  const openEditModelModal = () => {
    let permissions = { read: [], write: [] };
    try {
      if (model.permissions) {
        const parsed = JSON.parse(model.permissions);
        permissions = { read: parsed.read || [], write: parsed.write || [] };
      }
    } catch (e) {
      console.error("Error parsing permissions", e);
    }
    
    setModelForm({
      name: model.name,
      title: model.title,
      description: model.description || '',
      permissions: permissions
    });
    setShowEditModelModal(true);
  };

  const handleUpdateModel = async (e) => {
    e.preventDefault();
    try {
      const payload = { ...modelForm, permissions: JSON.stringify(modelForm.permissions) };
      const response = await apiFetch(`/sys-models/${modelId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.message || 'Failed to update model');
      }

      await fetchModel();
      setShowEditModelModal(false);
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  const handleModelFormChange = (e) => {
    const { name, value } = e.target;
    setModelForm(prev => ({ ...prev, [name]: value }));
  };

  const handlePermissionChange = (action, role) => {
    setModelForm(prev => {
      const currentRoles = prev.permissions[action] || [];
      let newRoles;
      if (currentRoles.includes(role)) {
        newRoles = currentRoles.filter(r => r !== role);
      } else {
        newRoles = [...currentRoles, role];
      }
      return { ...prev, permissions: { ...prev.permissions, [action]: newRoles } };
    });
  };

  const handleDragEnd = async (event) => {
    const { active, over } = event;
    if (active.id !== over.id) {
      setModel((prevModel) => {
        const oldIndex = prevModel.fields.findIndex((f) => f.id === active.id);
        const newIndex = prevModel.fields.findIndex((f) => f.id === over.id);
        const newFields = arrayMove(prevModel.fields, oldIndex, newIndex);
        
        // Aggiorna l'ordine nel backend
        const updates = newFields.map((field, index) => ({
          id: field.id,
          order: index + 1
        }));

        // Invia aggiornamenti in background (ottimistico)
        Promise.all(updates.map(u => 
          apiFetch(`/sys-fields/${u.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ order: u.order, model_id: parseInt(modelId) })
          })
        )).catch(err => console.error("Error updating order", err));

        return { ...prevModel, fields: newFields };
      });
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div className="alert alert-danger">{error}</div>;
  if (!model) return <div>Model not found.</div>;

  return (
    <Layout>
      <div className="container-fluid p-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h2>Model: {model.title}</h2>
        <Link to="/admin/builder" className="btn btn-secondary">Back to Models</Link>
      </div>

      <div className="card mb-4">
        <div className="card-body">
          <div className="d-flex justify-content-between align-items-start">
            <div>
              <h5 className="card-title">Details</h5>
              <p className="mb-1"><strong>Name:</strong> <code>{model.name}</code></p>
              <p className="mb-1"><strong>Description:</strong> {model.description || 'N/A'}</p>
              <p className="mb-1"><strong>Permissions:</strong> <small className="text-muted">{model.permissions || 'None'}</small></p>
            </div>
            <button className="btn btn-outline-primary" onClick={openEditModelModal}>Edit Model</button>
          </div>
          <hr />
          <div className="d-flex gap-2">
            <button className="btn btn-primary" onClick={handleGenerateTable}>
              Generate/Update DB Table
            </button>
            <ResetTableButton modelId={modelId} onSuccess={fetchModel} />
          </div>
        </div>
      </div>

      <div className="d-flex justify-content-between align-items-center mb-3">
        <h4>Fields</h4>
        <button className="btn btn-success" onClick={openAddFieldModal}>Add New Field</button>
      </div>

      <div className="table-responsive">
        <table className="table table-striped">
          <thead>
            <tr>
              <th>Name</th><th>Title</th><th>Type</th><th>Required</th><th>Unique</th><th>Default</th><th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {model.fields && model.fields.length > 0 ? (
              <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
                <SortableContext items={model.fields.map(f => f.id)} strategy={verticalListSortingStrategy}>
                  {model.fields.map(field => (
                    <SortableRow 
                      key={field.id} 
                      field={field} 
                      onEdit={openEditFieldModal} 
                      onDelete={handleDeleteField} 
                    />
                  ))}
                </SortableContext>
              </DndContext>
            ) : ( <tr><td colSpan="7" className="text-center">No fields defined for this model yet.</td></tr> )}
          </tbody>
        </table>
      </div>

      <SysFieldModal 
        show={showFieldModal}
        onClose={() => setShowFieldModal(false)}
        onSave={handleSaveField}
        modelId={modelId}
        fieldToEdit={editingField}
      />

      {/* Edit Model Modal */}
      {showEditModelModal && (
        <div className="modal fade show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog">
            <div className="modal-content">
              <form onSubmit={handleUpdateModel}>
                <div className="modal-header">
                  <h5 className="modal-title">Edit Model</h5>
                  <button type="button" className="btn-close" onClick={() => setShowEditModelModal(false)}></button>
                </div>
                <div className="modal-body">
                  <div className="mb-3">
                    <label className="form-label">Display Title</label>
                    <input type="text" name="title" className="form-control" value={modelForm.title} onChange={handleModelFormChange} required />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Description</label>
                    <textarea name="description" className="form-control" value={modelForm.description} onChange={handleModelFormChange} />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Permissions (ACL)</label>
                    <div className="table-responsive">
                      <table className="table table-sm table-bordered">
                        <thead>
                          <tr>
                            <th>Role</th>
                            <th className="text-center">Read</th>
                            <th className="text-center">Write</th>
                          </tr>
                        </thead>
                        <tbody>
                          {AVAILABLE_ROLES.map(role => (
                            <tr key={role}>
                              <td>{role}</td>
                              <td className="text-center">
                                <input type="checkbox" className="form-check-input" checked={modelForm.permissions.read.includes(role)} onChange={() => handlePermissionChange('read', role)} />
                              </td>
                              <td className="text-center">
                                <input type="checkbox" className="form-check-input" checked={modelForm.permissions.write.includes(role)} onChange={() => handlePermissionChange('write', role)} />
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
                <div className="modal-footer">
                  <button type="button" className="btn btn-secondary" onClick={() => setShowEditModelModal(false)}>Cancel</button>
                  <button type="submit" className="btn btn-primary">Update Model</button>
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

export default SysModelDetail;