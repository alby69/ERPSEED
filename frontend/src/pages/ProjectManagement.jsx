import React, { useState, useEffect, useCallback } from 'react';
import { Card, Table, Tabs, Button, Modal, Form, Input, InputNumber, DatePicker, Select, Space, Tag, Statistic, Row, Col, message } from 'antd';
import { PlusOutlined, EditOutlined } from '@ant-design/icons';
import { apiFetch } from '@/utils';
import { parseDateForForm, formatDateForApi, formatDateForDisplay } from '@/utils/dateUtils';

const statusColors = { active: 'green', closed: 'orange', archived: 'default', draft: 'default', submitted: 'blue', approved: 'green' };

const ProjectTab = () => {
    const [data, setData] = useState([]);
    const [subjects, setSubjects] = useState([]);
    const [loading, setLoading] = useState(false);
    const [modalVisible, setModalVisible] = useState(false);
    const [editing, setEditing] = useState(null);
    const [form] = Form.useForm();

    const fetch = useCallback(async () => {
        setLoading(true);
        try {
            const [pRes, sRes] = await Promise.all([
                apiFetch('/api/v1/project-management/projects'),
                apiFetch('/api/v1/soggetti'),
            ]);
            if (pRes.ok) setData(await pRes.json());
            if (sRes.ok) setSubjects(await sRes.json());
        } catch { message.error('Error'); }
        finally { setLoading(false); }
    }, []);

    useEffect(() => { fetch(); }, [fetch]);

    const handleSubmit = async () => {
        try {
            const values = await form.validateFields();
            values.start_date = formatDateForApi(values.start_date);
            values.end_date = formatDateForApi(values.end_date);
            let res;
            if (editing) res = await apiFetch(`/api/v1/project-management/projects/${editing.id}`, { method: 'PUT', body: JSON.stringify(values) });
            else res = await apiFetch('/api/v1/project-management/projects', { method: 'POST', body: JSON.stringify(values) });
            if (res.ok) { message.success('Salvato'); setModalVisible(false); form.resetFields(); setEditing(null); fetch(); }
            else { const e = await res.json(); message.error(e.message || 'Errore'); }
        } catch { message.error('Validation'); }
    };

    const columns = [
        { title: 'Codice', dataIndex: 'code' },
        { title: 'Nome', dataIndex: 'name' },
        { title: 'Cliente', dataIndex: 'client_id', render: (id) => { const s = subjects.find(x => x.id === id); return s?.nome || s?.ragione_sociale || '-'; } }, // No change needed here
        { title: 'Inizio', dataIndex: 'start_date', render: (v) => formatDateForDisplay(v) || '-' },
        { title: 'Fine', dataIndex: 'end_date', render: (v) => formatDateForDisplay(v) || '-' },
        { title: 'Budget', dataIndex: 'budget_amount', render: (v) => `€${(v || 0).toFixed(2)}` },
        { title: 'Ore St.', dataIndex: 'estimated_hours' },
        { title: 'Stato', dataIndex: 'status', render: (v) => <Tag color={statusColors[v]}>{v}</Tag> },
        { title: 'Azioni', render: (_, r) => (
            <Button type="link" icon={<EditOutlined />} onClick={() => { setEditing(r); form.setFieldsValue({ ...r, start_date: parseDateForForm(r.start_date), end_date: parseDateForForm(r.end_date) }); setModalVisible(true); }}>Modifica</Button>
        )},
    ];

    return (
        <>
            <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditing(null); form.resetFields(); setModalVisible(true); }} style={{ marginBottom: 16 }}>Nuovo Progetto</Button>
            <Table dataSource={data} columns={columns} rowKey="id" loading={loading} />
            <Modal title={editing ? 'Modifica Progetto' : 'Nuovo Progetto'} open={modalVisible} onOk={handleSubmit} onCancel={() => { setModalVisible(false); form.resetFields(); setEditing(null); }} okText="Salva" cancelText="Annulla" width={700}>
                <Form form={form} layout="vertical">
                    <Space size={16}>
                        <Form.Item name="code" label="Codice" rules={[{ required: true }]}><Input /></Form.Item>
                        <Form.Item name="name" label="Nome" rules={[{ required: true }]}><Input style={{ width: 300 }} /></Form.Item>
                    </Space>
                    <Space size={16}>
                        <Form.Item name="client_id" label="Cliente"><Select style={{ width: 200 }} allowClear showSearch optionFilterProp="label" options={subjects.map(s => ({ value: s.id, label: s.nome || s.ragione_sociale }))} /></Form.Item>
                        <Form.Item name="status" label="Stato"><Select options={[{ value: 'active', label: 'Attivo' }, { value: 'closed', label: 'Chiuso' }, { value: 'archived', label: 'Archiviato' }]} /></Form.Item>
                    </Space>
                    <Space size={16}> {/* Use formatDateForDisplay for DatePicker format */}
                        <Form.Item name="start_date" label="Data Inizio"><DatePicker format={formatDateForDisplay} /></Form.Item>
                        <Form.Item name="end_date" label="Data Fine"><DatePicker format={formatDateForDisplay} /></Form.Item>
                        <Form.Item name="budget_amount" label="Budget"><InputNumber min={0} step={100} prefix="€" /></Form.Item>
                        <Form.Item name="estimated_hours" label="Ore Stimate"><InputNumber min={0} /></Form.Item>
                    </Space>
                    <Space size={16}>
                        <Form.Item name="hourly_rate" label="Tariffa Oraria"><InputNumber min={0} prefix="€" /></Form.Item>
                    </Space>
                    <Form.Item name="description" label="Descrizione"><Input.TextArea rows={2} /></Form.Item>
                </Form>
            </Modal>
        </>
    );
};

const TimesheetTab = () => {
    const [data, setData] = useState([]);
    const [employees, setEmployees] = useState([]);
    const [projects, setProjects] = useState([]);
    const [loading, setLoading] = useState(false);
    const [modalVisible, setModalVisible] = useState(false);
    const [editing, setEditing] = useState(null);
    const [form] = Form.useForm();

    const fetch = useCallback(async () => {
        setLoading(true);
        try {
            const [tRes, eRes, pRes] = await Promise.all([
                apiFetch('/api/v1/project-management/timesheets'),
                apiFetch('/hr/employees'),
                apiFetch('/api/v1/project-management/projects'),
            ]);
            if (tRes.ok) setData(await tRes.json());
            if (eRes.ok) setEmployees(await eRes.json());
            if (pRes.ok) setProjects(await pRes.json());
        } catch { message.error('Error'); }
        finally { setLoading(false); }
    }, []);

    useEffect(() => { fetch(); }, [fetch]);

    const handleSubmit = async () => {
        try {
            const values = await form.validateFields();
            values.date = formatDateForApi(values.date);
            let res;
            if (editing) res = await apiFetch(`/api/v1/project-management/timesheets/${editing.id}`, { method: 'PUT', body: JSON.stringify(values) });
            else res = await apiFetch('/api/v1/project-management/timesheets', { method: 'POST', body: JSON.stringify(values) });
            if (res.ok) { message.success('Salvato'); setModalVisible(false); form.resetFields(); setEditing(null); fetch(); }
            else { const e = await res.json(); message.error(e.message || 'Errore'); }
        } catch { message.error('Validation'); }
    };

    const handleAction = async (id, action) => {
        try {
            const res = await apiFetch(`/api/v1/project-management/timesheets/${id}/${action}`, { method: 'POST' });
            if (res.ok) { message.success('Ok'); fetch(); }
            else { const e = await res.json(); message.error(e.message || 'Errore'); }
        } catch { message.error('Error'); }
    };

    const columns = [
        { title: 'Data', dataIndex: 'date', render: (v) => formatDateForDisplay(v) || '-' },
        { title: 'Dipendente', dataIndex: 'employee_id', render: (id) => { const e = employees.find(x => x.id === id); return e ? `${e.first_name} ${e.last_name}` : '-'; } }, // No change needed here
        { title: 'Ore', key: 'hours', render: (_, r) => (r.lines || []).reduce((s, l) => s + (l.hours || 0), 0) }, // No change needed here
        { title: 'Stato', dataIndex: 'status', render: (v) => <Tag color={statusColors[v]}>{v}</Tag> }, // No change needed here
        { title: 'Azioni', render: (_, r) => (
            <Space>
                <Button type="link" icon={<EditOutlined />} onClick={() => { setEditing(r); form.setFieldsValue({ ...r, date: parseDateForForm(r.date) }); setModalVisible(true); }}>Modifica</Button>
                {r.status === 'draft' && <Button type="link" onClick={() => handleAction(r.id, 'submit')}>Invia</Button>}
                {r.status === 'submitted' && <Button type="link" onClick={() => handleAction(r.id, 'approve')}>Approva</Button>}
            </Space>
        )},
    ];

    const expandedRowRender = (record) => {
        const cols = [
            { title: 'Progetto', dataIndex: 'project_id', render: (id) => { const p = projects.find(x => x.id === id); return p?.name || '-'; } },
            { title: 'Ore', dataIndex: 'hours' },
            { title: 'Descrizione', dataIndex: 'description' },
        ];
        return <Table dataSource={record.lines || []} columns={cols} rowKey="id" pagination={false} size="small" />;
    };

    return (
        <>
            <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditing(null); form.resetFields(); setModalVisible(true); }} style={{ marginBottom: 16 }}>Nuova Scheda Ore</Button>
            <Table dataSource={data} columns={columns} rowKey="id" loading={loading} expandable={{ expandedRowRender }} />
            <Modal title={editing ? 'Modifica Scheda Ore' : 'Nuova Scheda Ore'} open={modalVisible} onOk={handleSubmit} onCancel={() => { setModalVisible(false); form.resetFields(); setEditing(null); }} okText="Salva" cancelText="Annulla" width={700}>
                <Form form={form} layout="vertical">
                    <Space size={16}>
                        <Form.Item name="employee_id" label="Dipendente" rules={[{ required: true }]}>
                            <Select style={{ width: 250 }} showSearch optionFilterProp="label" options={employees.map(e => ({ value: e.id, label: `${e.first_name} ${e.last_name}` }))} />
                        </Form.Item>
                        <Form.Item name="date" label="Data" rules={[{ required: true }]}><DatePicker format={formatDateForDisplay} /></Form.Item>
                        <Form.Item name="status" label="Stato"><Select options={[{ value: 'draft', label: 'Bozza' }, { value: 'submitted', label: 'Inviato' }]} /></Form.Item>
                    </Space>
                    <Form.Item name="notes" label="Note"><Input.TextArea rows={2} /></Form.Item>
                </Form>
            </Modal>
        </>
    );
};

const ProjectManagement = () => {
    const [summary, setSummary] = useState(null);

    useEffect(() => {
        apiFetch('/api/v1/project-management/summary').then(r => r.ok && r.json().then(setSummary));
    }, []);

    return (
        <div style={{ padding: 24 }}>
            {summary && (
                <Row gutter={16} style={{ marginBottom: 16 }}>
                    <Col span={4}><Card><Statistic title="Progetti" value={summary.total_projects} suffix={`/${summary.active_projects} attivi`} /></Card></Col>
                    <Col span={5}><Card><Statistic title="Budget Totale" value={summary.total_budget} precision={2} prefix="€" /></Card></Col>
                    <Col span={5}><Card><Statistic title="Ore Stimate" value={summary.total_estimated_hours} /></Card></Col>
                    <Col span={5}><Card><Statistic title="Ore Registrate" value={summary.total_logged_hours} /></Card></Col>
                </Row>
            )}
            <Card title="Progetti e Timesheet">
                <Tabs items={[
                    { key: 'projects', label: 'Progetti', children: <ProjectTab /> },
                    { key: 'timesheets', label: 'Timesheet', children: <TimesheetTab /> },
                ]} />
            </Card>
        </div>
    );
};
