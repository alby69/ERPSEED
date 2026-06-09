import React, { useState, useEffect, useCallback } from 'react';
import { Card, Table, Button, Modal, Form, Input, InputNumber, DatePicker, Tag, Select, message, Space } from 'antd';
import { PlusOutlined, EditOutlined } from '@ant-design/icons';
import { apiFetch } from '@/utils';
import dayjs from 'dayjs';

const statusColors = { draft: 'default', active: 'green', completed: 'blue', terminated: 'red', cancelled: 'orange' };

const Contracts = () => {
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
            values.start_date = values.start_date?.format('YYYY-MM-DD');
            values.end_date = values.end_date?.format('YYYY-MM-DD');
            let res;
            if (editing) res = await apiFetch(`/api/v1/contracts/${editing.id}`, { method: 'PUT', body: JSON.stringify(values) });
            else res = await apiFetch('/api/v1/contracts', { method: 'POST', body: JSON.stringify(values) });
            if (res.ok) { message.success('Salvato'); setModalVisible(false); form.resetFields(); setEditing(null); fetch(); }
            else { const e = await res.json(); message.error(e.message || 'Errore'); }
        } catch { message.error('Validation failed'); }
    };

    const columns = [
        { title: 'Numero', dataIndex: 'number' },
        { title: 'Nome', dataIndex: 'name' },
        { title: 'Cliente', dataIndex: 'party_id', render: (id) => { const s = subjects.find(x => x.id === id); return s?.nome || s?.ragione_sociale || '-'; } },
        { title: 'Inizio', dataIndex: 'start_date' },
        { title: 'Fine', dataIndex: 'end_date', render: (v) => v || '-' },
        { title: 'Valore', dataIndex: 'value', render: (v) => `€ ${(v || 0).toFixed(2)}` },
        { title: 'Stato', dataIndex: 'status', render: (v) => <Tag color={statusColors[v]}>{v}</Tag> },
        { title: 'Azioni', render: (_, r) => (
            <Button type="link" icon={<EditOutlined />} onClick={() => { setEditing(r); form.setFieldsValue({ ...r, start_date: r.start_date ? dayjs(r.start_date) : null, end_date: r.end_date ? dayjs(r.end_date) : null }); setModalVisible(true); }}>Modifica</Button>
        )},
    ];

    return (
        <div style={{ padding: 24 }}>
            <Card title="Contratti">
                <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditing(null); form.resetFields(); setModalVisible(true); }} style={{ marginBottom: 16 }}>Nuovo Contratto</Button>
                <Table dataSource={data} columns={columns} rowKey="id" loading={loading} />
                <Modal title={editing ? 'Modifica Contratto' : 'Nuovo Contratto'} open={modalVisible} onOk={handleSubmit} onCancel={() => { setModalVisible(false); form.resetFields(); setEditing(null); }} okText="Salva" cancelText="Annulla" width={700}>
                    <Form form={form} layout="vertical">
                        <Space size={16}>
                            <Form.Item name="name" label="Nome" rules={[{ required: true }]}><Input style={{ width: 250 }} /></Form.Item>
                            <Form.Item name="party_id" label="Cliente/Foraitore" rules={[{ required: true }]}>
                                <Select style={{ width: 250 }} showSearch optionFilterProp="label" options={subjects.map(s => ({ value: s.id, label: s.nome || s.ragione_sociale || `${s.name || ''} ${s.last_name || ''}` }))} />
                            </Form.Item>
                        </Space>
                        <Space size={16}>
                            <Form.Item name="start_date" label="Data Inizio" rules={[{ required: true }]}><DatePicker /></Form.Item>
                            <Form.Item name="end_date" label="Data Fine"><DatePicker /></Form.Item>
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
    );
};

export default Contracts;
