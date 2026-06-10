import React, { useState, useEffect, useCallback } from 'react';
import { Card, Table, Input, Space, message, Tag } from 'antd';
import { GlobalOutlined } from '@ant-design/icons';
import { apiFetch } from '@/utils';
import Layout from '@/components/Layout';
import { useColumnManagerWithDrawer } from '@/hooks/useColumnManager';
import ColumnSettingsButton from '@/components/ColumnSettingsButton';

export default function RegioniPage() {
  const [regioni, setRegioni] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 20, total: 0 });
  const [search, setSearch] = useState('');

  const fetchRegioni = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: pagination.current,
        per_page: pagination.pageSize,
      });
      if (search) params.append('q', search);
      const response = await apiFetch(`/api/v1/regioni?${params}`);
      if (response.ok) {
        const data = await response.json();
        setRegioni(data.items || []);
        setPagination(prev => ({ ...prev, total: data.total || 0 }));
      }
    } catch {
      message.error('Errore nel caricamento');
    } finally {
      setLoading(false);
    }
  }, [pagination.current, pagination.pageSize, search]);

  useEffect(() => { fetchRegioni(); }, [fetchRegioni]);

  const rawColumns = [
    {
      title: 'Codice', dataIndex: 'codice', key: 'codice', width: 80,
      render: (text) => <Tag>{text}</Tag>,
    },
    { title: 'Nome', dataIndex: 'nome', key: 'nome', width: 300 },
  ];

  const colManager = useColumnManagerWithDrawer('regioni', rawColumns);

  return (
    <Layout>
      <div style={{ padding: '0' }}>
        <Card
          title={<Space><GlobalOutlined /><span>Geografia (Regioni)</span></Space>}
          extra={<ColumnSettingsButton manager={colManager} />}
        >
          <Input.Search
            placeholder="Cerca regione..."
            allowClear
            onSearch={setSearch}
            style={{ marginBottom: 16, width: 300 }}
          />
          <Table
            dataSource={regioni}
            columns={colManager.processedColumns}
            rowKey="codice"
            loading={loading}
            pagination={{
              current: pagination.current,
              pageSize: pagination.pageSize,
              total: pagination.total,
              showSizeChanger: true,
              showTotal: (t) => `${t} regioni`,
            }}
            onChange={(p) => setPagination(prev => ({ ...prev, current: p.current, pageSize: p.pageSize }))}
            scroll={{ x: 500 }}
            size="small"
          />
        </Card>
      </div>
    </Layout>
  );
};
