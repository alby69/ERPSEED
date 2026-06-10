import React, { useState, useEffect, useCallback } from 'react';
import { Card, Table, Button, Modal, Form, Input, InputNumber, DatePicker, Select, Space, Tag, Popconfirm, message, Tabs, Descriptions, Divider } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, CheckCircleOutlined, StopOutlined, DollarOutlined, FileTextOutlined } from '@ant-design/icons';
import { apiFetch } from '@/utils';
import { parseDateForForm, formatDateForApi, formatDateForDisplay } from '@/utils/dateUtils';
import { useColumnManagerWithDrawer } from '@/hooks/useColumnManager';
import ColumnSettingsButton from '@/components/ColumnSettingsButton';

const statusColors = {
    draft: 'default',
    sent: 'blue',
    paid: 'green',
    cancelled: 'red',
};

const statusLabels = {
    draft: 'Bozza',
    sent: 'Inviata',
    paid: 'Pagata',
    cancelled: 'Annullata',
};

export default function Invoices() {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [total, setTotal] = useState(0);
    const [page, setPage] = useState(1);
    const [modalVisible, setModalVisible] = useState(false);
    const [editingRecord, setEditingRecord] = useState(null);
    const [soggetti, setSoggetti] = useState([]);
    const [products, setProducts] = useState([]);
    const [form] = Form.useForm();
    const [statusFilter, setStatusFilter] = useState(null);

    const fetchData = useCallback(async (p = page) => {
        setLoading(true);
        try {
            const params = new URLSearchParams({ page: p, per_page: 20 });
            if (statusFilter) params.set('status', statusFilter);
            const res = await apiFetch(`/api/v1/invoicing/invoices?${params}`);
            if (res.ok) {
                const json = await res.json();
                setData(json.items || []);
                setTotal(json.total || 0);
            } else {
                const err = await res.json();
                message.error(err.message || 'Error loading invoices');
            }
        } catch (err) {
            message.error('Error loading invoices');
        } finally {
            setLoading(false);
        }
    }, [page, statusFilter]);

    const fetchSoggetti = useCallback(async () => {
        try {
            const res = await apiFetch('/api/v1/soggetti?per_page=500');
            if (res.ok) {
                const json = await res.json();
                setSoggetti(json.items || json || []);
            }
        } catch {}
    }, []);

    const fetchProducts = useCallback(async () => {
        try {
            const res = await apiFetch('/api/v1/products?per_page=500');
            if (res.ok) {
                const json = await res.json();
                setProducts(json.items || []);
            }
        } catch {}
    }, []);

    useEffect(() => { fetchData(); fetchSoggetti(); fetchProducts(); }, [fetchData, fetchSoggetti, fetchProducts]);

    const handleSubmit = async () => {
        try {
            const values = await form.validateFields();
            const payload = {
                ...values,
                date: formatDateForApi(values.date),
                due_date: formatDateForApi(values.due_date),
                lines: values.lines?.map(l => ({
                    ...l,
                    product_id: l.product_id,
                    quantity: parseFloat(l.quantity || 1),
                    unit_price: parseFloat(l.unit_price || 0),
                    discount_percent: parseFloat(l.discount_percent || 0),
                    tax_percent: parseFloat(l.tax_percent || 0),
                })) || [],
            };
            let res;
            if (editingRecord) {
                res = await apiFetch(`/api/v1/invoicing/invoices/${editingRecord.id}`, { method: 'PUT', body: JSON.stringify(payload) });
            } else {
                res = await apiFetch('/api/v1/invoicing/invoices', { method: 'POST', body: JSON.stringify(payload) });
            }
            if (res.ok) {
                message.success(editingRecord ? 'Fattura aggiornata' : 'Fattura creata');
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

    const handleAction = async (id, action, payload = {}) => {
        try {
            const res = await apiFetch(`/api/v1/invoicing/invoices/${id}/${action}`, { method: 'POST', body: JSON.stringify(payload) });
            if (res.ok) {
                message.success('Operazione completata');
                fetchData();
            } else {
                const err = await res.json();
                message.error(err.message || 'Operation failed');
            }
        } catch {
            message.error('Operation failed');
        }
    };

    const rawColumns = [
        { title: 'Numero', dataIndex: 'invoice_number', key: 'invoice_number', width: 160 },
        { title: 'Data', dataIndex: 'date', key: 'date', width: 110, render: (v) => formatDateForDisplay(v) || '-' },
        { title: 'Cliente', dataIndex: 'party_id', key: 'party_id', render: (id) => { const s = soggetti.find(x => x.id === id); return s ? s.ragione_sociale || `${s.nome || ''} ${s.cognome || ''}` : `ID: ${id}`; } },
        { title: 'Totale', dataIndex: 'total', key: 'total', width: 120, align: 'right', render: (v) => `€ ${(v || 0).toFixed(2)}` },
        { title: 'Stato', dataIndex: 'status', key: 'status', width: 100, render: (v) => <Tag color={statusColors[v] || 'default'}>{statusLabels[v] || v}</Tag> },
        { title: 'Azioni', key: 'actions', width: 280, render: (_, r) => (
            <Space>
                {r.status === 'draft' && <Button type="link" icon={<CheckCircleOutlined />} onClick={() => handleAction(r.id, 'issue')}>Emitti</Button>}
                {r.status === 'draft' && <Button type="link" icon={<EditOutlined />} onClick={() => { setEditingRecord(r); form.setFieldsValue({ ...r, date: parseDateForForm(r.date), due_date: parseDateForForm(r.due_date) }); setModalVisible(true); }} />}
                {r.status === 'sent' && <Button type="link" icon={<DollarOutlined />} onClick={() => handleAction(r.id, 'pay', { amount: r.total })}>Paga</Button>}
                {r.status !== 'cancelled' && r.status !== 'paid' && (
                    <Popconfirm title="Annullare la fattura?" onConfirm={() => handleAction(r.id, 'cancel', { reason: 'Annullamento manuale' })}>
                        <Button type="link" danger icon={<StopOutlined />}>Annulla</Button>
                    </Popconfirm>
                )}
            </Space>
        )},
    ];

    const colManager = useColumnManagerWithDrawer('invoices', rawColumns);

    return (
        <div style={{ padding: 24 }}>
            <Card title="Fatture Emesse" extra={
                <Space>
                    <ColumnSettingsButton manager={colManager} />
                    <Select allowClear placeholder="Filtra stato" style={{ width: 140 }} value={statusFilter} onChange={(v) => { setStatusFilter(v); setPage(1); }}
                        options={[
                            { value: '', label: 'Tutti' },
                            { value: 'draft', label: 'Bozza' },
                            { value: 'sent', label: 'Inviata' },
                            { value: 'paid', label: 'Pagata' },
                            { value: 'cancelled', label: 'Annullata' },
                        ]} />
                    <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditingRecord(null); form.resetFields(); setModalVisible(true); }}>Nuova Fattura</Button>
                </Space>
            }>
                <Table dataSource={data} columns={colManager.processedColumns} rowKey="id" loading={loading}
                    pagination={{ current: page, pageSize: 20, total, onChange: setPage, showTotal: (t) => `${t} fatture` }} />
            </Card>
            <Modal title={editingRecord ? 'Modifica Fattura' : 'Nuova Fattura'} open={modalVisible} onOk={handleSubmit} onCancel={() => { setModalVisible(false); form.resetFields(); setEditingRecord(null); }}
                okText="Salva" cancelText="Annulla" width={800}>
                <Form form={form} layout="vertical">
                    <Space style={{ width: '100%' }} size={16}>
                        <Form.Item name="date" label="Data" rules={[{ required: true }]}><DatePicker format={formatDateForDisplay} /></Form.Item>
                        <Form.Item name="due_date" label="Scadenza"><DatePicker format={formatDateForDisplay} /></Form.Item>
                        <Form.Item name="party_id" label="Cliente" rules={[{ required: true }]} style={{ minWidth: 250 }}>
                            <Select showSearch placeholder="Seleziona cliente" optionFilterProp="label"
                                options={soggetti.map(s => ({ value: s.id, label: s.ragione_sociale || `${s.nome || ''} ${s.cognome || ''}` }))} />
                        </Form.Item>
                    </Space>
                    <Form.Item name="description" label="Descrizione"><Input /></Form.Item>
                    <Form.Item name="notes" label="Note"><Input.TextArea rows={2} /></Form.Item>
                    <Divider>Righe Fattura</Divider>
                    <Form.List name="lines">
                        {(fields, { add, remove }) => (
                            <>
                                {fields.map(({ key, name, ...rest }) => (
                                    <Space key={key} style={{ display: 'flex', marginBottom: 8 }} align="baseline">
                                        <Form.Item {...rest} name={[name, 'product_id']} rules={[{ required: true }]}>
                                            <Select showSearch placeholder="Prodotto" style={{ width: 200 }} optionFilterProp="label"
                                                options={products.map(p => ({ value: p.id, label: `${p.code || ''} - ${p.name}` }))} />
                                        </Form.Item>
                                        <Form.Item {...rest} name={[name, 'quantity']} rules={[{ required: true }]}>
                                            <InputNumber min={0.01} step={1} placeholder="Q.tà" style={{ width: 80 }} />
                                        </Form.Item>
                                        <Form.Item {...rest} name={[name, 'unit_price']} rules={[{ required: true }]}>
                                            <InputNumber min={0} step={0.01} prefix="€" placeholder="Prezzo" style={{ width: 120 }} />
                                        </Form.Item>
                                        <Form.Item {...rest} name={[name, 'discount_percent']}>
                                            <InputNumber min={0} max={100} step={0.5} placeholder="Sconto %" style={{ width: 90 }} />
                                        </Form.Item>
                                        <Form.Item {...rest} name={[name, 'tax_percent']}>
                                            <InputNumber min={0} max={100} step={0.1} placeholder="IVA %" style={{ width: 90 }} />
                                        </Form.Item>
                                        <Button type="link" danger onClick={() => remove(name)}>Rimuovi</Button>
                                    </Space>
                                ))}
                                <Button type="dashed" onClick={() => add({ quantity: 1, unit_price: 0, discount_percent: 0, tax_percent: 22 })} icon={<PlusOutlined />}>Aggiungi Riga</Button>
                            </>
                        )}
                    </Form.List>
                </Form>
            </Modal>
        </div>
    );
};
