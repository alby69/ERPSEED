/**
 * Builder Canvas - Main editing area for Visual Builder (Free Canvas version)
 */

import React from 'react';
import { Empty, Card, Button, Space } from 'antd';
import { DeleteOutlined, DragOutlined } from '@ant-design/icons';
import { useDraggable, useDroppable } from '@dnd-kit/core';
import { ComponentRenderer } from '@/components/core';

const GRID_SIZE = 32;

const DraggableComponent = ({
  id,
  component,
  isSelected,
  onSelect,
  onDelete,
  previewMode,
  projectId
}) => {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: id,
    data: component
  });

  const style = {
    position: 'absolute',
    left: component.x || 0,
    top: component.y || 0,
    width: component.w || 300,
    height: component.h || 'auto',
    transform: transform ? `translate3d(${transform.x}px, ${transform.y}px, 0)` : undefined,
    zIndex: isDragging ? 1000 : (isSelected ? 100 : 1),
    opacity: isDragging ? 0.6 : 1,
    cursor: previewMode ? 'default' : 'auto',
  };

  // Mock context for preview mode
  const mockContext = {
    user: { name: 'Mario Rossi', role: 'admin' },
    company: { name: 'Esempio s.r.l.' },
    now: new Date().toISOString()
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      onClick={(e) => {
        e.stopPropagation();
        onSelect(id);
      }}
    >
      <Card
        size="small"
        className={`builder-component-card ${isSelected ? 'selected' : ''}`}
        style={{
          height: '100%',
          border: isSelected ? '2px solid #1677ff' : '1px solid #d9d9d9',
          boxShadow: isSelected ? '0 0 8px rgba(22, 119, 255, 0.2)' : 'none',
          display: 'flex',
          flexDirection: 'column'
        }}
        bodyStyle={{ flex: 1, overflow: 'auto', padding: 8 }}
        title={
          !previewMode ? (
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Space>
                <div {...listeners} {...attributes} style={{ cursor: 'grab', display: 'flex' }}>
                  <DragOutlined />
                </div>
                <span style={{ fontSize: 12 }}>{component.name || component.type}</span>
              </Space>
              <Space>
                <Button
                  type="text"
                  size="small"
                  danger
                  icon={<DeleteOutlined style={{ fontSize: 12 }} />}
                  onClick={(e) => { e.stopPropagation(); onDelete(id); }}
                />
              </Space>
            </div>
          ) : null
        }
      >
        <div style={{ pointerEvents: previewMode ? 'auto' : 'none' }}>
          <ComponentRenderer
            type={component.type}
            config={component.config}
            context={mockContext}
            projectId={projectId}
            modelId={component.modelId}
          />
        </div>
      </Card>
    </div>
  );
};

const BuilderCanvas = ({
  components = [],
  selectedId,
  onSelect,
  onDelete,
  previewMode,
  projectId
}) => {
  const { setNodeRef, isOver } = useDroppable({
    id: 'builder-canvas',
  });

  const canvasStyle = {
    width: '100%',
    minHeight: '800px',
    position: 'relative',
    background: previewMode ? '#fff' : (isOver ? '#f0f5ff' : '#fafafa'),
    backgroundImage: previewMode ? 'none' : `
      linear-gradient(to right, #eee 1px, transparent 1px),
      linear-gradient(to bottom, #eee 1px, transparent 1px)
    `,
    backgroundSize: `${GRID_SIZE}px ${GRID_SIZE}px`,
    border: previewMode ? '1px solid #f0f0f0' : (isOver ? '2px dashed #1677ff' : '1px solid #d9d9d9'),
    borderRadius: 8,
    transition: 'background-color 0.2s',
    overflow: 'hidden'
  };

  return (
    <div
      ref={setNodeRef}
      style={canvasStyle}
      onClick={() => onSelect(null)}
    >
      {components.length === 0 && !previewMode ? (
        <div style={{ height: '400px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Empty description="Drag components from the palette to start building" />
        </div>
      ) : (
        components.map((comp) => (
          <DraggableComponent
            key={comp.id}
            id={comp.id}
            component={comp}
            isSelected={selectedId === comp.id}
            onSelect={onSelect}
            onDelete={onDelete}
            previewMode={previewMode}
            projectId={projectId}
          />
        ))
      )}
    </div>
  );
};

export default BuilderCanvas;
