import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { List, Avatar, Button, Typography, Spin, Alert, Modal, Input, Select, Radio, Row, Col, Card, message } from 'antd';
import { PlusOutlined, ProjectOutlined, AppstoreOutlined, UnorderedListOutlined, DownloadOutlined, EditOutlined } from '@ant-design/icons';
import { apiFetch } from '../utils';
import { useAuth } from '../context';
import ProjectForm from '../components/ProjectForm';
import ImportProjectButton from '../components/ImportProjectButton';

const { Title, Paragraph, Text } = Typography;
const { Option } = Select;

const ProjectSelectionPage = () => {
    const [projects, setProjects] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const navigate = useNavigate();
    const { user } = useAuth();
    const [editingProject, setEditingProject] = useState(null);
    const [isModalVisible, setIsModalVisible] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const [sortOrder, setSortOrder] = useState('title_asc');
    const [viewMode, setViewMode] = useState(localStorage.getItem('projectViewMode') || 'list');

    const fetchProjects = useCallback(async () => {
        setLoading(true);
        try {
            const response = await apiFetch('/projects');                
            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.message || "Unable to load projects.");
            }
            const data = await response.json();
            setProjects(data);
        } catch (err) {
            setError("Server connection error.");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchProjects();
    }, [fetchProjects]);

    useEffect(() => {
        localStorage.setItem('projectViewMode', viewMode);
    }, [viewMode]);

    const handleSelectProject = (projectId) => {
        navigate(`/projects/${projectId}`);
    };

    const handleShowModal = (project = null) => {
        setEditingProject(project);
        setIsModalVisible(true);
    };

    const handleModalClose = () => {
        setIsModalVisible(false);
        setEditingProject(null);
    };

    const handleFormSuccess = () => {
        handleModalClose();
        fetchProjects();
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

    const filteredAndSortedProjects = projects
        .filter(project =>
            project.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
            (project.description && project.description.toLowerCase().includes(searchTerm.toLowerCase())) ||
            project.name.toLowerCase().includes(searchTerm.toLowerCase())
        )
        .sort((a, b) => {
            switch (sortOrder) {
                case 'title_desc':
                    return b.title.localeCompare(a.title);
                case 'date_desc':
                    return new Date(b.created_at) - new Date(a.created_at);
                case 'date_asc':
                    return new Date(a.created_at) - new Date(b.created_at);
                default: // title_asc
                    return a.title.localeCompare(b.title);
            }
        });

    const handleViewChange = (e) => {
        setViewMode(e.target.value);
    };

    if (loading) {
        return (
            <Spin size="large" tip="Loading projects..." fullscreen />
        );
    }

    return (
        <div style={{ padding: '40px', maxWidth: '1200px', margin: '0 auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '40px' }}>
                <Title level={2} style={{ margin: 0 }}>
                    Select a Project
                </Title>
                <div style={{ display: 'flex', gap: '16px' }}>
                    <Radio.Group value={viewMode} onChange={handleViewChange}>
                        <Radio.Button value="list"><UnorderedListOutlined /></Radio.Button>
                        <Radio.Button value="grid"><AppstoreOutlined /></Radio.Button>
                    </Radio.Group>
                    <Select
                        value={sortOrder}
                        onChange={setSortOrder}
                        style={{ width: 180 }}
                    >
                        <Option value="title_asc">Sort by Title (A-Z)</Option>
                        <Option value="title_desc">Sort by Title (Z-A)</Option>
                        <Option value="date_desc">Most Recent</Option>
                        <Option value="date_asc">Least Recent</Option>
                    </Select>
                    <Input.Search
                        placeholder="Search project..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        style={{ width: 250 }}
                    />
                    {user?.role === 'admin' && (
                        <>
                            <ImportProjectButton onSuccess={fetchProjects} />
                            <Button type="primary" icon={<PlusOutlined />} onClick={handleShowModal}>
                                Create Project
                            </Button>
                        </>
                    )}
                </div>
            </div>

            {error && (
                <Alert 
                    message="Error" 
                    description={error} 
                    type="error" 
                    showIcon 
                    style={{ marginBottom: '20px' }} 
                />
            )}

            {filteredAndSortedProjects.length > 0 ? (
                viewMode === 'list' ? (
                    <List
                    itemLayout="horizontal"
                    dataSource={filteredAndSortedProjects}
                    renderItem={(project) => (
                        <List.Item
                            actions={[
                                user?.role === 'admin' && (
                                    <>
                                        <Button icon={<EditOutlined />} onClick={() => handleShowModal(project)}>
                                            Edit
                                        </Button>
                                        <Button icon={<DownloadOutlined />} onClick={() => handleExport(project)}>
                                            Export
                                        </Button>
                                    </>
                                ),
                                <Button type="primary" onClick={() => project.id && handleSelectProject(project.id)} disabled={!project.id}>
                                    Open
                                </Button>,
                            ].filter(Boolean)}
                        >
                            <List.Item.Meta
                                avatar={<Avatar shape="square" size="large" icon={<ProjectOutlined />} />}
                                title={<a onClick={() => handleSelectProject(project.id)}>{project.title}</a>}
                                description={project.description || "No description available."}
                            />
                            <div style={{ textAlign: 'right', marginLeft: 24, flexShrink: 0 }}>
                                <Text type="secondary" style={{ fontSize: '12px' }}>Version</Text>
                                <br />
                                <Text>{project.version}</Text>
                            </div>
                        </List.Item>
                    )}
                    />
                ) : (
                    <Row gutter={[24, 24]}>
                        {filteredAndSortedProjects.map((project) => (
                            <Col xs={24} sm={12} md={8} lg={6} key={project.id}>
                                <Card
                                    hoverable
                                    title={project.title}
                                    style={{ height: '100%', display: 'flex', flexDirection: 'column' }}
                                    styles={{ body: { flex: 1, display: 'flex', flexDirection: 'column' } }}
                                    actions={[
                                        user?.role === 'admin' && (
                                            <>
                                                <Button icon={<EditOutlined />} onClick={() => handleShowModal(project)}>
                                                    Edit
                                                </Button>
                                                <Button icon={<DownloadOutlined />} onClick={() => handleExport(project)}>
                                                    Export
                                                </Button>
                                            </>
                                        ),
                                        <Button type="primary" block onClick={() => project.id && handleSelectProject(project.id)} disabled={!project.id}>
                                            Open Project
                                        </Button>
                                    ].filter(Boolean)}
                                >
                                    <Paragraph ellipsis={{ rows: 3, expandable: false }}>
                                        {project.description || "No description available."}
                                    </Paragraph>
                                    <div style={{ marginTop: 'auto' }}>
                                        <Text type="secondary" style={{ fontSize: '12px' }}>
                                            Version: {project.version}
                                        </Text>
                                    </div>
                                </Card>
                            </Col>
                        ))}
                    </Row>
                )
            ) : (
                !loading && !error && (
                    <div style={{ textAlign: 'center', padding: '40px', background: '#f5f5f5', borderRadius: '8px' }}>
                        <Title level={4}>No projects available</Title>
                        <Paragraph>There are no visible projects that match your search.</Paragraph>
                    </div>
                )
            )}

            <Modal
                title={editingProject ? "Edit Project" : "Create New Project"}
                open={isModalVisible}
                onCancel={handleModalClose}
                footer={null}
            >
                <ProjectForm project={editingProject} onSuccess={handleFormSuccess} onCancel={handleModalClose} />
            </Modal>
        </div>
    );
};

export default ProjectSelectionPage;
