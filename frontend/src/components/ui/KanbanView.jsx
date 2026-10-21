import React from 'react';
import { Card, Tag, Typography, Flex, Spin } from 'antd';

const { Text, Title } = Typography;

export default function KanbanView({
  columns = [],
  items = [],
  statusField = 'status',
  titleField = 'title',
  subtitleField = 'subtitle',
  loading = false,
  onCardClick,
}) {
  if (loading) {
    return (
      <Flex justify="center" align="center" style={{ minHeight: 200 }}>
        <Spin size="large" />
      </Flex>
    );
  }

  return (
    <Flex gap="middle" align="start" style={{ overflowX: 'auto', paddingBottom: 16 }}>
      {columns.map((col) => {
        const columnItems = items.filter((item) => item[statusField] === col.key);

        return (
          <Card
            key={col.key}
            title={
              <Flex justify="space-between" align="center">
                <Text bold>{col.title}</Text>
                <Tag color={col.color || 'blue'}>{columnItems.length}</Tag>
              </Flex>
            }
            style={{ width: 280, minWidth: 280, backgroundColor: '#f5f5f5' }}
            styles={{ body: { padding: 12 } }}
          >
            <Flex vertical gap="small">
              {columnItems.map((item) => (
                <Card
                  key={item.id}
                  hoverable
                  size="small"
                  onClick={() => onCardClick && onCardClick(item)}
                  style={{ backgroundColor: '#fff', cursor: 'pointer' }}
                >
                  <Title level={5} style={{ margin: 0, fontSize: 14 }}>
                    {item[titleField] || item.name || `Item #${item.id}`}
                  </Title>
                  {subtitleField && item[subtitleField] && (
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      {item[subtitleField]}
                    </Text>
                  )}
                </Card>
              ))}
              {columnItems.length === 0 && (
                <Text type="secondary" style={{ fontStyle: 'italic', textAlign: 'center' }}>
                  Nessun elemento
                </Text>
              )}
            </Flex>
          </Card>
        );
      })}
    </Flex>
  );
}
