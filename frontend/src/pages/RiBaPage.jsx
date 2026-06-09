import React, { useState, useEffect, useCallback } from 'react';
import { Card, Table, Button, Modal, Form, Input, InputNumber, DatePicker, Select, Space, Tag, message, Row, Col, Statistic } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, SendOutlined, CheckOutlined, CloseOutlined } from '@ant-design/icons';
import { apiFetch } from '@/utils';
import dayjs from 'dayjs';

const statusColors = { draft: 'default', sent: 'blue', partially_collected: 'orange', collected: 'green', rejected: 'red' };

const RiBaPage = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [modalVisible, setModalVisible] = useState(false);
    const [editing, setEditing] = useState(null);
    const [form] = Form.useForm();

    const fetch = useCallback(async () => {
        setLoading(true);
        try {
            const rRes = await apiFetch('/api/v1/riba/batches');
            if (rRes.ok) setData(await rRes.json());
        } catch { message.error('Error'); }
        finally { setLoading(false); }
    }, []);

    useEffect(() => { fetch(); }, [fetch]);

    const handleSubmit = async () => {
        try {
            const values = await form.validateFields();
            values.batch_date = values.batch_date?.format('YYYY-MM-DD');
            if (values.items) {
                values.items = values.items.map(it => ({
                    ...it,
                    due_date: it.due_date?.format ? it.due_date.format('YYYY-MM-DD') : it.due_date,
                }));
            }
            let res;
            if (editing) res = await apiFetch(`/api/v1/riba/batches/${editing.id}`, { method: 'PUT', body: JSON.stringify(values) });
            else res = await apiFetch('/api/v1/riba/batches', { method: 'POST', body: JSON.stringify(values) });
            if (res.ok) { message.success('Salvato'); setModalVisible(false); form.resetFields(); setEditing(null); fetch(); }
            else { const e = await res.json(); message.error(e.message || 'Errore'); }
        } catch { message.error('Validation'); }
    };

    const handleAction = async (id, action) => {
        try {
            const res = await apiFetch(`/api/v1/riba/batches/${id}/${action}`, { method: 'POST' });
            if (res.ok) { message.success('Ok'); fetch(); }
            else { const e = await res.json(); message.error(e.message || 'Errore'); }
        } catch { message.error('Error'); }
    };

    const handleItemAction = async (itemId, action) => {
        try {
            const res = await apiFetch(`/api/v1/riba/items/${itemId}/${action}`, { method: 'POST' });
            if (res.ok) { message.success(action === 'collect' ? 'Incassato' : 'Respinto'); fetch(); }
            else { const e = await res.json(); message.error(e.message || 'Errore'); }
        } catch { message.error('Error'); }
    };

    const totalAmount = data.reduce((s, r) => s + (r.total_amount || 0), 0);
    const collectedAmount = data.reduce((s, r) => s + (r.collected_amount || 0), 0);

    const expandedRowRender = (record) => {
        const cols = [
            { title: 'Soggetto', dataIndex: 'soggetto_name' },
            { title: 'Importo', dataIndex: 'amount', render: (v) => `€${(v || 0).toFixed(2)}` },
            { title: 'Scadenza', dataIndex: 'due_date' },
            { title: 'Stato', dataIndex: 'status', render: (v) => <Tag color={v === 'collected' ? 'green' : v === 'rejected' ? 'red' : 'blue'}>{v}</Tag> },
            { title: 'Azioni', render: (_, i) => (
                <Space>
                    {i.status === 'pending' && (
                        <>
                            <Button type="link" size="small" icon={<CheckOutlined />} onClick={() => handleItemAction(i.id, 'collect')}>Incassa</Button>
                            <Button type="link" size="small" danger icon={<CloseOutlined />} onClick={() => handleItemAction(i.id, 'reject')}>Respingi</Button>
                        </>
                    )}
                </Space>
            )},
        ];
        return <Table dataSource={record.items || []} columns={cols} rowKey="id" pagination={false} size="small" />;
    };

    const columns = [
        { title: 'Numero', dataIndex: 'number' },
        { title: 'Data', dataIndex: 'batch_date' },
        { title: 'Banca', dataIndex: 'bank_name' },
        { title: 'Totale', dataIndex: 'total_amount', render: (v) => `€${(v || 0).toFixed(2)}` },
        { title: 'Incassato', dataIndex: 'collected_amount', render: (v) => `€${(v || 0).toFixed(2)}` },
        { title: 'Stato', dataIndex: 'status', render: (v) => <Tag color={statusColors[v]}>{v}</Tag> },
        { title: 'Azioni', render: (_, r) => (
            <Space>
                {r.status === 'draft' && <Button type="link" size="small" icon={<SendOutlined />} onClick={() => handleAction(r.id, 'send')}>Invia</Button>}
                <Button type="link" size="small" icon={<EditOutlined />} onClick={() => { setEditing(r); form.setFieldsValue({ ...r, batch_date: r.batch_date ? dayjs(r.batch_date) : null }); setModalVisible(true); }}>Modifica</Button>
                <Button type="link" size="small" danger icon={<DeleteOutlined />} onClick={async () => { const res = await apiFetch(`/api/v1/riba/batches/${r.id}`, { method: 'DELETE' }); if (res.ok) { message.success('Eliminato'); fetch(); } }} />
            </Space>
        )},
    ];

    return (
        <div style={{ padding: 24 }}>
            <Row gutter={16} style={{ marginBottom: 16 }}>
                <Col span={6}><Card size="small"><Statistic title="Totale Invii" value={totalAmount} precision={2} prefix="€" /></Card></Col>
                <Col span={6}><Card size="small"><Statistic title="Incassato" value={collectedAmount} precision={2} prefix="€" /></Card></Col>
            </Row>
            <Card title="Ri.Ba. (Ricevute Bancarie)" extra={
                <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditing(null); form.resetFields(); setModalVisible(true); }}>Nuovo Invio</Button>
            }>
                <Table dataSource={data} columns={columns} rowKey="id" loading={loading} expandable={{ expandedRowRender }} />
            </Card>
            <Modal title={editing ? 'Modifica Invio' : 'Nuovo Invio Ri.Ba.'} open={modalVisible} onOk={handleSubmit} onCancel={() => { setModalVisible(false); form.resetFields(); setEditing(null); }} okText="Salva" cancelText="Annulla" width={700}>
                <Form form={form} layout="vertical">
                    <Space size={16}>
                        <Form.Item name="batch_date" label="Data" rules={[{ required: true }]}><DatePicker /></Form.Item>
                        <Form.Item name="bank_name" label="Banca"><Input style={{ width: 250 }} /></Form.Item>
                        <Form.Item name="bank_iban" label="IBAN"><Input /></Form.Item>
                    </Space>
                    <Form.Item name="notes" label="Note"><Input.TextArea rows={2} /></Form.Item>
                </Form>
            </Modal>
        </div>
    );
};

export default RiBaPage;
