/**
 * Visual Builder - Generic UI Builder
 */

import React, { useState, useCallback, useEffect } from 'react';
import {
  Layout,
  Button,
  Space,
  Typography,
  message,
  Spin,
  Alert
} from 'antd';
import {
  SaveOutlined,
  ArrowLeftOutlined,
  EyeOutlined,
  CodeOutlined
} from '@ant-design/icons';
import {
  DndContext,
  PointerSensor,
  useSensor,
  useSensors
} from '@dnd-kit/core';

import BuilderPalette from './BuilderPalette';
import BuilderCanvas from './BuilderCanvas';
import PropertyPanel from './PropertyPanel';
import { registry } from '@/components/core';

const { Header, Sider, Content } = Layout;
const { Title } = Typography;

const GRID_SIZE = 32;

const VisualBuilder = ({
  title = "UI Builder",
  initialComponents = [],
  onSave,
  onBack,
  loading = false,
  extraHeader,
  projectId
}) => {
  const [components, setComponents] = useState(initialComponents);
  const [selectedId, setSelectedId] = useState(null);
  const [activeId, setActiveId] = useState(null);
  const [previewMode, setPreviewMode] = useState(false);

  useEffect(() => {
    setComponents(initialComponents);
  }, [initialComponents]);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 5,
      },
    })
  );

  const handleDragStart = (event) => {
    setActiveId(event.active.id);
  };

  const handleDragEnd = (event) => {
    const { active, over, delta } = event;
    setActiveId(null);

    // Handle adding new component from palette
    if (active.id.toString().startsWith('palette-')) {
      if (!over || over.id !== 'builder-canvas') return;

      const type = active.data.current.componentType;
      const archetype = registry.get(type);

      // Snap drop position to grid
      const rect = over.rect;
      const dropX = event.activatorEvent.clientX + delta.x;
      const dropY = event.activatorEvent.clientY + delta.y;

      const x = Math.round((dropX - rect.left) / GRID_SIZE) * GRID_SIZE;
      const y = Math.round((dropY - rect.top) / GRID_SIZE) * GRID_SIZE;

      const newComponent = {
        id: `comp_${Date.now()}`,
        type: type,
        name: `${archetype.title || type} ${components.length + 1}`,
        config: { ...archetype.defaultConfig },
        x: x || 0,
        y: y || 0,
        w: 320,
        h: 200
      };

      setComponents([...components, newComponent]);
      setSelectedId(newComponent.id);
      return;
    }

    // Handle moving component on canvas
    if (delta && (delta.x !== 0 || delta.y !== 0)) {
      setComponents((items) => {
        return items.map(item => {
          if (item.id === active.id) {
            return {
              ...item,
              x: Math.round((item.x + delta.x) / GRID_SIZE) * GRID_SIZE,
              y: Math.round((item.y + delta.y) / GRID_SIZE) * GRID_SIZE,
            };
          }
          return item;
        });
      });
    }
  };

  const handleDelete = (id) => {
    setComponents(components.filter(c => c.id !== id));
    if (selectedId === id) setSelectedId(null);
  };

  const handleUpdateComponent = (updatedComp) => {
    setComponents(components.map(c => c.id === updatedComp.id ? updatedComp : c));
  };

  const handleSave = () => {
    if (onSave) {
      onSave(components);
    }
  };

  const selectedComponent = components.find(c => c.id === selectedId);

  if (loading) return <div className="text-center p-5"><Spin size="large" /></div>;

  return (
    <DndContext
      sensors={sensors}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
    >
      <Layout style={{ height: '100vh', background: '#fff' }}>
        <Header style={{ background: '#fff', borderBottom: '1px solid #f0f0f0', padding: '0 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Space>
            <Button icon={<ArrowLeftOutlined />} onClick={onBack} />
            <Title level={4} style={{ margin: 0 }}>{title}</Title>
          </Space>
          <Space>
            {extraHeader}
            <Button
              icon={previewMode ? <CodeOutlined /> : <EyeOutlined />}
              onClick={() => setPreviewMode(!previewMode)}
            >
              {previewMode ? 'Designer' : 'Preview'}
            </Button>
            <Button type="primary" icon={<SaveOutlined />} onClick={handleSave}>
              Save
            </Button>
          </Space>
        </Header>

        <Layout>
          {!previewMode && (
            <Sider width={250} theme="light" style={{ borderRight: '1px solid #f0f0f0', overflow: 'auto' }}>
              <BuilderPalette />
            </Sider>
          )}

          <Content style={{ overflow: 'auto', background: '#f5f5f5', position: 'relative' }}>
            <div style={{ padding: 24 }}>
              {previewMode && (
                <Alert
                  message="Preview Mode"
                  description="This is how your block will look to users."
                  type="info"
                  showIcon
                  style={{ marginBottom: 16 }}
                />
              )}
              <BuilderCanvas
                components={components}
                selectedId={selectedId}
                onSelect={setSelectedId}
                onDelete={handleDelete}
                previewMode={previewMode}
                projectId={projectId}
              />
            </div>
          </Content>

          {!previewMode && (
            <Sider width={300} theme="light" style={{ borderLeft: '1px solid #f0f0f0', overflow: 'auto' }}>
              <PropertyPanel
                component={selectedComponent}
                onChange={handleUpdateComponent}
                projectId={projectId}
              />
            </Sider>
          )}
        </Layout>
      </Layout>
    </DndContext>
  );
};

export default VisualBuilder;
