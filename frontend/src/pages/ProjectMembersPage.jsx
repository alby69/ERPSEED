import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { Table, Button, Modal, Form, Input, Select, message, Popconfirm, Avatar, Tag } from 'antd';
import { DeleteOutlined, UserAddOutlined, UserOutlined, MailOutlined } from '@ant-design/icons';
import { apiFetch } from '@/utils';
import { useAuth } from '@/context/AuthContext';

const { Option } = Select;

const ProjectMembersPage = () => {
    const { projectId } = useParams();
    const { user } = useAuth();
    const [members, setMembers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [isModalVisible, setIsModalVisible] = useState(false);
    const [form] = Form.useForm();
    
    // Stato per la selezione utenti (solo per Admin)
    const [availableUsers, setAvailableUsers] = useState([]);
    const [loadingUsers, setLoadingUsers] = useState(false);

    const isAdmin = user?.role === 'admin';

    const fetchMembers = useCallback(async () => {
        setLoading(true);
        try {
            const response = await apiFetch(`/projects/${projectId}/members`);
            if (response.ok) {
                const data = await response.json();
                setMembers(data);
            } else {
                message.error("Impossibile caricare i membri del progetto.");
            }
        } catch (error) {
            console.error(error);
            message.error("Errore di connessione.");
        } finally {
            setLoading(false);
        }
    }, [projectId]);

    useEffect(() => {
        fetchMembers();
    }, [fetchMembers]);

    // Carica tutti gli utenti per la select (Solo Admin)
    const fetchAllUsers = async () => {
        if (!isAdmin) return;
        setLoadingUsers(true);
        try {
            const response = await apiFetch('/users');
            if (response.ok) {
                const data = await response.json();
                // Filtra gli utenti che sono già membri
                const memberIds = new Set(members.map(m => m.id));
                setAvailableUsers(data.filter(u => !memberIds.has(u.id)));
            }
        } catch (error) {
            console.error(error);
        } finally {
            setLoadingUsers(false);
        }
    };

    const handleOpenModal = () => {
        setIsModalVisible(true);
        if (isAdmin) {
            fetchAllUsers();
        }
    };

    const handleAddMember = async (values) => {
        try {
            const response = await apiFetch(`/projects/${projectId}/members`, {
                method: 'POST',
                body: JSON.stringify({ user_id: values.user_id })
            });

            if (response.ok) {
                message.success("Membro aggiunto con successo!");
                setIsModalVisible(false);
                form.resetFields();
                fetchMembers();
            } else {
                const err = await response.json();
                message.error(err.message || "Errore durante l'aggiunta del membro.");
            }
        } catch (error) {
            message.error("Errore di connessione.");
        }
    };

    const handleRemoveMember = async (userId) => {
        try {
            const response = await apiFetch(`/projects/${projectId}/members/${userId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                message.success("Membro rimosso.");
                fetchMembers();
            } else {
                const err = await response.json();
                message.error(err.message || "Impossibile rimuovere il membro.");
            }
        } catch (error) {
            message.error("Errore di connessione.");
        }
    };

    const columns = [
        {
            title: 'Utente',
            dataIndex: 'email',
            key: 'email',
            render: (text, record) => (
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <Avatar icon={<UserOutlined />} src={record.avatar} />
                    <div>
                        <div style={{ fontWeight: 'bold' }}>{record.first_name} {record.last_name}</div>
                        <div style={{ fontSize: '12px', color: '#888' }}><MailOutlined /> {text}</div>
                    </div>
                </div>
            )
        },
        {
            title: 'Ruolo Sistema',
            dataIndex: 'role',
            key: 'role',
            render: (role) => (
                <Tag color={role === 'admin' ? 'red' : 'blue'}>
                    {role.toUpperCase()}
                </Tag>
            )
        },
        {
            title: 'Azioni',
            key: 'actions',
            render: (_, record) => (
                <Popconfirm
                    title="Rimuovere membro?"
                    description={`Sei sicuro di voler rimuovere ${record.email} dal progetto?`}
                    onConfirm={() => handleRemoveMember(record.id)}
                    okText="Sì"
                    cancelText="No"
                    disabled={record.id === user.id}
                >
                    <Button danger icon={<DeleteOutlined />} size="small" disabled={record.id === user.id} />
                </Popconfirm>
            )
        }
    ];

    return (
        <div style={{ padding: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
                <h2>Membri del Team</h2>
                <Button type="primary" icon={<UserAddOutlined />} onClick={handleOpenModal}>
                    Aggiungi Membro
                </Button>
            </div>

            <Table 
                columns={columns} 
                dataSource={members} 
                rowKey="id" 
                loading={loading}
                pagination={false}
            />

            <Modal
                title="Aggiungi Membro al Progetto"
                open={isModalVisible}
                onCancel={() => setIsModalVisible(false)}
                onOk={() => form.submit()}
                confirmLoading={loadingUsers}
            >
                <Form form={form} layout="vertical" onFinish={handleAddMember}>
                    {isAdmin ? (
                        <Form.Item 
                            name="user_id" 
                            label="Seleziona Utente" 
                            rules={[{ required: true, message: 'Seleziona un utente' }]}
                        >
                            <Select 
                                placeholder="Cerca utente..." 
                                showSearch
                                optionFilterProp="children"
                                loading={loadingUsers}
                            >
                                {availableUsers.map(u => (
                                    <Option key={u.id} value={u.id}>
                                        {u.first_name} {u.last_name} ({u.email})
                                    </Option>
                                ))}
                            </Select>
                        </Form.Item>
                    ) : (
                        <>
                            <Form.Item 
                                name="user_id" 
                                label="ID Utente" 
                                rules={[{ required: true, message: 'Inserisci l\'ID dell\'utente' }]}
                                help="Inserisci l'ID numerico dell'utente da invitare."
                            >
                                <Input type="number" placeholder="Es. 5" />
                            </Form.Item>
                            <div style={{ marginBottom: 16, color: '#faad14', fontSize: '12px' }}>
                                Nota: Come proprietario, devi conoscere l'ID dell'utente. Contatta un amministratore per cercare utenti per nome.
                            </div>
                        </>
                    )}
                </Form>
            </Modal>
        </div>
    );
};

export default ProjectMembersPage;