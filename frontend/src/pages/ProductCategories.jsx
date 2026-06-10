import React, { useState, useEffect, useCallback } from 'react';
import { Card, Table, Button, Modal, Form, Input, InputNumber, Switch, Select, Space, Tag, Popconfirm, message } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { apiFetch } from '@/utils';
import { useColumnManagerWithDrawer } from '@/hooks/useColumnManager';
import ColumnSettingsButton from '@/components/ColumnSettingsButton';

export default function ProductCategories() {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [modalVisible, setModalVisible] = useState(false);
    const [editingRecord, setEditingRecord] = useState(null);
    const [form] = Form.useForm();

    const fetchData = useCallback(async () => {
        setLoading(true);
        try {
            const res = await apiFetch('/api/v1/product-categories');
            if (res.ok) {
                setData(await res.json());
            }
        } catch (err) {
            message.error('Error loading categories');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => { fetchData(); }, [fetchData]);

    const handleSubmit = async () => {
        try {
            const values = await form.validateFields();
            let res;
            if (editingRecord) {
                res = await apiFetch(`/api/v1/product-categories/${editingRecord.id}`, {
                    method: 'PUT',
                    body: JSON.stringify(values),
                });
            } else {
                res = await apiFetch('/api/v1/product-categories', {
                    method: 'POST',
                    body: JSON.stringify(values),
                });
            }
            if (res.ok) {
                message.success(editingRecord ? 'Category updated' : 'Category created');
                setModalVisible(false);
                form.resetFields();
                setEditingRecord(null);
                fetchData();
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
            const res = await apiFetch(`/api/v1/product-categories/${id}`, { method: 'DELETE' });
            if (res.ok) {
                message.success('Category deleted');
                fetchData();
            } else {
                message.error('Delete failed');
            }
        } catch {
            message.error('Error deleting category');
        }
    };

    const rawColumns = [
        { title: 'Codice', dataIndex: 'code', key: 'code', width: 120 },
        { title: 'Nome', dataIndex: 'name', key: 'name' },
        {
            title: 'Categoria Padre', dataIndex: 'parent_id', key: 'parent_id', width: 200,
            render: (parent_id) => {
                if (!parent_id) return '-';
                const parent = data.find(c => c.id === parent_id);
                return parent ? parent.name : '-';
            }
        },
        { title: 'Ordine', dataIndex: 'sort_order', key: 'sort_order', width: 80 },
        {
            title: 'Attivo', dataIndex: 'is_active', key: 'is_active', width: 80,
            render: (v) => <Tag color={v ? 'green' : 'red'}>{v ? 'Sì' : 'No'}</Tag>
        },
        {
            title: 'Azioni', key: 'actions', width: 120,
            render: (_, record) => (
                <Space>
                    <Button type="link" icon={<EditOutlined />} onClick={() => {
                        setEditingRecord(record);
                        form.setFieldsValue(record);
                        setModalVisible(true);
                    }} />
                    <Popconfirm title="Eliminare questa categoria?" onConfirm={() => handleDelete(record.id)}>
                        <Button type="link" danger icon={<DeleteOutlined />} />
                    </Popconfirm>
                </Space>
            ),
        },
    ];

    const parentOptions = data.filter(c => c.id !== editingRecord?.id).map(c => ({
        value: c.id,
        label: c.name,
    }));

    const colManager = useColumnManagerWithDrawer('product_categories', rawColumns);

    return (
        <div style={{ padding: 24 }}>
            <Card
                title="Categorie Prodotto"
                extra={<Space><ColumnSettingsButton manager={colManager} /><Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditingRecord(null); form.resetFields(); setModalVisible(true); }}>Nuova Categoria</Button></Space>}
            >
                <Table dataSource={data} columns={colManager.processedColumns} rowKey="id" loading={loading} />
            </Card>

            <Modal
                title={editingRecord ? 'Modifica Categoria' : 'Nuova Categoria'}
                open={modalVisible}
                onOk={handleSubmit}
                onCancel={() => { setModalVisible(false); form.resetFields(); setEditingRecord(null); }}
                okText="Salva" cancelText="Annulla"
            >
                <Form form={form} layout="vertical">
                    <Form.Item name="code" label="Codice" rules={[{ required: true }]}>
                        <Input placeholder="es. ELETTRONICA" />
                    </Form.Item>
                    <Form.Item name="name" label="Nome" rules={[{ required: true }]}>
                        <Input placeholder="es. Elettronica" />
                    </Form.Item>
                    <Form.Item name="description" label="Descrizione">
                        <Input.TextArea rows={2} />
                    </Form.Item>
                    <Form.Item name="parent_id" label="Categoria Padre">
                        <Select allowClear placeholder="Nessuna (categoria radice)" options={parentOptions} />
                    </Form.Item>
                    <Form.Item name="sort_order" label="Ordine">
                        <InputNumber min={0} style={{ width: '100%' }} />
                    </Form.Item>
                    <Form.Item name="is_active" label="Attiva" valuePropName="checked">
                        <Switch defaultChecked />
                    </Form.Item>
                </Form>
            </Modal>
        </div>
    );
};
