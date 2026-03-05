/**
 * Builder Canvas - Main editing area for Visual Builder
 */

import React from 'react';
import { Empty, Card, Button, Space } from 'antd';
import { DeleteOutlined, SettingOutlined, HolderOutlined } from '@ant-design/icons';
import {
  useDroppable,
  DndContext,
  closestCenter,
  PointerSensor,
  useSensor,
  useSensors
} from '@dnd-kit/core';
import {
  SortableContext,
  verticalListSortingStrategy,
  useSortable
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { ComponentRenderer } from '@/components/core';

const SortableComponentWrapper = ({
  id,
  component,
  isSelected,
  onSelect,
  onDelete,
  onSettings
}) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging
  } = useSortable({ id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    marginBottom: 16,
    position: 'relative',
    opacity: isDragging ? 0.5 : 1,
    zIndex: isDragging ? 100 : 1,
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
          border: isSelected ? '2px solid #1677ff' : '1px solid #d9d9d9',
          boxShadow: isSelected ? '0 0 8px rgba(22, 119, 255, 0.2)' : 'none'
        }}
        title={
          <div className="d-flex justify-content-between align-items-center">
            <Space>
              <div {...listeners} {...attributes} style={{ cursor: 'grab', padding: '0 4px' }}>
                <HolderOutlined />
              </div>
              <span>{component.name || component.type}</span>
            </Space>
            <Space>
              <Button
                type="text"
                size="small"
                icon={<SettingOutlined />}
                onClick={(e) => { e.stopPropagation(); onSettings(id); }}
              />
              <Button
                type="text"
                size="small"
                danger
                icon={<DeleteOutlined />}
                onClick={(e) => { e.stopPropagation(); onDelete(id); }}
              />
            </Space>
          </div>
        }
      >
        <div style={{ pointerEvents: 'none', minHeight: 40 }}>
          <ComponentRenderer
            type={component.type}
            config={component.config}
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
  onReorder
}) => {
  const { setNodeRef, isOver } = useDroppable({
    id: 'builder-canvas',
  });

  const style = {
    minHeight: 'calc(100vh - 160px)',
    padding: 24,
    background: isOver ? '#f0f5ff' : '#f5f5f5',
    border: isOver ? '2px dashed #1677ff' : '2px solid transparent',
    borderRadius: 8,
    transition: 'all 0.2s',
  };

  return (
    <div ref={setNodeRef} style={style} onClick={() => onSelect(null)}>
      {components.length === 0 ? (
        <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Empty description="Drag components from the palette to start building" />
        </div>
      ) : (
        <SortableContext
          items={components.map(c => c.id)}
          strategy={verticalListSortingStrategy}
        >
          {components.map((comp) => (
            <SortableComponentWrapper
              key={comp.id}
              id={comp.id}
              component={comp}
              isSelected={selectedId === comp.id}
              onSelect={onSelect}
              onDelete={onDelete}
              onSettings={onSelect}
            />
          ))}
        </SortableContext>
      )}
    </div>
  );
};

export default BuilderCanvas;
