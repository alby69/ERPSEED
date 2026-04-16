/**
 * Component Renderer
 *
 * This module renders components dynamically based on their archetype.
 */

import React, { useMemo, useState, useEffect } from 'react';
import registry from './ArchetypeRegistry';
import { resolveDataBinding } from '@/utils/binding';
import { apiFetch } from '@/utils';

/**
 * ComponentRenderer - Renders a component based on its archetype
 *
 * @param {Object} props
 * @param {string} props.type - Component type (table, form, chart, etc.)
 * @param {Object} props.config - Component configuration
 * @param {Object} props.data - Component data
 * @param {Function} props.onChange - Callback when config changes
 * @param {Object} props.otherProps - Additional props passed to archetype
 */
const ComponentRenderer = ({
  type,
  config = {},
  data = null,
  context = {},
  projectId,
  modelId,
  onChange,
  ...otherProps
}) => {
  const archetype = useMemo(() => registry.get(type), [type]);
  const [modelName, setModelName] = useState(null);

  // Fetch model metadata if modelId is provided but modelName is not
  useEffect(() => {
    const fetchModelMeta = async () => {
      if (projectId && modelId) {
        try {
          const response = await apiFetch(`/projects/${projectId}/models/${modelId}`);
          const modelData = await response.json();
          setModelName(modelData.name);
        } catch (error) {
          console.error("Error fetching model metadata for renderer:", error);
        }
      }
    };
    fetchModelMeta();
  }, [projectId, modelId]);

  // Resolve data bindings in config using provided context
  const resolvedConfig = useMemo(() => {
    return resolveDataBinding(config, context);
  }, [config, context]);

  if (!archetype) {
    return (
      <div style={{ padding: 16, color: '#999', border: '1px dashed #ccc' }}>
        Unknown component type: {type}
      </div>
    );
  }

  const { Component } = archetype;

  if (!Component) {
    return (
      <div style={{ padding: 16, color: '#999', border: '1px dashed #ccc' }}>
        No renderer for component type: {type}
      </div>
    );
  }

  return (
    <Component
      config={resolvedConfig}
      data={data}
      onChange={onChange}
      projectId={projectId}
      modelName={modelName}
      {...otherProps}
    />
  );
};

/**
 * CollectionRenderer - Renders a collection of components
 *
 * @param {Object} props
 * @param {Array} props.components - Array of component configurations
 * @param {Object} props.layout - Layout configuration (grid, list, etc.)
 * @param {Function} props.onComponentChange - Callback when a component changes
 */
const CollectionRenderer = ({
  components = [],
  layout = 'grid',
  onComponentChange,
  ...props
}) => {
  const renderLayout = () => {
    switch (layout) {
      case 'grid':
        return renderGrid();
      case 'list':
        return renderList();
      case 'stack':
        return renderStack();
      default:
        return renderGrid();
    }
  };

  const renderGrid = () => (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
      gap: 16
    }}>
      {components.map((comp, index) => (
        <ComponentRenderer
          key={comp.id || index}
          type={comp.type}
          config={comp.config}
          data={comp.data}
          context={props.context}
          onChange={(newConfig) => onComponentChange?.(comp.id, newConfig)}
          {...props}
        />
      ))}
    </div>
  );

  const renderList = () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      {components.map((comp, index) => (
        <ComponentRenderer
          key={comp.id || index}
          type={comp.type}
          config={comp.config}
          data={comp.data}
          context={props.context}
          onChange={(newConfig) => onComponentChange?.(comp.id, newConfig)}
          {...props}
        />
      ))}
    </div>
  );

  const renderStack = () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {components.map((comp, index) => (
        <ComponentRenderer
          key={comp.id || index}
          type={comp.type}
          config={comp.config}
          data={comp.data}
          context={props.context}
          onChange={(newConfig) => onComponentChange?.(comp.id, newConfig)}
          {...props}
        />
      ))}
    </div>
  );

  if (!components || components.length === 0) {
    return (
      <div style={{ padding: 32, textAlign: 'center', color: '#999' }}>
        No components to display
      </div>
    );
  }

  return renderLayout();
};

/**
 * BlockRenderer - Renders a complete block with all its components
 *
 * @param {Object} props
 * @param {Object} props.block - Block configuration
 * @param {Object} props.data - Block data
 * @param {Function} props.onConfigChange - Callback when block config changes
 */
const BlockRenderer = ({
  block,
  data = {},
  onConfigChange,
  ...props
}) => {
  const { component_ids = [], relationships } = block;

  // = {} Transform component IDs to component configs
  const components = useMemo(() => {
    if (!Array.isArray(component_ids)) return [];

    return component_ids.map((id, index) => {
      const compData = data[id] || {};
      return {
        id,
        type: compData.type || 'table',
        config: compData.config || {},
        data: compData.data,
      };
    });
  }, [component_ids, data]);

  const handleComponentChange = (componentId, newConfig) => {
    onConfigChange?.(componentId, newConfig);
  };

  return (
    <CollectionRenderer
      components={components}
      layout="grid"
      onComponentChange={handleComponentChange}
      {...props}
    />
  );
};

export { ComponentRenderer, CollectionRenderer, BlockRenderer };
export default ComponentRenderer;
