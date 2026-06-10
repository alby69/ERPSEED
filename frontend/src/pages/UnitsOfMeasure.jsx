import React, { useState, useEffect, useCallback } from 'react';
import { Card, Table, Button, Modal, Form, Input, Switch, Space, Tag, Popconfirm, message } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { apiFetch } from '@/utils';
import { useColumnManagerWithDrawer } from '@/hooks/useColumnManager';
import ColumnSettingsButton from '@/components/ColumnSettingsButton';

export default function UnitsOfMeasure() {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [modalVisible, setModalVisible] = useState(false);
    const [editingRecord, setEditingRecord] = useState(null);
    const [form] = Form.useForm();

    const fetchData = useCallback(async () => {
        setLoading(true);
        try {
            const res = await apiFetch('/api/v1/units-of-measure');
            if (res.ok) setData(await res.json());
        } catch { message.error('Error loading units of measure'); }
        finally { setLoading(false); }
    }, []);

    useEffect(() => { fetchData(); }, [fetchData]);

    const handleSubmit = async () => {
        try {
            const values = await form.validateFields();
            let res;
            if (editingRecord) {
                res = await apiFetch(`/api/v1/units-of-measure/${editingRecord.id}`, { method: 'PUT', body: JSON.stringify(values) });
            } else {
                res = await apiFetch('/api/v1/units-of-measure', { method: 'POST', body: JSON.stringify(values) });
            }
            if (res.ok) {
                message.success(editingRecord ? 'Updated' : 'Created');
                setModalVisible(false); form.resetFields(); setEditingRecord(null); fetchData();
            } else {
                const err = await res.json();
                message.error(err.message || 'Operation failed');
            }
        } catch (err) {
            if (err.errorFields) return;
            message.error('Validation failed');
        }
    };

    const handleDelete = async (id) => {
        try {
            const res = await apiFetch(`/api/v1/units-of-measure/${id}`, { method: 'DELETE' });
            if (res.ok) { message.success('Deleted'); fetchData(); }
            else message.error('Delete failed');
        } catch { message.error('Error deleting'); }
    };

    const rawColumns = [
        { title: 'Codice', dataIndex: 'code', key: 'code', width: 100 },
        { title: 'Nome', dataIndex: 'name', key: 'name' },
        { title: 'Simbolo', dataIndex: 'symbol', key: 'symbol', width: 80 },
        { title: 'Descrizione', dataIndex: 'description', key: 'description' },
        { title: 'Attivo', dataIndex: 'is_active', key: 'is_active', width: 80, render: (v) => <Tag color={v ? 'green' : 'red'}>{v ? 'Sì' : 'No'}</Tag> },
        { title: 'Azioni', key: 'actions', width: 120, render: (_, r) => (
            <Space>
                <Button type="link" icon={<EditOutlined />} onClick={() => { setEditingRecord(r); form.setFieldsValue(r); setModalVisible(true); }} />
                <Popconfirm title="Eliminare?" onConfirm={() => handleDelete(r.id)}>
                    <Button type="link" danger icon={<DeleteOutlined />} />
                </Popconfirm>
            </Space>
        )},
    ];

    const colManager = useColumnManagerWithDrawer('udm', rawColumns);

    return (
        <div style={{ padding: 24 }}>
            <Card title="Unità di Misura" extra={<Space><ColumnSettingsButton manager={colManager} /><Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditingRecord(null); form.resetFields(); setModalVisible(true); }}>Nuova UM</Button></Space>}>
                <Table dataSource={data} columns={colManager.processedColumns} rowKey="id" loading={loading} />
            </Card>
            <Modal title={editingRecord ? 'Modifica UM' : 'Nuova UM'} open={modalVisible}
                onOk={handleSubmit} onCancel={() => { setModalVisible(false); form.resetFields(); setEditingRecord(null); }}
                okText="Salva" cancelText="Annulla">
                <Form form={form} layout="vertical">
                    <Form.Item name="code" label="Codice" rules={[{ required: true }]}><Input placeholder="es. KG" /></Form.Item>
                    <Form.Item name="name" label="Nome" rules={[{ required: true }]}><Input placeholder="es. Chilogrammo" /></Form.Item>
                    <Form.Item name="symbol" label="Simbolo"><Input placeholder="es. kg" /></Form.Item>
                    <Form.Item name="description" label="Descrizione"><Input.TextArea rows={2} /></Form.Item>
                    <Form.Item name="is_active" label="Attiva" valuePropName="checked"><Switch defaultChecked /></Form.Item>
                </Form>
            </Modal>
        </div>
    );
};
