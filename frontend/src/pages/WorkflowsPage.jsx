import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Modal, Form, Input, Select, Switch, Tag, Space, message, Tabs, Alert } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, PlayCircleOutlined, ApiOutlined, BuildOutlined } from '@ant-design/icons';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { apiFetch } from '@/utils';
import AppHeader from '@/components/AppHeader';

const { TextArea } = Input;

const WorkflowsPage = () => {
    const { projectId } = useParams();
    const navigate = useNavigate();
    const [workflows, setWorkflows] = useState([]);
    const [triggers, setTriggers] = useState([]);
    const [stepTypes, setStepTypes] = useState({});
    const [loading, setLoading] = useState(true);
    const [modalVisible, setModalVisible] = useState(false);
    const [editingWorkflow, setEditingWorkflow] = useState(null);
    const [selectedWorkflow, setSelectedWorkflow] = useState(null);
    const [executions, setExecutions] = useState([]);
    const [activeTab, setActiveTab] = useState('list');
    const [form] = Form.useForm();

    const breadcrumbs = [
        { title: <Link to="/projects">Progetti</Link> },
        { title: <Link to={`/projects/${projectId || 1}`}>Demo Project</Link> },
        { title: 'Workflows' },
    ];

    useEffect(() => {
        fetchWorkflows();
        fetchTriggers();
        fetchStepTypes();
    }, [projectId]);

    const fetchWorkflows = async () => {
        try {
            const response = await apiFetch(`/workflows?project_id=${projectId || ''}`);
            const data = await response.json();
            setWorkflows(data);
        } catch (error) {
            message.error('Error loading workflows');
        } finally {
            setLoading(false);
        }
    };

    const fetchTriggers = async () => {
        try {
            const response = await apiFetch('/workflows/triggers');
            const data = await response.json();
            setTriggers(data.triggers);
        } catch (error) {
            console.error('Error fetching triggers:', error);
        }
    };

    const fetchStepTypes = async () => {
        try {
            const response = await apiFetch('/workflows/step-types');
            const data = await response.json();
            setStepTypes(data);
        } catch (error) {
            console.error('Error fetching step types:', error);
        }
    };

    const fetchExecutions = async (workflowId) => {
        try {
            const response = await apiFetch(`/workflows/${workflowId}/executions`);
            const data = await response.json();
            setExecutions(data);
        } catch (error) {
            message.error('Error loading executions');
        }
    };

    const handleCreate = () => {
        setEditingWorkflow(null);
        form.resetFields();
        setModalVisible(true);
    };

    const handleEdit = (workflow) => {
        setEditingWorkflow(workflow);
        form.setFieldsValue(workflow);
        setModalVisible(true);
    };

    const handleDelete = async (id) => {
        try {
            await apiFetch(`/workflows/${id}`, { method: 'DELETE' });
            message.success('Workflow deleted');
            fetchWorkflows();
        } catch (error) {
            message.error('Error deleting workflow');
        }
    };

    const handleSubmit = async (values) => {
        try {
            if (editingWorkflow) {
                await apiFetch(`/workflows/${editingWorkflow.id}`, {
                    method: 'PUT',
                    body: JSON.stringify(values)
                });
                message.success('Workflow updated');
            } else {
                await apiFetch('/workflows', {
                    method: 'POST',
                    body: JSON.stringify({ ...values, project_id: projectId })
                });
                message.success('Workflow created');
            }
            setModalVisible(false);
            fetchWorkflows();
        } catch (error) {
            message.error('Error saving workflow');
        }
    };

    const handleToggleActive = async (workflow) => {
        try {
            await apiFetch(`/workflows/${workflow.id}`, {
                method: 'PUT',
                body: JSON.stringify({ is_active: !workflow.is_active })
            });
            fetchWorkflows();
        } catch (error) {
            message.error('Error updating workflow');
        }
    };

    const handleTestWorkflow = async (workflow) => {
        try {
            const response = await apiFetch(`/workflows/${workflow.id}/test`, { method: 'POST' });
            const data = await response.json();
            if (data.status === 'completed') {
                message.success('Workflow test completed successfully');
            } else {
                message.error(`Workflow test failed: ${data.error}`);
            }
            fetchExecutions(workflow.id);
            setSelectedWorkflow(workflow);
            setActiveTab('executions');
        } catch (error) {
            message.error('Error testing workflow');
        }
    };

    const handleViewWorkflow = async (workflow) => {
        try {
            const response = await apiFetch(`/workflows/${workflow.id}`);
            const data = await response.json();
            setSelectedWorkflow(data);
            fetchExecutions(workflow.id);
            setActiveTab('detail');
        } catch (error) {
            message.error('Error loading details');
        }
    };

    const columns = [
        {
            title: 'Name',
            dataIndex: 'name',
            key: 'name',
        },
        {
            title: 'Trigger',
            dataIndex: 'trigger_event',
            key: 'trigger_event',
            render: (text) => <Tag color="blue">{text}</Tag>,
        },
        {
            title: 'Steps',
            dataIndex: 'steps_count',
            key: 'steps_count',
        },
        {
            title: 'Status',
            dataIndex: 'is_active',
            key: 'is_active',
            render: (active, record) => (
                <Switch
                    checked={active}
                    onChange={() => handleToggleActive(record)}
                    checkedChildren="Active"
                    unCheckedChildren="Inactive"
                />
            ),
        },
        {
            title: 'Actions',
            key: 'actions',
            render: (_, record) => (
                <Space>
                    <Button type="link" icon={<BuildOutlined />} onClick={() => navigate(`/projects/${projectId}/workflow-builder/${record.id}`)}>
                        Builder
                    </Button>
                    <Button type="link" icon={<PlayCircleOutlined />} onClick={() => handleTestWorkflow(record)}>
                        Test
                    </Button>
                    <Button type="link" icon={<ApiOutlined />} onClick={() => handleViewWorkflow(record)}>
                        Details
                    </Button>
                    <Button type="link" icon={<EditOutlined />} onClick={() => handleEdit(record)} />
                    <Button type="link" danger icon={<DeleteOutlined />} onClick={() => handleDelete(record.id)} />
                </Space>
            ),
        },
    ];

    const executionColumns = [
        {
            title: 'ID',
            dataIndex: 'id',
            key: 'id',
        },
        {
            title: 'Event',
            dataIndex: 'trigger_event',
            key: 'trigger_event',
        },
        {
            title: 'Status',
            dataIndex: 'status',
            key: 'status',
            render: (status) => {
                const colors = {
                    completed: 'green',
                    failed: 'red',
                    running: 'blue',
                    cancelled: 'orange',
                };
                return <Tag color={colors[status] || 'default'}>{status}</Tag>;
            },
        },
        {
            title: 'Started',
            dataIndex: 'started_at',
            key: 'started_at',
            render: (text) => text ? new Date(text).toLocaleString() : '-',
        },
        {
            title: 'Completed',
            dataIndex: 'completed_at',
            key: 'completed_at',
            render: (text) => text ? new Date(text).toLocaleString() : '-',
        },
        {
            title: 'Error',
            dataIndex: 'error_message',
            key: 'error_message',
            render: (text) => text ? <span style={{ color: 'red' }}>{text}</span> : '-',
        },
    ];

    return (
        <div>
            <AppHeader breadcrumbs={breadcrumbs} />
            <div style={{ padding: '24px' }}>
                <h1>Workflow Automation</h1>
            <Alert
                message="Workflows allow you to automate actions based on events. Create a workflow and add steps to define automation logic."
                type="info"
                showIcon
                style={{ marginBottom: '16px' }}
            />

            <Tabs
                activeKey={activeTab}
                onChange={setActiveTab}
                items={[
                    {
                        key: 'list',
                        label: 'Workflows',
                        children: (
                            <Card>
                                <Space style={{ marginBottom: 16 }}>
                                    <Button
                                        type="primary"
                                        icon={<PlusOutlined />}
                                        onClick={handleCreate}
                                    >
                                        Nuovo Workflow
                                    </Button>
                                    <Button
                                        icon={<BuildOutlined />}
                                        onClick={() => navigate(`/projects/${projectId}/workflow-builder`)}
                                    >
                                        Builder Visivo
                                    </Button>
                                </Space>
                                <Table
                                    columns={columns}
                                    dataSource={workflows}
                                    loading={loading}
                                    rowKey="id"
                                />
                            </Card>
                        ),
                    },
                    {
                        key: 'detail',
                        label: 'Workflow Details',
                        disabled: !selectedWorkflow,
                        children: selectedWorkflow ? (
                            <Card>
                                <h2>{selectedWorkflow.name}</h2>
                                <p>{selectedWorkflow.description}</p>
                                <p><strong>Trigger:</strong> <Tag color="blue">{selectedWorkflow.trigger_event}</Tag></p>
                                <p><strong>Status:</strong> {selectedWorkflow.is_active ? 'Active' : 'Inactive'}</p>
                                
                                <h3>Steps</h3>
                                {selectedWorkflow.steps && selectedWorkflow.steps.length > 0 ? (
                                    <Table
                                        dataSource={selectedWorkflow.steps}
                                        rowKey="id"
                                        pagination={false}
                                        columns={[
                                            { title: 'Order', dataIndex: 'order', key: 'order' },
                                            { title: 'Name', dataIndex: 'name', key: 'name' },
                                            { title: 'Type', dataIndex: 'step_type', key: 'step_type' },
                                            { title: 'Configuration', dataIndex: 'config', key: 'config', 
                                              render: (config) => <pre>{JSON.stringify(config, null, 2)}</pre> },
                                        ]}
                                    />
                                ) : (
                                    <p>No steps defined</p>
                                )}

                                <h3 style={{ marginTop: '24px' }}>Recent Executions</h3>
                                <Table
                                    dataSource={executions}
                                    rowKey="id"
                                    pagination={{ pageSize: 10 }}
                                    columns={executionColumns}
                                />
                            </Card>
                        ) : (
                            <p>Select a workflow to view details</p>
                        ),
                    },
                ]}
            />

            <Modal
                title={editingWorkflow ? 'Edit Workflow' : 'New Workflow'}
                open={modalVisible}
                onCancel={() => setModalVisible(false)}
                onOk={form.submit}
            >
                <Form form={form} layout="vertical" onFinish={handleSubmit}>
                    <Form.Item
                        name="name"
                        label="Name"
                        rules={[{ required: true, message: 'Enter workflow name' }]}
                    >
                        <Input />
                    </Form.Item>
                    <Form.Item
                        name="description"
                        label="Description"
                    >
                        <TextArea rows={3} />
                    </Form.Item>
                    <Form.Item
                        name="trigger_event"
                        label="Trigger Event"
                        rules={[{ required: true, message: 'Select a trigger event' }]}
                    >
                        <Select>
                            <Select.Option value="*">Any event</Select.Option>
                            {triggers.map((trigger) => (
                                <Select.Option key={trigger} value={trigger}>
                                    {trigger}
                                </Select.Option>
                            ))}
                        </Select>
                    </Form.Item>
                </Form>
            </Modal>
            </div>
        </div>
    );
};

export default WorkflowsPage;
