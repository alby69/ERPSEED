import React from 'react';
import { Drawer, List, Button, Space, Typography, Switch } from 'antd';
import { UpOutlined, DownOutlined, UndoOutlined, SettingOutlined } from '@ant-design/icons';

const { Text } = Typography;

export default function ColumnSettingsDrawer({
  open,
  onClose,
  columns,
  onToggle,
  onMoveUp,
  onMoveDown,
  onReset,
  hasChanges,
}) {
  return (
    <Drawer
      title={
        <Space>
          <SettingOutlined />
          <span>Personalizza Colonne</span>
        </Space>
      }
      placement="right"
      onClose={onClose}
      open={open}
      width={380}
      extra={
        hasChanges ? (
          <Button size="small" icon={<UndoOutlined />} onClick={onReset}>
            Reset
          </Button>
        ) : null
      }
    >
      <Text type="secondary" style={{ display: 'block', marginBottom: 16 }}>
        Mostra, nascondi e riordina le colonne della tabella.
      </Text>

      <List
        dataSource={columns}
        renderItem={(col, index) => (
          <List.Item
            style={{
              padding: '8px 0',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            <Space>
              <Switch
                checked={col._visible}
                onChange={() => onToggle(col._key)}
                size="small"
              />
              <Text
                style={{
                  textDecoration: col._visible ? 'none' : 'line-through',
                  opacity: col._visible ? 1 : 0.5,
                }}
              >
                {col.title}
              </Text>
            </Space>
            <Space>
              <Button
                size="small"
                icon={<UpOutlined />}
                disabled={index === 0}
                onClick={() => onMoveUp(col._key)}
              />
              <Button
                size="small"
                icon={<DownOutlined />}
                disabled={index === columns.length - 1}
                onClick={() => onMoveDown(col._key)}
              />
            </Space>
          </List.Item>
        )}
      />
    </Drawer>
  );
}
