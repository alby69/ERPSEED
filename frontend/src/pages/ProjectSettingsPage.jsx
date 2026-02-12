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
                throw new Error(err.message || "Impossibile caricare i dettagli del progetto.");
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
                throw new Error(err.message || "Errore durante il salvataggio.");
            }
            message.success("Impostazioni del progetto salvate con successo!");
        } catch (err) {
            message.error(err.message);
        } finally {
            setSaving(false);
        }
    };

    const handleDeleteProject = () => {
        Modal.confirm({
            title: 'Sei assolutamente sicuro?',
            icon: <ExclamationCircleOutlined />,
            content: (
                <div>
                    <p>Questa azione è irreversibile e non può essere annullata.</p>
                    <p>Verranno eliminati permanentemente il progetto <strong>{project.title}</strong>, tutti i suoi modelli, i campi e <strong>TUTTI I DATI</strong> associati.</p>
                    <p className="mt-3">Per confermare, digita il nome del progetto: <strong>{project.name}</strong></p>
                    <Input id="delete-confirm-input" placeholder={project.name} />
                </div>
            ),
            okText: 'Sì, elimina questo progetto',
            okType: 'danger',
            cancelText: 'Annulla',
            async onOk() {
                const confirmInput = document.getElementById('delete-confirm-input').value;
                if (confirmInput !== project.name) {
                    message.error('Il nome del progetto non corrisponde. Eliminazione annullata.');
                    return Promise.reject('Confirmation text does not match');
                }
                
                try {
                    const response = await apiFetch(`/projects/${projectId}`, { method: 'DELETE' });
                    if (!response.ok) {
                        const err = await response.json();
                        throw new Error(err.message || 'Errore durante l\'eliminazione del progetto.');
                    }
                    message.success('Progetto eliminato con successo.');
                    navigate('/projects'); // Redirect to project selection
                } catch (err) {
                    message.error(err.message);
                    return Promise.reject(err.message);
                }
            },
        });
    };

    if (loading) {
        return <Spin tip="Caricamento impostazioni..." style={{ display: 'block', marginTop: '50px' }} />;
    }

    if (error) {
        return <Alert message="Errore" description={error} type="error" showIcon />;
    }

    return (
        <>
            <Card title="Impostazioni del Progetto">
                <Form form={form} layout="vertical" onFinish={onFinish}>
                    <Form.Item name="title" label="Titolo del Progetto" rules={[{ required: true, message: 'Il titolo è obbligatorio.' }]}>
                        <Input placeholder="Il nome visualizzato del progetto" />
                    </Form.Item>
                    <Form.Item name="description" label="Descrizione">
                        <Input.TextArea rows={4} placeholder="Una breve descrizione del progetto" />
                    </Form.Item>
                    <Form.Item name="version" label="Versione" rules={[{ required: true, message: 'La versione è obbligatoria.' }]}>
                        <Input placeholder="Es. 1.0.1" />
                    </Form.Item>
                    <Form.Item>
                        <Button type="primary" htmlType="submit" loading={saving}>Salva Impostazioni</Button>
                    </Form.Item>
                </Form>
            </Card>

            <Divider />

            <Card title="Danger Zone" styles={{ header: { color: '#cf1322', backgroundColor: '#fff1f0' } }} style={{ borderColor: '#ffccc7' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                        <h5 style={{ color: '#cf1322' }}>Elimina questo progetto</h5>
                        <p className="text-muted mb-0">Una volta eliminato, non c'è modo di tornare indietro. Assicurati.</p>
                    </div>
                    <Button type="primary" danger onClick={handleDeleteProject} disabled={!user || !project || (user.role !== 'admin' && user.id !== project.owner_id)}>
                        Elimina Progetto
                    </Button>
                </div>
            </Card>
        </>
    );
};

export default ProjectSettingsPage;