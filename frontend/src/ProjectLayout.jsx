import React, { useEffect, useState } from 'react';
import { useParams, Outlet } from 'react-router-dom';
import { Layout as AntLayout, Spin, theme } from 'antd';
import { apiFetch } from '@/utils';
import Sidebar from '@/components/Sidebar';
import AppHeader from '@/components/AppHeader';
import { useTheme } from '@/context';

const { Sider, Content } = AntLayout;

const ProjectLayout = () => {
    const { projectId } = useParams();
    const { themeConfig } = useTheme();
    const [projectMenuItems, setProjectMenuItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [projectTitle, setProjectTitle] = useState('');

    useEffect(() => {
        if (projectId) {
            setLoading(true);
            Promise.all([
                apiFetch(`/projects/${projectId}/models`),
                apiFetch(`/projects/${projectId}`)
            ])
                .then(([modelsRes, projectRes]) => {
                    if (!modelsRes.ok) throw new Error('Failed to fetch project models');
                    if (!projectRes.ok) throw new Error('Failed to fetch project');
                    return Promise.all([modelsRes.json(), projectRes.json()]);
                })
                .then(([models, project]) => {
                    const menuItems = models.map(model => ({
                        key: model.name,
                        label: model.title,
                        path: `/projects/${projectId}/data/${model.name}`
                    }));
                    setProjectMenuItems(menuItems);
                    setProjectTitle(project.title);
                })
                .catch(error => console.error("Error fetching project:", error))
                .finally(() => setLoading(false));
        }
    }, [projectId]);

    const { token } = theme.useToken();

    const breadcrumbs = [
        { title: <a onClick={() => window.location.href = '/projects'}>Progetti</a> },
        { title: projectTitle || '...' }
    ];

    return (
        <AntLayout style={{ minHeight: '100vh' }}>
            <Sider
                width={250}
                theme={themeConfig.mode === 'dark' ? 'dark' : 'light'}
                style={{
                    position: 'sticky',
                    top: 0,
                    height: '100vh',
                    boxShadow: '2px 0 8px 0 rgba(29,35,41,.05)'
                }}
            >
                <Sidebar projectMenuItems={projectMenuItems} />
            </Sider>
            <AntLayout>
                <Content style={{
                    margin: 0,
                    padding: 0,
                    background: themeConfig.mode === 'dark' ? token.colorBgContainer : '#fff',
                    minHeight: 280,
                }}>
                    <AppHeader breadcrumbs={breadcrumbs} />
                    <div style={{ padding: 24 }}>
                        {loading ? <div style={{textAlign: 'center', paddingTop: 50}}><Spin size="large" /></div> : <Outlet context={{ projectTitle, projectId }} />}
                    </div>
                </Content>
            </AntLayout>
        </AntLayout>
    );
};

export default ProjectLayout;