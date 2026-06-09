import React, { useState, useEffect, useCallback } from 'react';
import { Card, Table, Button, Modal, Form, Input, InputNumber, DatePicker, Select, Space, Tag, message, Divider } from 'antd';
import { PlusOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { apiFetch } from '@/utils';
import { parseDateForForm, formatDateForApi, formatDateForDisplay } from '@/utils/dateUtils'; // Import date utilities

const statusColors = { draft: 'default', posted: 'green', cancelled: 'red' };
const statusLabels = { draft: 'Bozza', posted: 'Registrata', cancelled: 'Annullata' };

export default function Journal() {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [total, setTotal] = useState(0);
    const [page, setPage] = useState(1);
    const [modalVisible, setModalVisible] = useState(false);
    const [accounts, setAccounts] = useState([]);
    const [form] = Form.useForm();

    const fetchData = useCallback(async () => {
        setLoading(true);
        try {
            const res = await apiFetch(`/accounting/journal?page=${page}&per_page=20`);
            if (res.ok) {
                const json = await res.json();
                setData(json.items || []);
                setTotal(json.total || 0);
            }
        } catch { message.error('Error loading journal'); }
        finally { setLoading(false); }
    }, [page]);

    const fetchAccounts = useCallback(async () => {
        try {
            const res = await apiFetch('/accounting/accounts');
            if (res.ok) setAccounts(await res.json());
        } catch {}
    }, []);

    useEffect(() => { fetchData(); fetchAccounts(); }, [fetchData, fetchAccounts]);

    const handleSubmit = async () => {
        try {
            const values = await form.validateFields();
            const payload = {
                date: formatDateForApi(values.date),
                description: values.description,
                reference: values.reference,
                lines: values.lines?.map(l => ({
                    account_id: l.account_id,
                    debit: parseFloat(l.debit || 0),
                    credit: parseFloat(l.credit || 0),
                    description: l.description || '',
                })) || [],
            };
            const res = await apiFetch('/accounting/journal', { method: 'POST', body: JSON.stringify(payload) });
            if (res.ok) { message.success('Scrittura creata'); setModalVisible(false); form.resetFields(); fetchData(); }
            else { const e = await res.json(); message.error(e.message || 'Errore'); }
        } catch { message.error('Validation failed'); }
    };

    const handlePost = async (id) => {
        const res = await apiFetch(`/accounting/journal/${id}`, { method: 'POST' });
        if (res.ok) { message.success('Registrata'); fetchData(); }
        else { const e = await res.json(); message.error(e.message || 'Errore'); }
    };

    const columns = [
        { title: 'Nr. Registrazione', dataIndex: 'entry_number', key: 'entry_number' },
        { title: 'Data', dataIndex: 'date', key: 'date', render: (v) => formatDateForDisplay(v) || '-' },
        { title: 'Descrizione', dataIndex: 'description', key: 'description' },
        { title: 'Dare', dataIndex: 'total_debit', key: 'total_debit', align: 'right', render: (v) => `€ ${(v || 0).toFixed(2)}` },
        { title: 'Avere', dataIndex: 'total_credit', key: 'total_credit', align: 'right', render: (v) => `€ ${(v || 0).toFixed(2)}` },
        { title: 'Stato', dataIndex: 'status', key: 'status', render: (v) => <Tag color={statusColors[v]}>{statusLabels[v] || v}</Tag> },
        { title: 'Azioni', key: 'actions', render: (_, r) => (
            <Space>
                {r.status === 'draft' && <Button type="link" icon={<CheckCircleOutlined />} onClick={() => handlePost(r.id)}>Registra</Button>}
            </Space>
        )},
    ];

    return (
        <div style={{ padding: 24 }}>
            <Card title="Prima Nota Contabile" extra={<Button type="primary" icon={<PlusOutlined />} onClick={() => { form.resetFields(); setModalVisible(true); }}>Nuova Scrittura</Button>}>
                <Table dataSource={data} columns={columns} rowKey="id" loading={loading}
                    pagination={{ current: page, pageSize: 20, total, onChange: setPage, showTotal: (t) => `${t} scritture` }}
                    expandedRowRender={(r) => r.lines ? (
                        <Table dataSource={r.lines} rowKey="id" size="small" pagination={false}
                            columns={[
                                { title: 'Conto', dataIndex: 'account_id', key: 'account_id', render: (id) => { const a = accounts.find(x => x.id === id); return a ? `${a.code} - ${a.name}` : `ID: ${id}`; } },
                                { title: 'Dare', dataIndex: 'debit', key: 'debit', align: 'right', render: (v) => `€ ${(v || 0).toFixed(2)}` },
                                { title: 'Avere', dataIndex: 'credit', key: 'credit', align: 'right', render: (v) => `€ ${(v || 0).toFixed(2)}` },
                                { title: 'Descrizione', dataIndex: 'description', key: 'description' },
                            ]} />
                    ) : null}
                />
            </Card>
            <Modal title="Nuova Scrittura Contabile" open={modalVisible} onOk={handleSubmit} onCancel={() => { setModalVisible(false); form.resetFields(); }} okText="Salva" cancelText="Annulla" width={800}>
                <Form form={form} layout="vertical">
                    <Space style={{ width: '100%' }} size={16}>
                        <Form.Item name="date" label="Data" rules={[{ required: true }]}><DatePicker format={formatDateForDisplay} /></Form.Item>
                        <Form.Item name="reference" label="Riferimento"><Input style={{ width: 200 }} /></Form.Item>
                    </Space>
                    <Form.Item name="description" label="Descrizione" rules={[{ required: true }]}><Input.TextArea rows={2} /></Form.Item>
                    <Divider>Righe (Dare/Avere)</Divider>
                    <Form.List name="lines">
                        {(fields, { add, remove }) => (
                            <>
                                {fields.map(({ key, name, ...rest }) => (
                                    <Space key={key} style={{ display: 'flex', marginBottom: 8 }} align="baseline">
                                        <Form.Item {...rest} name={[name, 'account_id']} rules={[{ required: true }]}>
                                            <Select showSearch placeholder="Conto" style={{ width: 250 }} optionFilterProp="label"
                                                options={accounts.map(a => ({ value: a.id, label: `${a.code} - ${a.name}` }))} />
                                        </Form.Item>
                                        <Form.Item {...rest} name={[name, 'debit']}>
                                            <InputNumber min={0} step={0.01} prefix="Dare" style={{ width: 120 }} />
                                        </Form.Item>
                                        <Form.Item {...rest} name={[name, 'credit']}>
                                            <InputNumber min={0} step={0.01} prefix="Avere" style={{ width: 120 }} />
                                        </Form.Item>
                                        <Form.Item {...rest} name={[name, 'description']}>
                                            <Input placeholder="Descrizione riga" style={{ width: 200 }} />
                                        </Form.Item>
                                        <Button type="link" danger onClick={() => remove(name)}>Rimuovi</Button>
                                    </Space>
                                ))}
                                <Button type="dashed" onClick={() => add({ debit: 0, credit: 0 })} icon={<PlusOutlined />}>Aggiungi Riga</Button>
                            </>
                        )}
                    </Form.List>
                </Form>
            </Modal>
        </div>
    );
};
