/**
 * Builder Palette - Component Selector for Visual Builder
 */

import React from 'react';
import { Card, Typography, Space, Tooltip } from 'antd';
import * as Icons from '@ant-design/icons';
import { useDraggable } from '@dnd-kit/core';
import { registry } from '@/components/core';

const { Text } = Typography;

const DraggableItem = ({ type, archetype }) => {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: `palette-${type}`,
    data: {
      type: 'palette-item',
      componentType: type,
    },
  });

  const IconComponent = Icons[archetype.icon] || Icons.AppstoreOutlined;

  const style = {
    transform: transform ? `translate3d(${transform.x}px, ${transform.y}px, 0)` : undefined,
    opacity: isDragging ? 0.5 : 1,
    cursor: 'grab',
    marginBottom: 8,
    border: '1px solid #d9d9d9',
    borderRadius: 4,
    padding: '8px 12px',
    background: '#fff',
    display: 'flex',
    alignItems: 'center',
    zIndex: isDragging ? 1000 : 1,
  };

  return (
    <div ref={setNodeRef} style={style} {...listeners} {...attributes}>
      <Tooltip title={archetype.description} placement="right">
        <Space>
          <IconComponent />
          <Text>{archetype.title || archetype.name}</Text>
        </Space>
      </Tooltip>
    </div>
  );
};

const BuilderPalette = () => {
  const archetypes = registry.getAll();
  const categories = {};

  Object.entries(archetypes).forEach(([type, arch]) => {
    const cat = arch.category || 'Basic';
    if (!categories[cat]) categories[cat] = [];
    categories[cat].push({ type, arch });
  });

  return (
    <div className="builder-palette" style={{ padding: 16 }}>
      <Typography.Title level={5}>Components</Typography.Title>
      {Object.entries(categories).map(([cat, items]) => (
        <div key={cat} style={{ marginBottom: 16 }}>
          <Typography.Title level={5} type="secondary" style={{ fontSize: 12, textTransform: 'uppercase' }}>
            {cat}
          </Typography.Title>
          {items.map(({ type, arch }) => (
            <DraggableItem key={type} type={type} archetype={arch} />
          ))}
        </div>
      ))}
    </div>
  );
};

export default BuilderPalette;
