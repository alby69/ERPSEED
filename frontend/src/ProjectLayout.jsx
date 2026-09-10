import React, { useEffect, useState } from 'react';
import { useParams, Outlet } from 'react-router-dom';
import { Layout as AntLayout, Spin, theme } from 'antd';
import { apiFetch } from '@/utils';
import Sidebar from '@/components/Sidebar';
import AppHeader from '@/components/AppHeader';
import CommandPalette from '@/components/core/CommandPalette';
import useCommandPalette from '@/hooks/useCommandPalette';
import { useTheme } from '@/context';

const { Sider, Content } = AntLayout;

const ProjectLayout = () => {
    const { projectId } = useParams();
    const { themeConfig } = useTheme();
    const [projectMenuItems, setProjectMenuItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [projectTitle, setProjectTitle] = useState('');
    const [collapsed, setCollapsed] = useState(false);
    const { isOpen, close } = useCommandPalette();

    // Global keyboard shortcuts (Ctrl+S / Cmd+S for Save, Esc to close/cancel)
    useEffect(() => {
        const handleGlobalKeyDown = (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 's') {
                e.preventDefault();
                // Find active visible modal/drawer or form submit button
                const activeForm = document.querySelector('.modal.show form, form.active, form');
                if (activeForm) {
                    const submitBtn = activeForm.querySelector('button[type="submit"], input[type="submit"]');
                    if (submitBtn) {
                        submitBtn.click();
                    } else {
                        activeForm.requestSubmit();
                    }
                }
            } else if (e.key === 'Escape') {
                // Trigger cancel on close buttons if modal or drawer open
                const closeBtn = document.querySelector('.modal.show .btn-close, .ant-modal-close, .ant-drawer-close');
                if (closeBtn) {
                    closeBtn.click();
                }
            }
        };

        window.addEventListener('keydown', handleGlobalKeyDown);
        return () => window.removeEventListener('keydown', handleGlobalKeyDown);
    }, []);

    useEffect(() => {
        if (projectId) {
            localStorage.setItem('currentProjectId', projectId);
            setLoading(true);
            Promise.all([
                apiFetch(`/projects/${projectId}/models`),
                apiFetch(`/projects/${projectId}`),
                apiFetch(`/api/v1/modules?projectId=${projectId}&status=published`)
            ])
                .then(([modelsRes, projectRes, modulesRes]) => {
                    if (!modelsRes.ok) throw new Error('Failed to fetch project models');
                    if (!projectRes.ok) throw new Error('Failed to fetch project');
                    return Promise.all([modelsRes.json(), projectRes.json(), modulesRes.json()]);
                })
                .then(([models, project, modulesData]) => {
                    const menuItems = [];

                    // Add published modules (App-like entries)
                    const modules = modulesData.modules || [];
                    modules.forEach(module => {
                        if (module.name === 'gdo_reconciliation') {
                            menuItems.push({
                                key: `module-gdo`,
                                label: module.title || module.name,
                                path: `/projects/${projectId}/gdo-reconciliation`,
                                isModule: true
                            });
                        } else {
                            menuItems.push({
                                key: `module-${module.name}`,
                                label: module.title || module.name,
                                path: `/projects/${projectId}/app/${module.name}`,
                                isModule: true
                            });
                        }
                    });

                    // Group models under the project name
                    menuItems.push({
                        key: `project-${projectId}-workflows`,
                        label: 'Workflows',
                        path: `/projects/${projectId}/workflows`
                    });

                    if (models.length > 0) {
                        menuItems.push({
                            key: `project-${projectId}-models`,
                            label: project.title || project.name,
                            children: models.map(model => ({
                                key: model.name,
                                label: model.title || model.name,
                                path: `/projects/${projectId}/data/${model.name}`
                            }))
                        });
                    }

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
            <CommandPalette isOpen={isOpen} onClose={close} />
            <Sider
                breakpoint="lg"
                collapsedWidth="0"
                onCollapse={(collapsedVal) => setCollapsed(collapsedVal)}
                width={250}
                theme={themeConfig.mode === 'dark' ? 'dark' : 'light'}
                style={{
                    position: 'sticky',
                    top: 0,
                    height: '100vh',
                    boxShadow: '2px 0 8px 0 rgba(29,35,41,.05)',
                    zIndex: 100
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
