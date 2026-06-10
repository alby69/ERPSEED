import React, { useState, useEffect, useCallback } from 'react';
import { Card, Table, Tabs, Button, Modal, Form, Input, InputNumber, DatePicker, Select, Space, Tag, message, Row, Col, Statistic } from 'antd';
import { PlusOutlined, UserOutlined, DollarOutlined } from '@ant-design/icons';
import { apiFetch } from '@/utils';
import { parseDateForForm, formatDateForApi, formatDateForDisplay } from '@/utils/dateUtils'; // Import date utilities
import { useColumnManagerWithDrawer } from '@/hooks/useColumnManager';
import ColumnSettingsButton from '@/components/ColumnSettingsButton';
import Layout from '../components/Layout';

const stageColors = { qualification: 'blue', proposal: 'purple', negotiation: 'orange', won: 'green', lost: 'red' };
const stageLabels = { qualification: 'Qualifica', proposal: 'Proposta', negotiation: 'Negoziazione', won: 'Vinta', lost: 'Persa' };
const leadStatusColors = { new: 'blue', contacted: 'purple', qualified: 'green', lost: 'red' };

export default function CRMPage() {
    const [leads, setLeads] = useState([]);
    const [opportunities, setOpportunities] = useState([]);
    const [pipelineSummary, setPipelineSummary] = useState([]);
    const [loading, setLoading] = useState(false);
    const [leadModalVisible, setLeadModalVisible] = useState(false);
    const [oppModalVisible, setOppModalVisible] = useState(false);
    const [editingLead, setEditingLead] = useState(null);
    const [editingOpp, setEditingOpp] = useState(null);
    const [leadForm] = Form.useForm();
    const [oppForm] = Form.useForm();

    const fetchAll = useCallback(async () => {
        setLoading(true);
        try {
            const [lRes, oRes, pRes] = await Promise.all([
                apiFetch('/api/v1/crm/leads'),
                apiFetch('/api/v1/crm/opportunities'),
                apiFetch('/api/v1/crm/pipeline-summary'),
            ]);
            if (lRes.ok) setLeads(await lRes.json());
            if (oRes.ok) setOpportunities(await oRes.json());
            if (pRes.ok) setPipelineSummary(await pRes.json());
        } catch { message.error('Error loading CRM data'); }
        finally { setLoading(false); }
    }, []);

    useEffect(() => { fetchAll(); }, [fetchAll]);

    const handleLeadSubmit = async () => {
        try {
            const values = await leadForm.validateFields();
            let res;
            if (editingLead) res = await apiFetch(`/api/v1/crm/leads/${editingLead.id}`, { method: 'PUT', body: JSON.stringify(values) });
            else res = await apiFetch('/api/v1/crm/leads', { method: 'POST', body: JSON.stringify(values) });
            if (res.ok) { message.success('Salvato'); setLeadModalVisible(false); leadForm.resetFields(); setEditingLead(null); fetchAll(); }
            else { const e = await res.json(); message.error(e.message || 'Errore'); }
        } catch { message.error('Validation failed'); }
    };

    const handleOppSubmit = async () => {
        try {
            const values = await oppForm.validateFields();
            values.expected_close_date = formatDateForApi(values.expected_close_date);
            let res;
            if (editingOpp) res = await apiFetch(`/api/v1/crm/opportunities/${editingOpp.id}`, { method: 'PUT', body: JSON.stringify(values) });
            else res = await apiFetch('/api/v1/crm/opportunities', { method: 'POST', body: JSON.stringify(values) });
            if (res.ok) { message.success('Salvato'); setOppModalVisible(false); oppForm.resetFields(); setEditingOpp(null); fetchAll(); }
            else { const e = await res.json(); message.error(e.message || 'Errore'); }
        } catch { message.error('Validation failed'); }
    };

    const rawLeadColumns = [
        { title: 'Nome', key: 'name', render: (_, r) => `${r.first_name} ${r.last_name}` },
        { title: 'Azienda', dataIndex: 'company', key: 'company' },
        { title: 'Email', dataIndex: 'email', key: 'email' },
        { title: 'Telefono', dataIndex: 'phone', key: 'phone' },
        { title: 'Provenienza', dataIndex: 'source', key: 'source' },
        { title: 'Stato', dataIndex: 'status', key: 'status', render: (v) => <Tag color={leadStatusColors[v]}>{v}</Tag> },
        { title: 'Azioni', key: 'actions', render: (_, r) => (
            <Button type="link" onClick={() => { setEditingLead(r); leadForm.setFieldsValue(r); setLeadModalVisible(true); }}>Modifica</Button>
        )},
    ];

    const rawOppColumns = [
        { title: 'Nome', dataIndex: 'name', key: 'name' },
        { title: 'Valore', dataIndex: 'expected_revenue', key: 'expected_revenue', align: 'right', render: (v) => `€ ${(v || 0).toFixed(2)}` },
        { title: 'Probabilità', dataIndex: 'probability', key: 'probability', render: (v) => `${v || 0}%` },
        { title: 'Stadio', dataIndex: 'stage', key: 'stage', render: (v) => <Tag color={stageColors[v]}>{stageLabels[v] || v}</Tag> }, // No change needed here
        { title: 'Chiusura Prevista', dataIndex: 'expected_close_date', key: 'expected_close_date', render: (v) => formatDateForDisplay(v) || '-' },
        { title: 'Azioni', key: 'actions', render: (_, r) => (
            <Button type="link" onClick={() => { setEditingOpp(r); oppForm.setFieldsValue({ ...r, expected_close_date: parseDateForForm(r.expected_close_date) }); setOppModalVisible(true); }}>Modifica</Button>
        )},
    ];

    const leadColManager = useColumnManagerWithDrawer('crm_leads', rawLeadColumns);
    const oppColManager = useColumnManagerWithDrawer('crm_opportunities', rawOppColumns);

    return (
        <Layout>
            <div style={{ padding: 24 }}>
                {pipelineSummary.length > 0 && (
                    <Row gutter={16} style={{ marginBottom: 16 }}>
                        {pipelineSummary.map(s => (
                            <Col span={4} key={s.stage}>
                                <Card size="small">
                                    <Statistic
                                        title={stageLabels[s.stage] || s.stage}
                                        value={s.count}
                                        suffix={`€${(s.total_revenue || 0).toFixed(0)}`}
                                        valueStyle={{ fontSize: 18 }}
                                    />
                                </Card>
                            </Col>
                        ))}
                    </Row>
                )}
                <Card extra={
                    <Space>
                        <ColumnSettingsButton manager={leadColManager} />
                        <ColumnSettingsButton manager={oppColManager} />
                    </Space>
                }>
                    <Tabs items={[
                        { key: 'leads', label: 'Lead', children: (
                            <>
                                <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditingLead(null); leadForm.resetFields(); setLeadModalVisible(true); }} style={{ marginBottom: 16 }}>Nuovo Lead</Button>
                                <Table dataSource={leads} columns={leadColManager.processedColumns} rowKey="id" loading={loading} />
                            </>
                        )},
                        { key: 'opportunities', label: 'Opportunità', children: (
                            <>
                                <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditingOpp(null); oppForm.resetFields(); setOppModalVisible(true); }} style={{ marginBottom: 16 }}>Nuova Opportunità</Button>
                                <Table dataSource={opportunities} columns={oppColManager.processedColumns} rowKey="id" loading={loading} />
                            </>
                        )},
                    ]} />
                </Card>
                <Modal title={editingLead ? 'Modifica Lead' : 'Nuovo Lead'} open={leadModalVisible} onOk={handleLeadSubmit} onCancel={() => { setLeadModalVisible(false); leadForm.resetFields(); setEditingLead(null); }}>
                    <Form form={leadForm} layout="vertical">
                        <Space size={16}>
                            <Form.Item name="first_name" label="Nome" rules={[{ required: true }]}><Input /></Form.Item>
                            <Form.Item name="last_name" label="Cognome" rules={[{ required: true }]}><Input /></Form.Item>
                        </Space>
                        <Form.Item name="company" label="Azienda"><Input /></Form.Item>
                        <Space size={16}>
                            <Form.Item name="email" label="Email"><Input /></Form.Item>
                            <Form.Item name="phone" label="Telefono"><Input /></Form.Item>
                        </Space>
                        <Form.Item name="source" label="Provenienza">
                            <Select options={[
                                { value: 'website', label: 'Sito Web' }, { value: 'referral', label: 'Referral' },
                                { value: 'cold_call', label: 'Chiamata' }, { value: 'email_campaign', label: 'Email' },
                                { value: 'trade_show', label: 'Fiera' }, { value: 'other', label: 'Altro' },
                            ]} />
                        </Form.Item>
                        <Form.Item name="notes" label="Note"><Input.TextArea rows={2} /></Form.Item>
                    </Form>
                </Modal>
                <Modal title={editingOpp ? 'Modifica Opportunità' : 'Nuova Opportunità'} open={oppModalVisible} onOk={handleOppSubmit} onCancel={() => { setOppModalVisible(false); oppForm.resetFields(); setEditingOpp(null); }}>
                    <Form form={oppForm} layout="vertical">
                        <Form.Item name="name" label="Nome" rules={[{ required: true }]}><Input /></Form.Item>
                        <Space size={16}>
                            <Form.Item name="expected_revenue" label="Valore Previsto"><InputNumber min={0} step={100} prefix="€" /></Form.Item>
                            <Form.Item name="probability" label="Probabilità %"><InputNumber min={0} max={100} step={5} /></Form.Item>
                        </Space>
                        <Form.Item name="stage" label="Stadio">
                            <Select options={Object.entries(stageLabels).map(([k, v]) => ({ value: k, label: v }))} />
                        </Form.Item>
                        <Form.Item name="expected_close_date" label="Chiusura Prevista"><DatePicker format={formatDateForDisplay} /></Form.Item>
                        <Form.Item name="notes" label="Note"><Input.TextArea rows={2} /></Form.Item>
                    </Form>
                </Modal>
            </div>
        </Layout>
    );
};
