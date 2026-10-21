import React from 'react';
import { Drawer, Spin, Descriptions, Empty } from 'antd';
import { useQuery } from '@tanstack/react-query';
import { apiFetch } from '../../utils';

export default function ContextualDrawer({
  open,
  onClose,
  title = 'Dettaglio Record',
  apiEndpoint,
  recordId,
  width = 480,
  renderContent,
}) {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['contextual-drawer', apiEndpoint, recordId],
    queryFn: async () => {
      if (!apiEndpoint || !recordId) return null;
      const res = await apiFetch(`${apiEndpoint}/${recordId}`);
      return res.json();
    },
    enabled: !!open && !!apiEndpoint && !!recordId,
  });

  return (
    <Drawer
      title={title}
      placement="right"
      width={width}
      onClose={onClose}
      open={open}
      destroyOnClose
    >
      {isLoading ? (
        <div style={{ textAlign: 'center', padding: '40px 0' }}>
          <Spin size="large" />
        </div>
      ) : isError ? (
        <Empty description="Errore nel caricamento del record" />
      ) : data ? (
        renderContent ? (
          renderContent(data)
        ) : (
          <Descriptions column={1} bordered size="small">
            {Object.entries(data).map(([key, value]) => (
              <Descriptions.Item key={key} label={key}>
                {typeof value === 'object' && value !== null
                  ? JSON.stringify(value)
                  : String(value ?? '-')}
              </Descriptions.Item>
            ))}
          </Descriptions>
        )
      ) : (
        <Empty description="Nessun dato disponibile" />
      )}
    </Drawer>
  );
}
