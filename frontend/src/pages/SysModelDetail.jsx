import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Card, Table, Button, Modal, Form, Input, Checkbox, Tag, Space, Typography,
  Popconfirm, message, Row, Col, Breadcrumb, Flex
} from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, DatabaseOutlined, HolderOutlined } from '@ant-design/icons';
import { DndContext, closestCenter, KeyboardSensor, PointerSensor, useSensor, useSensors } from '@dnd-kit/core';
import { arrayMove, SortableContext, sortableKeyboardCoordinates, verticalListSortingStrategy, useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

import { apiFetch } from '../utils';
import { Layout } from '../components';
import SysFieldModal from '../components/SysFieldModal';
import ResetTableButton from '../components/ResetTableButton';

const { Title, Text } = Typography;

const AVAILABLE_ROLES = ['user', 'admin', 'manager'];

function SysModelDetail() {
  const { modelId } = useParams();
  const [model, setModel] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showFieldModal, setShowFieldModal] = useState(false);
  const [showEditModelModal, setShowEditModelModal] = useState(false);
  const [modelForm, setModelForm] = useState({ name: '', title: '', description: '', permissions: { read: [], write: [] } });
  const [editingField, setEditingField] = useState(null);

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  );

  const SortableRow = ({ field, onEdit, onDelete }) => {
    const { attributes, listeners, setNodeRef, transform, transition } = useSortable({ id: field.id });
    const style = { transform: CSS.Transform.toString(transform), transition };

    return (
      <tr ref={setNodeRef} style={style} {...attributes}>
        <td {...listeners} style={{ cursor: 'grab', padding: '12px 8px' }}>
          <HolderOutlined style={{ marginRight: 8, color: '#8c8c8c' }} />
          <code>{field.name}</code>
        </td>
        <td style={{ padding: '12px 8px' }}>{field.title}</td>
        <td style={{ padding: '12px 8px' }}><Tag color="cyan">{field.type}</Tag></td>
        <td style={{ padding: '12px 8px' }}>{field.required ? <Tag color="green">Yes</Tag> : <Tag>No</Tag>}</td>
        <td style={{ padding: '12px 8px' }}>{field.is_unique ? <Tag color="blue">Yes</Tag> : <Tag>No</Tag>}</td>
        <td style={{ padding: '12px 8px' }}>{field.default_value || '-'}</td>
        <td style={{ padding: '12px 8px' }}>
          <Space>
            <Button type="text" icon={<EditOutlined />} onClick={() => onEdit(field)} />
            <Popconfirm title="Delete this field?" onConfirm={() => onDelete(field.id)} okText="Yes" cancelText="No">
              <Button type="text" danger icon={<DeleteOutlined />} />
            </Popconfirm>
          </Space>
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
      const fields = data.model_fields || data.fields || [];
      if (fields.length > 0) fields.sort((a, b) => (a.order || 0) - (b.order || 0));
      data.fields = fields;
      setModel(data);
    } catch (err) {
      message.error(err.message);
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
    try {
      const response = await apiFetch(`/sys-models/${modelId}/generate-table`, { method: 'POST' });
      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.message || 'Failed to generate table');
      }
      message.success('Table generated/updated successfully!');
    } catch (err) {
      message.error(`Error: ${err.message}`);
    }
  };

  const handleSaveField = async (fieldData) => {
    const url = editingField ? `/sys-fields/${editingField.id}` : '/sys-fields';
    const method = editingField ? 'PUT' : 'POST';

    try {
      const response = await apiFetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...fieldData, modelId: parseInt(modelId) })
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.message || 'Failed to save field');
      }

      await fetchModel();
      setShowFieldModal(false);
      setEditingField(null);
      message.success('Field saved');
    } catch (err) {
      message.error(`Error: ${err.message}`);
    }
  };

  const handleDeleteField = async (fieldId) => {
    try {
      const response = await apiFetch(`/sys-fields/${fieldId}`, { method: 'DELETE' });
      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.message || 'Failed to delete field');
      }
      await fetchModel();
      message.success('Field deleted');
    } catch (err) {
      message.error(`Error: ${err.message}`);
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
        const parsed = typeof model.permissions === 'string' ? JSON.parse(model.permissions) : model.permissions;
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

  const handleUpdateModel = async () => {
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
      message.success('Model updated');
    } catch (err) {
      message.error(`Error: ${err.message}`);
    }
  };

  const handlePermissionChange = (action, role, checked) => {
    setModelForm(prev => {
      const currentRoles = prev.permissions[action] || [];
      let newRoles = checked
        ? [...currentRoles, role]
        : currentRoles.filter(r => r !== role);

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

        const updates = newFields.map((field, index) => ({
          id: field.id,
          order: index + 1
        }));

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

  if (loading) return <Layout><Card loading /></Layout>;
  if (!model) return <Layout><Card><Text type="danger">Model not found.</Text></Card></Layout>;

  return (
    <Layout>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <Breadcrumb
          items={[
            { title: <Link to="/admin/builder">Model Builder</Link> },
            { title: model.title || model.name }
          ]}
        />

        <Flex justify="space-between" align="center">
          <Title level={3} style={{ margin: 0 }}>
            Model Detail: {model.title}
          </Title>
          <Link to="/admin/builder">
            <Button>Back to Models</Button>
          </Link>
        </Flex>

        <Card title="Model Details" extra={<Button type="outline" icon={<EditOutlined />} onClick={openEditModelModal}>Edit Model</Button>}>
          <Space direction="vertical" size="small" style={{ width: '100%' }}>
            <div><Text strong>System Name:</Text> <code>{model.name}</code></div>
            <div><Text strong>Description:</Text> {model.description || 'N/A'}</div>
            <div><Text strong>Permissions:</Text> <Text type="secondary">{typeof model.permissions === 'string' ? model.permissions : JSON.stringify(model.permissions)}</Text></div>
            <Space style={{ marginTop: 12 }}>
              <Popconfirm title="Generate or update table structure in database?" onConfirm={handleGenerateTable} okText="Generate" cancelText="Cancel">
                <Button type="primary" icon={<DatabaseOutlined />}>
                  Generate/Update DB Table
                </Button>
              </Popconfirm>
              <ResetTableButton modelId={modelId} onSuccess={fetchModel} />
            </Space>
          </Space>
        </Card>

        <Card
          title="Fields Specification"
          extra={
            <Button type="primary" icon={<PlusOutlined />} onClick={openAddFieldModal}>
              Add New Field
            </Button>
          }
        >
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #f0f0f0', textAlign: 'left', background: '#fafafa' }}>
                  <th style={{ padding: '12px 8px' }}>Name</th>
                  <th style={{ padding: '12px 8px' }}>Title</th>
                  <th style={{ padding: '12px 8px' }}>Type</th>
                  <th style={{ padding: '12px 8px' }}>Required</th>
                  <th style={{ padding: '12px 8px' }}>Unique</th>
                  <th style={{ padding: '12px 8px' }}>Default</th>
                  <th style={{ padding: '12px 8px' }}>Actions</th>
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
                ) : (
                  <tr>
                    <td colSpan="7" style={{ textAlign: 'center', padding: 24 }}>
                      <Text type="secondary">No fields defined for this model yet.</Text>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </Card>

        <SysFieldModal
          show={showFieldModal}
          onClose={() => setShowFieldModal(false)}
          onSave={handleSaveField}
          modelId={modelId}
          fieldToEdit={editingField}
        />

        {/* Edit Model Modal */}
        <Modal
          title="Edit Model Configuration"
          open={showEditModelModal}
          onCancel={() => setShowEditModelModal(false)}
          onOk={handleUpdateModel}
          okText="Update Model"
        >
          <Space direction="vertical" style={{ width: '100%' }} size="middle">
            <div>
              <Text strong style={{ display: 'block', marginBottom: 4 }}>Display Title</Text>
              <Input
                value={modelForm.title}
                onChange={e => setModelForm({ ...modelForm, title: e.target.value })}
              />
            </div>
            <div>
              <Text strong style={{ display: 'block', marginBottom: 4 }}>Description</Text>
              <Input.TextArea
                rows={3}
                value={modelForm.description}
                onChange={e => setModelForm({ ...modelForm, description: e.target.value })}
              />
            </div>
            <div>
              <Text strong style={{ display: 'block', marginBottom: 8 }}>Permissions (ACL)</Text>
              <table style={{ width: '100%', border: '1px solid #f0f0f0', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ background: '#fafafa', borderBottom: '1px solid #f0f0f0' }}>
                    <th style={{ padding: 8 }}>Role</th>
                    <th style={{ padding: 8, textAlign: 'center' }}>Read</th>
                    <th style={{ padding: 8, textAlign: 'center' }}>Write</th>
                  </tr>
                </thead>
                <tbody>
                  {AVAILABLE_ROLES.map(role => (
                    <tr key={role} style={{ borderBottom: '1px solid #f0f0f0' }}>
                      <td style={{ padding: 8 }}>{role}</td>
                      <td style={{ padding: 8, textAlign: 'center' }}>
                        <Checkbox
                          checked={modelForm.permissions.read.includes(role)}
                          onChange={e => handlePermissionChange('read', role, e.target.checked)}
                        />
                      </td>
                      <td style={{ padding: 8, textAlign: 'center' }}>
                        <Checkbox
                          checked={modelForm.permissions.write.includes(role)}
                          onChange={e => handlePermissionChange('write', role, e.target.checked)}
                        />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Space>
        </Modal>
      </Space>
    </Layout>
  );
}

export default SysModelDetail;
