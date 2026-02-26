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
  Statistic,
  Alert,
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
  PlayCircleOutlined,
  CheckCircleOutlined,
  SafetyCertificateOutlined,
  WarningOutlined,
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
  
  // Testing state
  const [testSuite, setTestSuite] = useState(null);
  const [runningTests, setRunningTests] = useState(false);
  const [testResults, setTestResults] = useState(null);

  // Load test suite for current block
  const loadTestSuite = async (blockId) => {
    try {
      const res = await apiFetch(`/api/blocks/${blockId}/test-suite`);
      if (res.ok) {
        const data = await res.json();
        setTestSuite(data);
      }
    } catch (err) {
      console.error('Error loading test suite:', err);
    }
  };

  // Run tests for block
  const runBlockTests = async () => {
    if (!editingBlock?.id) return;
    setRunningTests(true);
    setTestResults(null);
    try {
      const res = await apiFetch(`/api/blocks/${editingBlock.id}/run-tests`, { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        setTestResults(data);
        setEditingBlock({...editingBlock, quality_score: data.quality_score, status: data.status});
        message.success(`Tests completed! Quality score: ${data.quality_score}%`);
      } else {
        const err = await res.json();
        message.error(err.error || 'Tests failed');
      }
    } catch (err) {
      message.error('Error running tests');
    } finally {
      setRunningTests(false);
    }
  };

  // Create test suite for block
  const createTestSuite = async () => {
    if (!editingBlock?.id) return;
    try {
      const res = await apiFetch(`/api/blocks/${editingBlock.id}/test-suite`, { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        await loadTestSuite(editingBlock.id);
        message.success('Test suite created');
      }
    } catch (err) {
      message.error('Error creating test suite');
    }
  };

  // Certify block
  const certifyBlock = async () => {
    if (!editingBlock?.id) return;
    try {
      const res = await apiFetch(`/api/blocks/${editingBlock.id}/certify`, { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        setEditingBlock({...editingBlock, is_certified: true, status: 'published'});
        message.success('Block certified and published!');
      } else {
        const err = await res.json();
        message.error(err.error || 'Certification failed');
      }
    } catch (err) {
      message.error('Error certifying block');
    }
  };

  // Revoke certification
  const revokeCertification = async () => {
    if (!editingBlock?.id) return;
    try {
      const res = await apiFetch(`/api/blocks/${editingBlock.id}/certify`, { method: 'DELETE' });
      if (res.ok) {
        setEditingBlock({...editingBlock, is_certified: false, status: 'draft'});
        message.success('Certification revoked');
      }
    } catch (err) {
      message.error('Error revoking certification');
    }
  };

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
              {
                key: 'testing',
                label: 'Testing & Certification',
                children: (
                  <div>
                    <Card size="small" style={{ marginBottom: 16 }}>
                      <Row gutter={16}>
                        <Col span={8}>
                          <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: 24, fontWeight: 'bold', color: editingBlock?.quality_score >= 80 ? '#52c41a' : '#faad14' }}>
                              {editingBlock?.quality_score || 0}%
                            </div>
                            <div style={{ color: '#666' }}>Quality Score</div>
                          </div>
                        </Col>
                        <Col span={8}>
                          <div style={{ textAlign: 'center' }}>
                            {editingBlock?.is_certified ? (
                              <CheckCircleOutlined style={{ fontSize: 24, color: '#52c41a' }} />
                            ) : (
                              <WarningOutlined style={{ fontSize: 24, color: '#faad14' }} />
                            )}
                            <div style={{ color: '#666', marginTop: 4 }}>
                              {editingBlock?.is_certified ? 'Certified' : 'Not Certified'}
                            </div>
                          </div>
                        </Col>
                        <Col span={8}>
                          <div style={{ textAlign: 'center' }}>
                            <Tag color={editingBlock?.status === 'published' ? 'green' : editingBlock?.status === 'testing' ? 'blue' : 'default'}>
                              {editingBlock?.status || 'draft'}
                            </Tag>
                            <div style={{ color: '#666', marginTop: 4 }}>Status</div>
                          </div>
                        </Col>
                      </Row>
                    </Card>

                    <Space style={{ marginBottom: 16 }}>
                      {!testSuite?.id ? (
                        <Button icon={<PlayCircleOutlined />} onClick={createTestSuite}>
                          Create Test Suite
                        </Button>
                      ) : (
                        <>
                          <Button 
                            type="primary" 
                            icon={<PlayCircleOutlined />} 
                            onClick={runBlockTests}
                            loading={runningTests}
                          >
                            Run Tests
                          </Button>
                          {editingBlock?.quality_score >= 80 && !editingBlock?.is_certified && (
                            <Button 
                              type="primary" 
                              icon={<SafetyCertificateOutlined />} 
                              onClick={certifyBlock}
                              style={{ background: '#52c41a', borderColor: '#52c41a' }}
                            >
                              Certify Block
                            </Button>
                          )}
                          {editingBlock?.is_certified && (
                            <Button 
                              danger 
                              icon={<WarningOutlined />} 
                              onClick={revokeCertification}
                            >
                              Revoke
                            </Button>
                          )}
                        </>
                      )}
                    </Space>

                    {testResults && (
                      <Card size="small" title="Test Results">
                        <Row gutter={16}>
                          <Col span={8}>
                            <Statistic 
                              title="Passed" 
                              value={testResults.passed} 
                              valueStyle={{ color: '#52c41a' }}
                            />
                          </Col>
                          <Col span={8}>
                            <Statistic 
                              title="Failed" 
                              value={testResults.failed} 
                              valueStyle={{ color: testResults.failed > 0 ? '#ff4d4f' : '#52c41a' }}
                            />
                          </Col>
                          <Col span={8}>
                            <Statistic 
                              title="Success Rate" 
                              value={testResults.success_rate} 
                              suffix="%"
                              valueStyle={{ color: testResults.success_rate >= 80 ? '#52c41a' : '#faad14' }}
                            />
                          </Col>
                        </Row>
                        {testResults.failed > 0 && (
                          <Alert 
                            message="Quality score below 80% - Block cannot be certified" 
                            type="warning" 
                            showIcon 
                            style={{ marginTop: 16 }}
                          />
                        )}
                      </Card>
                    )}

                    {editingBlock?.is_certified && (
                      <Alert 
                        message="This block is certified and can be published to the Marketplace" 
                        type="success" 
                        showIcon 
                        icon={<CheckCircleOutlined />}
                        style={{ marginTop: 16 }}
                      />
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
