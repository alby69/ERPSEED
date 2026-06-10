import React, { useState, useEffect, useCallback } from 'react';
import { Card, Table, Button, Modal, Form, Input, Select, Space, Tag, message, Tabs, Drawer, Badge, Tooltip, Row, Col, Empty, Spin } from 'antd';
import { PlusOutlined, EditOutlined, PlayCircleOutlined, HistoryOutlined, DeleteOutlined, SettingOutlined } from '@ant-design/icons';
import { apiFetch } from '@/utils';

import { formatDateTimeForDisplay } from '@/utils/dateUtils';
import { useColumnManagerWithDrawer } from '@/hooks/useColumnManager';
import ColumnSettingsButton from '@/components/ColumnSettingsButton';
const ReportDesigner = () => {
    const [reports, setReports] = useState([]);
    const [sources, setSources] = useState([]);
    const [loading, setLoading] = useState(false);
    const [executing, setExecuting] = useState(false);
    const [results, setResults] = useState(null);
    const [activeReport, setActiveReport] = useState(null);
    const [showDesigner, setShowDesigner] = useState(false);
    const [editing, setEditing] = useState(null);
    const [history, setHistory] = useState([]);

    // Form state
    const [code, setCode] = useState('');
    const [name, setName] = useState('');
    const [category, setCategory] = useState('general');
    const [source, setSource] = useState('');
    const [selectedColumns, setSelectedColumns] = useState([]);
    const [filters, setFilters] = useState([]);
    const [limit, setLimit] = useState(500);

    const fetchReports = useCallback(async () => {
        setLoading(true);
        try {
            const res = await apiFetch('/api/v1/report-designer/reports');
            if (res.ok) setReports(await res.json());
        } catch { message.error('Error'); }
        finally { setLoading(false); }
    }, []);

    const fetchSources = useCallback(async () => {
        try {
            const res = await apiFetch('/api/v1/report-designer/sources');
            if (res.ok) setSources(await res.json());
        } catch (e) { console.error('fetchSources', e); }
    }, []);

    useEffect(() => { fetchReports(); fetchSources(); }, [fetchReports, fetchSources]);

    const currentSource = sources.find(s => s.key === source);

    const handleSave = async () => {
        if (!code || !name || !source || selectedColumns.length === 0) {
            message.error('Code, name, source, and at least one column required');
            return;
        }
        const config = { source, columns: selectedColumns, filters, limit };
        const payload = { code, name, category, config };
        try {
            let res;
            if (editing) res = await apiFetch(`/api/v1/report-designer/reports/${editing.id}`, { method: 'PUT', body: JSON.stringify(payload) });
            else res = await apiFetch('/api/v1/report-designer/reports', { method: 'POST', body: JSON.stringify(payload) });
            if (res.ok) { message.success('Salvato'); fetchReports(); setShowDesigner(false); resetForm(); }
            else { const e = await res.json(); message.error(e.message || 'Errore'); }
        } catch { message.error('Error'); }
    };

    const handleExecute = async (report) => {
        setExecuting(true);
        setActiveReport(report);
        try {
            const res = await apiFetch(`/api/v1/report-designer/reports/${report.id}/execute`, { method: 'POST', body: JSON.stringify({}) });
            if (res.ok) { const data = await res.json(); setResults(data); }
            else { const e = await res.json(); message.error(e.message || 'Errore'); }
        } catch { message.error('Error'); }
        finally { setExecuting(false); }
    };

    const handleDelete = async (id) => {
        try {
            const res = await apiFetch(`/api/v1/report-designer/reports/${id}`, { method: 'DELETE' });
            if (res.ok) { message.success('Eliminato'); fetchReports(); if (activeReport?.id === id) { setActiveReport(null); setResults(null); } }
        } catch { message.error('Error'); }
    };

    const handleEdit = (r) => {
        setEditing(r);
        const cfg = (r.config || {});
        setCode(r.code);
        setName(r.name);
        setCategory(r.category);
        setSource(cfg.source || '');
        setSelectedColumns(cfg.columns || []);
        setFilters(cfg.filters || []);
        setLimit(cfg.limit || 500);
        setShowDesigner(true);
    };

    const fetchHistory = async (reportId) => {
        try {
            const res = await apiFetch(`/api/v1/report-designer/reports/${reportId}/history`);
            if (res.ok) setHistory(await res.json());
        } catch (e) { console.error('fetchHistory', e); }
    };

    const addFilter = () => setFilters([...filters, { field: '', operator: 'eq', value: '' }]);
    const updateFilter = (i, k, v) => { const f = [...filters]; f[i][k] = v; setFilters(f); };
    const removeFilter = (i) => setFilters(filters.filter((_, idx) => idx !== i));

    const resetForm = () => {
        setEditing(null); setCode(''); setName(''); setCategory('general');
        setSource(''); setSelectedColumns([]); setFilters([]); setLimit(500);
    };

    const rawColumns = [
        { title: 'Codice', dataIndex: 'code' },
        { title: 'Nome', dataIndex: 'name' },
        { title: 'Categoria', dataIndex: 'category' },
        { title: 'Azioni', render: (_, r) => (
            <Space>
                <Button type="link" icon={<PlayCircleOutlined />} onClick={() => handleExecute(r)}>Esegui</Button>
                <Button type="link" icon={<EditOutlined />} onClick={() => handleEdit(r)}>Modifica</Button>
                <Button type="link" danger icon={<DeleteOutlined />} onClick={() => handleDelete(r.id)} />
            </Space>
        )},
    ];

    const colManager = useColumnManagerWithDrawer('report_designer', rawColumns);

    const resultColumns = results?.columns?.map(c => ({ title: c, dataIndex: c, ellipsis: true })) || [];

    return (
        <div style={{ padding: 24 }}>
            <Row gutter={16}>
                <Col span={activeReport ? 14 : 24}>
                    <Card title="Report Designer" extra={
                        <Space>
                            <ColumnSettingsButton manager={colManager} />
                            <Button type="primary" icon={<PlusOutlined />} onClick={() => { resetForm(); setShowDesigner(true); }}>Nuovo Report</Button>
                        </Space>
                    }>
                        <Table dataSource={reports} columns={colManager.processedColumns} rowKey="id" loading={loading} size="small" />
                    </Card>
                </Col>
                {activeReport && (
                    <Col span={10}>
                        <Card title={`Risultati: ${activeReport.name}`} size="small" extra={
                            <Space>
                                <Badge count={results?.row_count || 0}><Tag>{results?.execution_time_ms}ms</Tag></Badge>
                                <Button size="small" icon={<HistoryOutlined />} onClick={() => fetchHistory(activeReport.id)}>Storico</Button>
                            </Space>
                        }>
                            <Spin spinning={executing}>
                                {results ? (
                                    <Table dataSource={results.data} columns={resultColumns} rowKey={(_, i) => i} pagination={{ pageSize: 20 }} size="small" scroll={{ x: 'max-content' }} />
                                ) : (
                                    <Empty description="Esegui il report per vedere i risultati" />
                                )}
                            </Spin>
                            {history.length > 0 && (
                                <Card title="Esecuzioni Recenti" size="small" style={{ marginTop: 8 }}>
                                    <Table dataSource={history} size="small" pagination={false}
                                        columns={[
                                            { title: 'Data', dataIndex: 'created_at', render: (v) => formatDateTimeForDisplay(v) || '-' },
                                            { title: 'Righe', dataIndex: 'row_count' },
                                            { title: 'Tempo', dataIndex: 'execution_time_ms', render: (v) => `${v}ms` },
                                            { title: 'Stato', dataIndex: 'status', render: (v) => <Tag color={v === 'completed' ? 'green' : 'red'}>{v}</Tag> },
                                        ]} rowKey="id" />
                                </Card>
                            )}
                        </Card>
                    </Col>
                )}
            </Row>

            <Drawer title={editing ? 'Modifica Report' : 'Nuovo Report'} open={showDesigner} onClose={() => setShowDesigner(false)} width={500} extra={<Button type="primary" onClick={handleSave}>Salva</Button>}>
                <Form layout="vertical">
                    <Form.Item label="Codice" required><Input value={code} onChange={e => setCode(e.target.value)} /></Form.Item>
                    <Form.Item label="Nome" required><Input value={name} onChange={e => setName(e.target.value)} /></Form.Item>
                    <Form.Item label="Categoria"><Select value={category} onChange={setCategory} options={[
                        { value: 'general', label: 'Generale' }, { value: 'sales', label: 'Vendite' },
                        { value: 'purchases', label: 'Acquisti' }, { value: 'inventory', label: 'Magazzino' },
                        { value: 'accounting', label: 'Contabilità' }, { value: 'hr', label: 'HR' },
                    ]} /></Form.Item>
                    <Form.Item label="Origine Dati" required>
                        <Select value={source} onChange={(v) => { setSource(v); setSelectedColumns([]); }}
                            options={sources.map(s => ({ value: s.key, label: s.label }))} />
                    </Form.Item>
                    {currentSource && (
                        <Form.Item label="Colonne" required>
                            <Select mode="multiple" value={selectedColumns} onChange={setSelectedColumns}
                                options={currentSource.columns.map(c => ({ value: c, label: c }))} />
                        </Form.Item>
                    )}
                    <Form.Item label="Filtri">
                        {filters.map((f, i) => (
                            <Space key={i} style={{ display: 'flex', marginBottom: 8 }}>
                                <Select value={f.field} onChange={(v) => updateFilter(i, 'field', v)} style={{ width: 140 }}
                                    options={(currentSource?.columns || []).map(c => ({ value: c, label: c }))} placeholder="Campo" />
                                <Select value={f.operator} onChange={(v) => updateFilter(i, 'operator', v)} style={{ width: 100 }}
                                    options={[
                                        { value: 'eq', label: '=' }, { value: 'neq', label: '!=' },
                                        { value: 'gt', label: '>' }, { value: 'gte', label: '>=' },
                                        { value: 'lt', label: '<' }, { value: 'lte', label: '<=' },
                                        { value: 'like', label: 'contiene' }, { value: 'in', label: 'in' },
                                        { value: 'is_null', label: 'è nullo' }, { value: 'is_not_null', label: 'non nullo' },
                                    ]} />
                                {!['is_null', 'is_not_null'].includes(f.operator) && (
                                    <Input value={f.value} onChange={(e) => updateFilter(i, 'value', e.target.value)} placeholder="Valore" style={{ width: 120 }} />
                                )}
                                <Button type="text" danger icon={<DeleteOutlined />} onClick={() => removeFilter(i)} />
                            </Space>
                        ))}
                        <Button size="small" onClick={addFilter}>+ Aggiungi Filtro</Button>
                    </Form.Item>
                    <Form.Item label="Limite Righe"><Select value={limit} onChange={setLimit} options={[
                        { value: 100, label: '100' }, { value: 500, label: '500' },
                        { value: 1000, label: '1000' }, { value: 5000, label: '5000' },
                    ]} /></Form.Item>
                </Form>
            </Drawer>
        </div>
    );
};

export default ReportDesigner;
