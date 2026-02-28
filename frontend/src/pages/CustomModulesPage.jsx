import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Tag, Modal, Form, Input, Select, message, Spin, Alert, Space, Badge } from 'antd';
import { apiFetch } from '@/utils';
import { Layout } from '../components';
import { useParams } from 'react-router-dom';

const { TextArea } = Input;

function CustomModulesPage() {
    const { projectId } = useParams();
    const [modules, setModules] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [modalOpen, setModalOpen] = useState(false);
    const [editingModule, setEditingModule] = useState(null);
    const [form] = Form.useForm();
    const [submitting, setSubmitting] = useState(false);

    const fetchModules = async () => {
        setLoading(true);
        try {
            const url = projectId 
                ? `/api/v1/modules?project_id=${projectId}`
                : '/api/v1/modules';
            const response = await apiFetch(url);
            const data = await response.json();
            setModules(data.modules || []);
            setError(null);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchModules();
    }, [projectId]);

    const handleCreate = async (values) => {
        setSubmitting(true);
        try {
            const response = await apiFetch('/api/v1/modules', {
                method: 'POST',
                body: JSON.stringify({
                    ...values,
                    project_id: parseInt(projectId) || 1
                })
            });
            
            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.message || 'Errore nella creazione');
            }
            
            message.success('Modulo creato con successo!');
            setModalOpen(false);
            form.resetFields();
            setEditingModule(null);
            fetchModules();
        } catch (err) {
            message.error(err.message);
        } finally {
            setSubmitting(false);
        }
    };

    const handleStatusChange = async (moduleId, newStatus) => {
        try {
            const response = await apiFetch(`/api/v1/modules/${moduleId}/status`, {
                method: 'POST',
                body: JSON.stringify({ status: newStatus })
            });
            
            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.message || 'Errore');
            }
            
            message.success('Stato aggiornato!');
            fetchModules();
        } catch (err) {
            message.error(err.message);
        }
    };

    const handleDelete = async (moduleId) => {
        Modal.confirm({
            title: 'Elimina modulo',
            content: 'Sei sicuro di voler eliminare questo modulo?',
            okText: 'Elimina',
            cancelText: 'Annulla',
            okButtonProps: { danger: true },
            onOk: async () => {
                try {
                    const response = await apiFetch(`/api/v1/modules/${moduleId}`, {
                        method: 'DELETE'
                    });
                    
                    if (!response.ok) {
                        const err = await response.json();
                        throw new Error(err.message || 'Errore');
                    }
                    
                    message.success('Modulo eliminato!');
                    fetchModules();
                } catch (err) {
                    message.error(err.message);
                }
            }
        });
    };

    const statusColors = {
        draft: 'default',
        testing: 'processing',
        published: 'success',
        deprecated: 'error'
    };

    const statusLabels = {
        draft: 'Bozza',
        testing: 'Test',
        published: 'Pubblicato',
        deprecated: 'Obsoleto'
    };

    const columns = [
        {
            title: 'Nome',
            dataIndex: 'name',
            key: 'name',
            render: (text, record) => (
                <div>
                    <strong>{text}</strong>
                    <br />
                    <small style={{ color: '#888' }}>{record.title}</small>
                </div>
            )
        },
        {
            title: 'Descrizione',
            dataIndex: 'description',
            key: 'description',
            ellipsis: true
        },
        {
            title: 'Stato',
            dataIndex: 'status',
            key: 'status',
            render: (status) => (
                <Badge 
                    status={
                        status === 'published' ? 'success' :
                        status === 'testing' ? 'processing' :
                        status === 'deprecated' ? 'error' : 'default'
                    } 
                    text={statusLabels[status] || status} 
                />
            )
        },
        {
            title: 'Modelli',
            key: 'models',
            render: (_, record) => record.models?.length || 0
        },
        {
            title: 'Blocchi',
            key: 'blocks',
            render: (_, record) => record.blocks?.length || 0
        },
        {
            title: 'Azioni',
            key: 'actions',
            render: (_, record) => (
                <Space>
                    {record.status === 'draft' && (
                        <Button 
                            size="small" 
                            onClick={() => handleStatusChange(record.id, 'testing')}
                        >
                            Test
                        </Button>
                    )}
                    {record.status === 'testing' && (
                        <Button 
                            size="small" 
                            type="primary"
                            onClick={() => handleStatusChange(record.id, 'published')}
                        >
                            Pubblica
                        </Button>
                    )}
                    {record.status === 'published' && (
                        <Button 
                            size="small" 
                            onClick={() => handleStatusChange(record.id, 'draft')}
                        >
                            Revoca
                        </Button>
                    )}
                    <Button 
                        size="small" 
                        danger
                        onClick={() => handleDelete(record.id)}
                    >
                        Elimina
                    </Button>
                </Space>
            )
        }
    ];

    if (loading) {
        return (
            <Layout>
                <div style={{ textAlign: 'center', padding: 50 }}>
                    <Spin size="large" />
                </div>
            </Layout>
        );
    }

    return (
        <Layout>
            <div style={{ padding: 24 }}>
                <Card
                    title="Moduli Personalizzati"
                    extra={
                        <Space>
                            <Button onClick={fetchModules}>
                                Aggiorna
                            </Button>
                            <Button type="primary" onClick={() => setModalOpen(true)}>
                                Nuovo Modulo
                            </Button>
                        </Space>
                    }
                >
                    <p style={{ marginBottom: 16 }}>
                        Crea e gestisci moduli personalizzati per la tua applicazione.
                        Ogni modulo può contenere modelli dati e blocchi UI.
                    </p>
                    
                    {error && (
                        <Alert
                            message="Errore"
                            description={error}
                            type="error"
                            showIcon
                            style={{ marginBottom: 16 }}
                        />
                    )}
                    
                    <Table
                        columns={columns}
                        dataSource={modules}
                        rowKey="id"
                        pagination={false}
                        locale={{
                            emptyText: 'Nessun modulo creato. Crea il tuo primo modulo!'
                        }}
                    />
                </Card>

                <Modal
                    title={editingModule ? 'Modifica Modulo' : 'Nuovo Modulo'}
                    open={modalOpen}
                    onCancel={() => {
                        setModalOpen(false);
                        form.resetFields();
                        setEditingModule(null);
                    }}
                    footer={null}
                >
                    <Form
                        form={form}
                        layout="vertical"
                        onFinish={handleCreate}
                    >
                        <Form.Item
                            name="name"
                            label="Nome tecnico"
                            rules={[{ required: true, message: 'Inserisci il nome' }]}
                        >
                            <Input placeholder="es: gestione_magazzino" />
                        </Form.Item>
                        
                        <Form.Item
                            name="title"
                            label="Titolo"
                            rules={[{ required: true, message: 'Inserisci il titolo' }]}
                        >
                            <Input placeholder="es: Gestione Magazzino" />
                        </Form.Item>
                        
                        <Form.Item
                            name="description"
                            label="Descrizione"
                        >
                            <TextArea rows={3} placeholder="Descrizione del modulo..." />
                        </Form.Item>
                        
                        <Form.Item
                            name="icon"
                            label="Icona"
                            initialValue="box"
                        >
                            <Select>
                                <Select.Option value="box">Box</Select.Option>
                                <Select.Option value="database">Database</Select.Option>
                                <Select.Option value="shopping-cart">Carrello</Select.Option>
                                <Select.Option value="users">Utenti</Select.Option>
                                <Select.Option value="file">Documenti</Select.Option>
                                <Select.Option value="chart">Statistiche</Select.Option>
                            </Select>
                        </Form.Item>
                        
                        <Form.Item>
                            <Space>
                                <Button type="primary" htmlType="submit" loading={submitting}>
                                    {editingModule ? 'Salva' : 'Crea'}
                                </Button>
                                <Button onClick={() => {
                                    setModalOpen(false);
                                    form.resetFields();
                                    setEditingModule(null);
                                }}>
                                    Annulla
                                </Button>
                            </Space>
                        </Form.Item>
                    </Form>
                </Modal>
            </div>
        </Layout>
    );
}

export default CustomModulesPage;
