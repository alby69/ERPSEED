import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Form, Input, Button, message, Spin, Alert, Card, Modal, Divider } from 'antd';
import { ExclamationCircleOutlined } from '@ant-design/icons';
import { apiFetch } from '@/utils';
import { useAuth } from '@/context';

const ProjectSettingsPage = () => {
    const { projectId } = useParams();
    const navigate = useNavigate();
    const { user } = useAuth();
    const [form] = Form.useForm();
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [project, setProject] = useState(null);
    const [error, setError] = useState(null);

    const fetchProjectDetails = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await apiFetch(`/projects/${projectId}`);
            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.message || "Unable to load project details.");
            }
            const data = await response.json();
            setProject(data);
            form.setFieldsValue({
                title: data.title,
                description: data.description,
                version: data.version
            });
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, [projectId, form]);

    useEffect(() => {
        fetchProjectDetails();
    }, [fetchProjectDetails]);

    const onFinish = async (values) => {
        setSaving(true);
        try {
            const response = await apiFetch(`/projects/${projectId}`, {
                method: 'PUT',
                body: JSON.stringify(values),
            });
            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.message || "Error during save.");
            }
            message.success("Project settings saved successfully!");
        } catch (err) {
            message.error(err.message);
        } finally {
            setSaving(false);
        }
    };

    const handleDeleteProject = () => {
        Modal.confirm({
            title: 'Are you absolutely sure?',
            icon: <ExclamationCircleOutlined />,
            content: (
                <div>
                    <p>This action is irreversible and cannot be undone.</p>
                    <p>The project <strong>{project.title}</strong>, all its models, fields, and <strong>ALL DATA</strong> associated with it will be permanently deleted.</p>
                    <p className="mt-3">To confirm, type the name of the project: <strong>{project.name}</strong></p>
                    <Input id="delete-confirm-input" placeholder={project.name} />
                </div>
            ),
            okText: 'Yes, delete this project',
            okType: 'danger',
            cancelText: 'Cancel',
            async onOk() {
                const confirmInput = document.getElementById('delete-confirm-input').value;
                if (confirmInput !== project.name) {
                    message.error('The project name does not match. Deletion cancelled.');
                    return Promise.reject('Confirmation text does not match');
                }
                
                try {
                    const response = await apiFetch(`/projects/${projectId}`, { method: 'DELETE' });
                    if (!response.ok) {
                        const err = await response.json();
                        throw new Error(err.message || 'Error deleting the project.');
                    }
                    message.success('Project deleted successfully.');
                    navigate('/projects'); // Redirect to project selection
                } catch (err) {
                    message.error(err.message);
                    return Promise.reject(err.message);
                }
            },
        });
    };

    if (loading) {
        return <Spin tip="Loading settings..." style={{ display: 'block', marginTop: '50px' }} />;
    }

    if (error) {
        return <Alert message="Error" description={error} type="error" showIcon />;
    }

    return (
        <>
            <Card title="Project Settings">
                <Form form={form} layout="vertical" onFinish={onFinish}>
                    <Form.Item name="title" label="Project Title" rules={[{ required: true, message: 'The title is required.' }]}>
                        <Input placeholder="The display name of the project" />
                    </Form.Item>
                    <Form.Item name="description" label="Description">
                        <Input.TextArea rows={4} placeholder="A brief description of the project" />
                    </Form.Item>
                    <Form.Item name="version" label="Version" rules={[{ required: true, message: 'The version is required.' }]}>
                        <Input placeholder="e.g., 1.0.1" />
                    </Form.Item>
                    <Form.Item>
                        <Button type="primary" htmlType="submit" loading={saving}>Save Settings</Button>
                    </Form.Item>
                </Form>
            </Card>

            <Divider />

            <Card title="Danger Zone" styles={{ header: { color: '#cf1322', backgroundColor: '#fff1f0' } }} style={{ borderColor: '#ffccc7' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                        <h5 style={{ color: '#cf1322' }}>Delete this project</h5>
                        <p className="text-muted mb-0">Once deleted, there is no going back. Be sure.</p>
                    </div>
                    <Button type="primary" danger onClick={handleDeleteProject} disabled={!user || !project || (user.role !== 'admin' && user.id !== project.owner_id)}>
                        Delete Project
                    </Button>
                </div>
            </Card>
        </>
    );
};

export default ProjectSettingsPage;
