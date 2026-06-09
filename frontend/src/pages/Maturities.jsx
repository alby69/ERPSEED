import React, { useState, useEffect, useCallback } from 'react';
import { Card, Table, Button, Modal, Form, Input, InputNumber, DatePicker, Select, Space, Tag, message, Row, Col, Statistic } from 'antd';
import { PlusOutlined, DollarOutlined, WarningOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { apiFetch } from '@/utils';
import { parseDateForForm, formatDateForApi, formatDateForDisplay } from '@/utils/dateUtils';

const statusColors = { open: 'orange', partial: 'blue', paid: 'green', overdue: 'red', cancelled: 'default' };
const statusLabels = { open: 'Aperta', partial: 'Parziale', paid: 'Pagata', overdue: 'Scaduta', cancelled: 'Annullata' };

export default function Maturities() {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [summary, setSummary] = useState(null);
    const [modalVisible, setModalVisible] = useState(false);
    const [payModalVisible, setPayModalVisible] = useState(false);
    const [selectedMaturity, setSelectedMaturity] = useState(null);
    const [soggetti, setSoggetti] = useState([]);
    const [form] = Form.useForm();
    const [payForm] = Form.useForm();
    const [statusFilter, setStatusFilter] = useState(null);
    const [overdueOnly, setOverdueOnly] = useState(false);

    const fetchData = useCallback(async () => {
        setLoading(true);
        try {
            const params = new URLSearchParams();
            if (statusFilter) params.set('status', statusFilter);
            if (overdueOnly) params.set('overdue', 'true');
            const [dRes, sRes] = await Promise.all([
                apiFetch(`/api/v1/maturities?${params}`),
                apiFetch('/api/v1/maturities/summary'),
            ]);
            if (dRes.ok) setData(await dRes.json());
            if (sRes.ok) setSummary(await sRes.json());
        } catch { message.error('Error loading'); }
        finally { setLoading(false); }
    }, [statusFilter, overdueOnly]);

    const fetchSoggetti = useCallback(async () => {
        try {
            const res = await apiFetch('/api/v1/soggetti?per_page=500');
            if (res.ok) { const j = await res.json(); setSoggetti(j.items || j || []); }
        } catch {}
    }, []);

    useEffect(() => { fetchData(); fetchSoggetti(); }, [fetchData, fetchSoggetti]);

    const handleCreateFromInvoices = async () => {
        const res = await apiFetch('/api/v1/maturities/from-invoices', { method: 'POST' });
        if (res.ok) { const j = await res.json(); message.success(j.message); fetchData(); }
        else { const e = await res.json(); message.error(e.message || 'Errore'); }
    };

    const handleSubmit = async () => {
        try {
            const values = await form.validateFields();
            values.due_date = formatDateForApi(values.due_date);
            const res = await apiFetch('/api/v1/maturities', { method: 'POST', body: JSON.stringify(values) });
            if (res.ok) { message.success('Scadenza creata'); setModalVisible(false); form.resetFields(); fetchData(); }
            else { const e = await res.json(); message.error(e.message || 'Errore'); }
        } catch { message.error('Validation failed'); }
    };

    const handlePay = async () => {
        try {
            const values = await payForm.validateFields();
            const res = await apiFetch(`/api/v1/maturities/${selectedMaturity.id}`, {
                method: 'PUT',
                body: JSON.stringify({
                    paid_amount: parseFloat(values.paid_amount) + (selectedMaturity.paid_amount || 0),
                }),
            });
            if (res.ok) { message.success('Pagamento registrato'); setPayModalVisible(false); setSelectedMaturity(null); payForm.resetFields(); fetchData(); }
            else { const e = await res.json(); message.error(e.message || 'Errore'); }
        } catch { message.error('Validation failed'); }
    };

    const isOverdue = (dueDate, status) => {
        return parseDateForForm(dueDate)?.isBefore(dayjs(), 'day') && ['open', 'partial'].includes(status);
    };

    const columns = [
        { title: 'Scadenza', dataIndex: 'due_date', key: 'due_date', render: (v, r) => { // v is already a string here
            const overdue = isOverdue(v, r.status); // Use isOverdue utility
            return <span style={{ color: overdue ? '#ff4d4f' : undefined, fontWeight: overdue ? 600 : undefined }}>{dayjs(v).format('DD/MM/YYYY')}</span>;
        }},
        { title: 'Soggetto', dataIndex: 'party_id', key: 'party_id', render: (id) => { const s = soggetti.find(x => x.id === id); return s ? s.ragione_sociale || `${s.nome || ''} ${s.cognome || ''}` : `ID: ${id}`; } },
        { title: 'Importo', dataIndex: 'amount', key: 'amount', align: 'right', render: (v) => `€ ${(v || 0).toFixed(2)}` },
        { title: 'Residuo', dataIndex: 'balance', key: 'balance', align: 'right', render: (v, r) => <span style={{ fontWeight: 600, color: (v || 0) > 0 ? '#fa8c16' : '#52c41a' }}>€ ${(v || 0).toFixed(2)}</span> },
        { title: 'Riferimento', dataIndex: 'reference_number', key: 'reference_number', render: (v) => v || '-' },
        { title: 'Descrizione', dataIndex: 'description', key: 'description', ellipsis: true },
        { title: 'Stato', dataIndex: 'status', key: 'status', render: (v, r) => {
            if (isOverdue(r.due_date, r.status)) return <Tag color="red">Scaduta</Tag>;
            return <Tag color={statusColors[v]}>{statusLabels[v] || v}</Tag>;
        }},
        { title: 'Azioni', key: 'actions', render: (_, r) => (
            <Space>
                {['open', 'partial', 'overdue'].includes(r.status) && (
                    <Button type="link" icon={<DollarOutlined />} onClick={() => { setSelectedMaturity(r); payForm.setFieldsValue({ paid_amount: r.balance }); setPayModalVisible(true); }}>Paga</Button>
                )}
            </Space>
        )},
    ];

    return (
        <div style={{ padding: 24 }}>
            {summary && (
                <Row gutter={16} style={{ marginBottom: 16 }}>
                    <Col span={6}><Card size="small"><Statistic title="Totale Aperto" value={summary.total_open} precision={2} prefix="€" valueStyle={{ color: '#fa8c16' }} /></Card></Col>
                    <Col span={6}><Card size="small"><Statistic title="Scaduto" value={summary.total_overdue} precision={2} prefix={<WarningOutlined />} valueStyle={{ color: '#ff4d4f' }} /></Card></Col>
                    <Col span={6}><Card size="small"><Statistic title="In Scadenza (30gg)" value={summary.due_next_30_days} precision={2} prefix="€" /></Card></Col>
                    <Col span={6}><Card size="small"><Statistic title="Pagato" value={summary.total_paid} precision={2} prefix={<CheckCircleOutlined />} valueStyle={{ color: '#52c41a' }} /></Card></Col>
                </Row>
            )}
            <Card title="Scadenzario" extra={
                <Space>
                    <Select allowClear placeholder="Filtra stato" style={{ width: 140 }} value={statusFilter} onChange={(v) => { setStatusFilter(v); }}
                        options={[
                            { value: '', label: 'Tutti' }, { value: 'open', label: 'Aperte' },
                            { value: 'partial', label: 'Parziali' }, { value: 'paid', label: 'Pagate' },
                            { value: 'overdue', label: 'Scadute' },
                        ]} />
                    <Button onClick={() => setOverdueOnly(!overdueOnly)} type={overdueOnly ? 'primary' : 'default'} icon={<WarningOutlined />}>Scadute</Button>
                    <Button onClick={handleCreateFromInvoices}>Genera da Fatture</Button>
                    <Button type="primary" icon={<PlusOutlined />} onClick={() => { form.resetFields(); setModalVisible(true); }}>Nuova Scadenza</Button>
                </Space>
            }>
                <Table dataSource={data} columns={columns} rowKey="id" loading={loading}
                    pagination={{ pageSize: 25, showTotal: (t) => `${t} scadenze` }} />
            </Card>
            <Modal title="Nuova Scadenza" open={modalVisible} onOk={handleSubmit} onCancel={() => { setModalVisible(false); form.resetFields(); }} okText="Salva" cancelText="Annulla">
                <Form form={form} layout="vertical">
                    <Form.Item name="party_id" label="Soggetto" rules={[{ required: true }]}>
                        <Select showSearch placeholder="Seleziona" optionFilterProp="label"
                            options={soggetti.map(s => ({ value: s.id, label: s.ragione_sociale || `${s.nome || ''} ${s.cognome || ''}` }))} />
                    </Form.Item>
                    <Space style={{ width: '100%' }} size={16}> {/* Use formatDateForDisplay for DatePicker format */}
                        <Form.Item name="due_date" label="Data Scadenza" rules={[{ required: true }]}><DatePicker /></Form.Item>
                        <Form.Item name="amount" label="Importo" rules={[{ required: true }]}><InputNumber min={0.01} step={0.01} prefix="€" /></Form.Item>
                    </Space>
                    <Form.Item name="description" label="Descrizione"><Input /></Form.Item>
                    <Form.Item name="reference_number" label="Numero Riferimento"><Input /></Form.Item>
                </Form>
            </Modal>
            <Modal title="Registra Pagamento" open={payModalVisible} onOk={handlePay} onCancel={() => { setPayModalVisible(false); setSelectedMaturity(null); payForm.resetFields(); }} okText="Registra" cancelText="Annulla">
                {selectedMaturity && (
                    <p>Scadenza: {dayjs(selectedMaturity.due_date).format('DD/MM/YYYY')} — Residuo: € {selectedMaturity.balance?.toFixed(2)}</p>
                )} {/* Here dayjs is still used for direct display, which is fine as it's not form interaction */}
                <Form form={payForm} layout="vertical">
                    <Form.Item name="paid_amount" label="Importo Pagato" rules={[{ required: true }]}>
                        <InputNumber min={0.01} step={0.01} prefix="€" style={{ width: '100%' }} />
                    </Form.Item>
                </Form>
            </Modal>
        </div>
    );
};
