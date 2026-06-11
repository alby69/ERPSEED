import React, { useState, useEffect, useCallback } from 'react';
import { Card, Table, Button, Space, Tag, message, Row, Col, Statistic } from 'antd';
import { ReloadOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
import { apiFetch } from '@/utils';
import Layout from '../components/Layout';

export default function TrialBalance() {
    const [data, setData] = useState([]);
    const [summary, setSummary] = useState(null);
    const [loading, setLoading] = useState(false);

    const fetchData = useCallback(async () => {
        setLoading(true);
        try {
            const res = await apiFetch('/api/v1/accounting/reports/trial-balance');
            if (res.ok) { const j = await res.json(); setData(j.accounts || []); setSummary(j); }
        } catch { message.error('Error loading'); }
        finally { setLoading(false); }
    }, []);

    useEffect(() => { fetchData(); }, [fetchData]);

    const typeLabels = { asset: 'Attivo', liability: 'Passivo', equity: 'Patrimonio Netto', revenue: 'Ricavo', expense: 'Costo', unknown: 'Altro' };
    const typeColors = { asset: 'blue', liability: 'orange', equity: 'purple', revenue: 'green', expense: 'red', unknown: 'default' };

    const columns = [
        { title: 'Codice', dataIndex: 'code', key: 'code', width: 120 },
        { title: 'Nome', dataIndex: 'name', key: 'name' },
        { title: 'Tipo', dataIndex: 'type', key: 'type', width: 140, render: (v) => <Tag color={typeColors[v]}>{typeLabels[v] || v}</Tag> },
        { title: 'Saldo Dare', key: 'debit', width: 140, align: 'right',
            render: (_, r) => r.balance > 0 && ['asset', 'expense'].includes(r.type) ? `€ ${r.balance.toFixed(2)}` : '—'
        },
        { title: 'Saldo Avere', key: 'credit', width: 140, align: 'right',
            render: (_, r) => r.balance > 0 && ['liability', 'equity', 'revenue'].includes(r.type) ? `€ ${r.balance.toFixed(2)}` : '—'
        },
    ];

    return (
        <Layout>
            <div style={{ padding: 24 }}>
                {summary && (
                    <Row gutter={16} style={{ marginBottom: 16 }}>
                        <Col span={6}><Card size="small"><Statistic title="Totale Dare" value={summary.total_debit} precision={2} prefix="€" valueStyle={{ color: '#1890ff' }} /></Card></Col>
                        <Col span={6}><Card size="small"><Statistic title="Totale Avere" value={summary.total_credit} precision={2} prefix="€" valueStyle={{ color: '#fa8c16' }} /></Card></Col>
                        <Col span={6}><Card size="small"><Statistic title="Differenza" value={Math.abs(summary.total_debit - summary.total_credit)} precision={2} prefix="€" valueStyle={{ color: summary.balanced ? '#52c41a' : '#ff4d4f' }} /></Card></Col>
                        <Col span={6}><Card size="small">
                            <Statistic
                                title="Stato"
                                value={summary.balanced ? 'Bilanciato' : 'SBilanciato'}
                                prefix={summary.balanced ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
                                valueStyle={{ color: summary.balanced ? '#52c41a' : '#ff4d4f' }}
                            />
                        </Card></Col>
                    </Row>
                )}
                <Card title="Bilancio di Verifica" extra={
                    <Space>
                        <Button icon={<ReloadOutlined />} onClick={fetchData}>Aggiorna</Button>
                    </Space>
                }>
                    <Table dataSource={data} columns={columns} rowKey="code" loading={loading}
                        pagination={{ pageSize: 50, showTotal: (t) => `${t} conti` }}
                        summary={() => data.length > 0 ? (
                            <Table.Summary.Row>
                                <Table.Summary.Cell index={0}><strong>Totali</strong></Table.Summary.Cell>
                                <Table.Summary.Cell index={1} />
                                <Table.Summary.Cell index={2} />
                                <Table.Summary.Cell index={3} align="right"><strong>€ {data.filter(r => r.balance > 0 && ['asset', 'expense'].includes(r.type)).reduce((s, r) => s + r.balance, 0).toFixed(2)}</strong></Table.Summary.Cell>
                                <Table.Summary.Cell index={4} align="right"><strong>€ {data.filter(r => r.balance > 0 && ['liability', 'equity', 'revenue'].includes(r.type)).reduce((s, r) => s + r.balance, 0).toFixed(2)}</strong></Table.Summary.Cell>
                            </Table.Summary.Row>
                        ) : null}
                    />
                </Card>
            </div>
        </Layout>
    );
}
