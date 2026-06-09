import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Form, Input, InputNumber, Switch, Button, Card, Space, Spin, Alert, Typography, Select } from 'antd';
import { ArrowLeftOutlined, SaveOutlined } from '@ant-design/icons';
import { apiClient } from './api'; // No date fields in this page

function ProductDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isNew = id === 'new';
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(!isNew);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!isNew) {
      apiClient.get(`/api/v1/products/${id}`)
        .then(data => {
          form.setFieldsValue(data);
        })
        .catch(err => setError(err.message))
        .finally(() => setLoading(false));
    }
  }, [id, isNew, form]);

  const handleSubmit = async (values) => {
    setSaving(true);
    setError(null);
    try {
      if (isNew) {
        await apiClient.post('/api/v1/products', values);
      } else {
        await apiClient.put(`/api/v1/products/${id}`, values);
      }
      navigate('/products');
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="p-5 text-center"><Spin size="large" /></div>;
  }

  return (
    <>
      <div style={{ padding: 24, background: '#fff', borderBottom: '1px solid #f0f0f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Space>
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/products')} />
          <Typography.Title level={4} style={{ margin: 0 }}>{isNew ? 'New Product' : 'Edit Product'}</Typography.Title>
        </Space>
        <Button type="primary" icon={<SaveOutlined />} onClick={() => form.submit()} loading={saving}>
          Save
        </Button>
      </div>
      <div style={{ padding: 24 }}>
        {error && <Alert message="Error" description={error} type="error" showIcon className="mb-4" />}
        <Card>
          <Form form={form} layout="vertical" onFinish={handleSubmit} initialValues={{ is_active: true, track_inventory: false, current_stock: 0, reorder_level: 0, unit_of_measure: 'pcs' }}>
            <div className="row">
              <div className="col-md-6">
                <Form.Item name="name" label="Name" rules={[{ required: true, message: 'Product name is required' }]}>
                  <Input />
                </Form.Item>
              </div>
              <div className="col-md-3">
                <Form.Item name="code" label="Code">
                  <Input />
                </Form.Item>
              </div>
              <div className="col-md-3">
                <Form.Item name="category" label="Category">
                  <Input />
                </Form.Item>
              </div>
            </div>
            <div className="row">
              <div className="col-md-12">
                <Form.Item name="description" label="Description">
                  <Input.TextArea rows={3} />
                </Form.Item>
              </div>
            </div>
            <div className="row">
              <div className="col-md-3">
                <Form.Item name="unit_price" label="Unit Price">
                  <InputNumber min={0} step={0.01} style={{ width: '100%' }} />
                </Form.Item>
              </div>
              <div className="col-md-3">
                <Form.Item name="sku" label="SKU">
                  <Input />
                </Form.Item>
              </div>
              <div className="col-md-3">
                <Form.Item name="barcode" label="Barcode">
                  <Input />
                </Form.Item>
              </div>
              <div className="col-md-3">
                <Form.Item name="unit_of_measure" label="Unit of Measure">
                  <Select>
                    <Select.Option value="pcs">Pieces</Select.Option>
                    <Select.Option value="kg">Kilograms</Select.Option>
                    <Select.Option value="g">Grams</Select.Option>
                    <Select.Option value="l">Liters</Select.Option>
                    <Select.Option value="ml">Milliliters</Select.Option>
                    <Select.Option value="m">Meters</Select.Option>
                    <Select.Option value="cm">Centimeters</Select.Option>
                    <Select.Option value="box">Box</Select.Option>
                    <Select.Option value="pack">Pack</Select.Option>
                  </Select>
                </Form.Item>
              </div>
            </div>
            <div className="row">
              <div className="col-md-3">
                <Form.Item name="weight" label="Weight">
                  <InputNumber min={0} step={0.01} style={{ width: '100%' }} />
                </Form.Item>
              </div>
              <div className="col-md-3">
                <Form.Item name="dimensions" label="Dimensions">
                  <Input placeholder="e.g. 10x20x30 cm" />
                </Form.Item>
              </div>
              <div className="col-md-3">
                <Form.Item name="is_active" label="Active" valuePropName="checked">
                  <Switch />
                </Form.Item>
              </div>
            </div>
            <Typography.Title level={5}>Inventory</Typography.Title>
            <div className="row">
              <div className="col-md-3">
                <Form.Item name="track_inventory" label="Track Inventory" valuePropName="checked">
                  <Switch />
                </Form.Item>
              </div>
              <div className="col-md-3">
                <Form.Item name="current_stock" label="Current Stock">
                  <InputNumber min={0} step={1} style={{ width: '100%' }} />
                </Form.Item>
              </div>
              <div className="col-md-3">
                <Form.Item name="reorder_level" label="Reorder Level">
                  <InputNumber min={0} step={1} style={{ width: '100%' }} />
                </Form.Item>
              </div>
            </div>
          </Form>
        </Card>
      </div>
    </>
  );
}

export default ProductDetail;
