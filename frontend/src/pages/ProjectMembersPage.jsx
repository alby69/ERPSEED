import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { Table, Button, Modal, Form, Input, Select, message, Popconfirm, Avatar, Tag } from 'antd';
import { DeleteOutlined, UserAddOutlined, UserOutlined, MailOutlined } from '@ant-design/icons';
import { apiFetch } from '../utils';
import { useAuth } from '../context/AuthContext';

const { Option } = Select;

const ProjectMembersPage = () => {
    const { projectId } = useParams();
    const { user } = useAuth();
    const [members, setMembers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [isModalVisible, setIsModalVisible] = useState(false);
    const [form] = Form.useForm();
    
    // State for user selection (Admin only)
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
                message.error("Could not load project members.");
            }
        } catch (error) {
            console.error(error);
            message.error("Connection error.");
        } finally {
            setLoading(false);
        }
    }, [projectId]);

    useEffect(() => {
        fetchMembers();
    }, [fetchMembers]);

    // Load all users for the select (Admin only)
    const fetchAllUsers = async () => {
        if (!isAdmin) return;
        setLoadingUsers(true);
        try {
            const response = await apiFetch('/users');
            if (response.ok) {
                const data = await response.json();
                // Filter users who are already members
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
                message.success("Member added successfully!");
                setIsModalVisible(false);
                form.resetFields();
                fetchMembers();
            } else {
                const err = await response.json();
                message.error(err.message || "Error adding the member.");
            }
        } catch (error) {
            message.error("Connection error.");
        }
    };

    const handleRemoveMember = async (userId) => {
        try {
            const response = await apiFetch(`/projects/${projectId}/members/${userId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                message.success("Member removed.");
                fetchMembers();
            } else {
                const err = await response.json();
                message.error(err.message || "Could not remove the member.");
            }
        } catch (error) {
            message.error("Connection error.");
        }
    };

    const columns = [
        {
            title: 'User',
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
            title: 'System Role',
            dataIndex: 'role',
            key: 'role',
            render: (role) => (
                <Tag color={role === 'admin' ? 'red' : 'blue'}>
                    {role.toUpperCase()}
                </Tag>
            )
        },
        {
            title: 'Actions',
            key: 'actions',
            render: (_, record) => (
                <Popconfirm
                    title="Remove member?"
                    description={`Are you sure you want to remove ${record.email} from the project?`}
                    onConfirm={() => handleRemoveMember(record.id)}
                    okText="Yes"
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
                <h2>Team Members</h2>
                <Button type="primary" icon={<UserAddOutlined />} onClick={handleOpenModal}>
                    Add Member
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
                title="Add Member to Project"
                open={isModalVisible}
                onCancel={() => setIsModalVisible(false)}
                onOk={() => form.submit()}
                confirmLoading={loadingUsers}
            >
                <Form form={form} layout="vertical" onFinish={handleAddMember}>
                    {isAdmin ? (
                        <Form.Item 
                            name="user_id" 
                            label="Select User" 
                            rules={[{ required: true, message: 'Select a user' }]}
                        >
                            <Select 
                                placeholder="Search user..." 
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
                                label="User ID" 
                                rules={[{ required: true, message: 'Enter the user ID' }]}
                                help="Enter the numeric ID of the user to invite."
                            >
                                <Input type="number" placeholder="e.g., 5" />
                            </Form.Item>
                            <div style={{ marginBottom: 16, color: '#faad14', fontSize: '12px' }}>
                                Note: As an owner, you need to know the user's ID. Contact an administrator to search for users by name.
                            </div>
                        </>
                    )}
                </Form>
            </Modal>
        </div>
    );
};

export default ProjectMembersPage;
