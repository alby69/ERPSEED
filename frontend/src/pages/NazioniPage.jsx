import React, { useState, useEffect, useCallback } from 'react';
import { Card, Table, Button, Modal, Form, Input, Select, Space, message, Tag } from 'antd';
import { PlusOutlined, EditOutlined, SearchOutlined, GlobalOutlined } from '@ant-design/icons';
import { apiFetch } from '@/utils';
import Layout from '@/components/Layout';

const CONTINENTI = {
  AF: { label: 'Africa', color: 'orange' },
  AS: { label: 'Asia', color: 'red' },
  EU: { label: 'Europa', color: 'blue' },
  NA: { label: 'Nord America', color: 'cyan' },
  SA: { label: 'Sud America', color: 'green' },
  OC: { label: 'Oceania', color: 'purple' },
};

const NazioniPage = () => {
  const [nazioni, setNazioni] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 50, total: 0 });
  const [search, setSearch] = useState('');
  const [modalVisible, setModalVisible] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form] = Form.useForm();

  const fetchNazioni = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: pagination.current,
        per_page: pagination.pageSize,
      });
      if (search) params.append('q', search);
      const response = await apiFetch(`/api/v1/nazioni?${params}`);
      if (response.ok) {
        const data = await response.json();
        setNazioni(data.items || []);
        setPagination(prev => ({ ...prev, total: data.total || 0 }));
      }
    } catch {
      message.error('Errore nel caricamento');
    } finally {
      setLoading(false);
    }
  }, [pagination.current, pagination.pageSize, search]);

  useEffect(() => { fetchNazioni(); }, [fetchNazioni]);

  const handleEdit = (record) => {
    setEditing(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  const handleCreate = () => {
    setEditing(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleSubmit = async (values) => {
    try {
      const url = editing ? `/api/v1/nazioni/${editing.codice_iso}` : '/api/v1/nazioni';
      const method = editing ? 'PUT' : 'POST';
      const body = editing ? values : values;
      const response = await apiFetch(url, { method, body: JSON.stringify(body) });
      if (response.ok) {
        message.success(editing ? 'Nazione aggiornata' : 'Nazione creata');
        setModalVisible(false);
        fetchNazioni();
      }
    } catch (err) {
      message.error(err.message);
    }
  };

  const columns = [
    { title: 'ISO', dataIndex: 'codice_iso', key: 'codice_iso', width: 70 },
    { title: 'ISO2', dataIndex: 'codice_iso2', key: 'codice_iso2', width: 60 },
    { title: 'Nome', dataIndex: 'nome', key: 'nome', width: 200 },
    {
      title: 'Continente', dataIndex: 'continente', key: 'continente', width: 120,
      render: (text) => {
        const c = CONTINENTI[text];
        return c ? <Tag color={c.color}>{c.label}</Tag> : text;
      }
    },
    { title: 'Nazionalità', dataIndex: 'nazionalita', key: 'nazionalita', width: 150 },
    { title: 'Valuta', dataIndex: 'valuta', key: 'valuta', width: 70 },
    { title: 'Prefisso', dataIndex: 'prefisso_telefonico', key: 'prefisso_telefonico', width: 80 },
    {
      title: 'Azioni', key: 'azioni', width: 60,
      render: (_, record) => (
        <Button type="text" icon={<EditOutlined />} onClick={() => handleEdit(record)} />
      ),
    },
  ];

  return (
    <Layout>
      <div style={{ padding: '0' }}>
        <Card
          title={<Space><GlobalOutlined /><span>Nazioni</span></Space>}
          extra={
            <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
              Nuova Nazione
            </Button>
          }
        >
          <Input.Search
            placeholder="Cerca nazione..."
            allowClear
            onSearch={setSearch}
            style={{ marginBottom: 16, width: 300 }}
          />
          <Table
            dataSource={nazioni}
            columns={columns}
            rowKey="codice_iso"
            loading={loading}
            pagination={{
              current: pagination.current,
              pageSize: pagination.pageSize,
              total: pagination.total,
              showSizeChanger: true,
              showTotal: (t) => `${t} nazioni`,
            }}
            onChange={(p) => setPagination(prev => ({ ...prev, current: p.current, pageSize: p.pageSize }))}
            scroll={{ x: 900 }}
            size="small"
          />
        </Card>

        <Modal
          title={editing ? 'Modifica Nazione' : 'Nuova Nazione'}
          open={modalVisible}
          onCancel={() => setModalVisible(false)}
          onOk={() => form.submit()}
          width={600}
        >
          <Form form={form} layout="vertical" onFinish={handleSubmit}>
            <Form.Item name="codice_iso" label="Codice ISO (3 lettere)" rules={[{ required: true, len: 3 }]}>
              <Input disabled={!!editing} maxLength={3} style={{ textTransform: 'uppercase' }} />
            </Form.Item>
            <Form.Item name="codice_iso2" label="Codice ISO (2 lettere)" rules={[{ required: true, len: 2 }]}>
              <Input disabled={!!editing} maxLength={2} style={{ textTransform: 'uppercase' }} />
            </Form.Item>
            <Form.Item name="nome" label="Nome (italiano)" rules={[{ required: true }]}>
              <Input />
            </Form.Item>
            <Form.Item name="nome_inglese" label="Nome (inglese)">
              <Input />
            </Form.Item>
            <Form.Item name="continente" label="Continente">
              <Select allowClear>
                {Object.entries(CONTINENTI).map(([k, v]) => (
                  <Select.Option key={k} value={k}>{v.label}</Select.Option>
                ))}
              </Select>
            </Form.Item>
            <Form.Item name="nazionalita" label="Nazionalità">
              <Input />
            </Form.Item>
            <Form.Item name="valuta" label="Valuta (ISO 4217)">
              <Input maxLength={3} style={{ textTransform: 'uppercase' }} />
            </Form.Item>
            <Form.Item name="prefisso_telefonico" label="Prefisso telefonico">
              <Input placeholder="+39" />
            </Form.Item>
          </Form>
        </Modal>
      </div>
    </Layout>
  );
};

export default NazioniPage;
