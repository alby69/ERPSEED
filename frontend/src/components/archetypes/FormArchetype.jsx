/**
 * Form Archetype
 *
 * Data entry form component
 */
import React from 'react';
import { Form, Input, Select, DatePicker, InputNumber, Switch, Button } from 'antd';

const FormArchetype = ({ config = {}, data = null, onChange, ...props }) => {
  const { fields = [], layout = 'vertical' } = config;

  const renderField = (field) => {
    const commonProps = {
      name: field.name,
      label: field.label,
      required: field.required,
    };

    switch (field.type) {
      case 'string':
      case 'text':
        return <Input {...commonProps} />;
      case 'textarea':
        return <Input.TextArea {...commonProps} />;
      case 'email':
        return <Input type="email" {...commonProps} />;
      case 'password':
        return <Input.Password {...commonProps} />;
      case 'number':
        return <InputNumber style={{ width: '100%' }} {...commonProps} />;
      case 'select':
        return (
          <Select {...commonProps}>
            {(field.options || []).map(opt => (
              <Select.Option key={opt.value} value={opt.value}>
                {opt.label}
              </Select.Option>
            ))}
          </Select>
        );
      case 'date':
        return <DatePicker style={{ width: '100%' }} {...commonProps} />;
      case 'boolean':
        return <Switch {...commonProps} />;
      default:
        return <Input {...commonProps} />;
    }
  };

  return (
    <Form layout={layout} {...props}>
      {fields.map(field => (
        <Form.Item key={field.name}>
          {renderField(field)}
        </Form.Item>
      ))}
    </Form>
  );
};

export default FormArchetype;
