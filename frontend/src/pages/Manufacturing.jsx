import React, { useState, useEffect, useCallback } from 'react';
import { Card, Table, Tabs, Button, Modal, Form, Input, InputNumber, DatePicker, Select, Space, Tag, message, InputNumber as IN } from 'antd';
import { PlusOutlined, EditOutlined, PlayCircleOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { apiFetch } from '@/utils';
import { parseDateForForm, formatDateForApi, formatDateForDisplay } from '@/utils/dateUtils'; // Import date utilities

const statusColors = { draft: 'default', active: 'green', archived: 'orange', planned: 'blue', released: 'geekblue', in_progress: 'processing', completed: 'green', cancelled: 'red' };

// ============== BOM Tab ==============
const BOMTab = () => {
    const [data, setData] = useState([]);
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(false);
    const [modalVisible, setModalVisible] = useState(false);
    const [editing, setEditing] = useState(null);
    const [form] = Form.useForm();

    const fetch = useCallback(async () => {
        setLoading(true);
        try {
            const [bRes, pRes] = await Promise.all([
                apiFetch('/api/v1/manufacturing/bom'),
                apiFetch('/api/v1/products'),
            ]);
            if (bRes.ok) setData(await bRes.json());
            if (pRes.ok) setProducts(await pRes.json());
        } catch { message.error('Error'); }
        finally { setLoading(false); }
    }, []);

    useEffect(() => { fetch(); }, [fetch]);

    const handleSubmit = async () => {
        try {
            const values = await form.validateFields();
            let res; // No date fields in BOM, so no change to values.
            if (editing) res = await apiFetch(`/api/v1/manufacturing/bom/${editing.id}`, { method: 'PUT', body: JSON.stringify(values) });
            else res = await apiFetch('/api/v1/manufacturing/bom', { method: 'POST', body: JSON.stringify(values) });
            if (res.ok) { message.success('Salvato'); setModalVisible(false); form.resetFields(); setEditing(null); fetch(); }
            else { const e = await res.json(); message.error(e.message || 'Errore'); }
        } catch { message.error('Validation'); }
    };

    const columns = [
        { title: 'Codice', dataIndex: 'code' },
        { title: 'Nome', dataIndex: 'name' },
        { title: 'Prodotto', dataIndex: 'product_name' },
        { title: 'Versione', dataIndex: 'version' },
        { title: 'Stato', dataIndex: 'status', render: (v) => <Tag color={statusColors[v]}>{v}</Tag> },
        { title: 'Azioni', render: (_, r) => (
            <Button type="link" icon={<EditOutlined />} onClick={() => { setEditing(r); form.setFieldsValue(r); setModalVisible(true); }}>Modifica</Button>
        )},
    ];

    return (
        <>
            <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditing(null); form.resetFields(); setModalVisible(true); }} style={{ marginBottom: 16 }}>Nuova D.B.</Button>
            <Table dataSource={data} columns={columns} rowKey="id" loading={loading} />
            <Modal title={editing ? 'Modifica D.B.' : 'Nuova Distinta Base'} open={modalVisible} onOk={handleSubmit} onCancel={() => { setModalVisible(false); form.resetFields(); setEditing(null); }} okText="Salva" cancelText="Annulla" width={800}>
                <Form form={form} layout="vertical">
                    <Space size={16}>
                        <Form.Item name="code" label="Codice" rules={[{ required: true }]}><Input /></Form.Item>
                        <Form.Item name="name" label="Nome"><Input style={{ width: 250 }} /></Form.Item>
                        <Form.Item name="product_id" label="Prodotto" rules={[{ required: true }]}>
                            <Select style={{ width: 200 }} showSearch optionFilterProp="label" options={products.map(p => ({ value: p.id, label: `${p.code || p.name} - ${p.name}` }))} />
                        </Form.Item>
                        <Form.Item name="status" label="Stato"><Select options={[{ value: 'draft', label: 'Bozza' }, { value: 'active', label: 'Attivo' }]} /></Form.Item>
                    </Space>
                </Form>
            </Modal>
        </>
    );
};

// ============== Work Cycles Tab ==============
const WorkCyclesTab = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [modalVisible, setModalVisible] = useState(false);
    const [editing, setEditing] = useState(null);
    const [form] = Form.useForm();

    const fetch = useCallback(async () => {
        setLoading(true);
        try {
            const res = await apiFetch('/api/v1/manufacturing/work-cycles');
            if (res.ok) setData(await res.json());
        } catch { message.error('Error'); }
        finally { setLoading(false); }
    }, []);

    useEffect(() => { fetch(); }, [fetch]);

    const handleSubmit = async () => {
        try {
            const values = await form.validateFields();
            let res;
            if (editing) res = await apiFetch(`/api/v1/manufacturing/work-cycles/${editing.id}`, { method: 'PUT', body: JSON.stringify(values) });
            else res = await apiFetch('/api/v1/manufacturing/work-cycles', { method: 'POST', body: JSON.stringify(values) });
            if (res.ok) { message.success('Salvato'); setModalVisible(false); form.resetFields(); setEditing(null); fetch(); }
            else { const e = await res.json(); message.error(e.message || 'Errore'); }
        } catch { message.error('Validation'); }
    };

    const columns = [
        { title: 'Codice', dataIndex: 'code' },
        { title: 'Nome', dataIndex: 'name' },
        { title: 'Setup (min)', dataIndex: 'total_setup_time' },
        { title: 'Lavorazione (min)', dataIndex: 'total_run_time' },
        { title: 'Stato', dataIndex: 'status', render: (v) => <Tag color={statusColors[v]}>{v}</Tag> },
        { title: 'Azioni', render: (_, r) => (
            <Button type="link" icon={<EditOutlined />} onClick={() => { setEditing(r); form.setFieldsValue(r); setModalVisible(true); }}>Modifica</Button>
        )},
    ];

    const expandedRowRender = (record) => {
        const cols = [
            { title: '#', dataIndex: 'phase_number' },
            { title: 'Nome', dataIndex: 'name' },
            { title: 'Setup (min)', dataIndex: 'setup_time' },
            { title: 'Lavorazione (min)', dataIndex: 'run_time' },
            { title: 'Macchina', dataIndex: 'machine' },
            { title: 'Tipo', dataIndex: 'resource_type' },
        ];
        return <Table dataSource={record.phases || []} columns={cols} rowKey="id" pagination={false} size="small" />;
    };

    return (
        <>
            <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditing(null); form.resetFields(); setModalVisible(true); }} style={{ marginBottom: 16 }}>Nuovo Ciclo</Button>
            <Table dataSource={data} columns={columns} rowKey="id" loading={loading} expandable={{ expandedRowRender }} />
            <Modal title={editing ? 'Modifica Ciclo' : 'Nuovo Ciclo di Lavoro'} open={modalVisible} onOk={handleSubmit} onCancel={() => { setModalVisible(false); form.resetFields(); setEditing(null); }} okText="Salva" cancelText="Annulla" width={700}>
                <Form form={form} layout="vertical">
                    <Space size={16}>
                        <Form.Item name="code" label="Codice" rules={[{ required: true }]}><Input /></Form.Item>
                        <Form.Item name="name" label="Nome" rules={[{ required: true }]}><Input style={{ width: 250 }} /></Form.Item>
                        <Form.Item name="status" label="Stato"><Select options={[{ value: 'draft', label: 'Bozza' }, { value: 'active', label: 'Attivo' }]} /></Form.Item>
                    </Space>
                    <Form.Item name="description" label="Descrizione"><Input.TextArea rows={2} /></Form.Item>
                </Form>
            </Modal>
        </>
    );
};

// ============== Production Orders Tab ==============
const ProductionOrdersTab = () => {
    const [data, setData] = useState([]);
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(false);
    const [modalVisible, setModalVisible] = useState(false);
    const [editing, setEditing] = useState(null);
    const [form] = Form.useForm();

    const fetch = useCallback(async () => {
        setLoading(true);
        try {
            const [oRes, pRes] = await Promise.all([
                apiFetch('/api/v1/manufacturing/production-orders'),
                apiFetch('/api/v1/products'),
            ]);
            if (oRes.ok) setData(await oRes.json());
            if (pRes.ok) setProducts(await pRes.json());
        } catch { message.error('Error'); }
        finally { setLoading(false); }
    }, []);

    useEffect(() => { fetch(); }, [fetch]);

    const handleSubmit = async () => {
        try {
            const values = await form.validateFields();
            values.planned_start_date = formatDateForApi(values.planned_start_date);
            values.planned_end_date = formatDateForApi(values.planned_end_date);
            let res;
            if (editing) res = await apiFetch(`/api/v1/manufacturing/production-orders/${editing.id}`, { method: 'PUT', body: JSON.stringify(values) });
            else res = await apiFetch('/api/v1/manufacturing/production-orders', { method: 'POST', body: JSON.stringify(values) });
            if (res.ok) { message.success('Salvato'); setModalVisible(false); form.resetFields(); setEditing(null); fetch(); }
            else { const e = await res.json(); message.error(e.message || 'Errore'); }
        } catch { message.error('Validation'); }
    };

    const handleAction = async (id, action) => {
        try {
            const res = await apiFetch(`/api/v1/manufacturing/production-orders/${id}/${action}`, { method: 'POST' });
            if (res.ok) { message.success(`${action} riuscito`); fetch(); }
            else { const e = await res.json(); message.error(e.message || 'Errore'); }
        } catch { message.error('Error'); }
    };

    const columns = [
        { title: 'Numero', dataIndex: 'number' },
        { title: 'Prodotto', dataIndex: 'product_name' },
        { title: 'Q.tà', dataIndex: 'quantity' },
        { title: 'Prodotte', dataIndex: 'quantity_produced' }, // No change needed here
        { title: 'Inizio Plan.', dataIndex: 'planned_start_date', render: (v) => formatDateForDisplay(v) || '-' },
        { title: 'Fine Plan.', dataIndex: 'planned_end_date', render: (v) => formatDateForDisplay(v) || '-' },
        { title: 'Stato', dataIndex: 'status', render: (v) => <Tag color={statusColors[v]}>{v}</Tag> },
        { title: 'Azioni', render: (_, r) => (
            <Space>
                <Button type="link" icon={<EditOutlined />} onClick={() => { setEditing(r); form.setFieldsValue({ ...r, planned_start_date: parseDateForForm(r.planned_start_date), planned_end_date: parseDateForForm(r.planned_end_date) }); setModalVisible(true); }}>Modifica</Button>
                {r.status === 'planned' && <Button type="link" icon={<PlayCircleOutlined />} onClick={() => handleAction(r.id, 'release')}>Rilascia</Button>}
                {r.status === 'released' && <Button type="link" icon={<PlayCircleOutlined />} onClick={() => handleAction(r.id, 'start')}>Avvia</Button>}
                {r.status === 'in_progress' && <Button type="link" icon={<CheckCircleOutlined />} onClick={() => handleAction(r.id, 'complete')}>Completa</Button>}
            </Space>
        )},
    ];

    return (
        <>
            <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditing(null); form.resetFields(); setModalVisible(true); }} style={{ marginBottom: 16 }}>Nuovo ODP</Button>
            <Table dataSource={data} columns={columns} rowKey="id" loading={loading} />
            <Modal title={editing ? 'Modifica ODP' : 'Nuovo Ordine di Produzione'} open={modalVisible} onOk={handleSubmit} onCancel={() => { setModalVisible(false); form.resetFields(); setEditing(null); }} okText="Salva" cancelText="Annulla" width={700}>
                <Form form={form} layout="vertical">
                    <Space size={16}>
                        <Form.Item name="product_id" label="Prodotto" rules={[{ required: true }]}>
                            <Select style={{ width: 250 }} showSearch optionFilterProp="label" options={products.map(p => ({ value: p.id, label: `${p.code || p.name} - ${p.name}` }))} />
                        </Form.Item>
                        <Form.Item name="quantity" label="Quantità" rules={[{ required: true }]}><IN min={1} /></Form.Item> {/* No change needed here */}
                        <Form.Item name="status" label="Stato"><Select options={[{ value: 'planned', label: 'Pianificato' }, { value: 'released', label: 'Rilasciato' }]} /></Form.Item> {/* No change needed here */}
                    </Space>
                    <Space size={16}> {/* Use formatDateForDisplay for DatePicker format */}
                        <Form.Item name="planned_start_date" label="Inizio Plan."><DatePicker format={formatDateForDisplay} /></Form.Item>
                        <Form.Item name="planned_end_date" label="Fine Plan."><DatePicker format={formatDateForDisplay} /></Form.Item>
                    </Space>
                    <Form.Item name="notes" label="Note"><Input.TextArea rows={2} /></Form.Item>
                </Form>
            </Modal>
        </>
    );
};

// ============== Main Page ==============
const Manufacturing = () => (
    <div style={{ padding: 24 }}>
        <Card title="Produzione">
            <Tabs items={[
                { key: 'bom', label: 'Distinte Base', children: <BOMTab /> },
                { key: 'workcycles', label: 'Cicli di Lavoro', children: <WorkCyclesTab /> },
                { key: 'production-orders', label: 'ODP', children: <ProductionOrdersTab /> },
            ]} />
        </Card>
    </div>
);

export default Manufacturing;
