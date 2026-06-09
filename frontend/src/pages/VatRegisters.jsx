import React, { useState, useEffect, useCallback } from 'react';
import { Card, Table, Tabs, Button, Modal, Form, Input, InputNumber, DatePicker, Select, Space, Tag, message, Row, Col, Statistic } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, ThunderboltOutlined } from '@ant-design/icons';
import { apiFetch } from '@/utils';
import dayjs from 'dayjs';

const registerTypes = { sales: 'Vendite', purchases: 'Acquisti', corrispettivi: 'Corrispettivi' };
const statusColors = { draft: 'default', computed: 'blue', paid: 'green', credited: 'orange' };

// ========== VAT Register Tab ==========
const VatRegisterTab = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [registerType, setRegisterType] = useState('sales');
    const [period, setPeriod] = useState(dayjs().format('YYYY-MM'));
    const [modalVisible, setModalVisible] = useState(false);
    const [editing, setEditing] = useState(null);
    const [form] = Form.useForm();
    const [generating, setGenerating] = useState(false);

    const fetch = useCallback(async () => {
        setLoading(true);
        try {
            const res = await apiFetch(`/api/v1/vat/register?register_type=${registerType}&period=${period}`);
            if (res.ok) setData(await res.json());
        } catch { message.error('Error'); }
        finally { setLoading(false); }
    }, [registerType, period]);

    useEffect(() => { fetch(); }, [fetch]);

    const handleGenerate = async () => {
        setGenerating(true);
        try {
            const res = await apiFetch('/api/v1/vat/register/generate', {
                method: 'POST', body: JSON.stringify({ register_type: registerType, period })
            });
            if (res.ok) { const d = await res.json(); message.success(`Create ${d.created} registrazioni`); fetch(); }
            else { const e = await res.json(); message.error(e.message || 'Errore'); }
        } catch { message.error('Error'); }
        finally { setGenerating(false); }
    };

    const handleSubmit = async () => {
        try {
            const values = await form.validateFields();
            values.entry_date = values.entry_date?.format('YYYY-MM-DD');
            values.document_date = values.document_date?.format('YYYY-MM-DD');
            values.register_type = registerType;
            values.period = period;
            values.fiscal_year = parseInt(period.split('-')[0]);
            let res;
            if (editing) res = await apiFetch(`/api/v1/vat/register/${editing.id}`, { method: 'PUT', body: JSON.stringify(values) });
            else res = await apiFetch('/api/v1/vat/register', { method: 'POST', body: JSON.stringify(values) });
            if (res.ok) { message.success('Salvato'); setModalVisible(false); form.resetFields(); setEditing(null); fetch(); }
            else { const e = await res.json(); message.error(e.message || 'Errore'); }
        } catch { message.error('Validation'); }
    };

    const handleDelete = async (id) => {
        try {
            const res = await apiFetch(`/api/v1/vat/register/${id}`, { method: 'DELETE' });
            if (res.ok) { message.success('Eliminato'); fetch(); }
        } catch { message.error('Error'); }
    };

    const totalTaxable = data.reduce((s, r) => s + (r.taxable_amount || 0), 0);
    const totalVat = data.reduce((s, r) => s + (r.vat_amount || 0), 0);

    const columns = [
        { title: '#', dataIndex: 'entry_number', width: 60 },
        { title: 'Data', dataIndex: 'entry_date' },
        { title: 'Documento', dataIndex: 'document_number' },
        { title: 'Soggetto', dataIndex: 'soggetto_name' },
        { title: 'Imponibile', dataIndex: 'taxable_amount', render: (v) => `€${(v || 0).toFixed(2)}` },
        { title: 'IVA', dataIndex: 'vat_amount', render: (v) => `€${(v || 0).toFixed(2)}` },
        { title: 'Aliquota', dataIndex: 'vat_rate', render: (v) => v ? `${v}%` : '-' },
        { title: 'Natura', dataIndex: 'tax_nature' },
        { title: 'Azioni', render: (_, r) => (
            <Space>
                <Button type="link" size="small" icon={<EditOutlined />} onClick={() => { setEditing(r); form.setFieldsValue({ ...r, entry_date: r.entry_date ? dayjs(r.entry_date) : null, document_date: r.document_date ? dayjs(r.document_date) : null }); setModalVisible(true); }}>Modifica</Button>
                <Button type="link" size="small" danger icon={<DeleteOutlined />} onClick={() => handleDelete(r.id)} />
            </Space>
        )},
    ];

    return (
        <>
            <Row gutter={16} style={{ marginBottom: 16 }}>
                <Col span={4}>
                    <Select value={registerType} onChange={setRegisterType} style={{ width: '100%' }}
                        options={Object.entries(registerTypes).map(([k, v]) => ({ value: k, label: v }))} />
                </Col>
                <Col span={3}>
                    <Input value={period} onChange={e => setPeriod(e.target.value)} placeholder="YYYY-MM" />
                </Col>
                <Col span={3}>
                    <Button icon={<ThunderboltOutlined />} onClick={handleGenerate} loading={generating}>Genera da Fatture</Button>
                </Col>
                <Col span={3}>
                    <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditing(null); form.resetFields(); setModalVisible(true); }}>Nuovo</Button>
                </Col>
            </Row>
            <Row gutter={16} style={{ marginBottom: 16 }}>
                <Col span={6}><Card size="small"><Statistic title="Totale Imponibile" value={totalTaxable} precision={2} prefix="€" /></Card></Col>
                <Col span={6}><Card size="small"><Statistic title="Totale IVA" value={totalVat} precision={2} prefix="€" /></Card></Col>
            </Row>
            <Table dataSource={data} columns={columns} rowKey="id" loading={loading} size="small" />
            <Modal title={editing ? 'Modifica Registrazione' : 'Nuova Registrazione IVA'} open={modalVisible} onOk={handleSubmit} onCancel={() => { setModalVisible(false); form.resetFields(); setEditing(null); }}>
                <Form form={form} layout="vertical">
                    <Space size={16}>
                        <Form.Item name="entry_date" label="Data" rules={[{ required: true }]}><DatePicker /></Form.Item>
                        <Form.Item name="document_number" label="Num. Documento"><Input /></Form.Item>
                        <Form.Item name="document_date" label="Data Doc."><DatePicker /></Form.Item>
                    </Space>
                    <Space size={16}>
                        <Form.Item name="soggetto_name" label="Soggetto"><Input style={{ width: 250 }} /></Form.Item>
                        <Form.Item name="soggetto_vat" label="P.IVA"><Input /></Form.Item>
                    </Space>
                    <Space size={16}>
                        <Form.Item name="taxable_amount" label="Imponibile"><InputNumber min={0} step={10} prefix="€" /></Form.Item>
                        <Form.Item name="vat_amount" label="IVA"><InputNumber min={0} prefix="€" /></Form.Item>
                        <Form.Item name="vat_rate" label="Aliquota %"><InputNumber min={0} step={0.5} /></Form.Item>
                    </Space>
                    <Space size={16}>
                        <Form.Item name="vat_code" label="Codice IVA"><Input /></Form.Item>
                        <Form.Item name="tax_nature" label="Natura">
                            <Select options={[
                                { value: 'I', label: 'Imponibile' },
                                { value: 'NI', label: 'Non Imponibile' },
                                { value: 'E', label: 'Esente' },
                                { value: 'S', label: 'Soggetto a inversione contabile' },
                            ]} />
                        </Form.Item>
                    </Space>
                    <Form.Item name="notes" label="Note"><Input.TextArea rows={2} /></Form.Item>
                </Form>
            </Modal>
        </>
    );
};

// ========== Liquidation Tab ==========
const LiquidationTab = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [modalVisible, setModalVisible] = useState(false);
    const [editing, setEditing] = useState(null);
    const [form] = Form.useForm();

    const fetch = useCallback(async () => {
        setLoading(true);
        try {
            const res = await apiFetch('/api/v1/vat/liquidations');
            if (res.ok) setData(await res.json());
        } catch { message.error('Error'); }
        finally { setLoading(false); }
    }, []);

    useEffect(() => { fetch(); }, [fetch]);

    const handleCompute = async () => {
        const values = await form.validateFields();
        try {
            const res = await apiFetch('/api/v1/vat/liquidations', {
                method: 'POST',
                body: JSON.stringify({ ...values, fiscal_year: parseInt(values.period.split('-')[0]) })
            });
            if (res.ok) { message.success('Liquidazione calcolata'); setModalVisible(false); form.resetFields(); fetch(); }
            else { const e = await res.json(); message.error(e.message || 'Errore'); }
        } catch { message.error('Error'); }
    };

    const handleUpdate = async () => {
        try {
            const values = await form.validateFields();
            const res = await apiFetch(`/api/v1/vat/liquidations/${editing.id}`, { method: 'PUT', body: JSON.stringify(values) });
            if (res.ok) { message.success('Aggiornato'); setModalVisible(false); form.resetFields(); setEditing(null); fetch(); }
        } catch { message.error('Error'); }
    };

    const columns = [
        { title: 'Periodo', dataIndex: 'period' },
        { title: 'Tipo', dataIndex: 'type' },
        { title: 'IVA Vendite', dataIndex: 'sales_vat', render: (v) => `€${(v || 0).toFixed(2)}` },
        { title: 'IVA Acquisti', dataIndex: 'purchases_vat', render: (v) => `€${(v || 0).toFixed(2)}` },
        { title: 'Netto', dataIndex: 'net_vat', render: (v) => `€${(v || 0).toFixed(2)}` },
        { title: 'Da Pagare', dataIndex: 'to_pay', render: (v) => `€${(v || 0).toFixed(2)}` },
        { title: 'Stato', dataIndex: 'status', render: (v) => <Tag color={statusColors[v]}>{v}</Tag> },
        { title: 'Azioni', render: (_, r) => (
            <Button type="link" icon={<EditOutlined />} onClick={() => { setEditing(r); form.setFieldsValue(r); setModalVisible(true); }}>Modifica</Button>
        )},
    ];

    return (
        <>
            <Button type="primary" icon={<ThunderboltOutlined />} onClick={() => { setEditing(null); form.resetFields(); setModalVisible(true); }} style={{ marginBottom: 16 }}>Nuova Liquidazione</Button>
            <Table dataSource={data} columns={columns} rowKey="id" loading={loading} />
            <Modal title={editing ? 'Modifica Liquidazione' : 'Nuova Liquidazione IVA'} open={modalVisible} onOk={editing ? handleUpdate : handleCompute} onCancel={() => { setModalVisible(false); form.resetFields(); setEditing(null); }}>
                <Form form={form} layout="vertical">
                    {!editing && (
                        <Space size={16}>
                            <Form.Item name="period" label="Periodo" rules={[{ required: true }]}><Input placeholder="YYYY-MM" /></Form.Item>
                            <Form.Item name="type" label="Tipo"><Select options={[{ value: 'monthly', label: 'Mensile' }, { value: 'quarterly', label: 'Trimestrale' }]} /></Form.Item>
                            <Form.Item name="previous_credit" label="Credito Prec."><InputNumber min={0} prefix="€" /></Form.Item>
                        </Space>
                    )}
                    {editing && (
                        <>
                            <Space size={16}>
                                <Form.Item name="status" label="Stato">
                                    <Select options={[{ value: 'draft', label: 'Bozza' }, { value: 'computed', label: 'Calcolato' }, { value: 'paid', label: 'Pagato' }, { value: 'credited', label: 'Accreditato' }]} />
                                </Form.Item>
                                <Form.Item name="paid_at" label="Data Pagamento"><DatePicker /></Form.Item>
                                <Form.Item name="to_pay" label="Da Pagare"><InputNumber min={0} prefix="€" /></Form.Item>
                            </Space>
                            <Form.Item name="notes" label="Note"><Input.TextArea rows={2} /></Form.Item>
                        </>
                    )}
                </Form>
            </Modal>
        </>
    );
};

// ========== Main Page ==========
const VatRegisters = () => (
    <div style={{ padding: 24 }}>
        <Card title="Registri IVA">
            <Tabs items={[
                { key: 'register', label: 'Registro', children: <VatRegisterTab /> },
                { key: 'liquidation', label: 'Liquidazioni', children: <LiquidationTab /> },
            ]} />
        </Card>
    </div>
);

export default VatRegisters;
