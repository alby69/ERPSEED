/**
 * BlockBuilder Page
 * 
 * Page for creating and managing Blocks with Components
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Card, 
  Button, 
  List, 
  Modal, 
  Form, 
  Input, 
  Select, 
  Space, 
  Tag, 
  Typography, 
  Row, 
  Col,
  Empty,
  message,
  Spin,
  Tabs,
  Dropdown,
} from 'antd';
import { 
  PlusOutlined, 
  DeleteOutlined, 
  EditOutlined, 
  SettingOutlined,
  AppstoreOutlined,
  BlockOutlined,
  SaveOutlined,
  ExportOutlined,
} from '@ant-design/icons';
import { apiFetch } from '@/utils';
import { ComponentRenderer } from '@/components/core';

const { Title, Text } = Typography;
const { TextArea } = Input;

function BlockBuilder() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const [blocks, setBlocks] = useState([]);
  const [archetypes, setArchetypes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [showComponentModal, setShowComponentModal] = useState(false);
  const [editingBlock, setEditingBlock] = useState(null);
  const [selectedComponent, setSelectedComponent] = useState(null);
  const [form] = Form.useForm();
  const [componentForm] = Form.useForm();

  useEffect(() => {
    loadData();
  }, [projectId]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [blocksRes, archetypesRes] = await Promise.all([
        apiFetch(`/api/projects/${projectId}/blocks`),
        apiFetch('/api/archetypes'),
      ]);
      
      if (blocksRes.ok) setBlocks(await blocksRes.json());
      if (archetypesRes.ok) setArchetypes(await archetypesRes.json());
    } catch (error) {
      message.error('Error loading data');
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
        message.success('Block created');
        setShowModal(false);
        form.resetFields();
        loadData();
      } else {
        message.error('Error creating block');
      }
    } catch (error) {
      message.error('Error creating block');
    }
  };

  const handleDeleteBlock = async (blockId) => {
    if (!confirm('Delete this block?')) return;
    
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

  const handleAddComponent = async (values) => {
    if (!editingBlock) return;
    
    try {
      const res = await apiFetch(`/api/projects/${projectId}/components`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...values,
          block_id: editingBlock.id,
        }),
      });
      
      if (res.ok) {
        message.success('Component added');
        setShowComponentModal(false);
        componentForm.resetFields();
        loadBlockDetail(editingBlock.id);
      }
    } catch (error) {
      message.error('Error adding component');
    }
  };

  const loadBlockDetail = async (blockId) => {
    try {
      const res = await apiFetch(`/api/blocks/${blockId}`);
      if (res.ok) {
        const block = await res.json();
        setEditingBlock(block);
      }
    } catch (error) {
      message.error('Error loading block');
    }
  };

  const handleEditBlock = (block) => {
    loadBlockDetail(block.id);
  };

  const handleSaveBlock = async () => {
    if (!editingBlock) return;
    
    try {
      const res = await apiFetch(`/api/blocks/${editingBlock.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: editingBlock.name,
          description: editingBlock.description,
          component_ids: editingBlock.component_ids || [],
          relationships: editingBlock.relationships || {},
        }),
      });
      
      if (res.ok) {
        message.success('Block saved');
        loadData();
      }
    } catch (error) {
      message.error('Error saving block');
    }
  };

  const handleUpdateComponentOrder = async (newOrder) => {
    if (!editingBlock) return;
    
    const newBlock = { 
      ...editingBlock, 
      component_ids: newOrder 
    };
    setEditingBlock(newBlock);
  };

  const handlePublish = async (blockId) => {
    try {
      const res = await apiFetch(`/api/blocks/${blockId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'testing' }),
      });
      
      if (res.ok) {
        message.success('Block submitted for testing');
        loadData();
      }
    } catch (error) {
      message.error('Error publishing block');
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

  const getArchetypeInfo = (archetypeId) => {
    return archetypes.find(a => a.id === archetypeId) || {};
  };

  return (
    <div className="block-builder-page" style={{ padding: 24 }}>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <Title level={2} style={{ margin: 0 }}>
            <BlockOutlined /> Block Builder
          </Title>
          <Text type="secondary">Create and manage Blocks with Components</Text>
        </div>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setShowModal(true)}>
          New Block
        </Button>
      </div>

      {loading ? (
        <div className="text-center p-5"><Spin /></div>
      ) : blocks.length === 0 ? (
        <Empty description="No blocks yet. Create your first block!" />
      ) : (
        <Row gutter={[16, 16]}>
          {blocks.map(block => (
            <Col xs={24} sm={12} lg={8} key={block.id}>
              <Card
                hoverable
                actions={[
                  <Button type="text" icon={<EditOutlined />} onClick={() => handleEditBlock(block)}>
                    Edit
                  </Button>,
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
            </Col>
          ))}
        </Row>
      )}

      {/* Block Edit Modal */}
      <Modal
        title={editingBlock ? `Edit: ${editingBlock.name}` : 'Edit Block'}
        open={!!editingBlock}
        onCancel={() => setEditingBlock(null)}
        width={900}
        footer={[
          <Button key="cancel" onClick={() => setEditingBlock(null)}>
            Close
          </Button>,
          <Button key="save" type="primary" icon={<SaveOutlined />} onClick={handleSaveBlock}>
            Save Changes
          </Button>,
        ]}
      >
        {editingBlock && (
          <Tabs
            items={[
              {
                key: 'details',
                label: 'Details',
                children: (
                  <Form layout="vertical">
                    <Form.Item label="Name">
                      <Input 
                        value={editingBlock.name} 
                        onChange={(e) => setEditingBlock({...editingBlock, name: e.target.value})}
                      />
                    </Form.Item>
                    <Form.Item label="Description">
                      <TextArea 
                        value={editingBlock.description} 
                        onChange={(e) => setEditingBlock({...editingBlock, description: e.target.value})}
                        rows={3}
                      />
                    </Form.Item>
                  </Form>
                ),
              },
              {
                key: 'components',
                label: 'Components',
                children: (
                  <div>
                    <div className="mb-3">
                      <Button 
                        type="dashed" 
                        icon={<PlusOutlined />} 
                        onClick={() => setShowComponentModal(true)}
                        block
                      >
                        Add Component
                      </Button>
                    </div>
                    
                    <List
                      bordered
                      dataSource={editingBlock.components || []}
                      renderItem={(comp) => (
                        <List.Item
                          actions={[
                            <Button type="text" size="small" icon={<SettingOutlined />} />,
                            <Button type="text" size="small" danger icon={<DeleteOutlined />} />,
                          ]}
                        >
                          <List.Item.Meta
                            avatar={<AppstoreOutlined />}
                            title={comp.name}
                            description={comp.archetype_name || getArchetypeInfo(comp.archetype_id)?.name}
                          />
                        </List.Item>
                      )}
                    />
                    
                    {(!editingBlock.components || editingBlock.components.length === 0) && (
                      <Empty description="No components yet" />
                    )}
                  </div>
                ),
              },
              {
                key: 'preview',
                label: 'Preview',
                children: (
                  <div>
                    {editingBlock.components?.length > 0 ? (
                      <div style={{ background: '#f5f5f5', padding: 16, borderRadius: 8 }}>
                        {editingBlock.components.map((comp, idx) => (
                          <div key={idx} style={{ marginBottom: 16 }}>
                            <ComponentRenderer
                              type={comp.archetype_name || getArchetypeInfo(comp.archetype_id)?.component_type}
                              config={comp.config}
                            />
                          </div>
                        ))}
                      </div>
                    ) : (
                      <Empty description="Add components to see preview" />
                    )}
                  </div>
                ),
              },
            ]}
          />
        )}
      </Modal>

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

      {/* Add Component Modal */}
      <Modal
        title="Add Component to Block"
        open={showComponentModal}
        onCancel={() => { setShowComponentModal(false); componentForm.resetFields(); }}
        footer={null}
      >
        <Form form={componentForm} layout="vertical" onFinish={handleAddComponent}>
          <Form.Item name="name" label="Component Name" rules={[{ required: true }]}>
            <Input placeholder="e.g., Orders Table" />
          </Form.Item>
          <Form.Item name="archetype_id" label="Component Type" rules={[{ required: true }]}>
            <Select placeholder="Select archetype">
              {archetypes.map(arch => (
                <Select.Option key={arch.id} value={arch.id}>
                  {arch.name} - {arch.description}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              Add Component
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

export default BlockBuilder;
