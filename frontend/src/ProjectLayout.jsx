import React, { useEffect, useState } from 'react';
import { useParams, Outlet } from 'react-router-dom';
import { Layout as AntLayout, Spin, theme } from 'antd';
import { apiFetch } from '@/utils';
import Sidebar from '@/components/Sidebar';
import { useTheme } from '@/context';

const { Sider, Content } = AntLayout;

const ProjectLayout = () => {
    const { projectId } = useParams();
    const { themeConfig } = useTheme();
    const [projectMenuItems, setProjectMenuItems] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (projectId) {
            setLoading(true);
            apiFetch(`/projects/${projectId}/models`)
                .then(response => {
                    if (!response.ok) throw new Error('Failed to fetch project models');
                    return response.json();
                })
                .then(data => {
                    const menuItems = data.map(model => ({
                        key: model.name,
                        label: model.title,
                        path: `/projects/${projectId}/data/${model.name}`
                    }));
                    setProjectMenuItems(menuItems);
                })
                .catch(error => console.error("Error fetching project models:", error))
                .finally(() => setLoading(false));
        }
    }, [projectId]);

    const { token } = theme.useToken();

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
                    margin: '24px 16px',
                    padding: 24,
                    background: themeConfig.mode === 'dark' ? token.colorBgContainer : '#fff',
                    minHeight: 280,
                    borderRadius: themeConfig.borderRadius
                }}>
                    {loading ? <div style={{textAlign: 'center', paddingTop: 50}}><Spin size="large" /></div> : <Outlet />}
                </Content>
            </AntLayout>
        </AntLayout>
    );
};

export default ProjectLayout;