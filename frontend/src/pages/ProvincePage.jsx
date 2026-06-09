import React, { useState, useEffect, useCallback } from 'react';
import { Card, Table, Input, Select, Space, message, Tag } from 'antd';
import { GlobalOutlined } from '@ant-design/icons';
import { apiFetch } from '@/utils';
import Layout from '@/components/Layout';

export default function ProvincePage() {
  const [province, setProvince] = useState([]);
  const [regioni, setRegioni] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 50, total: 0 });
  const [search, setSearch] = useState('');
  const [filtroRegione, setFiltroRegione] = useState('');

  const fetchRegioni = useCallback(async () => {
    try {
      const response = await apiFetch('/api/v1/regioni?per_page=100');
      if (response.ok) {
        const data = await response.json();
        setRegioni(data.items || []);
      }
    } catch { /* ignore */ }
  }, []);

  useEffect(() => { fetchRegioni(); }, [fetchRegioni]);

  const fetchProvince = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: pagination.current,
        per_page: pagination.pageSize,
      });
      if (search) params.append('q', search);
      if (filtroRegione) params.append('regione', filtroRegione);
      const response = await apiFetch(`/api/v1/province?${params}`);
      if (response.ok) {
        const data = await response.json();
        setProvince(data.items || []);
        setPagination(prev => ({ ...prev, total: data.total || 0 }));
      }
    } catch {
      message.error('Errore nel caricamento');
    } finally {
      setLoading(false);
    }
  }, [pagination.current, pagination.pageSize, search, filtroRegione]);

  useEffect(() => { fetchProvince(); }, [fetchProvince]);

  const columns = [
    {
      title: 'Sigla', dataIndex: 'codice', key: 'codice', width: 70,
      render: (text) => <Tag>{text}</Tag>,
    },
    { title: 'Nome', dataIndex: 'nome', key: 'nome', width: 250 },
    {
      title: 'Regione', key: 'regione', width: 200,
      render: (_, record) => {
        if (!record.regione) return '-';
        const r = regioni.find(r => r.codice === record.regione);
        return r ? r.nome : record.regione;
      },
    },
  ];

  return (
    <Layout>
      <div style={{ padding: '0' }}>
        <Card
          title={<Space><GlobalOutlined /><span>Province</span></Space>}
        >
          <Space style={{ marginBottom: 16 }}>
            <Input.Search
              placeholder="Cerca provincia..."
              allowClear
              onSearch={setSearch}
              style={{ width: 250 }}
            />
            <Select
              placeholder="Filtra per regione"
              allowClear
              style={{ width: 200 }}
              value={filtroRegione || undefined}
              onChange={(v) => { setFiltroRegione(v || ''); setPagination(prev => ({ ...prev, current: 1 })); }}
            >
              {regioni.map(r => (
                <Select.Option key={r.codice} value={r.codice}>{r.nome}</Select.Option>
              ))}
            </Select>
          </Space>
          <Table
            dataSource={province}
            columns={columns}
            rowKey="codice"
            loading={loading}
            pagination={{
              current: pagination.current,
              pageSize: pagination.pageSize,
              total: pagination.total,
              showSizeChanger: true,
              showTotal: (t) => `${t} province`,
            }}
            onChange={(p) => setPagination(prev => ({ ...prev, current: p.current, pageSize: p.pageSize }))}
            scroll={{ x: 600 }}
            size="small"
          />
        </Card>
      </div>
    </Layout>
  );
};
