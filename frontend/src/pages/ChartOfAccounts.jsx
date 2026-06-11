import React, { useState, useEffect, useCallback } from 'react';
import { Card, Table, Button, Modal, Form, Input, Select, Space, Popconfirm, message, Tag, Switch } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { apiFetch } from '@/utils';
import { useColumnManagerWithDrawer } from '@/hooks/useColumnManager';
import ColumnSettingsButton from '@/components/ColumnSettingsButton';
import Layout from '../components/Layout';

const ACCOUNT_TYPES = [
  { value: 'asset', label: 'Attivo' },
  { value: 'liability', label: 'Passivo' },
  { value: 'equity', label: 'Patrimonio' },
  { value: 'revenue', label: 'Ricavo' },
  { value: 'expense', label: 'Costo' },
];

const ChartOfAccountsPage = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingRecord, setEditingRecord] = useState(null);
  const [form] = Form.useForm();
  const [pagination, setPagination] = useState({ current: 1, pageSize: 20, total: 0 });

  const fetchData = useCallback(async (page = 1, pageSize = 20) => {
    setLoading(true);
    try {
      const res = await apiFetch(`/api/v1/accounting/coa?page=${page}&per_page=${pageSize}`);
      if (res.ok) {
        const result = await res.json();
        setData(result.items || result || []);
        setPagination(prev => ({ ...prev, current: page, total: result.total || 0 }));
      }
    } catch (err) {
      message.error('Error loading chart of accounts');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      const payload = { ...values };

      let res;
      if (editingRecord) {
        res = await apiFetch(`/api/v1/accounting/coa/${editingRecord.id}`, {
          method: 'PUT',
          body: JSON.stringify(payload),
        });
      } else {
        res = await apiFetch('/api/v1/accounting/coa', {
          method: 'POST',
          body: JSON.stringify(payload),
        });
      }

      if (res.ok) {
        message.success(editingRecord ? 'Account aggiornato' : 'Account creato');
        setModalVisible(false);
        form.resetFields();
        setEditingRecord(null);
        fetchData();
      } else {
        const err = await res.json();
        message.error(err.message || 'Operazione fallita');
      }
    } catch (err) {
      if (err.errorFields) return;
      message.error('Validazione fallita');
    }
  };

  const handleDelete = async (id) => {
    try {
      const res = await apiFetch(`/api/v1/accounting/coa/${id}`, { method: 'DELETE' });
      if (res.ok) {
        message.success('Account disattivato');
        fetchData();
      } else {
        message.error('Eliminazione fallita');
      }
    } catch {
      message.error('Errore durante l\'eliminazione');
    }
  };

  const handleEdit = (record) => {
    setEditingRecord(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  const typeColors = {
    asset: 'blue',
    liability: 'orange',
    equity: 'purple',
    revenue: 'green',
    expense: 'red',
  };

  const rawColumns = [
    { title: 'Codice', dataIndex: 'code', key: 'code', width: 100 },
    { title: 'Nome', dataIndex: 'name', key: 'name' },
    { title: 'Tipo', dataIndex: 'type', key: 'type', width: 130, render: (v) => <Tag color={typeColors[v] || 'default'}>{v}</Tag> },
    { title: 'Attivo', dataIndex: 'is_active', key: 'is_active', width: 80, render: (v) => <Tag color={v ? 'green' : 'red'}>{v ? 'Sì' : 'No'}</Tag> },
    {
      title: 'Azioni', key: 'actions', width: 120,
      render: (_, record) => (
        <Space>
          <Button type="link" icon={<EditOutlined />} onClick={() => handleEdit(record)} />
          <Popconfirm title="Disattivare questo account?" onConfirm={() => handleDelete(record.id)}>
            <Button type="link" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const colManager = useColumnManagerWithDrawer('chartofaccounts', rawColumns);

  return (
    <Layout>
    <div style={{ padding: 24 }}>
      <Card title="Piano dei Conti"
        extra={<Space><ColumnSettingsButton manager={colManager} /><Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditingRecord(null); form.resetFields(); setModalVisible(true); }}>Nuovo Account</Button></Space>}
      >
        <Table
          dataSource={data}
          columns={colManager.processedColumns}
          rowKey="id"
          loading={loading}
          pagination={{
            ...pagination,
            onChange: (page, pageSize) => fetchData(page, pageSize),
          }}
        />
      </Card>

      <Modal
        title={editingRecord ? 'Modifica Account' : 'Nuovo Account'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => { setModalVisible(false); form.resetFields(); setEditingRecord(null); }}
        okText="Salva"
        cancelText="Annulla"
      >
        <Form form={form} layout="vertical">
          <Form.Item name="code" label="Codice" rules={[{ required: true, message: 'Inserisci il codice conto' }]}>
            <Input placeholder="es. 10.01.001" />
          </Form.Item>
          <Form.Item name="name" label="Nome" rules={[{ required: true, message: 'Inserisci il nome del conto' }]}>
            <Input placeholder="es. Cassa contanti" />
          </Form.Item>
          <Form.Item name="type" label="Tipo" rules={[{ required: true, message: 'Seleziona il tipo' }]}>
            <Select options={ACCOUNT_TYPES} placeholder="Seleziona tipo conto" />
          </Form.Item>
          <Form.Item name="is_active" label="Attivo" valuePropName="checked">
            <Switch defaultChecked />
          </Form.Item>
        </Form>
      </Modal>
    </div>
    </Layout>
  );
};

export default ChartOfAccountsPage;
