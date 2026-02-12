import React, { useEffect, useState } from 'react';
import { useParams, Outlet } from 'react-router-dom';
import { Layout as AntLayout, Spin } from 'antd';
import { apiFetch } from '@/utils';
import Sidebar from '@/components/Sidebar';

const { Sider, Content } = AntLayout;

const ProjectLayout = () => {
    const { projectId } = useParams();
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

    return (
        <AntLayout style={{ minHeight: '100vh' }}>
            <Sider width={250} theme="dark" style={{ position: 'sticky', top: 0, height: '100vh' }}>
                <Sidebar projectMenuItems={projectMenuItems} />
            </Sider>
            <AntLayout>
                <Content style={{ margin: '24px 16px', padding: 24, background: '#fff', minHeight: 280 }}>
                    {loading ? <div style={{textAlign: 'center', paddingTop: 50}}><Spin size="large" /></div> : <Outlet />}
                </Content>
            </AntLayout>
        </AntLayout>
    );
};

export default ProjectLayout;