/**
 * Property Panel - Component configuration for Visual Builder
 */

import React, { useEffect } from 'react';
import { Form, Input, InputNumber, Switch, Select, Typography, Card, Empty, Divider, Button } from 'antd';
import { registry } from '@/components/core';

const { Title, Text } = Typography;

const PropertyPanel = ({ component, onChange }) => {
  const [form] = Form.useForm();

  useEffect(() => {
    if (component) {
      form.setFieldsValue({
        name: component.name,
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
    const { name, ...config } = allValues;
    onChange({
      ...component,
      name,
      config
    });
  };

  const renderField = (key, schema) => {
    const label = schema.title || key;

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
        <Input />
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
          <Input placeholder="Unique name for this instance" />
        </Form.Item>

        <Divider orientation="left" plain style={{ fontSize: 12 }}>Config</Divider>

        {Object.entries(propsSchema.properties || {}).map(([key, schema]) => (
          renderField(key, schema)
        ))}

        {(!propsSchema.properties || Object.keys(propsSchema.properties).length === 0) && (
          <Text type="secondary" italic>No specific properties for this component.</Text>
        )}
      </Form>
    </div>
  );
};

export default PropertyPanel;
