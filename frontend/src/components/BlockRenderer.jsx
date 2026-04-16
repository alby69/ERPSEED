/**
 * BlockRenderer - Dynamic renderer for Block layouts
 *
 * Renders a block's UI configuration as interactive React components
 */

import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Table, Button, Space, Typography, message } from 'antd';
import { useNavigate } from 'react-router-dom';
import { apiFetch } from '@/utils';

const { Title, Text } = Typography;

const COMPONENT_RENDERERS = {
  // Card component
  card: (config, children) => (
    <Card
      title={config.title}
      size={config.size || 'default'}
      style={config.style || {}}
    >
      {children}
    </Card>
  ),

  // Statistic component
  statistic: (config) => (
    <Statistic
      title={config.title}
      value={config.value || 0}
      precision={config.precision || 0}
      prefix={config.prefix}
      suffix={config.suffix}
      valueStyle={config.valueStyle || {}}
      formatter={config.formatter}
    />
  ),

  // Row/Grid component
  row: (config, children) => (
    <Row
      gutter={config.gutter || 16}
      style={config.style || {}}
    >
      {children}
    </Row>
  ),

  // Column component
  col: (config, children) => (
    <Col
      span={config.span || 24}
      style={config.style || {}}
    >
      {children}
    </Col>
  ),

  // Button component
  button: (config, onClick) => (
    <Button
      type={config.type || 'default'}
      icon={config.icon}
      onClick={onClick}
      block={config.block}
      disabled={config.disabled}
    >
      {config.label}
    </Button>
  ),

  // Text component
  text: (config) => (
    <Text
      strong={config.strong}
      italic={config.italic}
      style={config.style || {}}
    >
      {config.content}
    </Text>
  ),

  // Title component
  title: (config) => (
    <Title
      level={config.level || 4}
      style={config.style || {}}
    >
      {config.content}
    </Title>
  ),

  // Space component
  space: (config, children) => (
    <Space
      direction={config.direction || 'horizontal'}
      size={config.size || 'small'}
      style={config.style || {}}
    >
      {children}
    </Space>
  ),

  // Table component
  table: (config, dataSource) => (
    <Table
      dataSource={dataSource || []}
      columns={config.columns || []}
      pagination={config.pagination !== false ? { pageSize: 10 } : false}
      size={config.size || 'default'}
      rowKey={config.rowKey || 'id'}
    />
  ),

  // Div container
  div: (config, children) => (
    <div style={config.style || {}}>
      {children}
    </div>
  )
};

/**
 * BlockRenderer - Main component
 *
 * @param {number} blockId - ID of the block to render
 * @param {object} data - Data to pass to the components
 * @param {function} onAction - Callback for button actions
 * @param {string} projectId - Project ID for navigation
 */
function BlockRenderer({ blockId, data = {}, onAction, projectId }) {
  const [block, setBlock] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (blockId) {
      loadBlock(blockId);
    }
  }, [blockId]);

  const loadBlock = async (id) => {
    setLoading(true);
    try {
      const response = await apiFetch(`/api/blocks/${id}`);
      if (response.ok) {
        const blockData = await response.json();
        setBlock(blockData);
      } else {
        setError('Block not found');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAction = (action, config, data) => {
    if (action === 'navigate' && config.path) {
      // Replace {projectId} placeholder with actual projectId
      const path = config.path.replace('{projectId}', projectId || '1');
      navigate(path);
      return;
    }
    if (action === 'navigate_external' && config.url) {
      window.open(config.url, config.target || '_self');
      return;
    }
    if (onAction) {
      onAction(action, config, data);
    }
  };

  const renderComponent = (comp, index) => {
    const renderer = COMPONENT_RENDERERS[comp.type];
    if (!renderer) {
      return <div key={index}>Unknown component: {comp.type}</div>;
    }

    const config = comp.config || {};
    let children = null;
    let onClick = null;

    // Handle nested components
    if (comp.children && comp.children.length > 0) {
      children = comp.children.map((child, i) => renderComponent(child, i));
    }

    // Handle button click
    if (comp.type === 'button') {
      onClick = () => handleAction(config.action, config, data);
    }

    // Pass data for table components
    if (comp.type === 'table') {
      return renderer(config, data[comp.dataSource] || []);
    }

    return (
      <div key={comp.id || index} style={{ position: 'absolute', left: comp.x || 0, top: comp.y || 0 }}>
        {renderer(config, children, onClick)}
      </div>
    );
  };

  if (loading) {
    return <div>Loading block...</div>;
  }

  if (error) {
    return <div style={{ color: 'red' }}>Error: {error}</div>;
  }

  if (!block || (!block.components && !block.visual_builder_config)) {
    return <div>No components to render</div>;
  }

  // Support both visual_builder_config and components
  const renderComponents = block.visual_builder_config || block.components || [];

  return (
    <div style={{ position: 'relative', minHeight: 400 }}>
      {renderComponents.map((comp, index) => renderComponent(comp, index))}
    </div>
  );
}

/**
 * Create a simple static renderer that doesn't require API calls
 * Useful for preview or when block data is already available
 */
function StaticBlockRenderer({ components = [], data = {}, onAction, projectId }) {
  const navigate = useNavigate();

  const handleAction = (action, config, data) => {
    if (action === 'navigate' && config.path) {
      // Replace {projectId} placeholder with actual projectId
      const path = config.path.replace('{projectId}', projectId || '1');
      navigate(path);
      return;
    }
    if (action === 'navigate_external' && config.url) {
      window.open(config.url, config.target || '_self');
      return;
    }
    if (onAction) {
      onAction(action, config, data);
    }
  };

  const renderComponent = (comp, index) => {
    const renderer = COMPONENT_RENDERERS[comp.type];
    if (!renderer) {
      return <div key={index} style={{ padding: 8, border: '1px dashed red' }}>Unknown: {comp.type}</div>;
    }

    const config = comp.config || {};
    let children = null;
    let onClick = null;

    if (comp.children && comp.children.length > 0) {
      children = comp.children.map((child, i) => renderComponent(child, i));
    }

    if (comp.type === 'button') {
      onClick = () => handleAction(config.action, config, data);
    }

    if (comp.type === 'table') {
      return (
        <div key={comp.id || index} style={{ position: 'relative' }}>
          {renderer(config, data[comp.dataSource] || [])}
        </div>
      );
    }

    const Wrapper = comp.type === 'col' ? 'span' : comp.type === 'row' ? 'div' : 'div';
    const wrapperStyle = comp.x !== undefined ? {
      position: 'relative',
      left: comp.x,
      top: comp.y,
      width: comp.w,
      height: comp.h
    } : {};

    return (
      <Wrapper key={comp.id || index} style={wrapperStyle}>
        {renderer(config, children, onClick)}
      </Wrapper>
    );
  };

  return <div>{components.map((comp, i) => renderComponent(comp, i))}</div>;
}

export { BlockRenderer, StaticBlockRenderer, COMPONENT_RENDERERS };
export default BlockRenderer;
