import React, { useState, useEffect, useCallback } from 'react';
import { Card, Table, Button, Modal, Form, Input, InputNumber, DatePicker, Select, Space, Tag, message, Row, Col, Statistic, Spin } from 'antd';
import { PlusOutlined, ThunderboltOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { apiFetch } from '@/utils';
import { parseDateForForm, formatDateForApi, formatDateTimeForDisplay } from '@/utils/dateUtils'; // Import date utilities
import { useColumnManagerWithDrawer } from '@/hooks/useColumnManager';
import ColumnSettingsButton from '@/components/ColumnSettingsButton';
import Layout from '../components/Layout';
const statusColors = { open: 'blue', in_progress: 'processing', fulfilled: 'green', cancelled: 'red' };

export default function MRPPage() {
    const [runs, setRuns] = useState([]);
    const [selectedRun, setSelectedRun] = useState(null);
    const [suggestions, setSuggestions] = useState([]);
    const [loading, setLoading] = useState(false);
    const [running, setRunning] = useState(false);
    const [modalVisible, setModalVisible] = useState(false);
    const [form] = Form.useForm();

    const fetch = useCallback(async (autoSelect) => {
        setLoading(true);
        try {
            const res = await apiFetch('/api/v1/mrp/runs');
            if (res.ok) {
                const d = await res.json();
                setRuns(d);
                if (autoSelect && d.length > 0) fetchRun(d[0].id);
            }
        } catch { message.error('Error'); }
        finally { setLoading(false); }
    }, []);
    
    useEffect(() => { fetch(true); }, [fetch]);

    const fetchRun = async (id) => {
        try {
            const res = await apiFetch(`/api/v1/mrp/runs/${id}`);
            if (res.ok) { const d = await res.json(); setSelectedRun(d); setSuggestions(d.suggestions || []); }
        } catch { message.error('Error'); }
    };

    const handleRun = async () => {
        setRunning(true);
        try {
            const values = await form.validateFields();
            const res = await apiFetch('/api/v1/mrp/runs', {
                method: 'POST', body: JSON.stringify({ notes: values.notes, horizon_date: formatDateForApi(values.horizon_date) })
            });
            if (res.ok) { const d = await res.json(); message.success(`MRP completato: ${d.suggestions_created} suggerimenti`); fetch(); setModalVisible(false); }
            else { const e = await res.json(); message.error(e.message || 'Errore'); }
        } catch { message.error('Error'); }
        finally { setRunning(false); }
    };

    const handleUpdateSuggestion = async (id, status) => {
        try {
            const res = await apiFetch(`/api/v1/mrp/suggestions/${id}`, { method: 'PUT', body: JSON.stringify({ status }) });
            if (res.ok) { message.success('Aggiornato'); if (selectedRun) fetchRun(selectedRun.id); }
        } catch { message.error('Error'); }
    };

    const runColumns = [
        { title: 'Data', dataIndex: 'run_date', render: (v) => formatDateTimeForDisplay(v) || '-' },
        { title: 'Suggerimenti', dataIndex: 'total_suggestions' },
        { title: 'Stato', dataIndex: 'status', render: (v) => <Tag color={v === 'completed' ? 'green' : 'red'}>{v}</Tag> },
        { title: 'Azioni', render: (_, r) => (
            <Button type="link" onClick={() => fetchRun(r.id)}>Vedi</Button>
        )},
    ];

    const rawSugColumns = [
        { title: 'Prodotto', dataIndex: 'product_name' },
        { title: 'Tipo', dataIndex: 'suggestion_type', render: (v) => <Tag color={v === 'purchase' ? 'orange' : 'blue'}>{v === 'purchase' ? 'Acquista' : 'Produci'}</Tag> },
        { title: 'Richiesto', dataIndex: 'required_quantity' },
        { title: 'Disponibile', dataIndex: 'available_quantity' },
        { title: 'Suggerito', dataIndex: 'suggested_quantity' },
        { title: 'Fonte', dataIndex: 'source' },
        { title: 'Stato', dataIndex: 'status', render: (v) => <Tag color={statusColors[v]}>{v}</Tag> },
        { title: 'Azioni', render: (_, r) => (
            <Space>
                {r.status === 'open' && <Button type="link" size="small" icon={<CheckCircleOutlined />} onClick={() => handleUpdateSuggestion(r.id, 'in_progress')}>Avvia</Button>}
                {r.status === 'in_progress' && <Button type="link" size="small" icon={<CheckCircleOutlined />} onClick={() => handleUpdateSuggestion(r.id, 'fulfilled')}>Evadi</Button>}
            </Space>
        )},
    ];

    const runColManager = useColumnManagerWithDrawer('mrp_runs', runColumns);
    const sugColManager = useColumnManagerWithDrawer('mrp_suggestions', rawSugColumns);

    const purchaseSugs = suggestions.filter(s => s.suggestion_type === 'purchase');
    const produceSugs = suggestions.filter(s => s.suggestion_type === 'produce');

    return (
        <Layout>
            <div style={{ padding: 24 }}>
                <Row gutter={16} style={{ marginBottom: 16 }}>
                    <Col span={4}><Card size="small"><Statistic title="Corse MRP" value={runs.length} /></Card></Col>
                    <Col span={5}><Card size="small"><Statistic title="Da Acquistare" value={purchaseSugs.reduce((s, i) => s + (i.suggested_quantity || 0), 0)} /></Card></Col>
                    <Col span={5}><Card size="small"><Statistic title="Da Produrre" value={produceSugs.reduce((s, i) => s + (i.suggested_quantity || 0), 0)} /></Card></Col>
                    <Col span={5}><Card size="small"><Statistic title="Suggerimenti Aperti" value={suggestions.filter(s => s.status === 'open').length} /></Card></Col>
                </Row>
                <Card title="Produzione (MRP)" extra={
                    <Space>
                        <ColumnSettingsButton manager={runColManager} />
                        <ColumnSettingsButton manager={sugColManager} />
                        <Button type="primary" icon={<ThunderboltOutlined />} onClick={() => { form.resetFields(); setModalVisible(true); }}>Esegui MRP</Button>
                    </Space>
                }>
                    <Row gutter={16}>
                        <Col span={8}>
                            <Table dataSource={runs} columns={runColManager.processedColumns} rowKey="id" loading={loading} size="small" />
                        </Col>
                        <Col span={16}>
                            {selectedRun && (
                                <Table dataSource={suggestions} columns={sugColManager.processedColumns} rowKey="id" size="small"
                                    pagination={false} />
                            )}
                        </Col>
                    </Row>
                </Card>
                <Modal title="Esegui MRP" open={modalVisible} onOk={handleRun} onCancel={() => setModalVisible(false)} okText="Esegui" cancelText="Annulla" confirmLoading={running}>
                    <Form form={form} layout="vertical">
                        <Form.Item name="horizon_date" label="Orizzonte (data max)">
                            <DatePicker style={{ width: '100%' }} />
                        </Form.Item>
                        <Form.Item name="notes" label="Note"><Input.TextArea rows={2} /></Form.Item>
                    </Form>
                </Modal>
            </div>
        </Layout>
    );
};
