import React, { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import {
  ApiOutlined,
  FunctionOutlined,
  BellOutlined,
  ClockCircleOutlined,
  PlayCircleOutlined
} from '@ant-design/icons';

const nodeStyles = {
  trigger: {
    background: '#1890ff',
    borderColor: '#1890ff',
    color: '#fff',
    icon: <PlayCircleOutlined />,
  },
  condition: {
    background: '#722ed1',
    borderColor: '#722ed1',
    color: '#fff',
    icon: <FunctionOutlined />,
  },
  action: {
    background: '#52c41a',
    borderColor: '#52c41a',
    color: '#fff',
    icon: <ApiOutlined />,
  },
  notification: {
    background: '#fa8c16',
    borderColor: '#fa8c16',
    color: '#fff',
    icon: <BellOutlined />,
  },
  delay: {
    background: '#eb2f96',
    borderColor: '#eb2f96',
    color: '#fff',
    icon: <ClockCircleOutlined />,
  },
  webhook: {
    background: '#13c2c2',
    borderColor: '#13c2c2',
    color: '#fff',
    icon: <ApiOutlined />,
  },
};

const TriggerNode = memo(({ data, selected }) => {
  return (
    <div style={{
      padding: '12px 16px',
      borderRadius: 8,
      border: `2px solid ${selected ? '#1890ff' : '#1890ff'}`,
      background: '#1890ff',
      color: '#fff',
      minWidth: 150,
      textAlign: 'center',
      boxShadow: selected ? '0 0 0 2px rgba(24,144,255,0.3)' : 'none',
    }}>
      <Handle type="source" position={Position.Bottom} style={{ background: '#fff' }} />
      <div style={{ fontSize: 16, fontWeight: 600 }}>
        <PlayCircleOutlined style={{ marginRight: 8 }} />
        {data.triggerEvent || 'Trigger'}
      </div>
      <div style={{ fontSize: 11, opacity: 0.8, marginTop: 4 }}>
        {data.triggerEvent}
      </div>
    </div>
  );
});

const ConditionNode = memo(({ data, selected }) => {
  return (
    <div style={{
      padding: '12px 16px',
      borderRadius: 8,
      border: `2px solid ${selected ? '#722ed1' : '#722ed1'}`,
      background: '#722ed1',
      color: '#fff',
      minWidth: 160,
      textAlign: 'center',
      transform: 'rotate(0deg)',
      boxShadow: selected ? '0 0 0 2px rgba(114,46,209,0.3)' : 'none',
    }}>
      <Handle type="target" position={Position.Top} style={{ background: '#fff' }} />
      <div style={{ fontSize: 14, fontWeight: 600 }}>
        <FunctionOutlined style={{ marginRight: 8 }} />
        {data.label || 'Condition'}
      </div>
      {data.field && (
        <div style={{ fontSize: 11, opacity: 0.8, marginTop: 4 }}>
          {data.field} {data.operator} {data.value}
        </div>
      )}
      <Handle type="source" position={Position.Bottom} id="true" style={{
        background: '#52c41a',
        left: '30%'
      }} />
      <Handle type="source" position={Position.Bottom} id="false" style={{
        background: '#ff4d4f',
        left: '70%'
      }} />
      <div style={{
        position: 'absolute',
        bottom: -20,
        left: '30%',
        transform: 'translateX(-50%)',
        fontSize: 10,
        color: '#52c41a',
        fontWeight: 'bold'
      }}>
        TRUE
      </div>
      <div style={{
        position: 'absolute',
        bottom: -20,
        left: '70%',
        transform: 'translateX(-50%)',
        fontSize: 10,
        color: '#ff4d4f',
        fontWeight: 'bold'
      }}>
        FALSE
      </div>
    </div>
  );
});

const ActionNode = memo(({ data, selected }) => {
  return (
    <div style={{
      padding: '12px 16px',
      borderRadius: 8,
      border: `2px solid ${selected ? '#52c41a' : '#52c41a'}`,
      background: '#52c41a',
      color: '#fff',
      minWidth: 150,
      textAlign: 'center',
      boxShadow: selected ? '0 0 0 2px rgba(82,196,26,0.3)' : 'none',
    }}>
      <Handle type="target" position={Position.Top} style={{ background: '#fff' }} />
      <div style={{ fontSize: 14, fontWeight: 600 }}>
        <ApiOutlined style={{ marginRight: 8 }} />
        {data.label || 'Action'}
      </div>
      {data.actionType && (
        <div style={{ fontSize: 11, opacity: 0.8, marginTop: 4 }}>
          {data.actionType}: {data.field}
        </div>
      )}
      <Handle type="source" position={Position.Bottom} style={{ background: '#fff' }} />
    </div>
  );
});

const NotificationNode = memo(({ data, selected }) => {
  return (
    <div style={{
      padding: '12px 16px',
      borderRadius: 50,
      border: `2px solid ${selected ? '#fa8c16' : '#fa8c16'}`,
      background: '#fa8c16',
      color: '#fff',
      minWidth: 140,
      textAlign: 'center',
      boxShadow: selected ? '0 0 0 2px rgba(250,140,22,0.3)' : 'none',
    }}>
      <Handle type="target" position={Position.Top} style={{ background: '#fff' }} />
      <div style={{ fontSize: 14, fontWeight: 600 }}>
        <BellOutlined style={{ marginRight: 8 }} />
        {data.label || 'Notification'}
      </div>
      {data.notificationType && (
        <div style={{ fontSize: 11, opacity: 0.8, marginTop: 4 }}>
          {data.notificationType}
        </div>
      )}
      <Handle type="source" position={Position.Bottom} style={{ background: '#fff' }} />
    </div>
  );
});

const DelayNode = memo(({ data, selected }) => {
  return (
    <div style={{
      padding: '12px 16px',
      borderRadius: 8,
      border: `2px solid ${selected ? '#eb2f96' : '#eb2f96'}`,
      background: '#eb2f96',
      color: '#fff',
      minWidth: 120,
      textAlign: 'center',
      boxShadow: selected ? '0 0 0 2px rgba(235,47,150,0.3)' : 'none',
    }}>
      <Handle type="target" position={Position.Top} style={{ background: '#fff' }} />
      <div style={{ fontSize: 14, fontWeight: 600 }}>
        <ClockCircleOutlined style={{ marginRight: 8 }} />
        {data.label || 'Delay'}
      </div>
      {data.duration && (
        <div style={{ fontSize: 11, opacity: 0.8, marginTop: 4 }}>
          {data.duration} {data.unit}
        </div>
      )}
      <Handle type="source" position={Position.Bottom} style={{ background: '#fff' }} />
    </div>
  );
});

const WebhookNode = memo(({ data, selected }) => {
  return (
    <div style={{
      padding: '12px 16px',
      borderRadius: 8,
      border: `2px solid ${selected ? '#13c2c2' : '#13c2c2'}`,
      background: '#13c2c2',
      color: '#fff',
      minWidth: 150,
      textAlign: 'center',
      boxShadow: selected ? '0 0 0 2px rgba(19,194,194,0.3)' : 'none',
    }}>
      <Handle type="target" position={Position.Top} style={{ background: '#fff' }} />
      <div style={{ fontSize: 14, fontWeight: 600 }}>
        <ApiOutlined style={{ marginRight: 8 }} />
        {data.label || 'Webhook'}
      </div>
      {data.url && (
        <div style={{ fontSize: 10, opacity: 0.8, marginTop: 4, maxWidth: 130, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {data.url}
        </div>
      )}
      <Handle type="source" position={Position.Bottom} style={{ background: '#fff' }} />
    </div>
  );
});

export const nodeTypes = {
  trigger: TriggerNode,
  condition: ConditionNode,
  action: ActionNode,
  notification: NotificationNode,
  delay: DelayNode,
  webhook: WebhookNode,
};

export default nodeTypes;
