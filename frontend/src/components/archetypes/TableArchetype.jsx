/**
 * Table Archetype
 * 
 * Data table component with sorting, filtering, pagination, and drag & drop columns
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Table, Input, Select, Button, Space } from 'antd';
import { SearchOutlined, FilterOutlined, SortAscendingOutlined } from '@ant-design/icons';
import { useSortable } from '@dnd-kit/sortable';
import { DndContext, closestCenter, KeyboardSensor, PointerSensor, useSensor, useSensors } from '@dnd-kit/core';
import { arrayMove, SortableContext, sortableKeyboardCoordinates, horizontalListSortingStrategy } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { apiFetch } from '@/utils';

// Sortable column header
const SortableHeaderCell = ({ column, onResize, ...props }) => {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ 
    id: column.dataIndex 
  });

  const style = {
    ...props.style,
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
    cursor: 'grab',
    position: 'relative',
  };

  return (
    <th ref={setNodeRef} style={style} {...attributes} {...listeners}>
      <div className="d-flex align-items-center">
        <span>{column.title}</span>
      </div>
    </th>
  );
};

// Drag handle wrapper
const DragHandle = ({ column }) => {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: column.dataIndex,
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    cursor: 'grab',
    marginRight: 8,
  };

  return (
    <span ref={setNodeRef} style={style} {...attributes} {...listeners}>
      ≡
    </span>
  );
};

const TableArchetype = ({ 
  config = {}, 
  data = null, 
  onChange,
  projectId,
  modelName,
  ...props 
}) => {
  const [columns, setColumns] = useState(config.columns || []);
  const [loading, setLoading] = useState(false);
  const [tableData, setTableData] = useState([]);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: config.pageSize || 10,
    total: 0,
  });
  const [sortInfo, setSortInfo] = useState({ field: null, order: null });
  const [filters, setFilters] = useState({});
  const [searchText, setSearchText] = useState('');

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  // Load data from API
  const loadData = useCallback(async () => {
    if (!projectId || !modelName) return;
    
    setLoading(true);
    try {
      const params = new URLSearchParams();
      params.append('page', pagination.current);
      params.append('per_page', pagination.pageSize);
      
      if (sortInfo.field) {
        params.append('sort_by', sortInfo.field);
        params.append('sort_order', sortInfo.order);
      }
      
      if (searchText) {
        params.append('q', searchText);
      }

      const response = await apiFetch(`/projects/${projectId}/data/${modelName}?${params}`);
      if (response.ok) {
        const result = await response.json();
        setTableData(result.items || []);
        setPagination(prev => ({ ...prev, total: result.total || 0 }));
      }
    } catch (error) {
      console.error('Error loading table data:', error);
    } finally {
      setLoading(false);
    }
  }, [projectId, modelName, pagination.current, pagination.pageSize, sortInfo, searchText]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Handle column reordering
  const handleDragEnd = (event) => {
    const { active, over } = event;
    if (active.id !== over.id) {
      setColumns((items) => {
        const oldIndex = items.findIndex(i => i.dataIndex === active.id);
        const newIndex = items.findIndex(i => i.dataIndex === over.id);
        const newColumns = arrayMove(items, oldIndex, newIndex);
        
        // Notify parent of config change
        if (onChange) {
          onChange({ ...config, columns: newColumns });
        }
        
        return newColumns;
      });
    }
  };

  // Handle sorting
  const handleTableChange = (newPagination, tableFilters, sorter) => {
    setPagination(prev => ({ ...prev, ...newPagination }));
    
    if (sorter.field) {
      setSortInfo({ field: sorter.field, order: sorter.order === 'ascend' ? 'asc' : 'desc' });
    } else {
      setSortInfo({ field: null, order: null });
    }
  };

  // Handle search
  const handleSearch = (value) => {
    setSearchText(value);
    setPagination(prev => ({ ...prev, current: 1 }));
  };

  // Build columns for Ant Design Table
  const tableColumns = columns.map(col => ({
    ...col,
    sorter: config.sortable !== false && col.sortable !== false,
    filterable: config.filterable !== false && col.filterable !== false,
  }));

  return (
    <div className="table-archetype">
      {/* Search and Filter Bar */}
      <div className="mb-3 d-flex justify-content-between align-items-center">
        <Space>
          <Input.Search
            placeholder="Search..."
            allowClear
            onSearch={handleSearch}
            style={{ width: 250 }}
            prefix={<SearchOutlined />}
          />
        </Space>
        <Space>
          {config.draggable !== false && (
            <Button icon={<SortAscendingOutlined />} title="Drag columns to reorder">
              Reorder
            </Button>
          )}
        </Space>
      </div>

      {/* Draggable Table */}
      <DndContext 
        sensors={sensors} 
        collisionDetection={closestCenter} 
        onDragEnd={handleDragEnd}
      >
        <SortableContext 
          items={tableColumns.map(c => c.dataIndex)} 
          strategy={horizontalListSortingStrategy}
        >
          <Table
            columns={tableColumns}
            dataSource={tableData}
            loading={loading}
            pagination={{
              ...pagination,
              onChange: (page, pageSize) => setPagination(prev => ({ ...prev, current: page, pageSize })),
            }}
            onChange={handleTableChange}
            rowKey="id"
            {...props}
          />
        </SortableContext>
      </DndContext>
    </div>
  );
};

export default TableArchetype;
