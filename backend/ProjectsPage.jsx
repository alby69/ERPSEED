import React, { useState, useEffect, useCallback } from 'react';
import { Modal, Button, Table, Space, message, Popconfirm } from 'antd';
import ProjectForm from '../components/ProjectForm';
import ImportProjectButton from './ImportProjectButton';
import { apiFetch } from '../utils/api'; // Assumo che tu abbia un helper per le API

const ProjectsPage = () => {
    const [projects, setProjects] = useState([]);
    const [loading, setLoading] = useState(false);
    const [isModalVisible, setIsModalVisible] = useState(false);
    const [editingProject, setEditingProject] = useState(null);

    const fetchProjects = useCallback(async () => {
        setLoading(true);
        try {
            const response = await apiFetch('/projects');
            if (response.ok) {
                const data = await response.json();
                setProjects(data);
            } else {
                message.error('Errore nel caricamento dei progetti.');
            }
        } catch (error) {
            message.error('Si è verificato un errore durante il caricamento dei progetti.');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchProjects();
    }, [fetchProjects]);

    const handleCreate = () => {
        setEditingProject(null);
        setIsModalVisible(true);
    };

    const handleEdit = (project) => {
        setEditingProject(project);
        setIsModalVisible(true);
    };

    const handleDelete = async (projectId) => {
        try {
            const response = await apiFetch(`/projects/${projectId}`, { method: 'DELETE' });
            if (response.ok) {
                message.success('Progetto eliminato con successo');
                fetchProjects(); // Aggiorna la lista
            } else {
                const errorData = await response.json();
                message.error(errorData.message || 'Errore nell\'eliminazione del progetto.');
            }
        } catch (error) {
            message.error('Si è verificato un errore durante l\'eliminazione del progetto.');
        }
    };

    const handleExport = async (project) => {
        try {
            const response = await apiFetch(`/projects/${project.id}/export`);
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = `${project.name}_template.json`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                a.remove();
                message.success(`Template per '${project.title}' esportato.`);
            } else {
                message.error('Errore nell\'esportazione del template.');
            }
        } catch (error) {
            message.error('Si è verificato un errore durante l\'esportazione del template.');
        }
    };

    const handleModalClose = () => {
        setIsModalVisible(false);
        setEditingProject(null);
    };

    const handleFormSuccess = () => {
        handleModalClose();
        fetchProjects(); // Aggiorna la lista dopo il successo
    };

    const columns = [
        { title: 'Nome Interno', dataIndex: 'name', key: 'name', sorter: (a, b) => a.name.localeCompare(b.name) },
        { title: 'Titolo', dataIndex: 'title', key: 'title' },
        { title: 'Versione', dataIndex: 'version', key: 'version' },
        { title: 'Proprietario', dataIndex: ['owner', 'email'], key: 'owner' },
        {
            title: 'Azione',
            key: 'action',
            render: (_, record) => (
                <Space size="middle">
                    <Button type="link" onClick={() => handleEdit(record)}>Modifica</Button>
                    <Button type="link" onClick={() => handleExport(record)}>Export</Button>
                    <Popconfirm
                        title="Elimina il progetto"
                        description="Sei sicuro di voler eliminare questo progetto? L'azione è irreversibile."
                        onConfirm={() => handleDelete(record.id)}
                        okText="Sì"
                        cancelText="No"
                    >
                        <Button type="link" danger>Elimina</Button>
                    </Popconfirm>
                </Space>
            ),
        },
    ];

    return (
        <div>
            <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h1>Gestione Progetti</h1>
                <Space>
                    <ImportProjectButton onSuccess={fetchProjects} />
                    <Button type="primary" onClick={handleCreate}>
                        Crea Nuovo Progetto
                    </Button>
                </Space>
            </div>
            <Table columns={columns} dataSource={projects} rowKey="id" loading={loading} />
            <Modal
                title={editingProject ? 'Modifica Progetto' : 'Crea Nuovo Progetto'}
                open={isModalVisible}
                onCancel={handleModalClose}
                footer={null} // Il footer è gestito dal form
            >
                <ProjectForm project={editingProject} onSuccess={handleFormSuccess} onCancel={handleModalClose} />
            </Modal>
        </div>
    );
};

export default ProjectsPage;