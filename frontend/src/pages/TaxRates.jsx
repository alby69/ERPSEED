import React, { useState, useEffect, useCallback } from 'react';
import { Card, Table, Button, Modal, Form, Input, InputNumber, Switch, DatePicker, Space, Tag, Popconfirm, message } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { apiFetch } from '@/utils';
import { parseDateForForm, formatDateForApi, formatDateForDisplay } from '@/utils/dateUtils'; // Import date utilities

const TaxRatesPage = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [modalVisible, setModalVisible] = useState(false);
    const [editingRecord, setEditingRecord] = useState(null);
    const [form] = Form.useForm();
    const [pagination, setPagination] = useState({ current: 1, pageSize: 20, total: 0 });

    const fetchData = useCallback(async (page = 1, pageSize = 20) => {
        setLoading(true);
        try {
            const res = await apiFetch(`/api/v1/tax-rates?page=${page}&per_page=${pageSize}`);
            if (res.ok) {
                const result = await res.json();
                setData(result.items || []);
                setPagination(prev => ({ ...prev, current: page, total: result.total || 0 }));
            }
        } catch (err) {
            message.error('Error loading tax rates');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => { fetchData(); }, [fetchData]);

    const handleSubmit = async () => {
        try {
            const values = await form.validateFields();
            const payload = {
                ...values,
                valid_from: formatDateForApi(values.valid_from),
                valid_to: formatDateForApi(values.valid_to),
            };

            let res;
            if (editingRecord) {
                res = await apiFetch(`/api/v1/tax-rates/${editingRecord.id}`, {
                    method: 'PUT',
                    body: JSON.stringify(payload),
                });
            } else {
                res = await apiFetch('/api/v1/tax-rates', {
                    method: 'POST',
                    body: JSON.stringify(payload),
                });
            }

            if (res.ok) {
                message.success(editingRecord ? 'Tax rate updated' : 'Tax rate created');
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
            const res = await apiFetch(`/api/v1/tax-rates/${id}`, { method: 'DELETE' });
            if (res.ok) {
                message.success('Tax rate deleted');
                fetchData();
            } else {
                message.error('Delete failed');
            }
        } catch {
            message.error('Error deleting tax rate');
        }
    };

    const handleEdit = (record) => {
        setEditingRecord(record);
        form.setFieldsValue({
            ...record,
            valid_from: parseDateForForm(record.valid_from),
            valid_to: parseDateForForm(record.valid_to),
        });
        setModalVisible(true);
    };

    const columns = [
        { title: 'Codice', dataIndex: 'code', key: 'code', width: 100 },
        { title: 'Nome', dataIndex: 'name', key: 'name' },
        { title: 'Aliquota', dataIndex: 'rate', key: 'rate', width: 120, render: (v) => `${v}%` },
        { title: 'Attivo', dataIndex: 'is_active', key: 'is_active', width: 80, render: (v) => <Tag color={v ? 'green' : 'red'}>{v ? 'Sì' : 'No'}</Tag> },
        { title: 'Dal', dataIndex: 'valid_from', key: 'valid_from', width: 120, render: (v) => formatDateForDisplay(v) || '-' },
        { title: 'Al', dataIndex: 'valid_to', key: 'valid_to', width: 120, render: (v) => formatDateForDisplay(v) || '-' },
        {
            title: 'Azioni', key: 'actions', width: 120,
            render: (_, record) => (
                <Space>
                    <Button type="link" icon={<EditOutlined />} onClick={() => handleEdit(record)} />
                    <Popconfirm title="Eliminare questa aliquota?" onConfirm={() => handleDelete(record.id)}>
                        <Button type="link" danger icon={<DeleteOutlined />} />
                    </Popconfirm>
                </Space>
            ),
        },
    ];

    return (
        <div style={{ padding: 24 }}>
            <Card
                title="Aliquote IVA"
                extra={<Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditingRecord(null); form.resetFields(); setModalVisible(true); }}>Nuova Aliquota</Button>}
            >
                <Table
                    dataSource={data}
                    columns={columns}
                    rowKey="id"
                    loading={loading}
                    pagination={{
                        ...pagination,
                        onChange: (page, pageSize) => fetchData(page, pageSize),
                    }}
                />
            </Card>

            <Modal
                title={editingRecord ? 'Modifica Aliquota IVA' : 'Nuova Aliquota IVA'}
                open={modalVisible}
                onOk={handleSubmit}
                onCancel={() => { setModalVisible(false); form.resetFields(); setEditingRecord(null); }}
                okText="Salva"
                cancelText="Annulla"
            >
                <Form form={form} layout="vertical">
                    <Form.Item name="code" label="Codice" rules={[{ required: true, message: 'Inserisci il codice' }]}>
                        <Input placeholder="es. IVA22" />
                    </Form.Item>
                    <Form.Item name="name" label="Nome" rules={[{ required: true, message: 'Inserisci il nome' }]}>
                        <Input placeholder="es. IVA 22%" />
                    </Form.Item>
                    <Form.Item name="rate" label="Aliquota (%)" rules={[{ required: true, message: 'Inserisci l\'aliquota' }]}>
                        <InputNumber min={0} max={100} step={0.01} style={{ width: '100%' }} />
                    </Form.Item>
                    <Form.Item name="description" label="Descrizione">
                        <Input.TextArea rows={2} />
                    </Form.Item>
                    <Form.Item name="valid_from" label="Valida dal">
                        <DatePicker style={{ width: '100%' }} />
                    </Form.Item>
                    <Form.Item name="valid_to" label="Valida al">
                        <DatePicker style={{ width: '100%' }} />
                    </Form.Item>
                    <Form.Item name="is_active" label="Attiva" valuePropName="checked">
                        <Switch defaultChecked />
                    </Form.Item>
                </Form>
            </Modal>
        </div>
    );
};

export default TaxRatesPage;
