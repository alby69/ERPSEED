import React, { useState, useEffect, useCallback } from 'react';
import { Card, Table, Button, Modal, Form, Input, InputNumber, DatePicker, Select, Space, Tag, Popconfirm, message, Divider } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, CheckCircleOutlined, StopOutlined } from '@ant-design/icons';
import { apiFetch } from '@/utils';
import dayjs from 'dayjs';

const statusColors = { draft: 'default', confirmed: 'blue', received: 'green', cancelled: 'red' };
const statusLabels = { draft: 'Bozza', confirmed: 'Confermato', received: 'Ricevuto', cancelled: 'Annullato' };

const PurchaseOrders = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [total, setTotal] = useState(0);
    const [page, setPage] = useState(1);
    const [modalVisible, setModalVisible] = useState(false);
    const [editingRecord, setEditingRecord] = useState(null);
    const [form] = Form.useForm();
    const [suppliers, setSuppliers] = useState([]);
    const [products, setProducts] = useState([]);
    const [statusFilter, setStatusFilter] = useState(null);

    const fetchData = useCallback(async () => {
        setLoading(true);
        try {
            const params = new URLSearchParams({ page, per_page: 20 });
            if (statusFilter) params.set('status', statusFilter);
            const res = await apiFetch(`/api/v1/purchases?${params}`);
            if (res.ok) {
                const json = await res.json();
                setData(json.items || []);
                setTotal(json.total || 0);
            }
        } catch { message.error('Error loading orders'); }
        finally { setLoading(false); }
    }, [page, statusFilter]);

    const fetchLookups = useCallback(async () => {
        try {
            const [sRes, pRes] = await Promise.all([
                apiFetch('/api/v1/soggetti?per_page=500'),
                apiFetch('/api/v1/products?per_page=500'),
            ]);
            if (sRes.ok) { const j = await sRes.json(); setSuppliers(j.items || j || []); }
            if (pRes.ok) { const j = await pRes.json(); setProducts(j.items || []); }
        } catch {}
    }, []);

    useEffect(() => { fetchData(); fetchLookups(); }, [fetchData, fetchLookups]);

    const handleSubmit = async () => {
        try {
            const values = await form.validateFields();
            const payload = {
                ...values,
                date: values.date?.format('YYYY-MM-DD'),
                expected_date: values.expected_date?.format('YYYY-MM-DD'),
                lines: values.lines?.map(l => ({
                    product_id: l.product_id,
                    description: l.description,
                    quantity: parseFloat(l.quantity || 1),
                    unit_price: parseFloat(l.unit_price || 0),
                })) || [],
            };
            let res;
            if (editingRecord) {
                res = await apiFetch(`/api/v1/purchases/${editingRecord.id}`, { method: 'PUT', body: JSON.stringify(payload) });
            } else {
                res = await apiFetch('/api/v1/purchases', { method: 'POST', body: JSON.stringify(payload) });
            }
            if (res.ok) { message.success('Salvato'); setModalVisible(false); form.resetFields(); setEditingRecord(null); fetchData(); }
            else { const e = await res.json(); message.error(e.message || 'Errore'); }
        } catch { message.error('Validation failed'); }
    };

    const handleAction = async (id, action) => {
        const res = await apiFetch(`/api/v1/purchases/${id}/${action}`, { method: 'POST' });
        if (res.ok) { message.success('Operazione completata'); fetchData(); }
        else { const e = await res.json(); message.error(e.message || 'Errore'); }
    };

    const columns = [
        { title: 'Numero', dataIndex: 'number', key: 'number' },
        { title: 'Data', dataIndex: 'date', key: 'date', render: (v) => v ? dayjs(v).format('DD/MM/YYYY') : '-' },
        { title: 'Fornitore', dataIndex: 'supplier_id', key: 'supplier_id', render: (id) => { const s = suppliers.find(x => x.id === id); return s ? s.ragione_sociale || `${s.nome || ''} ${s.cognome || ''}` : `ID: ${id}`; } },
        { title: 'Totale', dataIndex: 'total_amount', key: 'total_amount', align: 'right', render: (v) => `€ ${(v || 0).toFixed(2)}` },
        { title: 'Stato', dataIndex: 'status', key: 'status', render: (v) => <Tag color={statusColors[v]}>{statusLabels[v] || v}</Tag> },
        { title: 'Azioni', key: 'actions', render: (_, r) => (
            <Space>
                {r.status === 'draft' && <Button type="link" icon={<CheckCircleOutlined />} onClick={() => handleAction(r.id, 'confirm')}>Conferma</Button>}
                {r.status === 'draft' && <Button type="link" icon={<EditOutlined />} onClick={() => { setEditingRecord(r); form.setFieldsValue({ ...r, date: r.date ? dayjs(r.date) : null, expected_date: r.expected_date ? dayjs(r.expected_date) : null }); setModalVisible(true); }} />}
                {r.status === 'confirmed' && <Button type="link" icon={<CheckCircleOutlined />} onClick={() => handleAction(r.id, 'receive')}>Ricevi</Button>}
                {r.status !== 'cancelled' && <Popconfirm title="Annullare?" onConfirm={() => handleAction(r.id, 'cancel')}><Button type="link" danger icon={<StopOutlined />}>Annulla</Button></Popconfirm>}
            </Space>
        )},
    ];

    return (
        <div style={{ padding: 24 }}>
            <Card title="Ordini Acquisto" extra={
                <Space>
                    <Select allowClear placeholder="Filtra stato" style={{ width: 140 }} value={statusFilter} onChange={(v) => { setStatusFilter(v); setPage(1); }}
                        options={[
                            { value: '', label: 'Tutti' }, { value: 'draft', label: 'Bozza' },
                            { value: 'confirmed', label: 'Confermato' }, { value: 'received', label: 'Ricevuto' },
                            { value: 'cancelled', label: 'Annullato' },
                        ]} />
                    <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditingRecord(null); form.resetFields(); setModalVisible(true); }}>Nuovo Ordine</Button>
                </Space>
            }>
                <Table dataSource={data} columns={columns} rowKey="id" loading={loading}
                    pagination={{ current: page, pageSize: 20, total, onChange: setPage, showTotal: (t) => `${t} ordini` }} />
            </Card>
            <Modal title={editingRecord ? 'Modifica Ordine' : 'Nuovo Ordine Acquisto'} open={modalVisible} onOk={handleSubmit} onCancel={() => { setModalVisible(false); form.resetFields(); setEditingRecord(null); }} okText="Salva" cancelText="Annulla" width={800}>
                <Form form={form} layout="vertical">
                    <Space style={{ width: '100%' }} size={16}>
                        <Form.Item name="number" label="Numero Ordine"><Input placeholder="Auto-generato" /></Form.Item>
                        <Form.Item name="date" label="Data"><DatePicker /></Form.Item>
                        <Form.Item name="expected_date" label="Data Prevista"><DatePicker /></Form.Item>
                    </Space>
                    <Form.Item name="supplier_id" label="Fornitore" rules={[{ required: true }]}>
                        <Select showSearch placeholder="Seleziona fornitore" optionFilterProp="label"
                            options={suppliers.map(s => ({ value: s.id, label: s.ragione_sociale || `${s.nome || ''} ${s.cognome || ''}` }))} />
                    </Form.Item>
                    <Form.Item name="notes" label="Note"><Input.TextArea rows={2} /></Form.Item>
                    <Divider>Righe Ordine</Divider>
                    <Form.List name="lines">
                        {(fields, { add, remove }) => (
                            <>
                                {fields.map(({ key, name, ...rest }) => (
                                    <Space key={key} style={{ display: 'flex', marginBottom: 8 }} align="baseline">
                                        <Form.Item {...rest} name={[name, 'product_id']} rules={[{ required: true }]}>
                                            <Select showSearch placeholder="Prodotto" style={{ width: 200 }} optionFilterProp="label"
                                                options={products.map(p => ({ value: p.id, label: `${p.code || ''} - ${p.name}` }))} />
                                        </Form.Item>
                                        <Form.Item {...rest} name={[name, 'description']}>
                                            <Input placeholder="Descrizione" style={{ width: 200 }} />
                                        </Form.Item>
                                        <Form.Item {...rest} name={[name, 'quantity']} rules={[{ required: true }]}>
                                            <InputNumber min={0.01} step={1} placeholder="Q.tà" style={{ width: 80 }} />
                                        </Form.Item>
                                        <Form.Item {...rest} name={[name, 'unit_price']} rules={[{ required: true }]}>
                                            <InputNumber min={0} step={0.01} prefix="€" placeholder="Prezzo" style={{ width: 120 }} />
                                        </Form.Item>
                                        <Button type="link" danger onClick={() => remove(name)}>Rimuovi</Button>
                                    </Space>
                                ))}
                                <Button type="dashed" onClick={() => add({ quantity: 1, unit_price: 0 })} icon={<PlusOutlined />}>Aggiungi Riga</Button>
                            </>
                        )}
                    </Form.List>
                </Form>
            </Modal>
        </div>
    );
};

export default PurchaseOrders;
