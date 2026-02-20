import React, { useState, useEffect, useCallback } from 'react';
import {
  Card, Table, Button, Modal, Form, Input, Select, Tag, Space,
  message, Row, Col, Statistic, Typography, InputNumber, Alert, Upload
} from 'antd';
import {
  PlusOutlined, EditOutlined, ReloadOutlined, SearchOutlined,
  GlobalOutlined, EnvironmentOutlined, UploadOutlined
} from '@ant-design/icons';
import { apiFetch } from '@/utils';

const { Title, Text } = Typography;
const { Option } = Select;

const ComuniPage = () => {
  const [comuni, setComuni] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 50, total: 0 });
  const [sorter, setSorter] = useState({ field: 'nome', order: 'asc' });
  const [filters, setFilters] = useState({ q: '', regione: '', provincia: '' });
  
  const [regioni, setRegioni] = useState([]);
  const [province, setProvince] = useState([]);
  
  const [modalVisible, setModalVisible] = useState(false);
  const [editingComune, setEditingComune] = useState(null);
  const [form] = Form.useForm();
  
  const [stats, setStats] = useState({ total: 0, istat: 0, manuali: 0, regioni: 0, province: 0 });
  const [uploadLoading, setUploadLoading] = useState(false);

  const fetchStats = useCallback(async () => {
    try {
      const response = await apiFetch('/api/v1/comuni/stats');
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Errore nel caricamento statistiche:', error);
    }
  }, []);

  const fetchComuni = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: pagination.current,
        per_page: pagination.pageSize,
        sort_by: sorter.field,
        order: sorter.order,
      });
      
      if (filters.q) params.append('q', filters.q);
      if (filters.regione) params.append('regione', filters.regione);
      if (filters.provincia) params.append('provincia', filters.provincia);
      
      const response = await apiFetch(`/api/v1/comuni?${params}`);
      if (response.ok) {
        const data = await response.json();
        setComuni(data.items);
        setPagination(prev => ({
          ...prev,
          total: data.total,
          current: data.page
        }));
      }
    } catch (error) {
      message.error('Errore nel caricamento dei comuni');
    } finally {
      setLoading(false);
    }
  }, [pagination.current, pagination.pageSize, sorter, filters]);

  const fetchRegioni = useCallback(async () => {
    try {
      const response = await apiFetch('/api/v1/comuni/regioni');
      if (response.ok) {
        const data = await response.json();
        setRegioni(data);
      }
    } catch (error) {
      console.error('Errore nel caricamento delle regioni:', error);
    }
  }, []);

  const fetchProvince = useCallback(async (regioneCodice) => {
    if (!regioneCodice) {
      setProvince([]);
      return;
    }
    try {
      const response = await apiFetch(`/api/v1/comuni/province?regione=${regioneCodice}`);
      if (response.ok) {
        const data = await response.json();
        setProvince(data);
      }
    } catch (error) {
      console.error('Errore nel caricamento delle province:', error);
    }
  }, []);

  useEffect(() => {
    fetchStats();
    fetchRegioni();
  }, [fetchStats, fetchRegioni]);

  useEffect(() => {
    fetchComuni();
  }, [fetchComuni]);

  const handleTableChange = (newPagination, tableFilters, tableSorter) => {
    setPagination(prev => ({ ...prev, current: newPagination.current, pageSize: newPagination.pageSize }));
    if (tableSorter.field) {
      setSorter({ field: tableSorter.field, order: tableSorter.order === 'descend' ? 'desc' : 'asc' });
    }
  };

  const handleSearch = (value) => {
    setFilters(prev => ({ ...prev, q: value }));
    setPagination(prev => ({ ...prev, current: 1 }));
  };

  const handleRegioneFilter = (value) => {
    setFilters(prev => ({ ...prev, regione: value, provincia: '' }));
    setProvince([]);
    if (value) fetchProvince(value);
    setPagination(prev => ({ ...prev, current: 1 }));
  };

  const handleProvinciaFilter = (value) => {
    setFilters(prev => ({ ...prev, provincia: value }));
    setPagination(prev => ({ ...prev, current: 1 }));
  };

  const handleEdit = (record) => {
    setEditingComune(record);
    form.setFieldsValue({
      nome: record.nome,
      cap: record.cap,
      latitudine: record.latitudine,
      longitudine: record.longitudine,
      denominazione: record.denominazione
    });
    setModalVisible(true);
  };

  const handleSubmit = async (values) => {
    try {
      const url = editingComune ? `/api/v1/comuni/${editingComune.id}` : '/api/v1/comuni';
      const method = editingComune ? 'PUT' : 'POST';
      
      const response = await apiFetch(url, {
        method,
        body: JSON.stringify(values)
      });
      
      if (response.ok) {
        message.success(editingComune ? 'Comune aggiornato' : 'Comune creato');
        setModalVisible(false);
        fetchComuni();
        fetchStats();
      } else {
        const err = await response.json();
        message.error(err.error || err.message || 'Errore nel salvataggio');
      }
    } catch (error) {
      message.error('Errore nel salvataggio');
    }
  };

  const handleUpload = async (file) => {
    setUploadLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await apiFetch('/api/v1/admin/comuni/sync/upload', {
        method: 'POST',
        body: formData
      });
      
      if (response.ok) {
        const data = await response.json();
        message.success(data.message || 'Upload completato');
        fetchComuni();
        fetchStats();
      } else {
        message.error('Errore nell\'upload');
      }
    } catch (error) {
      message.error('Errore nell\'upload');
    } finally {
      setUploadLoading(false);
    }
    
    return false;
  };

  const columns = [
    {
      title: 'Codice',
      dataIndex: 'codice',
      key: 'codice',
      width: 100,
      sorter: true
    },
    {
      title: 'Nome',
      dataIndex: 'nome',
      key: 'nome',
      width: 200,
      sorter: true,
      render: (text, record) => (
        <Space>
          {text}
          {record.is_manuale && <Tag color="orange">Manuale</Tag>}
        </Space>
      )
    },
    {
      title: 'Provincia',
      dataIndex: 'provincia',
      key: 'provincia',
      width: 80
    },
    {
      title: 'Regione',
      dataIndex: 'regione',
      key: 'regione',
      width: 80
    },
    {
      title: 'CAP',
      dataIndex: 'cap',
      key: 'cap',
      width: 80,
      sorter: true
    },
    {
      title: 'Coordinate',
      key: 'coordinate',
      width: 150,
      render: (_, record) => (
        record.latitudine && record.longitudine ? (
          <Text type="secondary" style={{ fontSize: 12 }}>
            {record.latitudine.toFixed(4)}, {record.longitudine.toFixed(4)}
          </Text>
        ) : '-'
      )
    },
    {
      title: 'Azioni',
      key: 'azioni',
      width: 100,
      render: (_, record) => (
        <Space>
          <Button type="text" icon={<EditOutlined />} onClick={() => handleEdit(record)} />
        </Space>
      )
    }
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic title="Totale Comuni" value={stats.total} prefix={<GlobalOutlined />} />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic title="Da ISTAT" value={stats.istat} valueStyle={{ color: '#3f8600' }} />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic title="Manuali" value={stats.manuali} valueStyle={{ color: '#cf1322' }} />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic title="Province" value={stats.province} prefix={<EnvironmentOutlined />} />
          </Card>
        </Col>
      </Row>

      <Card style={{ marginTop: 16 }}
        title={
          <Space>
            <GlobalOutlined />
            <span>Gestione Comuni Italiani</span>
          </Space>
        }
        extra={
          <Space>
            <Upload beforeUpload={handleUpload} showUploadList={false} accept=".csv,.json,.zip">
              <Button icon={<UploadOutlined />} loading={uploadLoading}>
                Carica Dati
              </Button>
            </Upload>
            <Button icon={<ReloadOutlined />} onClick={() => { fetchComuni(); fetchStats(); }}>
              Aggiorna
            </Button>
          </Space>
        }
      >
        <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
          <Col xs={24} sm={24} md={8}>
            <Input.Search
              placeholder="Cerca comune..."
              allowClear
              enterButton={<SearchOutlined />}
              onSearch={handleSearch}
              style={{ width: '100%' }}
            />
          </Col>
          <Col xs={12} sm={8} md={4}>
            <Select
              placeholder="Regione"
              style={{ width: '100%' }}
              allowClear
              value={filters.regione || undefined}
              onChange={handleRegioneFilter}
            >
              {regioni.map(r => (
                <Option key={r.codice} value={r.codice}>{r.nome}</Option>
              ))}
            </Select>
          </Col>
          <Col xs={12} sm={8} md={4}>
            <Select
              placeholder="Provincia"
              style={{ width: '100%' }}
              allowClear
              value={filters.provincia || undefined}
              onChange={handleProvinciaFilter}
              disabled={!filters.regione}
            >
              {province.map(p => (
                <Option key={p.codice} value={p.codice}>{p.nome}</Option>
              ))}
            </Select>
          </Col>
          <Col xs={24} sm={8} md={8}>
            <Text type="secondary">
              {pagination.total} comuni trovati
            </Text>
          </Col>
        </Row>

        <Table
          columns={columns}
          dataSource={comuni}
          rowKey="id"
          loading={loading}
          pagination={{
            ...pagination,
            showSizeChanger: true,
            showTotal: (total) => `Totale ${total} comuni`,
            pageSizeOptions: ['20', '50', '100', '200']
          }}
          onChange={handleTableChange}
          scroll={{ x: 800 }}
          size="small"
        />
      </Card>

      <Modal
        title={editingComune ? `Modifica: ${editingComune.nome}` : 'Nuovo Comune'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={500}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item name="nome" label="Nome Comune" rules={[{ required: true }]}>
            <Input placeholder="Es: Roma" />
          </Form.Item>
          
          <Form.Item name="denominazione" label="Denominazione completa">
            <Input placeholder="Denominazione ufficiale" />
          </Form.Item>
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="cap" label="CAP">
                <Input placeholder="00100" maxLength={5} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="codice_provincia" label="Provincia">
                <Input placeholder="RM" maxLength={3} />
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="latitudine" label="Latitudine">
                <InputNumber step={0.000001} style={{ width: '100%' }} placeholder="41.9028" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="longitudine" label="Longitudine">
                <InputNumber step={0.000001} style={{ width: '100%' }} placeholder="12.4964" />
              </Form.Item>
            </Col>
          </Row>
          
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingComune ? 'Aggiorna' : 'Crea'}
              </Button>
              <Button onClick={() => setModalVisible(false)}>Annulla</Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default ComuniPage;
