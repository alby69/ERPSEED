import React, { useState, useEffect, useCallback } from 'react';
import { Card, Table, Button, Modal, Form, Input, InputNumber, DatePicker, Select, Space, Tag, message } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { apiFetch } from '@/utils';
import { parseDateForForm, formatDateForApi, formatDateForDisplay } from '@/utils/dateUtils'; // Import date utilities
import { useColumnManagerWithDrawer } from '@/hooks/useColumnManager';
import ColumnSettingsButton from '@/components/ColumnSettingsButton';
const statusColors = { draft: 'default', submitted: 'green' };
const natureOptions = [{ value: 'A', label: 'Beni' }, { value: 'B', label: 'Servizi' }];
const typeOptions = [{ value: 'sales', label: 'Cessioni' }, { value: 'purchases', label: 'Acquisti' }];

export default function IntrastatPage() {
    const [data, setData] = useState([]);
    const [subjects, setSubjects] = useState([]);
    const [loading, setLoading] = useState(false);
    const [modalVisible, setModalVisible] = useState(false);
    const [editing, setEditing] = useState(null);
    const [form] = Form.useForm();

    const fetch = useCallback(async () => {
        setLoading(true);
        try {
            const [dRes, sRes] = await Promise.all([
                apiFetch('/api/v1/vat/intrastat'),
                apiFetch('/api/v1/soggetti'),
            ]);
            if (dRes.ok) setData(await dRes.json());
            if (sRes.ok) setSubjects(await sRes.json());
        } catch { message.error('Error'); }
        finally { setLoading(false); }
    }, []);

    useEffect(() => { fetch(); }, [fetch]);

    const handleSubmit = async () => {
        try {
            const values = await form.validateFields();
            let res;
            if (editing) res = await apiFetch(`/api/v1/vat/intrastat/${editing.id}`, { method: 'PUT', body: JSON.stringify(values) });
            else res = await apiFetch('/api/v1/vat/intrastat', { method: 'POST', body: JSON.stringify(values) });
            if (res.ok) { message.success('Salvato'); setModalVisible(false); form.resetFields(); setEditing(null); fetch(); }
            else { const e = await res.json(); message.error(e.message || 'Errore'); }
        } catch { message.error('Validation'); }
    };

    const handleSubmitDeclaration = async (id) => {
        try {
            const res = await apiFetch(`/api/v1/vat/intrastat/${id}/submit`, { method: 'POST' });
            if (res.ok) { message.success('Inviata'); fetch(); }
            else { const e = await res.json(); message.error(e.message || 'Errore'); }
        } catch { message.error('Error'); }
    };

    const handleDelete = async (id) => {
        try {
            const res = await apiFetch(`/api/v1/vat/intrastat/${id}`, { method: 'DELETE' });
            if (res.ok) { message.success('Eliminata'); fetch(); }
        } catch { message.error('Error'); }
    };

    const rawColumns = [
        { title: 'Periodo', dataIndex: 'period' },
        { title: 'Tipo', dataIndex: 'type', render: (v) => typeOptions.find(t => t.value === v)?.label || v },
        { title: 'Soggetto', dataIndex: 'soggetto_id', render: (id) => { const s = subjects.find(x => x.id === id); return s?.nome || s?.ragione_sociale || '-'; } },
        { title: 'P.IVA', dataIndex: 'soggetto_partita_iva' },
        { title: 'Nazione', dataIndex: 'soggetto_nazione' },
        { title: 'Natura', dataIndex: 'nature', render: (v) => natureOptions.find(n => n.value === v)?.label || v },
        { title: 'Importo', dataIndex: 'amount', render: (v) => `€${(v || 0).toFixed(2)}` },
        { title: 'IVA', dataIndex: 'vat_amount', render: (v) => `€${(v || 0).toFixed(2)}` },
        { title: 'Stato', dataIndex: 'status', render: (v) => <Tag color={statusColors[v]}>{v}</Tag> },
        { title: 'Azioni', render: (_, r) => (
            <Space>
                <Button type="link" size="small" icon={<EditOutlined />} onClick={() => { setEditing(r); form.setFieldsValue(r); setModalVisible(true); }}>Modifica</Button>
                {r.status === 'draft' && <Button type="link" size="small" icon={<CheckCircleOutlined />} onClick={() => handleSubmitDeclaration(r.id)}>Invia</Button>}
                <Button type="link" size="small" danger icon={<DeleteOutlined />} onClick={() => handleDelete(r.id)} />
            </Space>
        )},
    ];

    const colManager = useColumnManagerWithDrawer('intrastat', rawColumns);

    return (
        <div style={{ padding: 24 }}>
            <Card title="Intrastat" extra={
                <Space>
                    <ColumnSettingsButton manager={colManager} />
                    <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditing(null); form.resetFields(); setModalVisible(true); }}>Nuova Dichiarazione</Button>
                </Space>
            }>
                <Table dataSource={data} columns={colManager.processedColumns} rowKey="id" loading={loading} />
                <Modal title={editing ? 'Modifica Dichiarazione' : 'Nuova Dichiarazione Intrastat'} open={modalVisible} onOk={handleSubmit} onCancel={() => { setModalVisible(false); form.resetFields(); setEditing(null); }} okText="Salva" cancelText="Annulla" width={700}>
                    <Form form={form} layout="vertical">
                        <Space size={16}>
                        <Form.Item name="fiscal_year" label="Anno" rules={[{ required: true }]}><InputNumber min={2020} max={2030} /></Form.Item> {/* No change needed here */}
                        <Form.Item name="period" label="Periodo" rules={[{ required: true }]}><Input placeholder="YYYY-MM" /></Form.Item> {/* Period is a string, not a date */}
                            <Form.Item name="type" label="Tipo" rules={[{ required: true }]}>
                                <Select options={typeOptions} />
                            </Form.Item>
                            <Form.Item name="is_quarterly" label="Trimestrale">
                                <Select options={[{ value: true, label: 'Sì' }, { value: false, label: 'No' }]} />
                            </Form.Item>
                        </Space>
                        <Space size={16}>
                            <Form.Item name="soggetto_id" label="Soggetto" rules={[{ required: true }]}>
                                <Select style={{ width: 250 }} showSearch optionFilterProp="label" options={subjects.map(s => ({ value: s.id, label: s.nome || s.ragione_sociale }))} />
                            </Form.Item>
                            <Form.Item name="soggetto_partita_iva" label="P.IVA"><Input /></Form.Item>
                            <Form.Item name="soggetto_nazione" label="Nazione"><Input /></Form.Item>
                        </Space>
                        <Space size={16}>
                            <Form.Item name="nature" label="Natura">
                                <Select options={natureOptions} />
                            </Form.Item>
                            <Form.Item name="amount" label="Importo" rules={[{ required: true }]}><InputNumber min={0} prefix="€" /></Form.Item>
                            <Form.Item name="vat_amount" label="IVA"><InputNumber min={0} prefix="€" /></Form.Item>
                        </Space>
                        <Space size={16}>
                            <Form.Item name="delivery_terms" label="Consegna"><Input /></Form.Item>
                            <Form.Item name="transport" label="Trasporto"><Input /></Form.Item>
                        </Space>
                        <Form.Item name="notes" label="Note"><Input.TextArea rows={2} /></Form.Item>
                    </Form>
                </Modal>
            </Card>
        </div>
    );
};
