import React, { useState } from 'react';
import { Card, Table, Button, Tag, Modal, message, Spin, Alert } from 'antd';
import { useModules } from '@/hooks/useModules';
import { Layout } from '../components';

function ModulesPage() {
    const {
        available,
        enabled,
        loading,
        error,
        enableModule,
        disableModule,
        refresh
    } = useModules();

    const [modalOpen, setModalOpen] = useState(false);
    const [selectedModule, setSelectedModule] = useState(null);
    const [actionLoading, setActionLoading] = useState(false);

    const handleEnable = async () => {
        if (!selectedModule) return;

        const moduleId = selectedModule.module_id || selectedModule.id;

        if (!moduleId) {
            message.error('ID modulo non valido');
            return;
        }

        setActionLoading(true);
        try {
            await enableModule(moduleId);
            message.success(`Modulo ${selectedModule.name} abilitato!`);
            setModalOpen(false);
            setSelectedModule(null);
        } catch (err) {
            message.error(`Errore: ${err.message}`);
        } finally {
            setActionLoading(false);
        }
    };

    const handleDisable = async (moduleId, moduleName) => {
        Modal.confirm({
            title: 'Disattivare modulo?',
            content: `Sei sicuro di voler disattivare "${moduleName}"?`,
            okText: 'Sì, disattiva',
            cancelText: 'Annulla',
            onOk: async () => {
                try {
                    await disableModule(moduleId);
                    message.success(`Modulo ${moduleName} disattivato!`);
                } catch (err) {
                    message.error(`Errore: ${err.message}`);
                }
            }
        });
    };

    const columns = [
        {
            title: 'Modulo',
            dataIndex: 'name',
            key: 'name',
            render: (text, record) => (
                <div>
                    <strong>{text}</strong>
                    <br />
                    <small style={{ color: '#888' }}>{record.module_id}</small>
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
            title: 'Categoria',
            dataIndex: 'category',
            key: 'category',
            render: (cat) => {
                const colors = {
                    core: 'blue',
                    builtin: 'green',
                    premium: 'gold',
                    third_party: 'purple'
                };
                return <Tag color={colors[cat] || 'default'}>{cat}</Tag>;
            }
        },
        {
            title: 'Stato',
            key: 'status',
            render: (_, record) => {
                const isEnabled = record.is_enabled || enabled.includes(record.module_id);
                return isEnabled ?
                    <Tag color="green">Attivo</Tag> :
                    <Tag color="default">Non attivo</Tag>;
            }
        },
        {
            title: 'Azioni',
            key: 'actions',
            render: (_, record) => {
                const isEnabled = record.is_enabled || enabled.includes(record.module_id);
                return isEnabled ? (
                    <Button
                        type="link"
                        danger
                        onClick={() => handleDisable(record.module_id, record.name)}
                    >
                        Disattiva
                    </Button>
                ) : (
                    <Button
                        type="link"
                        onClick={() => {
                            setSelectedModule(record);
                            setModalOpen(true);
                        }}
                    >
                        Attiva
                    </Button>
                );
            }
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

    if (error) {
        return (
            <Layout>
            <Alert
                message="Errore"
                description={error}
                type="error"
                showIcon
            />
            </Layout>
        );
    }

    return (
        <Layout>
            <div style={{ padding: 24 }}>
                <Card
                    title="Gestione Moduli"
                    extra={
                        <Button onClick={refresh} loading={loading}>
                            Aggiorna
                        </Button>
                    }
                >
                    <p style={{ marginBottom: 16 }}>
                        Abilita o disattiva i moduli del sistema. Ogni modulo aggiunge funzionalità specifiche.
                    </p>

                    <Table
                    columns={columns}
                    dataSource={available}
                    rowKey="module_id"
                    pagination={false}
                />
            </Card>

            <Modal
                title="Attiva Modulo"
                open={modalOpen}
                onOk={handleEnable}
                onCancel={() => {
                    setModalOpen(false);
                    setSelectedModule(null);
                }}
                confirmLoading={actionLoading}
                okText="Attiva"
                cancelText="Annulla"
            >
                {selectedModule && (
                    <div>
                        <p>Stai per attivare il modulo:</p>
                        <h3>{selectedModule.name}</h3>
                        <p>{selectedModule.description}</p>
                        {selectedModule.is_free ? (
                            <Tag color="green">Gratuito</Tag>
                        ) : (
                            <Tag color="gold">Premium - €{selectedModule.price}</Tag>
                        )}
                    </div>
                )}
            </Modal>
            </div>
        </Layout>
    );
}

export default ModulesPage;
