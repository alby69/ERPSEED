import React, { useState, useEffect, useCallback } from 'react';
import { Card, Table, Tabs, Button, Modal, Form, Input, InputNumber, DatePicker, Select, Space, Tag, message } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { apiFetch } from '@/utils';
import dayjs from 'dayjs'; // Keep dayjs for diff calculation in Tag
import { parseDateForForm, formatDateForApi, formatDateForDisplay } from '@/utils/dateUtils'; // Import date utilities
import { useColumnManagerWithDrawer } from '@/hooks/useColumnManager';
import ColumnSettingsButton from '@/components/ColumnSettingsButton';

const statusColors = { available: 'green', reserved: 'blue', sold: 'default', returned: 'orange', scrapped: 'red' };

// ========== Lots Tab ==========
const LotsTab = () => {
    const [data, setData] = useState([]);
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(false);
    const [modalVisible, setModalVisible] = useState(false);
    const [editing, setEditing] = useState(null);
    const [form] = Form.useForm();

    const fetch = useCallback(async () => {
        setLoading(true);
        try {
            const [lRes, pRes] = await Promise.all([
                apiFetch('/api/v1/lots'),
                apiFetch('/api/v1/products'),
            ]);
            if (lRes.ok) setData(await lRes.json());
            if (pRes.ok) setProducts(await pRes.json());
        } catch { message.error('Error'); }
        finally { setLoading(false); }
    }, []);

    useEffect(() => { fetch(); }, [fetch]);

    const handleSubmit = async () => {
        try {
            const values = await form.validateFields();
            values.manufacturing_date = formatDateForApi(values.manufacturing_date);
            values.expiry_date = formatDateForApi(values.expiry_date);
            let res;
            if (editing) res = await apiFetch(`/api/v1/lots/${editing.id}`, { method: 'PUT', body: JSON.stringify(values) });
            else res = await apiFetch('/api/v1/lots', { method: 'POST', body: JSON.stringify(values) });
            if (res.ok) { message.success('Salvato'); setModalVisible(false); form.resetFields(); setEditing(null); fetch(); }
            else { const e = await res.json(); message.error(e.message || 'Errore'); }
        } catch { message.error('Validation'); }
    };

    const rawColumns = [
        { title: 'Codice Lotto', dataIndex: 'code', key: 'code' },
        { title: 'Prodotto', dataIndex: 'product_name', key: 'product_name' },
        { title: 'Qtà Iniziale', dataIndex: 'initial_quantity', key: 'initial_quantity' },
        { title: 'Qtà Residua', dataIndex: 'quantity', key: 'quantity' },
        { title: 'Data Prod.', dataIndex: 'manufacturing_date', key: 'manufacturing_date', render: (v) => formatDateForDisplay(v) || '-' },
        { title: 'Scadenza', dataIndex: 'expiry_date', key: 'expiry_date', render: (v) => v ? <Tag color={parseDateForForm(v)?.diff(dayjs(), 'day') < 30 ? 'red' : 'default'}>{formatDateForDisplay(v)}</Tag> : '-' },
        { title: 'Azioni', key: 'actions', render: (_, r) => (
            <Space>
                <Button type="link" size="small" icon={<EditOutlined />} onClick={() => { setEditing(r); form.setFieldsValue({ ...r, manufacturing_date: parseDateForForm(r.manufacturing_date), expiry_date: parseDateForForm(r.expiry_date) }); setModalVisible(true); }}>Modifica</Button>
                <Button type="link" size="small" danger icon={<DeleteOutlined />} onClick={async () => { const res = await apiFetch(`/api/v1/lots/${r.id}`, { method: 'DELETE' }); if (res.ok) { message.success('Eliminato'); fetch(); } }} />
            </Space>
        )},
    ];

    const colManager = useColumnManagerWithDrawer('lots', rawColumns);

    return (
        <>
            <Space style={{ marginBottom: 16 }}>
                <ColumnSettingsButton manager={colManager} />
                <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditing(null); form.resetFields(); setModalVisible(true); }}>Nuovo Lotto</Button>
            </Space>
            <Table dataSource={data} columns={colManager.processedColumns} rowKey="id" loading={loading} />
            <Modal title={editing ? 'Modifica Lotto' : 'Nuovo Lotto'} open={modalVisible} onOk={handleSubmit} onCancel={() => { setModalVisible(false); form.resetFields(); setEditing(null); }} okText="Salva" cancelText="Annulla" width={600}>
                <Form form={form} layout="vertical">
                    <Space size={16}>
                        <Form.Item name="code" label="Codice Lotto" rules={[{ required: true }]}><Input /></Form.Item>
                        <Form.Item name="product_id" label="Prodotto" rules={[{ required: true }]}>
                            <Select style={{ width: 250 }} showSearch optionFilterProp="label" options={products.map(p => ({ value: p.id, label: `${p.name}` }))} />
                        </Form.Item>
                    </Space>
                    <Space size={16}> {/* Use formatDateForDisplay for DatePicker format */}
                        <Form.Item name="quantity" label="Quantità" rules={[{ required: true }]}><InputNumber min={0} /></Form.Item>
                        <Form.Item name="manufacturing_date" label="Data Prod."><DatePicker format={formatDateForDisplay} /></Form.Item>
                        <Form.Item name="expiry_date" label="Scadenza"><DatePicker format={formatDateForDisplay} /></Form.Item>
                    </Space>
                    <Form.Item name="notes" label="Note"><Input.TextArea rows={2} /></Form.Item>
                </Form>
            </Modal>
        </>
    );
};

// ========== Serial Numbers Tab ==========
const SerialTab = () => {
    const [data, setData] = useState([]);
    const [products, setProducts] = useState([]);
    const [lots, setLots] = useState([]);
    const [loading, setLoading] = useState(false);
    const [modalVisible, setModalVisible] = useState(false);
    const [editing, setEditing] = useState(null);
    const [form] = Form.useForm();

    const fetch = useCallback(async () => {
        setLoading(true);
        try {
            const [sRes, pRes, lRes] = await Promise.all([
                apiFetch('/api/v1/serial-numbers'),
                apiFetch('/api/v1/products'),
                apiFetch('/api/v1/lots'),
            ]);
            if (sRes.ok) setData(await sRes.json());
            if (pRes.ok) setProducts(await pRes.json());
            if (lRes.ok) setLots(await lRes.json());
        } catch { message.error('Error'); }
        finally { setLoading(false); }
    }, []);

    useEffect(() => { fetch(); }, [fetch]);

    const handleSubmit = async () => {
        try {
            const values = await form.validateFields();
            values.sold_date = formatDateForApi(values.sold_date);
            let res;
            if (editing) res = await apiFetch(`/api/v1/serial-numbers/${editing.id}`, { method: 'PUT', body: JSON.stringify(values) });
            else res = await apiFetch('/api/v1/serial-numbers', { method: 'POST', body: JSON.stringify(values) });
            if (res.ok) { message.success('Salvato'); setModalVisible(false); form.resetFields(); setEditing(null); fetch(); }
            else { const e = await res.json(); message.error(e.message || 'Errore'); }
        } catch { message.error('Validation'); }
    };

    const rawColumns = [
        { title: 'Seriale', dataIndex: 'code', key: 'code' },
        { title: 'Prodotto', dataIndex: 'product_name', key: 'product_name' },
        { title: 'Lotto', dataIndex: 'lot_id', key: 'lot_id', render: (id) => { const l = lots.find(x => x.id === id); return l?.code || '-'; } },
        { title: 'Stato', dataIndex: 'status', key: 'status', render: (v) => <Tag color={statusColors[v]}>{v}</Tag> },
        { title: 'Data Vendita', dataIndex: 'sold_date', key: 'sold_date', render: (v) => v || '-' },
        { title: 'Azioni', key: 'actions', render: (_, r) => (
            <Space>
                <Button type="link" size="small" icon={<EditOutlined />} onClick={() => { setEditing(r); form.setFieldsValue({ ...r, sold_date: r.sold_date ? dayjs(r.sold_date) : null }); setModalVisible(true); }}>Modifica</Button>
                <Button type="link" size="small" danger icon={<DeleteOutlined />} onClick={async () => { const res = await apiFetch(`/api/v1/serial-numbers/${r.id}`, { method: 'DELETE' }); if (res.ok) { message.success('Eliminato'); fetch(); } }} />
            </Space>
        )},
    ];

    const colManager = useColumnManagerWithDrawer('serials', rawColumns);

    return (
        <>
            <Space style={{ marginBottom: 16 }}>
                <ColumnSettingsButton manager={colManager} />
                <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditing(null); form.resetFields(); setModalVisible(true); }}>Nuovo Seriale</Button>
            </Space>
            <Table dataSource={data} columns={colManager.processedColumns} rowKey="id" loading={loading} />
            <Modal title={editing ? 'Modifica Seriale' : 'Nuovo Seriale'} open={modalVisible} onOk={handleSubmit} onCancel={() => { setModalVisible(false); form.resetFields(); setEditing(null); }} okText="Salva" cancelText="Annulla" width={600}>
                <Form form={form} layout="vertical">
                    <Space size={16}>
                        <Form.Item name="code" label="Seriale" rules={[{ required: true }]}><Input /></Form.Item>
                        <Form.Item name="product_id" label="Prodotto" rules={[{ required: true }]}>
                            <Select style={{ width: 250 }} showSearch optionFilterProp="label" options={products.map(p => ({ value: p.id, label: p.name }))} />
                        </Form.Item>
                    </Space>
                    <Space size={16}> {/* Use formatDateForDisplay for DatePicker format */}
                        <Form.Item name="lot_id" label="Lotto"><Select allowClear style={{ width: 200 }} options={lots.map(l => ({ value: l.id, label: l.code }))} /></Form.Item>
                        <Form.Item name="status" label="Stato">
                            <Select options={[
                                { value: 'available', label: 'Disponibile' },
                                { value: 'reserved', label: 'Riservato' },
                                { value: 'sold', label: 'Venduto' },
                                { value: 'returned', label: 'Reso' },
                                { value: 'scrapped', label: 'Dismesso' },
                            ]} />
                        </Form.Item>
                    </Space>
                    <Form.Item name="notes" label="Note"><Input.TextArea rows={2} /></Form.Item>
                </Form>
            </Modal>
        </>
    );
};

// ========== Main Page ==========
const LotsPage = () => (
    <div style={{ padding: 24 }}>
        <Card title="Lotti e Serial Number">
            <Tabs items={[
                { key: 'lots', label: 'Lotti', children: <LotsTab /> },
                { key: 'serials', label: 'Serial Number', children: <SerialTab /> },
            ]} />
        </Card>
    </div>
);

export default LotsPage;
