import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Form, Input, Button, message, Spin, Alert, Card, Modal, Divider, ColorPicker, InputNumber, Radio, Table, Switch, Tag, Tabs } from 'antd';
import { ExclamationCircleOutlined, RocketOutlined, SettingOutlined } from '@ant-design/icons';
import { apiFetch } from '../utils';
import { useAuth, useTheme } from '../context';
import TemplateGallery from '../components/ui/TemplateGallery';
import { CHART_LIBRARIES, CHART_LIBRARY_LABELS } from '../components/charts';

const ProjectSettingsPage = () => {
    const { projectId } = useParams();
    const navigate = useNavigate();
    const { user } = useAuth();
    const { updateTheme } = useTheme();
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
                version: data.version,
                primary_color: data.primary_color || '#1677ff',
                border_radius: data.border_radius || 6,
                theme_mode: data.theme_mode || 'light'
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

        // Convert color object to hex if it's from ColorPicker
        const payload = {
            ...values,
            primary_color: typeof values.primary_color === 'string' ? values.primary_color : values.primary_color.toHexString()
        };

        try {
            const response = await apiFetch(`/projects/${projectId}`, {
                method: 'PUT',
                body: JSON.stringify(payload),
            });
            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.message || "Error during save.");
            }

            // Update live theme
            updateTheme({
                primaryColor: payload.primary_color,
                borderRadius: payload.border_radius,
                mode: payload.theme_mode
            });

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

    const settingsTabs = [
        {
            key: 'general',
            label: <span><SettingOutlined /> General Settings</span>,
            children: (
                <Card>
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

                        <Divider orientation="left">Appearance & Theme</Divider>

                        <div className="row">
                            <div className="col-md-4">
                                <Form.Item name="theme_mode" label="Theme Mode">
                                    <Radio.Group buttonStyle="solid">
                                        <Radio.Button value="light">Light</Radio.Button>
                                        <Radio.Button value="dark">Dark</Radio.Button>
                                    </Radio.Group>
                                </Form.Item>
                            </div>
                            <div className="col-md-4">
                                <Form.Item name="primary_color" label="Primary Color">
                                    <ColorPicker showText />
                                </Form.Item>
                            </div>
                            <div className="col-md-4">
                                <Form.Item name="border_radius" label="Border Radius (px)">
                                    <InputNumber min={0} max={20} />
                                </Form.Item>
                            </div>
                        </div>

                        <Form.Item className="mt-4">
                            <Button type="primary" htmlType="submit" loading={saving}>Save Settings</Button>
                        </Form.Item>
                    </Form>
                </Card>
            )
        },
        {
            key: 'templates',
            label: <span><RocketOutlined /> Starter Templates</span>,
            children: (
                <Card>
                    <TemplateGallery projectId={projectId} onInstalled={() => fetchProjectDetails()} />
                </Card>
            )
        },
        {
            key: 'charts',
            label: <span><SettingOutlined /> Charts</span>,
            children: (
                <Card title="Chart Libraries">
                    <div className="mb-3">
                        <p className="text-muted">Configura le librerie grafiche disponibili per i dashboard.</p>
                    </div>
                    <ChartLibrarySettings />
                </Card>
            )
        }
    ];

    return (
        <>
            <Title level={3} style={{ marginBottom: 24 }}>Project Settings: {project?.title}</Title>

            <Tabs defaultActiveKey="general" items={settingsTabs} />

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

function ChartLibrarySettings() {
    const [libraries, setLibraries] = useState([]);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);

    const defaultLibraries = [
        { id: 1, library_name: 'chartjs', is_default: true, is_active: true },
        { id: 2, library_name: 'apexcharts', is_default: false, is_active: true },
        { id: 3, library_name: 'echarts', is_default: false, is_active: true },
    ];

    const fetchLibraries = useCallback(async () => {
        setLoading(true);
        try {
            const res = await apiFetch('/chart-libraries');
            if (res.ok) {
                const data = await res.json();
                if (Array.isArray(data) && data.length > 0) {
                    setLibraries(data);
                } else {
                    const resPost = await apiFetch('/chart-libraries', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(defaultLibraries[0])
                    });
                    if (resPost.ok) {
                        setLibraries([await resPost.json(), ...defaultLibraries.slice(1)]);
                    }
                }
            }
        } catch (err) {
            console.error('Error loading libraries:', err);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchLibraries();
    }, [fetchLibraries]);

    const handleToggleActive = async (record) => {
        setSaving(true);
        try {
            const res = await apiFetch(`/chart-libraries/${record.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ is_active: !record.is_active }),
            });
            if (res.ok) {
                setLibraries(prev => prev.map(lib => 
                    lib.id === record.id ? { ...lib, is_active: !lib.is_active } : lib
                ));
                message.success('Libreria aggiornata');
            }
        } catch (err) {
            message.error('Errore nell\'aggiornamento');
        } finally {
            setSaving(false);
        }
    };

    const handleSetDefault = async (record) => {
        setSaving(true);
        try {
            const updatedLibs = libraries.map(lib => ({
                ...lib,
                is_default: lib.id === record.id
            }));

            for (const lib of updatedLibs) {
                await apiFetch(`/chart-libraries/${lib.id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ is_default: lib.is_default }),
                });
            }

            setLibraries(updatedLibs);
            message.success('Libreria predefinita aggiornata');
        } catch (err) {
            message.error('Errore nell\'aggiornamento');
        } finally {
            setSaving(false);
        }
    };

    const columns = [
        {
            title: 'Libreria',
            dataIndex: 'library_name',
            key: 'library_name',
            render: (name) => (
                <Tag color="blue">{CHART_LIBRARY_LABELS[name] || name}</Tag>
            ),
        },
        {
            title: 'Stato',
            dataIndex: 'is_active',
            key: 'is_active',
            render: (active, record) => (
                <Switch
                    checked={active}
                    loading={saving}
                    onChange={() => handleToggleActive(record)}
                    checkedChildren="Attiva"
                    unCheckedChildren="Disattiva"
                />
            ),
        },
        {
            title: 'Predefinita',
            dataIndex: 'is_default',
            key: 'is_default',
            render: (isDefault, record) => (
                <Radio
                    checked={isDefault}
                    onChange={() => handleSetDefault(record)}
                    disabled={saving || !record.is_active}
                />
            ),
        },
    ];

    return (
        <Table
            dataSource={libraries}
            columns={columns}
            rowKey="id"
            loading={loading}
            pagination={false}
            size="small"
        />
    );
}

export default ProjectSettingsPage;
