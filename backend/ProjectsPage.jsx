import React, { useState, useEffect, useCallback } from 'react';
import { Modal, Button, Table, Space, message, Popconfirm } from 'antd';
import ProjectForm from '../components/ProjectForm';
import ImportProjectButton from './ImportProjectButton';
import { apiFetch } from '../utils/api'; // Assuming you have an API helper

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
                message.error('Error loading projects.');
            }
        } catch (error) {
            message.error('An error occurred while loading projects.');
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
                message.success('Project deleted successfully');
                fetchProjects(); // Refresh the list
            } else {
                const errorData = await response.json();
                message.error(errorData.message || 'Error deleting the project.');
            }
        } catch (error) {
            message.error('An error occurred while deleting the project.');
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
                message.success(`Template for '${project.title}' exported.`);
            } else {
                message.error('Error exporting the template.');
            }
        } catch (error) {
            message.error('An error occurred while exporting the template.');
        }
    };

    const handleModalClose = () => {
        setIsModalVisible(false);
        setEditingProject(null);
    };

    const handleFormSuccess = () => {
        handleModalClose();
        fetchProjects(); // Refresh the list after success
    };

    const columns = [
        { title: 'Internal Name', dataIndex: 'name', key: 'name', sorter: (a, b) => a.name.localeCompare(b.name) },
        { title: 'Title', dataIndex: 'title', key: 'title' },
        { title: 'Version', dataIndex: 'version', key: 'version' },
        { title: 'Owner', dataIndex: ['owner', 'email'], key: 'owner' },
        {
            title: 'Action',
            key: 'action',
            render: (_, record) => (
                <Space size="middle">
                    <Button type="link" onClick={() => handleEdit(record)}>Edit</Button>
                    <Button type="link" onClick={() => handleExport(record)}>Export</Button>
                    <Popconfirm
                        title="Delete the project"
                        description="Are you sure you want to delete this project? This action is irreversible."
                        onConfirm={() => handleDelete(record.id)}
                        okText="Yes"
                        cancelText="No"
                    >
                        <Button type="link" danger>Delete</Button>
                    </Popconfirm>
                </Space>
            ),
        },
    ];

    return (
        <div>
            <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h1>Project Management</h1>
                <Space>
                    <ImportProjectButton onSuccess={fetchProjects} />
                    <Button type="primary" onClick={handleCreate}>
                        Create New Project
                    </Button>
                </Space>
            </div>
            <Table columns={columns} dataSource={projects} rowKey="id" loading={loading} />
            <Modal
                title={editingProject ? 'Edit Project' : 'Create New Project'}
                open={isModalVisible}
                onCancel={handleModalClose}
                footer={null} // The footer is managed by the form
            >
                <ProjectForm project={editingProject} onSuccess={handleFormSuccess} onCancel={handleModalClose} />
            </Modal>
        </div>
    );
};

export default ProjectsPage;
