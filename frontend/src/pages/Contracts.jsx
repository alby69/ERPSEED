import React, { useState, useEffect, useCallback } from 'react';
import { Card, Table, Button, Modal, Form, Input, InputNumber, DatePicker, Tag, Select, message, Space } from 'antd';
import { PlusOutlined, EditOutlined } from '@ant-design/icons';
import { apiFetch } from '@/utils';
import { parseDateForForm, formatDateForApi, formatDateForDisplay } from '@/utils/dateUtils'; // Import date utilities
import { useColumnManagerWithDrawer } from '@/hooks/useColumnManager';
import ColumnSettingsButton from '@/components/ColumnSettingsButton';
import Layout from '../components/Layout';

const statusColors = { draft: 'default', active: 'green', completed: 'blue', terminated: 'red', cancelled: 'orange' };

export default function Contracts() {
    const [data, setData] = useState([]);
    const [subjects, setSubjects] = useState([]);
    const [loading, setLoading] = useState(false);
    const [modalVisible, setModalVisible] = useState(false);
    const [editing, setEditing] = useState(null);
    const [form] = Form.useForm();

    const fetch = useCallback(async () => {
        setLoading(true);
        try {
            const [cRes, sRes] = await Promise.all([
                apiFetch('/api/v1/contracts'),
                apiFetch('/api/v1/soggetti'),
            ]);
            if (cRes.ok) setData(await cRes.json());
            if (sRes.ok) setSubjects(await sRes.json());
        } catch { message.error('Error loading'); }
        finally { setLoading(false); }
    }, []);

    useEffect(() => { fetch(); }, [fetch]);

    const handleSubmit = async () => {
        try {
            const values = await form.validateFields();
            values.start_date = formatDateForApi(values.start_date);
            values.end_date = formatDateForApi(values.end_date);
            let res;
            if (editing) res = await apiFetch(`/api/v1/contracts/${editing.id}`, { method: 'PUT', body: JSON.stringify(values) });
            else res = await apiFetch('/api/v1/contracts', { method: 'POST', body: JSON.stringify(values) });
            if (res.ok) { message.success('Salvato'); setModalVisible(false); form.resetFields(); setEditing(null); fetch(); }
            else { const e = await res.json(); message.error(e.message || 'Errore'); }
        } catch { message.error('Validation failed'); }
    };

    const rawColumns = [
        { title: 'Numero', dataIndex: 'number', key: 'number' },
        { title: 'Nome', dataIndex: 'name', key: 'name' },
        { title: 'Cliente', dataIndex: 'party_id', key: 'party_id', render: (id) => { const s = subjects.find(x => x.id === id); return s?.nome || s?.ragione_sociale || '-'; } },
        { title: 'Inizio', dataIndex: 'start_date', key: 'start_date', render: (v) => formatDateForDisplay(v) || '-' },
        { title: 'Fine', dataIndex: 'end_date', key: 'end_date', render: (v) => formatDateForDisplay(v) || '-' },
        { title: 'Valore', dataIndex: 'value', key: 'value', render: (v) => `€ ${(v || 0).toFixed(2)}` },
        { title: 'Stato', dataIndex: 'status', key: 'status', render: (v) => <Tag color={statusColors[v]}>{v}</Tag> },
        { title: 'Azioni', key: 'actions', render: (_, r) => (
            <Button type="link" icon={<EditOutlined />} onClick={() => { setEditing(r); form.setFieldsValue({ ...r, start_date: parseDateForForm(r.start_date), end_date: parseDateForForm(r.end_date) }); setModalVisible(true); }}>Modifica</Button>
        )},
    ];

    const colManager = useColumnManagerWithDrawer('contracts', rawColumns);

    return (
        <Layout>
            <div style={{ padding: 24 }}>
                <Card title="Vendite (Contratti)" extra={<ColumnSettingsButton manager={colManager} />}>
                    <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditing(null); form.resetFields(); setModalVisible(true); }} style={{ marginBottom: 16 }}>Nuovo Contratto</Button>
                    <Table dataSource={data} columns={colManager.processedColumns} rowKey="id" loading={loading} />
                    <Modal title={editing ? 'Modifica Contratto' : 'Nuovo Contratto'} open={modalVisible} onOk={handleSubmit} onCancel={() => { setModalVisible(false); form.resetFields(); setEditing(null); }} okText="Salva" cancelText="Annulla" width={700}>
                        <Form form={form} layout="vertical">
                            <Space size={16}>
                                <Form.Item name="name" label="Nome" rules={[{ required: true }]}><Input style={{ width: 250 }} /></Form.Item>
                                <Form.Item name="party_id" label="Cliente/Foraitore" rules={[{ required: true }]}>
                                    <Select style={{ width: 250 }} showSearch optionFilterProp="label" options={subjects.map(s => ({ value: s.id, label: s.nome || s.ragione_sociale || `${s.name || ''} ${s.last_name || ''}` }))} />
                                </Form.Item>
                            </Space>
                            <Space size={16}> {/* Use formatDateForDisplay for DatePicker format */}
                                <Form.Item name="start_date" label="Data Inizio" rules={[{ required: true }]}><DatePicker format={formatDateForDisplay} /></Form.Item>
                                <Form.Item name="end_date" label="Data Fine"><DatePicker format={formatDateForDisplay} /></Form.Item>
                                <Form.Item name="value" label="Valore"><InputNumber min={0} step={100} prefix="€" /></Form.Item>
                                <Form.Item name="status" label="Stato"><Select options={[{ value: 'draft', label: 'Bozza' }, { value: 'active', label: 'Attivo' }, { value: 'completed', label: 'Completato' }, { value: 'terminated', label: 'Cessato' }, { value: 'cancelled', label: 'Annullato' }]} /></Form.Item>
                            </Space>
                            <Form.Item name="notes" label="Note"><Input.TextArea rows={3} /></Form.Item>
                            <Space size={16}>
                                <Form.Item name="auto_renew" label="Rinnovo Automatico"><Select options={[{ value: true, label: 'Sì' }, { value: false, label: 'No' }]} /></Form.Item>
                                <Form.Item name="renewal_notice_days" label="Giorni Preavviso"><InputNumber min={0} /></Form.Item>
                            </Space>
                        </Form>
                    </Modal>
                </Card>
            </div>
        </Layout>
    );
};
