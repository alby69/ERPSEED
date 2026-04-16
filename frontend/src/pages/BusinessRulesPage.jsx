import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Modal, Form, Input, Select, Switch, Tag, Space, message, Tabs, Alert, Badge } from 'antd';
import { PlusOutlined, DeleteOutlined, ApiOutlined, SettingOutlined, PlayCircleOutlined } from '@ant-design/icons';
import { useParams } from 'react-router-dom';
import { apiFetch } from '../utils';

const { TextArea } = Input;

const HOOK_TYPES = [
    { value: 'before_create', label: 'Before Create' },
    { value: 'after_create', label: 'After Create' },
    { value: 'before_update', label: 'Before Update' },
    { value: 'after_update', label: 'After Update' },
    { value: 'before_delete', label: 'Before Delete' },
    { value: 'after_delete', label: 'After Delete' },
];

const ACTION_TYPES = [
    { value: 'validate', label: 'Validate' },
    { value: 'set_field', label: 'Set Field' },
    { value: 'update_record', label: 'Update Record' },
    { value: 'create_record', label: 'Create Record' },
];

const BusinessRulesPage = () => {
    const { projectId } = useParams();
    const [rules, setRules] = useState([]);
    const [models, setModels] = useState([]);
    const [loading, setLoading] = useState(true);
    const [modalVisible, setModalVisible] = useState(false);
    const [form] = Form.useForm();
    const [activeTab, setActiveTab] = useState('rules');

    useEffect(() => {
        fetchRules();
        fetchModels();
    }, [projectId]);

    const fetchRules = async () => {
        try {
            const response = await apiFetch(`/projects/${projectId}/builder/business-rules`);
            const data = await response.json();
            setRules(data.rules || []);
        } catch (error) {
            console.error('Error loading rules:', error);
        } finally {
            setLoading(false);
        }
    };

    const fetchModels = async () => {
        try {
            const response = await apiFetch(`/projects/${projectId}/builder/sys-models`);
            const data = await response.json();
            setModels(data.items || []);
        } catch (error) {
            console.error('Error loading models:', error);
        }
    };

    const handleSubmit = async (values) => {
        try {
            await apiFetch(`/projects/${projectId}/builder/business-rules`, {
                method: 'POST',
                body: JSON.stringify(values)
            });
            message.success('Rule created successfully');
            setModalVisible(false);
            form.resetFields();
            fetchRules();
        } catch (error) {
            message.error('Error creating rule');
        }
    };

    const handleDelete = async (record) => {
        try {
            await apiFetch(`/projects/${projectId}/builder/business-rules/${record.id}`, {
                method: 'DELETE',
                body: JSON.stringify({ model_name: record.model_name })
            });
            message.success('Rule deleted');
            fetchRules();
        } catch (error) {
            message.error('Error deleting rule');
        }
    };

    const columns = [
        {
            title: 'Rule Name',
            dataIndex: 'rule_name',
            key: 'rule_name',
            render: (text, record) => (
                <Space direction="vertical" size={0}>
                    <span style={{ fontWeight: 500 }}>{text}</span>
                    <Tag color="blue">{record.model_title || record.model_name}</Tag>
                </Space>
            ),
        },
        {
            title: 'Trigger',
            dataIndex: 'hook_type',
            key: 'hook_type',
            render: (hook_type) => {
                const colors = {
                    before_create: 'green',
                    after_create: 'blue',
                    before_update: 'orange',
                    after_update: 'gold',
                    before_delete: 'red',
                    after_delete: 'purple',
                };
                return <Tag color={colors[hook_type] || 'default'}>{hook_type}</Tag>;
            },
        },
        {
            title: 'Condition',
            dataIndex: 'condition',
            key: 'condition',
            render: (cond) => {
                if (!cond) return <Tag>Always</Tag>;
                return (
                    <span>
                        {cond.field} {cond.operator} {cond.value}
                    </span>
                );
            },
        },
        {
            title: 'Action',
            dataIndex: 'action',
            key: 'action',
            render: (action) => {
                if (!action) return '-';
                return (
                    <Tag color="cyan">
                        {action.type}
                        {action.config?.field && `: ${action.config.field}`}
                    </Tag>
                );
            },
        },
        {
            title: 'Status',
            dataIndex: 'enabled',
            key: 'enabled',
            render: (enabled) => (
                enabled ? <Badge status="success" text="Active" /> : <Badge status="default" text="Disabled" />
            ),
        },
        {
            title: 'Actions',
            key: 'actions',
            render: (_, record) => (
                <Space>
                    <Button
                        type="link"
                        danger
                        icon={<DeleteOutlined />}
                        onClick={() => handleDelete(record)}
                    >
                        Delete
                    </Button>
                </Space>
            ),
        },
    ];

    const getRulesByModel = () => {
        const byModel = {};
        rules.forEach(rule => {
            const modelName = rule.model_name;
            if (!byModel[modelName]) {
                byModel[modelName] = {
                    model_name: modelName,
                    model_title: rule.model_title,
                    rules: [],
                };
            }
            byModel[modelName].rules.push(rule);
        });
        return Object.values(byModel);
    };

    const rulesByModel = getRulesByModel();

    return (
        <div style={{ padding: '24px' }}>
            <h1>Business Rules & Automation</h1>
            <Alert
                message="Business rules allow you to add custom validation and automation logic to your models. Define rules that run before or after record operations."
                type="info"
                showIcon
                style={{ marginBottom: '16px' }}
            />

            <Tabs
                activeKey={activeTab}
                onChange={setActiveTab}
                items={[
                    {
                        key: 'rules',
                        label: (
                            <span>
                                <SettingOutlined /> Business Rules
                            </span>
                        ),
                        children: (
                            <Card>
                                <Space style={{ marginBottom: 16 }}>
                                    <Button
                                        type="primary"
                                        icon={<PlusOutlined />}
                                        onClick={() => setModalVisible(true)}
                                    >
                                        Nuova Regola
                                    </Button>
                                </Space>
                                <Table
                                    columns={columns}
                                    dataSource={rules}
                                    loading={loading}
                                    rowKey="id"
                                    pagination={{ pageSize: 10 }}
                                />
                            </Card>
                        ),
                    },
                    {
                        key: 'by_model',
                        label: (
                            <span>
                                <ApiOutlined /> By Model
                            </span>
                        ),
                        children: (
                            <Card>
                                {rulesByModel.length === 0 ? (
                                    <Alert
                                        message="No business rules defined"
                                        type="warning"
                                        showIcon
                                    />
                                ) : (
                                    rulesByModel.map(model => (
                                        <div key={model.model_name} style={{ marginBottom: 24 }}>
                                            <h3>
                                                {model.model_title || model.model_name}
                                                <Badge
                                                    count={model.rules.length}
                                                    style={{ marginLeft: 8 }}
                                                />
                                            </h3>
                                            <Table
                                                columns={columns}
                                                dataSource={model.rules}
                                                rowKey="id"
                                                pagination={false}
                                                size="small"
                                            />
                                        </div>
                                    ))
                                )}
                            </Card>
                        ),
                    },
                    {
                        key: 'help',
                        label: (
                            <span>
                                <PlayCircleOutlined /> AI Help
                            </span>
                        ),
                        children: (
                            <Card>
                                <h3>Come creare regole con l'AI</h3>
                                <p>
                                    Puoi descrivere in linguaggio naturale cosa vuoi fare e l'AI
                                    genererà automaticamente le regole di business.
                                </p>
                                <h4>Esempi:</h4>
                                <ul>
                                    <li>"Valida che il campo partita IVA sia sempre presente quando si crea un fornitore"</li>
                                    <li>"Quando viene creato un ordine con totale &gt; 1000€, imposta lo stato a 'approvazione richiesta'"</li>
                                    <li>"Dopo la creazione di un cliente, invia una notifica al responsabile vendite"</li>
                                </ul>
                                <Alert
                                    message="Vai nell'AI Assistant per creare regole automaticamente"
                                    type="success"
                                    showIcon
                                />
                            </Card>
                        ),
                    },
                ]}
            />

            <Modal
                title="Nuova Business Rule"
                open={modalVisible}
                onCancel={() => setModalVisible(false)}
                footer={null}
            >
                <Form
                    form={form}
                    layout="vertical"
                    onFinish={handleSubmit}
                >
                    <Form.Item
                        name="model_name"
                        label="Modello"
                        rules={[{ required: true, message: 'Seleziona un modello' }]}
                    >
                        <Select
                            placeholder="Seleziona un modello"
                            options={models.map(m => ({ value: m.name, label: m.title || m.name }))}
                        />
                    </Form.Item>

                    <Form.Item
                        name="hook_type"
                        label="Trigger"
                        rules={[{ required: true, message: 'Seleziona un trigger' }]}
                    >
                        <Select
                            placeholder="Quando eseguire la regola"
                            options={HOOK_TYPES}
                        />
                    </Form.Item>

                    <Form.Item
                        name="rule_name"
                        label="Nome Regola"
                        rules={[{ required: true, message: 'Inserisci un nome' }]}
                    >
                        <Input placeholder="Es: Valida partita IVA obbligatoria" />
                    </Form.Item>

                    <Form.Item
                        name="rule_logic"
                        label="Descrizione (opzionale)"
                    >
                        <TextArea
                            placeholder="Descrivi cosa fa questa regola..."
                            rows={2}
                        />
                    </Form.Item>

                    <Form.Item
                        name="action_type"
                        label="Tipo Azione"
                    >
                        <Select
                            placeholder="Seleziona tipo azione"
                            options={ACTION_TYPES}
                            allowClear
                        />
                    </Form.Item>

                    <Form.Item>
                        <Button type="primary" htmlType="submit" block>
                            Crea Regola
                        </Button>
                    </Form.Item>
                </Form>
            </Modal>
        </div>
    );
};

export default BusinessRulesPage;
