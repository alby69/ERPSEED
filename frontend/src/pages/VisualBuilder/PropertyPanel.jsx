/**
 * Property Panel - Component configuration for Visual Builder
 */

import React, { useEffect, useState } from 'react';
import { Form, Input, InputNumber, Switch, Select, Typography, Divider, Empty, Row, Col, Tooltip, Spin } from 'antd';
import { InfoCircleOutlined } from '@ant-design/icons';
import { registry } from '@/components/core';
import { apiFetch } from '@/utils';

const { Title, Text } = Typography;

const PropertyPanel = ({ component, onChange, projectId }) => {
  const [form] = Form.useForm();
  const [models, setModels] = useState([]);
  const [loadingModels, setLoadingModels] = useState(false);
  const [context, setContext] = useState({
    user: { name: 'Admin', role: 'admin' },
    company: { name: 'FlaskERP Corp' },
    now: new Date().toISOString()
  });

  useEffect(() => {
    fetchModels();
  }, [projectId]);

  const fetchModels = async () => {
    if (!projectId) return;
    setLoadingModels(true);
    try {
      const response = await apiFetch(`/projects/${projectId}/models`);
      const data = await response.json();
      setModels(data);
    } catch (error) {
      console.error("Error fetching models:", error);
    } finally {
      setLoadingModels(false);
    }
  };

  useEffect(() => {
    if (component) {
      form.setFieldsValue({
        name: component.name,
        x: component.x,
        y: component.y,
        w: component.w,
        h: component.h,
        modelId: component.modelId,
        ...component.config
      });
    }
  }, [component, form]);

  if (!component) {
    return (
      <div style={{ padding: 24, textAlign: 'center' }}>
        <Empty description="Select a component to edit its properties" />
      </div>
    );
  }

  const archetype = registry.get(component.type);
  const propsSchema = archetype?.props_schema || {};

  const handleValuesChange = (_, allValues) => {
    const { name, x, y, w, h, modelId, ...config } = allValues;
    onChange({
      ...component,
      name,
      x,
      y,
      w,
      h,
      modelId,
      config
    });
  };

  const renderField = (key, schema) => {
    const label = (
      <span>
        {schema.title || key}
        <Tooltip title="Supports {{expressions}}">
          <InfoCircleOutlined style={{ marginLeft: 4, fontSize: 10, color: '#1677ff' }} />
        </Tooltip>
      </span>
    );

    if (schema.type === 'boolean') {
      return (
        <Form.Item key={key} name={key} label={label} valuePropName="checked">
          <Switch />
        </Form.Item>
      );
    }

    if (schema.type === 'number') {
      return (
        <Form.Item key={key} name={key} label={label}>
          <InputNumber style={{ width: '100%' }} />
        </Form.Item>
      );
    }

    if (schema.enum) {
      return (
        <Form.Item key={key} name={key} label={label}>
          <Select>
            {schema.enum.map(opt => (
              <Select.Option key={opt} value={opt}>{opt}</Select.Option>
            ))}
          </Select>
        </Form.Item>
      );
    }

    return (
      <Form.Item key={key} name={key} label={label}>
        <Input placeholder="{{expression}} or text" />
      </Form.Item>
    );
  };

  return (
    <div className="property-panel" style={{ padding: 16 }}>
      <Title level={4}>Properties</Title>
      <Text type="secondary">{archetype?.title || component.type}</Text>
      <Divider style={{ margin: '12px 0' }} />

      <Form
        form={form}
        layout="vertical"
        onValuesChange={handleValuesChange}
        size="small"
      >
        <Form.Item name="name" label="Component Name" rules={[{ required: true }]}>
          <Input placeholder="Unique name" />
        </Form.Item>

        <Form.Item name="modelId" label="Data Source (Model)">
          <Select
            placeholder="Select a model"
            allowClear
            loading={loadingModels}
          >
            {models.map(m => (
              <Select.Option key={m.id} value={m.id}>{m.title || m.name}</Select.Option>
            ))}
          </Select>
        </Form.Item>

        <Divider orientation="left" plain style={{ fontSize: 11 }}>Layout</Divider>
        <Row gutter={8}>
          <Col span={12}>
            <Form.Item name="x" label="X Pos">
              <InputNumber step={32} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="y" label="Y Pos">
              <InputNumber step={32} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
        </Row>
        <Row gutter={8}>
          <Col span={12}>
            <Form.Item name="w" label="Width">
              <InputNumber step={32} min={32} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="h" label="Height">
              <InputNumber step={32} min={32} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
        </Row>

        <Divider orientation="left" plain style={{ fontSize: 11 }}>Configuration</Divider>

        {Object.entries(propsSchema.properties || {}).map(([key, schema]) => (
          renderField(key, schema)
        ))}

        {(!propsSchema.properties || Object.keys(propsSchema.properties).length === 0) && (
          <Text type="secondary" italic style={{ fontSize: 12 }}>No specific properties.</Text>
        )}

        <Divider orientation="left" plain style={{ fontSize: 11 }}>Data Binding Info</Divider>
        <div style={{ fontSize: 11, background: '#f9f9f9', padding: 8, borderRadius: 4 }}>
          <Text type="secondary">Available context:</Text>
          <ul style={{ paddingLeft: 16, margin: '4px 0' }}>
            <li><code>user.name</code>, <code>user.role</code></li>
            <li><code>company.name</code></li>
            <li><code>now</code> (ISO Date)</li>
          </ul>
          <Divider style={{ margin: '4px 0' }} />
          <Text type="secondary">Built-in Functions:</Text>
          <ul style={{ paddingLeft: 16, margin: '4px 0' }}>
            <li><code>UPPER(text)</code> / <code>LOWER(text)</code></li>
            <li><code>IF(condition, then, else)</code></li>
            <li><code>COUNT(array)</code> / <code>SUM(array, "field")</code></li>
            <li><code>FORMAT_CURRENCY(val, "€")</code></li>
          </ul>
          <Text type="info" style={{ fontSize: 10 }}>Tip: Wrap expressions in <code>{`{{ ... }}`}</code></Text>
        </div>
      </Form>
    </div>
  );
};

export default PropertyPanel;
