import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Modal, Form, Input, Select, Switch, Tag, Space, message, Tabs, Alert } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, PlayCircleOutlined, ApiOutlined } from '@ant-design/icons';
import { useNavigate, useParams } from 'react-router-dom';
import api from './api';

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

    useEffect(() => {
        fetchWorkflows();
        fetchTriggers();
        fetchStepTypes();
    }, [projectId]);

    const fetchWorkflows = async () => {
        try {
            const response = await api.get(`/workflows?project_id=${projectId || ''}`);
            setWorkflows(response.data);
        } catch (error) {
            message.error('Error loading workflows');
        } finally {
            setLoading(false);
        }
    };

    const fetchTriggers = async () => {
        try {
            const response = await api.get('/workflows/triggers');
            setTriggers(response.data.triggers);
        } catch (error) {
            console.error('Error fetching triggers:', error);
        }
    };

    const fetchStepTypes = async () => {
        try {
            const response = await api.get('/workflows/step-types');
            setStepTypes(response.data);
        } catch (error) {
            console.error('Error fetching step types:', error);
        }
    };

    const fetchExecutions = async (workflowId) => {
        try {
            const response = await api.get(`/workflows/${workflowId}/executions`);
            setExecutions(response.data);
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
            await api.delete(`/workflows/${id}`);
            message.success('Workflow deleted');
            fetchWorkflows();
        } catch (error) {
            message.error('Error deleting workflow');
        }
    };

    const handleSubmit = async (values) => {
        try {
            if (editingWorkflow) {
                await api.put(`/workflows/${editingWorkflow.id}`, values);
                message.success('Workflow updated');
            } else {
                await api.post('/workflows', { ...values, project_id: projectId });
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
            await api.put(`/workflows/${workflow.id}`, { is_active: !workflow.is_active });
            fetchWorkflows();
        } catch (error) {
            message.error('Error updating workflow');
        }
    };

    const handleTestWorkflow = async (workflow) => {
        try {
            const response = await api.post(`/workflows/${workflow.id}/test`, {});
            if (response.data.status === 'completed') {
                message.success('Workflow test completed successfully');
            } else {
                message.error(`Workflow test failed: ${response.data.error}`);
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
            const response = await api.get(`/workflows/${workflow.id}`);
            setSelectedWorkflow(response.data);
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
                                <Button
                                    type="primary"
                                    icon={<PlusOutlined />}
                                    onClick={handleCreate}
                                    style={{ marginBottom: '16px' }}
                                >
New Workflow
                                </Button>
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
    );
};

export default WorkflowsPage;
