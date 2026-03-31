/**
 * BlockBuilder Page
 * 
 * Page for creating and managing Blocks with Components using the VisualBuilder
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { 
  Card, 
  Button, 
  List, 
  Modal, 
  Form, 
  Input, 
  Space, 
  Tag, 
  Typography, 
  Row, 
  Col,
  Empty,
  message,
  Spin,
  Select,
} from 'antd';
import AppHeader from '@/components/AppHeader';
import { 
  PlusOutlined, 
  DeleteOutlined, 
  EditOutlined, 
  BlockOutlined,
} from '@ant-design/icons';

import { apiFetch } from '../utils';
import VisualBuilder from './VisualBuilder';
import ImportExportToolbar from '../components/ui/ImportExportToolbar';
import ImportExportContextMenu from '../components/ui/ImportExportContextMenu';

const { Title, Text } = Typography;
const { TextArea } = Input;

function BlockBuilder() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const [blocks, setBlocks] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [showTemplateModal, setShowTemplateModal] = useState(false);
  const [editingBlockId, setEditingBlockId] = useState(null);
  const [editingBlockData, setEditingBlockData] = useState(null);
  const [form] = Form.useForm();
  const [templateForm] = Form.useForm();

  useEffect(() => {
    if (projectId) {
      loadData();
    }
  }, [projectId]);

  const loadData = async () => {
    setLoading(true);
    try {
      // Load regular blocks
      const res = await apiFetch(`/api/projects/${projectId}/blocks`);
      if (res.ok) {
        setBlocks(await res.json());
      }
      // Load templates (blocks with is_template=true)
      const templateRes = await apiFetch(`/api/projects/${projectId}/blocks?is_template=true`);
      if (templateRes.ok) {
        setTemplates(await templateRes.json());
      }
    } catch (error) {
      message.error('Error loading blocks');
    } finally {
      setLoading(false);
    }
  };

  const loadBlockForEdit = async (blockId) => {
    setLoading(true);
    try {
      const res = await apiFetch(`/api/blocks/${blockId}`);
      if (res.ok) {
        const data = await res.json();
        // Convert components from backend format to VisualBuilder format if needed
        const components = data.components.map(c => ({
          id: c.id,
          name: c.name,
          type: c.archetype_name,
          config: c.config || {}
        }));
        setEditingBlockData({ ...data, components });
        setEditingBlockId(blockId);
      }
    } catch (error) {
      message.error('Error loading block details');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateBlock = async (values) => {
    try {
      const res = await apiFetch(`/api/projects/${projectId}/blocks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(values),
      });
      
      if (res.ok) {
        const newBlock = await res.json();
        message.success('Block created');
        setShowModal(false);
        form.resetFields();
        loadBlockForEdit(newBlock.id);
      }
    } catch (error) {
      message.error('Error creating block');
    }
  };

  const handleCreateFromTemplate = async (values) => {
    try {
      const res = await apiFetch(`/api/projects/${projectId}/blocks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...values,
          template_id: values.template_id,
          params_override: values.params_override || {},
        }),
      });
      
      if (res.ok) {
        const newBlock = await res.json();
        message.success('Block created from template');
        setShowTemplateModal(false);
        templateForm.resetFields();
        loadBlockForEdit(newBlock.id);
        loadData();
      }
    } catch (error) {
      message.error('Error creating block from template');
    }
  };

  const handleConvertToTemplate = async (blockId) => {
    try {
      const res = await apiFetch(`/api/blocks/${blockId}/convert-to-template`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({}),
      });
      
      if (res.ok) {
        message.success('Block converted to template');
        loadData();
      }
    } catch (error) {
      message.error('Error converting block to template');
    }
  };

  const handleSaveBlock = async (components) => {
    try {
      // 1. Create/Update components in the backend
      const componentPromises = components.map(async (comp, index) => {
        const isNew = typeof comp.id === 'string' && comp.id.startsWith('comp_');
        const method = isNew ? 'POST' : 'PUT';
        const url = isNew
          ? `/api/projects/${projectId}/components`
          : `/api/components/${comp.id}`;

        // Find archetype ID for new components
        let archetype_id = comp.archetype_id;
        if (isNew) {
           const archRes = await apiFetch('/api/archetypes');
           const archetypes = await archRes.json();
           const arch = archetypes.find(a => a.component_type === comp.type);
           archetype_id = arch?.id;
        }

        const res = await apiFetch(url, {
          method,
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: comp.name,
            config: comp.config,
            archetype_id: archetype_id,
            order_index: index,
            block_id: editingBlockId
          }),
        });

        const data = await res.json();
        return isNew ? data.id : comp.id;
      });

      const componentIds = await Promise.all(componentPromises);

      // 2. Update block with the list of component IDs
      const res = await apiFetch(`/api/blocks/${editingBlockId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          component_ids: componentIds
        }),
      });

      if (res.ok) {
        message.success('Block saved successfully');
        setEditingBlockId(null);
        setEditingBlockData(null);
        loadData();
      }
    } catch (error) {
      message.error('Error saving block');
      console.error(error);
    }
  };

  const handleDeleteBlock = async (blockId) => {
    if (!window.confirm('Delete this block?')) return;
    
    try {
      const res = await apiFetch(`/api/blocks/${blockId}`, { method: 'DELETE' });
      if (res.ok) {
        message.success('Block deleted');
        loadData();
      }
    } catch (error) {
      message.error('Error deleting block');
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      draft: 'default',
      testing: 'processing',
      published: 'success',
    };
    return colors[status] || 'default';
  };

  const [testSuite, setTestSuite] = useState(null);
  const [runningTests, setRunningTests] = useState(false);
  const [testResults, setTestResults] = useState(null);

  const loadTestSuite = async (blockId) => {
    try {
      const res = await apiFetch(`/api/blocks/${blockId}/test-suite`);
      if (res.ok) {
        setTestSuite(await res.json());
      }
    } catch (err) {
      console.error('Error loading test suite:', err);
    }
  };

  const runBlockTests = async () => {
    if (!editingBlockId) return;
    setRunningTests(true);
    setTestResults(null);
    try {
      const res = await apiFetch(`/api/blocks/${editingBlockId}/run-tests`, { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        setTestResults(data);
        setEditingBlockData(prev => ({ ...prev, quality_score: data.quality_score, status: data.status }));
        message.success(`Tests completed! Quality score: ${data.quality_score}%`);
      }
    } catch (err) {
      message.error('Error running tests');
    } finally {
      setRunningTests(false);
    }
  };

  const certifyBlock = async () => {
    if (!editingBlockId) return;
    try {
      const res = await apiFetch(`/api/blocks/${editingBlockId}/certify`, { method: 'POST' });
      if (res.ok) {
        setEditingBlockData(prev => ({ ...prev, is_certified: true, status: 'published' }));
        message.success('Block certified!');
      }
    } catch (err) {
      message.error('Error certifying block');
    }
  };

  useEffect(() => {
    if (editingBlockId) {
      loadTestSuite(editingBlockId);
    }
  }, [editingBlockId]);

  if (editingBlockId && editingBlockData) {
    return (
      <VisualBuilder
        title={`Editing Block: ${editingBlockData.name}`}
        projectId={projectId}
        initialComponents={editingBlockData.components}
        onSave={handleSaveBlock}
        onBack={() => { setEditingBlockId(null); setEditingBlockData(null); }}
        loading={loading}
        extraHeader={
          <Space>
            {editingBlockData.quality_score !== undefined && (
               <Tag color={editingBlockData.quality_score >= 80 ? 'success' : 'warning'}>
                 Score: {editingBlockData.quality_score}%
               </Tag>
            )}
            <Button
              size="small"
              onClick={runBlockTests}
              loading={runningTests}
            >
              Run Tests
            </Button>
            {editingBlockData.quality_score >= 80 && !editingBlockData.is_certified && (
              <Button
                size="small"
                type="primary"
                onClick={certifyBlock}
                style={{ background: '#52c41a', borderColor: '#52c41a' }}
              >
                Certify
              </Button>
            )}
          </Space>
        }
      />
    );
  }

  const breadcrumbs = [
    { title: <Link to="/projects">Progetti</Link> },
    { title: <Link to={`/projects/${projectId || 1}`}>Demo Project</Link> },
    { title: 'Builder' },
    { title: 'Block Builder' },
  ];

  return (
    <div>
      <AppHeader breadcrumbs={breadcrumbs} />
      <div className="block-builder-page" style={{ padding: 24 }}>
        <div className="d-flex justify-content-between align-items-center mb-4">
          <div>
            <Title level={2} style={{ margin: 0 }}>
              <BlockOutlined /> Block Builder
            </Title>
            <Text type="secondary">Create and manage Blocks with Components</Text>
          </div>
        <Space>
          <ImportExportToolbar 
            type="block" 
            projectId={projectId || localStorage.getItem('currentProjectId') || 1}
            showExport={false}
            showImport={true}
            importConfigLabel="Importa Block"
          />
          <Button icon={<BlockOutlined />} onClick={() => setShowTemplateModal(true)}>
            New from Template
          </Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setShowModal(true)}>
            New Block
          </Button>
        </Space>
      </div>

      {loading ? (
        <div className="text-center p-5"><Spin /></div>
      ) : blocks.length === 0 ? (
        <Empty description="No blocks yet. Create your first block!" />
      ) : (
        <Row gutter={[16, 16]}>
          {blocks.map(block => (
            <Col xs={24} sm={12} lg={8} key={block.id}>
              <ImportExportContextMenu 
                type="block"
                entityId={block.id}
                entityName={block.name}
                projectId={projectId || localStorage.getItem('currentProjectId') || 1}
                showExportConfig={true}
                showExportData={false}
              >
                <Card
                  hoverable
                  actions={[
                    <Button type="text" icon={<EditOutlined />} onClick={() => loadBlockForEdit(block.id)}>
                      Edit
                    </Button>,
                    !block.is_template && block.status === 'published' && (
                      <Button type="text" icon={<BlockOutlined />} onClick={() => handleConvertToTemplate(block.id)}>
                        Make Template
                      </Button>
                    ),
                    <Button type="text" danger icon={<DeleteOutlined />} onClick={() => handleDeleteBlock(block.id)}>
                      Delete
                    </Button>,
                  ]}
                >
                  <Card.Meta
                    title={block.name}
                    description={
                      <Space direction="vertical" size={0}>
                        <Text type="secondary">{block.description || 'No description'}</Text>
                        <Space>
                          <Tag color={getStatusColor(block.status)}>{block.status}</Tag>
                          <Text type="secondary">{block.component_count || 0} components</Text>
                        </Space>
                        {block.is_certified && <Tag color="gold">Certified</Tag>}
                      </Space>
                    }
                  />
                </Card>
              </ImportExportContextMenu>
            </Col>
          ))}
        </Row>
      )}

      {/* Create Block Modal */}
      <Modal
        title="Create New Block"
        open={showModal}
        onCancel={() => { setShowModal(false); form.resetFields(); }}
        footer={null}
      >
        <Form form={form} layout="vertical" onFinish={handleCreateBlock}>
          <Form.Item name="name" label="Block Name" rules={[{ required: true }]}>
            <Input placeholder="e.g., Sales Dashboard" />
          </Form.Item>
          <Form.Item name="description" label="Description">
            <TextArea rows={3} placeholder="Describe what this block does..." />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              Create Block
            </Button>
          </Form.Item>
        </Form>
      </Modal>

      {/* Create from Template Modal */}
      <Modal
        title="Create Block from Template"
        open={showTemplateModal}
        onCancel={() => { setShowTemplateModal(false); templateForm.resetFields(); }}
        footer={null}
      >
        <Form form={templateForm} layout="vertical" onFinish={handleCreateFromTemplate}>
          <Form.Item name="template_id" label="Select Template" rules={[{ required: true }]}>
            <Select placeholder="Choose a template">
              {templates.map(t => (
                <Select.Option key={t.id} value={t.id}>
                  {t.name} {t.is_template && <Tag color="blue">Template</Tag>}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="name" label="Block Name" rules={[{ required: true }]}>
            <Input placeholder="e.g., My Custom Card" />
          </Form.Item>
          <Form.Item name="description" label="Description">
            <TextArea rows={2} placeholder="Optional description..." />
          </Form.Item>
          <Form.Item name="params_override" label="Parameters Override (JSON)">
            <TextArea rows={3} placeholder='{"title": "Custom Title", "model_id": 5}' />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              Create from Template
            </Button>
          </Form.Item>
        </Form>
      </Modal>
      </div>
    </div>
  );
}

export default BlockBuilder;
