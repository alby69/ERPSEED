import React, { useState, useEffect, useCallback } from 'react';
import { Card, Table, Tabs, Button, Modal, Form, Input, InputNumber, DatePicker, Select, Space, Tag, message, Row, Col, Badge } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, SendOutlined, CheckOutlined, CloseOutlined } from '@ant-design/icons';
import { apiFetch } from '@/utils';
import dayjs from 'dayjs';

const statusColors = { draft: 'default', pending: 'orange', approved: 'green', rejected: 'red', ordered: 'blue', sent: 'geekblue', received: 'processing' };

// ========== Purchase Requests Tab ==========
const PRTab = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [modalVisible, setModalVisible] = useState(false);
    const [editing, setEditing] = useState(null);
    const [form] = Form.useForm();

    const fetch = useCallback(async () => {
        setLoading(true);
        try {
            const rRes = await apiFetch('/api/v1/purchase-requests');
            if (rRes.ok) setData(await rRes.json());
        } catch { message.error('Error'); }
        finally { setLoading(false); }
    }, []);

    useEffect(() => { fetch(); }, [fetch]);

    const handleSubmit = async () => {
        try {
            const values = await form.validateFields();
            values.request_date = values.request_date?.format('YYYY-MM-DD');
            values.required_date = values.required_date?.format('YYYY-MM-DD');
            let res;
            if (editing) res = await apiFetch(`/api/v1/purchase-requests/${editing.id}`, { method: 'PUT', body: JSON.stringify(values) });
            else res = await apiFetch('/api/v1/purchase-requests', { method: 'POST', body: JSON.stringify(values) });
            if (res.ok) { message.success('Salvato'); setModalVisible(false); form.resetFields(); setEditing(null); fetch(); }
            else { const e = await res.json(); message.error(e.message || 'Errore'); }
        } catch { message.error('Validation'); }
    };

    const handleApprove = async (id) => {
        try {
            const res = await apiFetch(`/api/v1/purchase-requests/${id}/approve`, { method: 'POST' });
            if (res.ok) { message.success('Approvata'); fetch(); }
            else { const e = await res.json(); message.error(e.message || 'Errore'); }
        } catch { message.error('Error'); }
    };

    const columns = [
        { title: '#', dataIndex: 'number' },
        { title: 'Data Richiesta', dataIndex: 'request_date' },
        { title: 'Data Richiesta', render: (_, r) => (r.lines || []).reduce((s, l) => s + (l.quantity || 0), 0), hidden: true },
        { title: 'Stato', dataIndex: 'status', render: (v) => <Tag color={statusColors[v]}>{v}</Tag> },
        { title: 'Azioni', render: (_, r) => (
            <Space>
                <Button type="link" size="small" icon={<EditOutlined />} onClick={() => { setEditing(r); form.setFieldsValue({ ...r, request_date: r.request_date ? dayjs(r.request_date) : null, required_date: r.required_date ? dayjs(r.required_date) : null }); setModalVisible(true); }}>Modifica</Button>
                {r.status === 'pending' && <Button type="link" size="small" icon={<CheckOutlined />} onClick={() => handleApprove(r.id)}>Approva</Button>}
                <Button type="link" size="small" danger icon={<DeleteOutlined />} onClick={async () => { const res = await apiFetch(`/api/v1/purchase-requests/${r.id}`, { method: 'DELETE' }); if (res.ok) { message.success('Eliminato'); fetch(); } }} />
            </Space>
        )},
    ];

    const expandedRowRender = (record) => {
        const cols = [
            { title: 'Prodotto', dataIndex: 'product_name' },
            { title: 'Quantità', dataIndex: 'quantity' },
            { title: 'Note', dataIndex: 'notes' },
        ];
        return <Table dataSource={record.lines || []} columns={cols} rowKey="id" pagination={false} size="small" />;
    };

    return (
        <>
            <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditing(null); form.resetFields(); setModalVisible(true); }} style={{ marginBottom: 16 }}>Nuova Richiesta</Button>
            <Table dataSource={data} columns={columns} rowKey="id" loading={loading} expandable={{ expandedRowRender }} />
            <Modal title={editing ? 'Modifica Richiesta' : 'Nuova Richiesta d\'Acquisto'} open={modalVisible} onOk={handleSubmit} onCancel={() => { setModalVisible(false); form.resetFields(); setEditing(null); }} okText="Salva" cancelText="Annulla" width={600}>
                <Form form={form} layout="vertical">
                    <Space size={16}>
                        <Form.Item name="request_date" label="Data Rich." rules={[{ required: true }]}><DatePicker /></Form.Item>
                        <Form.Item name="required_date" label="Data Richiesta"><DatePicker /></Form.Item>
                        <Form.Item name="status" label="Stato"><Select options={[{ value: 'draft', label: 'Bozza' }, { value: 'pending', label: 'In Attesa' }]} /></Form.Item>
                    </Space>
                    <Form.Item name="notes" label="Note"><Input.TextArea rows={2} /></Form.Item>
                </Form>
            </Modal>
        </>
    );
};

// ========== RFQ Tab ==========
const RFQTab = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [modalVisible, setModalVisible] = useState(false);
    const [editing, setEditing] = useState(null);
    const [form] = Form.useForm();

    const fetch = useCallback(async () => {
        setLoading(true);
        try {
            const rRes = await apiFetch('/api/v1/rfqs');
            if (rRes.ok) setData(await rRes.json());
        } catch { message.error('Error'); }
        finally { setLoading(false); }
    }, []);

    useEffect(() => { fetch(); }, [fetch]);

    const handleSubmit = async () => {
        try {
            const values = await form.validateFields();
            values.rfq_date = values.rfq_date?.format('YYYY-MM-DD');
            values.valid_until = values.valid_until?.format('YYYY-MM-DD');
            let res;
            if (editing) res = await apiFetch(`/api/v1/rfqs/${editing.id}`, { method: 'PUT', body: JSON.stringify(values) });
            else res = await apiFetch('/api/v1/rfqs', { method: 'POST', body: JSON.stringify(values) });
            if (res.ok) { message.success('Salvato'); setModalVisible(false); form.resetFields(); setEditing(null); fetch(); }
            else { const e = await res.json(); message.error(e.message || 'Errore'); }
        } catch { message.error('Validation'); }
    };

    const columns = [
        { title: '#', dataIndex: 'number' },
        { title: 'Data RFQ', dataIndex: 'rfq_date' },
        { title: 'Valido fino al', dataIndex: 'valid_until', render: (v) => v || '-' },
        { title: 'Preventivi', dataIndex: 'quotations', render: (q) => <Badge count={q?.length || 0} /> },
        { title: 'Stato', dataIndex: 'status', render: (v) => <Tag color={statusColors[v]}>{v}</Tag> },
        { title: 'Azioni', render: (_, r) => (
            <Space>
                <Button type="link" size="small" icon={<EditOutlined />} onClick={() => { setEditing(r); form.setFieldsValue({ ...r, rfq_date: r.rfq_date ? dayjs(r.rfq_date) : null, valid_until: r.valid_until ? dayjs(r.valid_until) : null }); setModalVisible(true); }}>Modifica</Button>
                <Button type="link" size="small" danger icon={<DeleteOutlined />} onClick={async () => { const res = await apiFetch(`/api/v1/rfqs/${r.id}`, { method: 'DELETE' }); if (res.ok) { message.success('Eliminato'); fetch(); } }} />
            </Space>
        )},
    ];

    const expandedRowRender = (record) => {
        const lineCols = [
            { title: 'Prodotto', dataIndex: 'product_name' },
            { title: 'Quantità', dataIndex: 'quantity' },
        ];
        return (
            <div>
                <Table dataSource={record.lines || []} columns={lineCols} rowKey="id" pagination={false} size="small" style={{ marginBottom: 8 }} />
                {record.quotations?.length > 0 && (
                    <Table dataSource={record.quotations} rowKey="id" size="small"
                        columns={[
                            { title: 'Fornitore', dataIndex: 'supplier_id' },
                            { title: 'Importo', dataIndex: 'total_amount', render: (v) => `€${(v || 0).toFixed(2)}` },
                            { title: 'Stato', dataIndex: 'status', render: (v) => <Tag color={statusColors[v]}>{v}</Tag> },
                        ]} />
                )}
            </div>
        );
    };

    return (
        <>
            <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditing(null); form.resetFields(); setModalVisible(true); }} style={{ marginBottom: 16 }}>Nuovo RFQ</Button>
            <Table dataSource={data} columns={columns} rowKey="id" loading={loading} expandable={{ expandedRowRender }} />
            <Modal title={editing ? 'Modifica RFQ' : 'Nuovo RFQ'} open={modalVisible} onOk={handleSubmit} onCancel={() => { setModalVisible(false); form.resetFields(); setEditing(null); }} okText="Salva" cancelText="Annulla" width={600}>
                <Form form={form} layout="vertical">
                    <Space size={16}>
                        <Form.Item name="rfq_date" label="Data RFQ" rules={[{ required: true }]}><DatePicker /></Form.Item>
                        <Form.Item name="valid_until" label="Valido fino al"><DatePicker /></Form.Item>
                        <Form.Item name="status" label="Stato"><Select options={[{ value: 'draft', label: 'Bozza' }, { value: 'sent', label: 'Inviato' }]} /></Form.Item>
                    </Space>
                    <Form.Item name="notes" label="Note"><Input.TextArea rows={2} /></Form.Item>
                </Form>
            </Modal>
        </>
    );
};

// ========== Main Page ==========
const PurchaseRequests = () => (
    <div style={{ padding: 24 }}>
        <Card title="Richieste d'Acquisto e RFQ">
            <Tabs items={[
                { key: 'requests', label: 'Richieste', children: <PRTab /> },
                { key: 'rfqs', label: 'RFQ', children: <RFQTab /> },
            ]} />
        </Card>
    </div>
);

export default PurchaseRequests;
