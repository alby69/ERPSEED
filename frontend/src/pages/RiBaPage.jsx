import React, { useState, useEffect, useCallback } from 'react';
import { Card, Table, Button, Modal, Form, Input, InputNumber, DatePicker, Select, Space, Tag, message, Row, Col, Statistic } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, SendOutlined, CheckOutlined, CloseOutlined } from '@ant-design/icons';
import { apiFetch } from '@/utils';
import dayjs from 'dayjs'; // Keep dayjs for display in modal
import { parseDateForForm, formatDateForApi, formatDateForDisplay } from '@/utils/dateUtils'; // Import date utilities
import { useColumnManagerWithDrawer } from '@/hooks/useColumnManager';
import ColumnSettingsButton from '@/components/ColumnSettingsButton';

const statusColors = { draft: 'default', sent: 'blue', partially_collected: 'orange', collected: 'green', rejected: 'red' }; // This line was outside the component, moving it inside the export default function

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
            values.batch_date = formatDateForApi(values.batch_date);
            if (values.items) {
                values.items = values.items.map(it => ({
                    ...it, // No change needed here
                    due_date: formatDateForApi(parseDateForForm(it.due_date)), // Ensure it's a dayjs object before formatting
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
            { title: 'Soggetto', dataIndex: 'soggetto_name' }, // No change needed here
            { title: 'Importo', dataIndex: 'amount', render: (v) => `€${(v || 0).toFixed(2)}` }, // No change needed here
            { title: 'Scadenza', dataIndex: 'due_date', render: (v) => formatDateForDisplay(v) || '-' },
            { title: 'Stato', dataIndex: 'status', render: (v) => <Tag color={v === 'collected' ? 'green' : v === 'rejected' ? 'red' : 'blue'}>{v}</Tag> }, // No change needed here
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

    const rawColumns = [
        { title: 'Numero', dataIndex: 'number' }, // No change needed here
        { title: 'Data', dataIndex: 'batch_date', render: (v) => formatDateForDisplay(v) || '-' },
        { title: 'Banca', dataIndex: 'bank_name' }, // No change needed here
        { title: 'Totale', dataIndex: 'total_amount', render: (v) => `€${(v || 0).toFixed(2)}` }, // No change needed here
        { title: 'Incassato', dataIndex: 'collected_amount', render: (v) => `€${(v || 0).toFixed(2)}` }, // No change needed here
        { title: 'Stato', dataIndex: 'status', render: (v) => <Tag color={statusColors[v]}>{v}</Tag> }, // No change needed here
        { title: 'Azioni', render: (_, r) => (
            <Space>
                {r.status === 'draft' && <Button type="link" size="small" icon={<SendOutlined />} onClick={() => handleAction(r.id, 'send')}>Invia</Button>}
                <Button type="link" size="small" icon={<EditOutlined />} onClick={() => { setEditing(r); form.setFieldsValue({ ...r, batch_date: parseDateForForm(r.batch_date) }); setModalVisible(true); }}>Modifica</Button>
                <Button type="link" size="small" danger icon={<DeleteOutlined />} onClick={async () => { const res = await apiFetch(`/api/v1/riba/batches/${r.id}`, { method: 'DELETE' }); if (res.ok) { message.success('Eliminato'); fetch(); } }} />
            </Space>
        )},
    ];

    const colManager = useColumnManagerWithDrawer('riba', rawColumns);

    return (
        <div style={{ padding: 24 }}>
            <Row gutter={16} style={{ marginBottom: 16 }}>
                <Col span={6}><Card size="small"><Statistic title="Totale Invii" value={totalAmount} precision={2} prefix="€" /></Card></Col>
                <Col span={6}><Card size="small"><Statistic title="Incassato" value={collectedAmount} precision={2} prefix="€" /></Card></Col>
            </Row>
            <Card title="Ri.Ba. (Ricevute Bancarie)" extra={
                <Space>
                    <ColumnSettingsButton manager={colManager} />
                    <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditing(null); form.resetFields(); setModalVisible(true); }}>Nuovo Invio</Button>
                </Space>
            }>
                <Table dataSource={data} columns={colManager.processedColumns} rowKey="id" loading={loading} expandable={{ expandedRowRender }} />
            </Card>
            <Modal title={editing ? 'Modifica Invio' : 'Nuovo Invio Ri.Ba.'} open={modalVisible} onOk={handleSubmit} onCancel={() => { setModalVisible(false); form.resetFields(); setEditing(null); }} okText="Salva" cancelText="Annulla" width={700}>
                <Form form={form} layout="vertical">
                    <Space size={16}>
                        <Form.Item name="batch_date" label="Data" rules={[{ required: true }]}><DatePicker format={formatDateForDisplay} /></Form.Item> {/* Use formatDateForDisplay for DatePicker format */}
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
