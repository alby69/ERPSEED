import React, { useState, useEffect, useCallback } from 'react';
import { Card, Table, Button, Modal, Form, Input, InputNumber, Select, Space, Tag, message, Tabs, DatePicker } from 'antd';
import { PlusOutlined, SearchOutlined } from '@ant-design/icons';
import { apiFetch } from '@/utils';
import { parseDateForForm, formatDateForApi, formatDateForDisplay, formatDateTimeForDisplay } from '@/utils/dateUtils'; // Import date utilities

const typeColors = { in: 'green', out: 'red', transfer: 'blue', adjustment: 'orange' };
const typeLabels = { in: 'Carico', out: 'Scarico', transfer: 'Trasferimento', adjustment: 'Rettifica' };

const MovementReasonsTab = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [modalVisible, setModalVisible] = useState(false);
    const [editingRecord, setEditingRecord] = useState(null);
    const [form] = Form.useForm();

    const fetchData = useCallback(async () => {
        setLoading(true);
        try {
            const res = await apiFetch('/api/v1/movement-reasons');
            if (res.ok) setData(await res.json());
        } catch { message.error('Error loading'); }
        finally { setLoading(false); }
    }, []);

    useEffect(() => { fetchData(); }, [fetchData]);

    const handleSubmit = async () => {
        try {
            const values = await form.validateFields();
            let res;
            if (editingRecord) {
                res = await apiFetch(`/api/v1/movement-reasons/${editingRecord.id}`, { method: 'PUT', body: JSON.stringify(values) });
            } else {
                res = await apiFetch('/api/v1/movement-reasons', { method: 'POST', body: JSON.stringify(values) });
            }
            if (res.ok) { message.success('Salvato'); setModalVisible(false); form.resetFields(); setEditingRecord(null); fetchData(); }
            else { const e = await res.json(); message.error(e.message || 'Errore'); }
        } catch { message.error('Validation failed'); }
    };

    const handleDelete = async (id) => {
        try {
            const res = await apiFetch(`/api/v1/movement-reasons/${id}`, { method: 'DELETE' });
            if (res.ok) { message.success('Eliminato'); fetchData(); }
        } catch { message.error('Error'); }
    };

    const columns = [
        { title: 'Codice', dataIndex: 'code', key: 'code' },
        { title: 'Nome', dataIndex: 'name', key: 'name' },
        { title: 'Tipo', dataIndex: 'movement_type', key: 'movement_type', render: (v) => <Tag color={typeColors[v]}>{typeLabels[v] || v}</Tag> },
        { title: 'Attivo', dataIndex: 'is_active', key: 'is_active', render: (v) => <Tag color={v ? 'green' : 'red'}>{v ? 'Sì' : 'No'}</Tag> },
        { title: 'Azioni', key: 'actions', render: (_, r) => (
            <Space>
                <Button type="link" onClick={() => { setEditingRecord(r); form.setFieldsValue(r); setModalVisible(true); }}>Modifica</Button>
                <Button type="link" danger onClick={() => handleDelete(r.id)}>Elimina</Button>
            </Space>
        )},
    ];

    return (
        <>
            <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditingRecord(null); form.resetFields(); setModalVisible(true); }} style={{ marginBottom: 16 }}>Nuova Causale</Button>
            <Table dataSource={data} columns={columns} rowKey="id" loading={loading} size="small" />
            <Modal title={editingRecord ? 'Modifica Causale' : 'Nuova Causale'} open={modalVisible} onOk={handleSubmit} onCancel={() => { setModalVisible(false); form.resetFields(); setEditingRecord(null); }} okText="Salva" cancelText="Annulla">
                <Form form={form} layout="vertical">
                    <Form.Item name="code" label="Codice" rules={[{ required: true }]}><Input /></Form.Item>
                    <Form.Item name="name" label="Nome" rules={[{ required: true }]}><Input /></Form.Item>
                    <Form.Item name="movement_type" label="Tipo Movimento" rules={[{ required: true }]}>
                        <Select options={[
                            { value: 'in', label: 'Carico' }, { value: 'out', label: 'Scarico' },
                            { value: 'transfer', label: 'Trasferimento' }, { value: 'adjustment', label: 'Rettifica' },
                        ]} />
                    </Form.Item>
                    <Form.Item name="is_active" label="Attivo" valuePropName="checked">
                        <Select options={[{ value: true, label: 'Sì' }, { value: false, label: 'No' }]} />
                    </Form.Item>
                </Form>
            </Modal>
        </>
    );
};

const StockMovementsTab = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [total, setTotal] = useState(0);
    const [page, setPage] = useState(1);
    const [modalVisible, setModalVisible] = useState(false);
    const [form] = Form.useForm();
    const [products, setProducts] = useState([]);
    const [locations, setLocations] = useState([]);
    const [reasons, setReasons] = useState([]);

    const fetchData = useCallback(async () => {
        setLoading(true);
        try {
            const res = await apiFetch(`/inventory/movements?page=${page}&per_page=20`);
            if (res.ok) {
                const json = await res.json();
                setData(json.items || []);
                setTotal(json.total || 0);
            }
        } catch { message.error('Error loading movements'); }
        finally { setLoading(false); }
    }, [page]);

    const fetchLookups = useCallback(async () => {
        try {
            const [pRes, lRes, rRes] = await Promise.all([
                apiFetch('/api/v1/products?per_page=300'),
                apiFetch('/inventory/locations'),
                apiFetch('/api/v1/movement-reasons'),
            ]);
            if (pRes.ok) { const j = await pRes.json(); setProducts(j.items || []); }
            if (lRes.ok) setLocations(await lRes.json());
            if (rRes.ok) setReasons(await rRes.json());
        } catch {}
    }, []);

    useEffect(() => { fetchData(); fetchLookups(); }, [fetchData, fetchLookups]);

    const handleSubmit = async () => {
        try {
            const values = await form.validateFields();
            values.date = formatDateForApi(values.date);
            const res = await apiFetch('/inventory/movements', { method: 'POST', body: JSON.stringify(values) });
            if (res.ok) { message.success('Movimento creato'); setModalVisible(false); form.resetFields(); fetchData(); }
            else { const e = await res.json(); message.error(e.message || 'Errore'); }
        } catch { message.error('Validation failed'); }
    };

    const columns = [
        { title: 'Nr. Movimento', dataIndex: 'movement_number', key: 'movement_number' },
        { title: 'Data', dataIndex: 'created_at', key: 'created_at', render: (v) => formatDateTimeForDisplay(v) || '-' },
        { title: 'Tipo', dataIndex: 'movement_type', key: 'movement_type', render: (v) => <Tag color={typeColors[v]}>{typeLabels[v] || v}</Tag> },
        { title: 'Prodotto', dataIndex: 'product_id', key: 'product_id', render: (id) => { const p = products.find(x => x.id === id); return p ? `${p.code || ''} - ${p.name}` : `ID: ${id}`; } },
        { title: 'Ubicazione', dataIndex: 'location_id', key: 'location_id', render: (id) => { const l = locations.find(x => x.id === id); return l ? l.name : `ID: ${id}`; } },
        { title: 'Quantità', dataIndex: 'quantity', key: 'quantity', render: (v, r) => <span style={{ fontWeight: 600, color: r.movement_type === 'in' ? '#52c41a' : r.movement_type === 'out' ? '#ff4d4f' : '#1890ff' }}>{v}</span> },
        { title: 'Riferimento', dataIndex: 'reference_type', key: 'reference_type' },
    ];

    return (
        <>
            <Button type="primary" icon={<PlusOutlined />} onClick={() => { form.resetFields(); setModalVisible(true); }} style={{ marginBottom: 16 }}>Nuovo Movimento</Button>
            <Table dataSource={data} columns={columns} rowKey="id" loading={loading}
                pagination={{ current: page, pageSize: 20, total, onChange: setPage }} />
            <Modal title="Nuovo Movimento di Magazzino" open={modalVisible} onOk={handleSubmit} onCancel={() => { setModalVisible(false); form.resetFields(); }} okText="Salva" cancelText="Annulla" width={600}>
                <Form form={form} layout="vertical">
                    <Form.Item name="movement_type" label="Tipo" rules={[{ required: true }]}>
                        <Select options={[
                            { value: 'in', label: 'Carico' }, { value: 'out', label: 'Scarico' },
                            { value: 'transfer', label: 'Trasferimento' }, { value: 'adjustment', label: 'Rettifica' },
                        ]} />
                    </Form.Item>
                    <Form.Item name="product_id" label="Prodotto" rules={[{ required: true }]}>
                        <Select showSearch placeholder="Seleziona prodotto" optionFilterProp="label"
                            options={products.map(p => ({ value: p.id, label: `${p.code || ''} - ${p.name}` }))} />
                    </Form.Item>
                    <Form.Item name="location_id" label="Ubicazione" rules={[{ required: true }]}>
                        <Select options={locations.map(l => ({ value: l.id, label: l.name }))} />
                    </Form.Item>
                    <Space style={{ width: '100%' }} size={16}>
                        <Form.Item name="quantity" label="Quantità" rules={[{ required: true }]}>
                            <InputNumber min={0.001} step={1} />
                        </Form.Item> {/* Use formatDateForDisplay for DatePicker format */}
                        <Form.Item name="date" label="Data"><DatePicker format={formatDateForDisplay} /></Form.Item>
                    </Space>
                    <Form.Item name="reference_type" label="Tipo Riferimento">
                        <Input placeholder="es. ordine, ddt, inventario" />
                    </Form.Item>
                    <Form.Item name="reference_id" label="ID Riferimento">
                        <InputNumber min={0} />
                    </Form.Item>
                </Form>
            </Modal>
        </>
    );
};

const StockMovements = () => {
    const items = [
        { key: 'movements', label: 'Movimenti', children: <StockMovementsTab /> },
        { key: 'reasons', label: 'Cause di Movimento', children: <MovementReasonsTab /> },
    ];
    return (
        <div style={{ padding: 24 }}>
            <Card title="Movimenti di Magazzino">
                <Tabs items={items} />
            </Card>
        </div>
    );
};

export default StockMovements;
