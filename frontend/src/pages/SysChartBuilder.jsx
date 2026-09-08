import React, { useState, useEffect } from 'react';
import {
  Card, Row, Col, Button, Modal, Form, Input, Select, InputNumber,
  Tag, Space, Typography, List, Popconfirm, message, Empty, Flex
} from 'antd';
import { PlusOutlined, SettingOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { apiFetch } from '../utils';
import ChartWidget from '../components/ChartWidget';
import Layout from '../components/Layout';

const { Title, Text } = Typography;
const { Option } = Select;

const CHART_TYPES = [
  { value: 'bar', label: 'Bar Chart' },
  { value: 'line', label: 'Line Chart' },
  { value: 'pie', label: 'Pie Chart' },
  { value: 'doughnut', label: 'Doughnut Chart' },
  { value: 'area', label: 'Area Chart' },
  { value: 'scatter', label: 'Scatter Chart' },
  { value: 'text', label: 'Text / HTML Widget' },
  { value: 'table', label: 'Table Widget (Last N)' },
];

const AGGREGATIONS = [
  { value: 'sum', label: 'Sum' },
  { value: 'count', label: 'Count' },
  { value: 'avg', label: 'Average' },
  { value: 'min', label: 'Minimum' },
  { value: 'max', label: 'Maximum' },
];

const FILTER_TYPES = [
  { value: 'date_range', label: 'Date Range' },
  { value: 'select', label: 'Dropdown Select' },
  { value: 'multiselect', label: 'Multi-Select' },
  { value: 'text', label: 'Text Input' },
  { value: 'number_range', label: 'Number Range' },
];

function SysChartBuilder() {
  const [charts, setCharts] = useState([]);
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [showFiltersModal, setShowFiltersModal] = useState(false);
  const [editingChart, setEditingChart] = useState(null);

  const [form] = Form.useForm();
  const [filterForm] = Form.useForm();

  const [selectedModelId, setSelectedModelId] = useState('');
  const [selectedChartType, setSelectedChartType] = useState('bar');
  const [modelFields, setModelFields] = useState([]);
  const [filtersConfig, setFiltersConfig] = useState([]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [chartsRes, modelsRes] = await Promise.all([
        apiFetch('/analytics/sys-charts'),
        apiFetch('/sys-models')
      ]);

      if (chartsRes.ok) {
        const chartsData = await chartsRes.json();
        setCharts(Array.isArray(chartsData) ? chartsData : (chartsData.items || []));
      }
      if (modelsRes.ok) {
        const modelsData = await modelsRes.json();
        setModels(Array.isArray(modelsData) ? modelsData : (modelsData.items || []));
      }
    } catch (error) {
      console.error("Error fetching builder data", error);
      message.error("Failed to load chart builder data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    if (selectedModelId) {
      apiFetch(`/sys-models/${selectedModelId}`)
        .then(res => res.json())
        .then(data => setModelFields(data.fields || data.model_fields || []))
        .catch(console.error);
    } else {
      setModelFields([]);
    }
  }, [selectedModelId]);

  const handleOpenCreateModal = () => {
    setEditingChart(null);
    setSelectedModelId('');
    setSelectedChartType('bar');
    form.resetFields();
    setShowModal(true);
  };

  const handleOpenEditModal = (chart) => {
    setEditingChart(chart);
    setSelectedModelId(chart.model_id);
    setSelectedChartType(chart.type || chart.chart_type || 'bar');
    form.setFieldsValue({
      title: chart.title,
      type: chart.type || chart.chart_type || 'bar',
      model_id: chart.model_id,
      x_axis: chart.x_axis || '',
      y_axis: chart.y_axis || '',
      aggregation: chart.aggregation || 'sum',
      filters: chart.filters || ''
    });
    setShowModal(true);
  };

  const handleSaveChart = async (values) => {
    try {
      const payload = {
        title: values.title,
        chart_type: values.type,
        model_id: values.model_id,
        x_axis: values.x_axis || '',
        y_axis: values.y_axis || '',
        aggregation: values.aggregation || 'sum',
        filters: values.filters || '',
        filters_config: editingChart ? (editingChart.filters_config || []) : []
      };

      const url = editingChart ? `/analytics/sys-charts/${editingChart.id}` : '/analytics/sys-charts';
      const method = editingChart ? 'PUT' : 'POST';

      const res = await apiFetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        message.success(editingChart ? "Chart updated" : "Chart created");
        setShowModal(false);
        fetchData();
      } else {
        message.error("Error saving chart");
      }
    } catch (error) {
      console.error(error);
      message.error("Error saving chart");
    }
  };

  const handleDelete = async (id) => {
    try {
      const res = await apiFetch(`/analytics/sys-charts/${id}`, { method: 'DELETE' });
      if (res.ok) {
        message.success("Chart deleted");
        fetchData();
      } else {
        message.error("Error deleting chart");
      }
    } catch (error) {
      console.error(error);
      message.error("Error deleting chart");
    }
  };

  const openFiltersConfig = (chart) => {
    setEditingChart(chart);
    setSelectedModelId(chart.model_id);
    setFiltersConfig(chart.filters_config || []);
    filterForm.resetFields();
    setShowFiltersModal(true);
  };

  const handleAddFilter = (values) => {
    const newFilter = {
      field: values.field,
      type: values.type,
      label: values.label,
      options: values.options ? values.options.split(',').map(o => o.trim()) : []
    };
    setFiltersConfig(prev => [...prev, newFilter]);
    filterForm.resetFields();
  };

  const handleRemoveFilter = (index) => {
    setFiltersConfig(prev => prev.filter((_, i) => i !== index));
  };

  const saveFiltersConfig = async () => {
    try {
      const res = await apiFetch(`/analytics/sys-charts/${editingChart.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filters_config: filtersConfig })
      });

      if (res.ok) {
        message.success("Filters updated");
        setShowFiltersModal(false);
        fetchData();
      } else {
        message.error("Error saving filters");
      }
    } catch (error) {
      console.error(error);
      message.error("Error saving filters");
    }
  };

  return (
    <Layout>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <Flex justify="space-between" align="center">
          <Title level={3} style={{ margin: 0 }}>
            Analytics (Chart Builder)
          </Title>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleOpenCreateModal}>
            New Chart
          </Button>
        </Flex>

        <Row gutter={[16, 16]}>
          {charts.map(chart => (
            <Col key={chart.id} xs={24} md={12}>
              <Card
                title={chart.title}
                extra={
                  <Space>
                    <Button
                      type="text"
                      icon={<SettingOutlined />}
                      onClick={() => openFiltersConfig(chart)}
                      title="Configure Filters"
                    />
                    <Button
                      type="text"
                      icon={<EditOutlined />}
                      onClick={() => handleOpenEditModal(chart)}
                      title="Edit Chart"
                    />
                    <Popconfirm
                      title="Delete this chart?"
                      onConfirm={() => handleDelete(chart.id)}
                      okText="Yes"
                      cancelText="No"
                    >
                      <Button type="text" danger icon={<DeleteOutlined />} title="Delete Chart" />
                    </Popconfirm>
                  </Space>
                }
                styles={{ body: { minHeight: 300, padding: 16 } }}
              >
                <ChartWidget chartId={chart.id} />
                <div style={{ marginTop: 12, paddingTop: 8, borderTop: '1px solid #f0f0f0' }}>
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    {chart.type === 'text' ? (
                      'Type: Text Widget'
                    ) : (
                      `Type: ${chart.type} | Aggregation: ${chart.aggregation} of ${chart.y_axis} by ${chart.x_axis}`
                    )}
                  </Text>
                  {chart.filters_config && chart.filters_config.length > 0 && (
                    <Tag color="processing" style={{ marginLeft: 8 }}>
                      {chart.filters_config.length} filter(s)
                    </Tag>
                  )}
                </div>
              </Card>
            </Col>
          ))}
          {charts.length === 0 && !loading && (
            <Col span={24}>
              <Card>
                <Empty description="No charts created yet." />
              </Card>
            </Col>
          )}
        </Row>

        {/* Modal Chart Create/Edit */}
        <Modal
          title={editingChart ? 'Edit Chart' : 'Create Chart'}
          open={showModal}
          onCancel={() => setShowModal(false)}
          footer={null}
          destroyOnClose
        >
          <Form
            form={form}
            layout="vertical"
            onFinish={handleSaveChart}
            initialValues={{ type: 'bar', aggregation: 'sum' }}
          >
            <Form.Item name="title" label="Chart Title" rules={[{ required: true, message: 'Title is required' }]}>
              <Input placeholder="E.g., Sales by Region" />
            </Form.Item>

            <Row gutter={16}>
              <Col span={12}>
                <Form.Item name="type" label="Chart Type" rules={[{ required: true }]}>
                  <Select onChange={val => setSelectedChartType(val)}>
                    {CHART_TYPES.map(t => (
                      <Option key={t.value} value={t.value}>{t.label}</Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item name="model_id" label="Data Source (Model)" rules={[{ required: true }]}>
                  <Select placeholder="Select Model..." onChange={val => setSelectedModelId(val)}>
                    {models.map(m => (
                      <Option key={m.id} value={m.id}>{m.title}</Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
            </Row>

            {selectedChartType !== 'text' && selectedChartType !== 'table' && (
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item name="x_axis" label="X Axis (Category)" rules={[{ required: true }]}>
                    <Select placeholder="Select Field...">
                      {modelFields.map(f => (
                        <Option key={f.name} value={f.name}>{f.title || f.name}</Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="y_axis" label="Y Axis (Value)" rules={[{ required: true }]}>
                    <Select placeholder="Select Field...">
                      <Option value="*">Count All (*)</Option>
                      {modelFields.filter(f => ['integer', 'float', 'currency'].includes(f.type)).map(f => (
                        <Option key={f.name} value={f.name}>{f.title || f.name}</Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
              </Row>
            )}

            {selectedChartType !== 'text' && (
              <Form.Item name="aggregation" label="Aggregation Function">
                <Select>
                  {AGGREGATIONS.map(a => (
                    <Option key={a.value} value={a.value}>{a.label}</Option>
                  ))}
                </Select>
              </Form.Item>
            )}

            <Form.Item name="filters" label="Fixed Filters (JSON)">
              <Input.TextArea rows={2} placeholder='e.g. {"status": "confirmed"}' />
            </Form.Item>

            <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
              <Space>
                <Button onClick={() => setShowModal(false)}>Cancel</Button>
                <Button type="primary" htmlType="submit">
                  {editingChart ? 'Update' : 'Create'}
                </Button>
              </Space>
            </Form.Item>
          </Form>
        </Modal>

        {/* Modal Dynamic Filters */}
        <Modal
          title="Configure Dynamic Filters"
          open={showFiltersModal}
          onCancel={() => setShowFiltersModal(false)}
          footer={
            <Space>
              <Button onClick={() => setShowFiltersModal(false)}>Cancel</Button>
              <Button type="primary" onClick={saveFiltersConfig}>Save Filters</Button>
            </Space>
          }
        >
          <Space direction="vertical" style={{ width: '100%' }} size="middle">
            <Text type="secondary" style={{ fontSize: 13 }}>
              Add interactive filters that users can apply when viewing the dashboard.
            </Text>

            <Card size="small" style={{ background: '#fafafa' }}>
              <Form form={filterForm} layout="vertical" onFinish={handleAddFilter}>
                <Row gutter={8}>
                  <Col span={8}>
                    <Form.Item name="label" label="Label" rules={[{ required: true }]}>
                      <Input placeholder="Filter Name" size="small" />
                    </Form.Item>
                  </Col>
                  <Col span={8}>
                    <Form.Item name="type" label="Type" initialValue="select">
                      <Select size="small">
                        {FILTER_TYPES.map(f => (
                          <Option key={f.value} value={f.value}>{f.label}</Option>
                        ))}
                      </Select>
                    </Form.Item>
                  </Col>
                  <Col span={8}>
                    <Form.Item name="field" label="Field" rules={[{ required: true }]}>
                      <Select size="small" placeholder="Select Field">
                        {modelFields.map(f => (
                          <Option key={f.name} value={f.name}>{f.title || f.name}</Option>
                        ))}
                      </Select>
                    </Form.Item>
                  </Col>
                </Row>
                <Form.Item name="options" label="Options (Comma separated, for dropdowns)">
                  <Input placeholder="Val1, Val2, Val3" size="small" />
                </Form.Item>
                <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
                  <Button type="primary" size="small" htmlType="submit" icon={<PlusOutlined />}>
                    Add Filter
                  </Button>
                </Form.Item>
              </Form>
            </Card>

            <List
              size="small"
              bordered
              dataSource={filtersConfig}
              renderItem={(f, i) => (
                <List.Item
                  actions={[
                    <Button
                      type="text"
                      danger
                      size="small"
                      icon={<DeleteOutlined />}
                      onClick={() => handleRemoveFilter(i)}
                    />
                  ]}
                >
                  <Space>
                    <Text strong>{f.label}</Text>
                    <Tag color="blue">{f.type}</Tag>
                    <Text type="secondary">({f.field})</Text>
                  </Space>
                </List.Item>
              )}
              locale={{ emptyText: 'No dynamic filters configured yet.' }}
            />
          </Space>
        </Modal>
      </Space>
    </Layout>
  );
}

export default SysChartBuilder;
