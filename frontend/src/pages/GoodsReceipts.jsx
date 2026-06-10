import React, { useState, useEffect, useCallback } from 'react';
import { Card, Table, Button, Modal, Form, Input, InputNumber, DatePicker, Select, Space, Tag, Popconfirm, message, Divider } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { apiFetch } from '@/utils';
import { parseDateForForm, formatDateForApi, formatDateForDisplay } from '@/utils/dateUtils';
import { useColumnManagerWithDrawer } from '@/hooks/useColumnManager';
import ColumnSettingsButton from '@/components/ColumnSettingsButton';

const statusColors = { draft: 'default', completed: 'green', cancelled: 'red' };
const statusLabels = { draft: 'Bozza', completed: 'Completato', cancelled: 'Annullato' };

export default function GoodsReceipts() {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [modalVisible, setModalVisible] = useState(false);
    const [editingRecord, setEditingRecord] = useState(null);
    const [form] = Form.useForm();
    const [suppliers, setSuppliers] = useState([]);
    const [products, setProducts] = useState([]);
    const [locations, setLocations] = useState([]);
    const [purchaseOrders, setPurchaseOrders] = useState([]);

    const fetchData = useCallback(async () => {
        setLoading(true);
        try {
            const res = await apiFetch('/api/v1/goods-receipts');
            if (res.ok) setData(await res.json());
        } catch { message.error('Error loading'); }
        finally { setLoading(false); }
    }, []);

    const fetchLookups = useCallback(async () => {
        try {
            const [sRes, pRes, lRes, poRes] = await Promise.all([
                apiFetch('/api/v1/soggetti?per_page=500'),
                apiFetch('/api/v1/products?per_page=500'),
                apiFetch('/inventory/locations'),
                apiFetch('/api/v1/purchases?per_page=100'),
            ]);
            if (sRes.ok) { const j = await sRes.json(); setSuppliers(j.items || j || []); }
            if (pRes.ok) { const j = await pRes.json(); setProducts(j.items || []); }
            if (lRes.ok) setLocations(await lRes.json());
            if (poRes.ok) { const j = await poRes.json(); setPurchaseOrders(j.items || []); }
        } catch {}
    }, []);

    useEffect(() => { fetchData(); fetchLookups(); }, [fetchData, fetchLookups]);

    const handleSubmit = async () => {
        try {
            const values = await form.validateFields();
            const payload = {
                ...values,
                date: formatDateForApi(values.date),
                lines: values.lines?.map(l => ({
                    product_id: l.product_id,
                    quantity: parseFloat(l.quantity || 1),
                    location_id: l.location_id || 1,
                    description: l.description || '',
                })) || [],
            };
            let res;
            if (editingRecord) {
                res = await apiFetch(`/api/v1/goods-receipts/${editingRecord.id}`, { method: 'PUT', body: JSON.stringify(payload) });
            } else {
                res = await apiFetch('/api/v1/goods-receipts', { method: 'POST', body: JSON.stringify(payload) });
            }
            if (res.ok) { message.success('Salvato'); setModalVisible(false); form.resetFields(); setEditingRecord(null); fetchData(); }
            else { const e = await res.json(); message.error(e.message || 'Errore'); }
        } catch { message.error('Validation failed'); }
    };

    const handleComplete = async (id) => {
        const res = await apiFetch(`/api/v1/goods-receipts/${id}/complete`, { method: 'POST' });
        if (res.ok) { message.success('DDT Completato — carico generato'); fetchData(); }
        else { const e = await res.json(); message.error(e.message || 'Errore'); }
    };

    const handleDelete = async (id) => {
        const res = await apiFetch(`/api/v1/goods-receipts/${id}`, { method: 'DELETE' });
        if (res.ok) { message.success('Eliminato'); fetchData(); }
    };

    const rawColumns = [
        { title: 'Numero', dataIndex: 'number', key: 'number' },
        { title: 'Data', dataIndex: 'date', key: 'date', render: (v) => formatDateForDisplay(v) || '-' },
        { title: 'Fornitore', dataIndex: 'supplier_id', key: 'supplier_id', render: (id) => { const s = suppliers.find(x => x.id === id); return s ? s.ragione_sociale || `${s.nome || ''} ${s.cognome || ''}` : `ID: ${id}`; } },
        { title: 'Stato', dataIndex: 'status', key: 'status', render: (v) => <Tag color={statusColors[v]}>{statusLabels[v] || v}</Tag> },
        { title: 'Azioni', key: 'actions', render: (_, r) => (
            <Space>
                {r.status === 'draft' && <Button type="link" icon={<CheckCircleOutlined />} onClick={() => handleComplete(r.id)}>Completa</Button>}
                {r.status === 'draft' && <Button type="link" icon={<EditOutlined />} onClick={() => { setEditingRecord(r); form.setFieldsValue({ ...r, date: parseDateForForm(r.date) }); setModalVisible(true); }} />}
                {r.status === 'draft' && <Popconfirm title="Eliminare?" onConfirm={() => handleDelete(r.id)}><Button type="link" danger icon={<DeleteOutlined />} /></Popconfirm>}
            </Space>
        )},
    ];

    const colManager = useColumnManagerWithDrawer('goods_receipts', rawColumns);

    return (
        <div style={{ padding: 24 }}>
            <Card title="DDT Entrata Merci" extra={<Space><ColumnSettingsButton manager={colManager} /><Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditingRecord(null); form.resetFields(); setModalVisible(true); }}>Nuovo DDT</Button></Space>}>
                <Table dataSource={data} columns={colManager.processedColumns} rowKey="id" loading={loading}
                    expandedRowRender={(r) => r.lines ? (
                        <Table dataSource={r.lines} rowKey="id" size="small" pagination={false}
                            columns={[
                                { title: 'Prodotto', dataIndex: 'product_id', key: 'product_id', render: (id) => { const p = products.find(x => x.id === id); return p ? `${p.code || ''} - ${p.name}` : `ID: ${id}`; } },
                                { title: 'Q.tà', dataIndex: 'quantity', key: 'quantity' },
                                { title: 'Descrizione', dataIndex: 'description', key: 'description' },
                            ]} />
                    ) : null}
                />
            </Card>
            <Modal title={editingRecord ? 'Modifica DDT' : 'Nuovo DDT Entrata'} open={modalVisible} onOk={handleSubmit} onCancel={() => { setModalVisible(false); form.resetFields(); setEditingRecord(null); }} okText="Salva" cancelText="Annulla" width={800}>
                <Form form={form} layout="vertical">
                    <Space style={{ width: '100%' }} size={16}>
                        <Form.Item name="date" label="Data" rules={[{ required: true }]}><DatePicker format={formatDateForDisplay} /></Form.Item>
                        <Form.Item name="supplier_id" label="Fornitore" rules={[{ required: true }]} style={{ minWidth: 250 }}>
                            <Select showSearch placeholder="Seleziona fornitore" optionFilterProp="label"
                                options={suppliers.map(s => ({ value: s.id, label: s.ragione_sociale || `${s.nome || ''} ${s.cognome || ''}` }))} />
                        </Form.Item>
                        <Form.Item name="purchase_order_id" label="Ordine Acquisto">
                            <Select allowClear showSearch placeholder="(opzionale)" style={{ width: 200 }} optionFilterProp="label"
                                options={purchaseOrders.map(po => ({ value: po.id, label: po.number }))} />
                        </Form.Item>
                    </Space>
                    <Form.Item name="notes" label="Note"><Input.TextArea rows={2} /></Form.Item>
                    <Divider>Righe Carico</Divider>
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
                                        <Form.Item {...rest} name={[name, 'description']}>
                                            <Input placeholder="Descrizione" style={{ width: 200 }} />
                                        </Form.Item>
                                        <Form.Item {...rest} name={[name, 'location_id']}>
                                            <Select placeholder="Ubicazione" style={{ width: 150 }} allowClear
                                                options={locations.map(l => ({ value: l.id, label: l.name }))} />
                                        </Form.Item>
                                        <Button type="link" danger onClick={() => remove(name)}>Rimuovi</Button>
                                    </Space>
                                ))}
                                <Button type="dashed" onClick={() => add({ quantity: 1 })} icon={<PlusOutlined />}>Aggiungi Riga</Button>
                            </>
                        )}
                    </Form.List>
                </Form>
            </Modal>
        </div>
    );
};
