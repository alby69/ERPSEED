import React, { useState, useEffect, useCallback } from 'react';
import { Card, Table, Tabs, Button, Modal, Form, Input, InputNumber, DatePicker, Select, Space, Tag, message, Row, Col, Statistic } from 'antd';
import { PlusOutlined, EditOutlined, CheckOutlined, CloseOutlined } from '@ant-design/icons';
import { apiFetch } from '@/utils';
import { useColumnManagerWithDrawer } from '@/hooks/useColumnManager';
import ColumnSettingsButton from '@/components/ColumnSettingsButton';
import dayjs from 'dayjs'; // Keep dayjs for time-only operations and diffs
import { parseDateForForm, formatDateForApi, formatDateForDisplay } from '@/utils/dateUtils'; // Import date utilities

const statusColors = { active: 'green', inactive: 'orange', terminated: 'red', present: 'green', absent: 'red', late: 'orange', leave: 'blue', pending: 'orange', approved: 'green', rejected: 'red', draft: 'default', submitted: 'blue' }; // This line was outside the component, moving it inside the export default function

// ========== Employees Tab ==========
const EmployeesTab = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [departments, setDepartments] = useState([]);
    const [modalVisible, setModalVisible] = useState(false);
    const [editingRecord, setEditingRecord] = useState(null);
    const [form] = Form.useForm();

    const fetchData = useCallback(async () => {
        setLoading(true);
        try {
            const [eRes, dRes] = await Promise.all([
                apiFetch('/hr/employees'),
                apiFetch('/hr/departments'),
            ]);
            if (eRes.ok) setData(await eRes.json());
            if (dRes.ok) setDepartments(await dRes.json());
        } catch { message.error('Error loading'); }
        finally { setLoading(false); }
    }, []);

    useEffect(() => { fetchData(); }, [fetchData]);

    const handleSubmit = async () => {
        try {
            const values = await form.validateFields();
            values.hire_date = formatDateForApi(values.hire_date);
            let res;
            if (editingRecord) res = await apiFetch(`/hr/employees/${editingRecord.id}`, { method: 'PUT', body: JSON.stringify(values) });
            else res = await apiFetch('/hr/employees', { method: 'POST', body: JSON.stringify(values) });
            if (res.ok) { message.success('Salvato'); setModalVisible(false); form.resetFields(); setEditingRecord(null); fetchData(); }
            else { const e = await res.json(); message.error(e.message || 'Errore'); }
        } catch { message.error('Validation failed'); }
    };

    const rawColumns = [
        { title: 'Matricola', dataIndex: 'employee_number' },
        { title: 'Nome', key: 'name', render: (_, r) => `${r.first_name} ${r.last_name}` },
        { title: 'Email', dataIndex: 'email' },
        { title: 'Reparto', dataIndex: 'department_id', render: (id) => { const d = departments.find(x => x.id === id); return d ? d.name : '-'; } },
        { title: 'Mansione', dataIndex: 'job_title' },
        { title: 'Stato', dataIndex: 'status', render: (v) => <Tag color={statusColors[v]}>{v}</Tag> },
        { title: 'Azioni', render: (_, r) => (
            <Button type="link" icon={<EditOutlined />} onClick={() => { setEditingRecord(r); form.setFieldsValue({ ...r, hire_date: parseDateForForm(r.hire_date) }); setModalVisible(true); }}>Modifica</Button>
        )},
    ];

    const colManager = useColumnManagerWithDrawer('hr_employees', rawColumns);

    return (
        <>
            <Space style={{ marginBottom: 16 }}>
                <ColumnSettingsButton manager={colManager} />
                <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditingRecord(null); form.resetFields(); setModalVisible(true); }}>Nuovo Dipendente</Button>
            </Space>
            <Table dataSource={data} columns={colManager.processedColumns} rowKey="id" loading={loading} />
            <Modal title={editingRecord ? 'Modifica Dipendente' : 'Nuovo Dipendente'} open={modalVisible} onOk={handleSubmit} onCancel={() => { setModalVisible(false); form.resetFields(); setEditingRecord(null); }} okText="Salva" cancelText="Annulla" width={600}>
                <Form form={form} layout="vertical">
                    <Space size={16}>
                        <Form.Item name="employee_number" label="Matricola" rules={[{ required: true }]}><Input /></Form.Item>
                        <Form.Item name="first_name" label="Nome" rules={[{ required: true }]}><Input /></Form.Item>
                        <Form.Item name="last_name" label="Cognome" rules={[{ required: true }]}><Input /></Form.Item>
                    </Space>
                    <Space size={16}>
                        <Form.Item name="email" label="Email"><Input /></Form.Item>
                        <Form.Item name="phone" label="Telefono"><Input /></Form.Item>
                    </Space>
                    <Space size={16}>
                        <Form.Item name="department_id" label="Reparto" style={{ minWidth: 200 }}>
                            <Select allowClear options={departments.map(d => ({ value: d.id, label: d.name }))} />
                        </Form.Item>
                        <Form.Item name="job_title" label="Mansione"><Input /></Form.Item>
                        <Form.Item name="status" label="Stato">
                            <Select options={[{ value: 'active', label: 'Attivo' }, { value: 'inactive', label: 'Inattivo' }, { value: 'terminated', label: 'Cessato' }]} />
                        </Form.Item>
                    </Space>
                    <Space size={16}>
                        <Form.Item name="employee_type" label="Tipo">
                            <Select options={[{ value: 'full-time', label: 'Full Time' }, { value: 'part-time', label: 'Part Time' }, { value: 'contractor', label: 'Consulente' }]} />
                        </Form.Item>
                        <Form.Item name="salary" label="Stipendio"><InputNumber min={0} step={100} prefix="€" /></Form.Item> {/* Use formatDateForDisplay for DatePicker format */}
                        <Form.Item name="hire_date" label="Data Assunzione"><DatePicker format={formatDateForDisplay} /></Form.Item>
                    </Space>
                </Form>
            </Modal>
        </>
    );
};

// ========== Departments Tab ==========
const DepartmentsTab = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [modalVisible, setModalVisible] = useState(false);
    const [editingRecord, setEditingRecord] = useState(null);
    const [form] = Form.useForm();

    const fetchData = useCallback(async () => {
        setLoading(true);
        try {
            const res = await apiFetch('/hr/departments');
            if (res.ok) setData(await res.json());
        } catch { message.error('Error loading'); }
        finally { setLoading(false); }
    }, []);

    useEffect(() => { fetchData(); }, [fetchData]);

    const handleSubmit = async () => {
        try {
            const values = await form.validateFields();
            let res;
            if (editingRecord) res = await apiFetch(`/hr/departments/${editingRecord.id}`, { method: 'PUT', body: JSON.stringify(values) });
            else res = await apiFetch('/hr/departments', { method: 'POST', body: JSON.stringify(values) });
            if (res.ok) { message.success('Salvato'); setModalVisible(false); form.resetFields(); setEditingRecord(null); fetchData(); }
        } catch { message.error('Validation failed'); }
    };

    const rawColumns = [
        { title: 'Codice', dataIndex: 'code' },
        { title: 'Nome', dataIndex: 'name' },
        { title: 'Attivo', dataIndex: 'is_active', render: (v) => <Tag color={v ? 'green' : 'red'}>{v ? 'Sì' : 'No'}</Tag> },
        { title: 'Azioni', render: (_, r) => (
            <Button type="link" icon={<EditOutlined />} onClick={() => { setEditingRecord(r); form.setFieldsValue(r); setModalVisible(true); }}>Modifica</Button>
        )},
    ];

    const colManager = useColumnManagerWithDrawer('hr_departments', rawColumns);

    return (
        <>
            <Space style={{ marginBottom: 16 }}>
                <ColumnSettingsButton manager={colManager} />
                <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditingRecord(null); form.resetFields(); setModalVisible(true); }}>Nuovo Reparto</Button>
            </Space>
            <Table dataSource={data} columns={colManager.processedColumns} rowKey="id" loading={loading} />
            <Modal title={editingRecord ? 'Modifica Reparto' : 'Nuovo Reparto'} open={modalVisible} onOk={handleSubmit} onCancel={() => { setModalVisible(false); form.resetFields(); setEditingRecord(null); }}>
                <Form form={form} layout="vertical">
                    <Form.Item name="code" label="Codice" rules={[{ required: true }]}><Input /></Form.Item>
                    <Form.Item name="name" label="Nome" rules={[{ required: true }]}><Input /></Form.Item>
                </Form>
            </Modal>
        </>
    );
};

// ========== Attendance Tab ==========
const AttendanceTab = () => {
    const [data, setData] = useState([]);
    const [employees, setEmployees] = useState([]);
    const [loading, setLoading] = useState(false);
    const [modalVisible, setModalVisible] = useState(false);
    const [editing, setEditing] = useState(null);
    const [form] = Form.useForm();

    const fetch = useCallback(async () => {
        setLoading(true);
        try {
            const [aRes, eRes] = await Promise.all([
                apiFetch('/hr/attendance'),
                apiFetch('/hr/employees'),
            ]);
            if (aRes.ok) setData(await aRes.json());
            if (eRes.ok) setEmployees(await eRes.json());
        } catch { message.error('Error'); }
        finally { setLoading(false); }
    }, []);

    useEffect(() => { fetch(); }, [fetch]);

    const handleSubmit = async () => {
        try {
            const values = await form.validateFields();
            values.date = formatDateForApi(values.date); // Use utility for date
            values.check_in = values.check_in ? dayjs(values.check_in).format('HH:mm') : null; // Time only, dayjs still needed
            values.check_out = values.check_out ? dayjs(values.check_out).format('HH:mm') : null; // Time only, dayjs still needed
            let res;
            if (editing) res = await apiFetch(`/hr/attendance/${editing.id}`, { method: 'PUT', body: JSON.stringify(values) });
            else res = await apiFetch('/hr/attendance', { method: 'POST', body: JSON.stringify(values) });
            if (res.ok) { message.success('Salvato'); setModalVisible(false); form.resetFields(); setEditing(null); fetch(); }
            else { const e = await res.json(); message.error(e.message || 'Errore'); }
        } catch { message.error('Validation'); }
    };

    const rawColumns = [
        { title: 'Data', dataIndex: 'date', render: (v) => formatDateForDisplay(v) || '-' },
        { title: 'Dipendente', dataIndex: 'employee_id', render: (id) => { const e = employees.find(x => x.id === id); return e ? `${e.first_name} ${e.last_name}` : '-'; } }, // No change needed here
        { title: 'Entrata', dataIndex: 'check_in', render: (v) => v || '-' }, // No change needed here
        { title: 'Uscita', dataIndex: 'check_out', render: (v) => v || '-' }, // No change needed here
        { title: 'Ore Lavorate', key: 'hours', render: (_, r) => r.check_in && r.check_out ? `${((dayjs(`2000-01-01T${r.check_out}`).diff(dayjs(`2000-01-01T${r.check_in}`), 'minute')) / 60 - (r.break_duration || 0) / 60).toFixed(1)}h` : '-' }, // dayjs still needed for time diff
        { title: 'Straordinario', dataIndex: 'overtime_hours' },
        { title: 'Stato', dataIndex: 'status', render: (v) => <Tag color={statusColors[v]}>{v}</Tag> },
        { title: 'Azioni', render: (_, r) => (
            <Button type="link" icon={<EditOutlined />} onClick={() => { setEditing(r); form.setFieldsValue({ ...r, date: parseDateForForm(r.date), check_in: r.check_in ? dayjs(r.check_in, 'HH:mm') : null, check_out: r.check_out ? dayjs(r.check_out, 'HH:mm') : null }); setModalVisible(true); }}>Modifica</Button>
        )},
    ];

    const colManager = useColumnManagerWithDrawer('hr_attendance', rawColumns);

    return (
        <>
            <Space style={{ marginBottom: 16 }}>
                <ColumnSettingsButton manager={colManager} />
                <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditing(null); form.resetFields(); setModalVisible(true); }}>Nuova Presenza</Button>
            </Space>
            <Table dataSource={data} columns={colManager.processedColumns} rowKey="id" loading={loading} />
            <Modal title={editing ? 'Modifica Presenza' : 'Nuova Presenza'} open={modalVisible} onOk={handleSubmit} onCancel={() => { setModalVisible(false); form.resetFields(); setEditing(null); }}>
                <Form form={form} layout="vertical">
                    <Space size={16}>
                        <Form.Item name="employee_id" label="Dipendente" rules={[{ required: true }]}>
                            <Select style={{ width: 250 }} showSearch optionFilterProp="label" options={employees.map(e => ({ value: e.id, label: `${e.first_name} ${e.last_name}` }))} />
                        </Form.Item>
                        <Form.Item name="date" label="Data" rules={[{ required: true }]}><DatePicker format={formatDateForDisplay} /></Form.Item>
                    </Space>
                    <Space size={16}>
                        <Form.Item name="check_in" label="Entrata"><DatePicker picker="time" format="HH:mm" /></Form.Item>
                        <Form.Item name="check_out" label="Uscita"><DatePicker picker="time" format="HH:mm" /></Form.Item>
                        <Form.Item name="break_duration" label="Pausa (min)"><InputNumber min={0} /></Form.Item>
                        <Form.Item name="overtime_hours" label="Straordinario"><InputNumber min={0} step={0.5} /></Form.Item>
                    </Space>
                    <Space size={16}>
                        <Form.Item name="status" label="Stato">
                            <Select options={[{ value: 'present', label: 'Presente' }, { value: 'absent', label: 'Assente' }, { value: 'late', label: 'Ritardo' }, { value: 'leave', label: 'Permesso' }]} />
                        </Form.Item>
                    </Space>
                    <Form.Item name="notes" label="Note"><Input.TextArea rows={2} /></Form.Item>
                </Form>
            </Modal>
        </>
    );
};

// ========== Leave Tab ==========
const LeaveTab = () => {
    const [data, setData] = useState([]);
    const [employees, setEmployees] = useState([]);
    const [loading, setLoading] = useState(false);
    const [modalVisible, setModalVisible] = useState(false);
    const [editing, setEditing] = useState(null);
    const [form] = Form.useForm();

    const fetch = useCallback(async () => {
        setLoading(true);
        try {
            const [lRes, eRes] = await Promise.all([
                apiFetch('/hr/leave'),
                apiFetch('/hr/employees'),
            ]);
            if (lRes.ok) setData(await lRes.json());
            if (eRes.ok) setEmployees(await eRes.json());
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
            if (editing) res = await apiFetch(`/hr/leave/${editing.id}`, { method: 'PUT', body: JSON.stringify(values) });
            else res = await apiFetch('/hr/leave', { method: 'POST', body: JSON.stringify(values) });
            if (res.ok) { message.success('Salvato'); setModalVisible(false); form.resetFields(); setEditing(null); fetch(); }
            else { const e = await res.json(); message.error(e.message || 'Errore'); }
        } catch { message.error('Validation'); }
    };

    const handleApprove = async (id, status) => {
        try {
            const res = await apiFetch(`/hr/leave/${id}/approve`, { method: 'POST', body: JSON.stringify({ status }) });
            if (res.ok) { message.success(status === 'approved' ? 'Approvato' : 'Rifiutato'); fetch(); }
            else { const e = await res.json(); message.error(e.message || 'Errore'); }
        } catch { message.error('Error'); }
    };

    const rawColumns = [
        { title: 'Dipendente', dataIndex: 'employee_id', render: (id) => { const e = employees.find(x => x.id === id); return e ? `${e.first_name} ${e.last_name}` : '-'; } },
        { title: 'Tipo', dataIndex: 'leave_type' }, // No change needed here
        { title: 'Dal', dataIndex: 'start_date', render: (v) => formatDateForDisplay(v) || '-' },
        { title: 'Al', dataIndex: 'end_date', render: (v) => formatDateForDisplay(v) || '-' },
        { title: 'Giorni', dataIndex: 'days' }, // No change needed here
        { title: 'Stato', dataIndex: 'status', render: (v) => <Tag color={statusColors[v]}>{v}</Tag> },
        { title: 'Azioni', render: (_, r) => (
            <Space>
                <Button type="link" icon={<EditOutlined />} onClick={() => { setEditing(r); form.setFieldsValue({ ...r, start_date: parseDateForForm(r.start_date), end_date: parseDateForForm(r.end_date) }); setModalVisible(true); }}>Modifica</Button>
                {r.status === 'pending' && (
                    <>
                        <Button type="link" icon={<CheckOutlined />} style={{ color: 'green' }} onClick={() => handleApprove(r.id, 'approved')}>Approva</Button>
                        <Button type="link" icon={<CloseOutlined />} danger onClick={() => handleApprove(r.id, 'rejected')}>Rifiuta</Button>
                    </>
                )}
            </Space>
        )},
    ];

    const colManager = useColumnManagerWithDrawer('hr_leave', rawColumns);

    return (
        <>
            <Space style={{ marginBottom: 16 }}>
                <ColumnSettingsButton manager={colManager} />
                <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditing(null); form.resetFields(); setModalVisible(true); }}>Nuova Richiesta</Button>
            </Space>
            <Table dataSource={data} columns={colManager.processedColumns} rowKey="id" loading={loading} />
            <Modal title={editing ? 'Modifica Richiesta' : 'Nuova Richiesta Ferie/Permesso'} open={modalVisible} onOk={handleSubmit} onCancel={() => { setModalVisible(false); form.resetFields(); setEditing(null); }}>
                <Form form={form} layout="vertical">
                    <Space size={16}>
                        <Form.Item name="employee_id" label="Dipendente" rules={[{ required: true }]}>
                            <Select style={{ width: 250 }} showSearch optionFilterProp="label" options={employees.map(e => ({ value: e.id, label: `${e.first_name} ${e.last_name}` }))} />
                        </Form.Item>
                        <Form.Item name="leave_type" label="Tipo" rules={[{ required: true }]}>
                            <Select options={[{ value: 'vacation', label: 'Ferie' }, { value: 'sick', label: 'Malattia' }, { value: 'personal', label: 'Permesso' }, { value: 'maternity', label: 'Maternità' }, { value: 'paternity', label: 'Paternità' }]} /> {/* No change needed here */}
                        </Form.Item> {/* No change needed here */}
                    </Space> {/* Use formatDateForDisplay for DatePicker format */}
                    <Space size={16}>
                        <Form.Item name="start_date" label="Dal" rules={[{ required: true }]}><DatePicker format={formatDateForDisplay} /></Form.Item>
                        <Form.Item name="end_date" label="Al" rules={[{ required: true }]}><DatePicker format={formatDateForDisplay} /></Form.Item>
                    </Space>
                    <Form.Item name="reason" label="Motivazione"><Input.TextArea rows={2} /></Form.Item>
                </Form>
            </Modal>
        </>
    );
};

// ========== Main Page ==========
const HR = () => {
    const [summary, setSummary] = useState(null);

    useEffect(() => {
        apiFetch('/hr/reports/attendance-summary').then(r => r.ok && r.json().then(setSummary));
    }, []);

    const totalDays = summary?.reduce((s, r) => s + (r.days_present || 0), 0) || 0;
    const totalOvertime = summary?.reduce((s, r) => s + (r.overtime_hours || 0), 0) || 0;

    return (
        <div style={{ padding: 24 }}>
            {summary && (
                <Row gutter={16} style={{ marginBottom: 16 }}>
                    <Col span={6}><Card><Statistic title="Dipendenti" value={summary.length} /></Card></Col>
                    <Col span={6}><Card><Statistic title="Giorni Presenza" value={totalDays} /></Card></Col>
                    <Col span={6}><Card><Statistic title="Straordinario (h)" value={totalOvertime.toFixed(1)} /></Card></Col>
                </Row>
            )}
            <Card title="Risorse Umane">
                <Tabs items={[
                    { key: 'employees', label: 'Dipendenti', children: <EmployeesTab /> },
                    { key: 'departments', label: 'Reparti', children: <DepartmentsTab /> },
                    { key: 'attendance', label: 'Presenze', children: <AttendanceTab /> },
                    { key: 'leave', label: 'Ferie e Permessi', children: <LeaveTab /> },
                ]} />
            </Card>
        </div>
    );
};

export default HR;
