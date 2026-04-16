import React from 'react';
import { Form, Input, Select, InputNumber, Button, Space, Divider, Empty } from 'antd';
import { DeleteOutlined } from '@ant-design/icons';
import { useWorkflowBuilderStore } from '../../stores/workflowBuilderStore';

const { Option } = Select;

const nodeTypeLabels = {
  trigger: 'Trigger',
  condition: 'Condizione',
  action: 'Azione',
  notification: 'Notifica',
  delay: 'Ritardo',
  webhook: 'Webhook',
};

const operatorOptions = [
  { value: 'equals', label: 'Uguale a' },
  { value: 'not_equals', label: 'Diverso da' },
  { value: 'greater_than', label: 'Maggiore di' },
  { value: 'less_than', label: 'Minore di' },
  { value: 'contains', label: 'Contiene' },
  { value: 'is_empty', label: 'È vuoto' },
  { value: 'is_not_empty', label: 'Non è vuoto' },
];

const actionTypeOptions = [
  { value: 'set_field', label: 'Imposta campo' },
  { value: 'update_record', label: 'Aggiorna record' },
  { value: 'create_record', label: 'Crea record' },
  { value: 'send_email', label: 'Invia email' },
];

const notificationTypeOptions = [
  { value: 'email', label: 'Email' },
  { value: 'webhook', label: 'Webhook' },
];

const unitOptions = [
  { value: 'seconds', label: 'Secondi' },
  { value: 'minutes', label: 'Minuti' },
  { value: 'hours', label: 'Ore' },
  { value: 'days', label: 'Giorni' },
];

const methodOptions = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'];

const TriggerProperties = ({ node, updateNode, onDelete }) => (
  <Form layout="vertical" size="small">
    <Form.Item label="Evento Trigger">
      <Select
        value={node.data.triggerEvent}
        onChange={(v) => updateNode('triggerEvent', v)}
      >
        <Option value="order.created">order.created</Option>
        <Option value="order.updated">order.updated</Option>
        <Option value="order.deleted">order.deleted</Option>
        <Option value="invoice.created">invoice.created</Option>
        <Option value="invoice.updated">invoice.updated</Option>
        <Option value="product.created">product.created</Option>
        <Option value="product.updated">product.updated</Option>
        <Option value="user.created">user.created</Option>
        <Option value="entity.created">entity.created (qualsiasi)</Option>
        <Option value="entity.updated">entity.updated (qualsiasi)</Option>
        <Option value="*">Qualsiasi evento</Option>
      </Select>
    </Form.Item>
  </Form>
);

const ConditionProperties = ({ node, updateNode, onDelete }) => (
  <Form layout="vertical" size="small">
    <Form.Item label="Nome">
      <Input
        value={node.data.label}
        onChange={(e) => updateNode('label', e.target.value)}
        placeholder="Es: Check totale ordine"
      />
    </Form.Item>
    <Form.Item label="Campo">
      <Input
        value={node.data.field}
        onChange={(e) => updateNode('field', e.target.value)}
        placeholder="Es: total, status, quantity"
      />
    </Form.Item>
    <Form.Item label="Operatore">
      <Select
        value={node.data.operator}
        onChange={(v) => updateNode('operator', v)}
      >
        {operatorOptions.map(o => <Option key={o.value} value={o.value}>{o.label}</Option>)}
      </Select>
    </Form.Item>
    <Form.Item label="Valore">
      <Input
        value={node.data.value}
        onChange={(e) => updateNode('value', e.target.value)}
        placeholder="Valore di confronto"
      />
    </Form.Item>
    <Divider />
    <Button danger block icon={<DeleteOutlined />} onClick={onDelete}>
      Elimina nodo
    </Button>
  </Form>
);

const ActionProperties = ({ node, updateNode, onDelete }) => (
  <Form layout="vertical" size="small">
    <Form.Item label="Nome">
      <Input
        value={node.data.label}
        onChange={(e) => updateNode('label', e.target.value)}
        placeholder="Es: Approva ordine"
      />
    </Form.Item>
    <Form.Item label="Tipo azione">
      <Select
        value={node.data.actionType}
        onChange={(v) => updateNode('actionType', v)}
      >
        {actionTypeOptions.map(o => <Option key={o.value} value={o.value}>{o.label}</Option>)}
      </Select>
    </Form.Item>
    <Form.Item label="Campo">
      <Input
        value={node.data.field}
        onChange={(e) => updateNode('field', e.target.value)}
        placeholder="Es: status"
      />
    </Form.Item>
    <Form.Item label="Valore">
      <Input
        value={node.data.value}
        onChange={(e) => updateNode('value', e.target.value)}
        placeholder="Es: approved"
      />
    </Form.Item>
    <Divider />
    <Button danger block icon={<DeleteOutlined />} onClick={onDelete}>
      Elimina nodo
    </Button>
  </Form>
);

const NotificationProperties = ({ node, updateNode, onDelete }) => (
  <Form layout="vertical" size="small">
    <Form.Item label="Nome">
      <Input
        value={node.data.label}
        onChange={(e) => updateNode('label', e.target.value)}
        placeholder="Es: Notifica manager"
      />
    </Form.Item>
    <Form.Item label="Tipo notifica">
      <Select
        value={node.data.notificationType}
        onChange={(v) => updateNode('notificationType', v)}
      >
        {notificationTypeOptions.map(o => <Option key={o.value} value={o.value}>{o.label}</Option>)}
      </Select>
    </Form.Item>
    <Form.Item label="Destinatario">
      <Input
        value={node.data.to}
        onChange={(e) => updateNode('to', e.target.value)}
        placeholder="email@domain.com"
      />
    </Form.Item>
    <Form.Item label="Oggetto">
      <Input
        value={node.data.subject}
        onChange={(e) => updateNode('subject', e.target.value)}
        placeholder="Oggetto dell'email"
      />
    </Form.Item>
    <Divider />
    <Button danger block icon={<DeleteOutlined />} onClick={onDelete}>
      Elimina nodo
    </Button>
  </Form>
);

const DelayProperties = ({ node, updateNode, onDelete }) => (
  <Form layout="vertical" size="small">
    <Form.Item label="Nome">
      <Input
        value={node.data.label}
        onChange={(e) => updateNode('label', e.target.value)}
        placeholder="Es: Attesa conferma"
      />
    </Form.Item>
    <Form.Item label="Durata">
      <InputNumber
        value={node.data.duration}
        onChange={(v) => updateNode('duration', v)}
        min={1}
        style={{ width: '100%' }}
      />
    </Form.Item>
    <Form.Item label="Unità">
      <Select
        value={node.data.unit}
        onChange={(v) => updateNode('unit', v)}
      >
        {unitOptions.map(o => <Option key={o.value} value={o.value}>{o.label}</Option>)}
      </Select>
    </Form.Item>
    <Divider />
    <Button danger block icon={<DeleteOutlined />} onClick={onDelete}>
      Elimina nodo
    </Button>
  </Form>
);

const WebhookProperties = ({ node, updateNode, onDelete }) => (
  <Form layout="vertical" size="small">
    <Form.Item label="Nome">
      <Input
        value={node.data.label}
        onChange={(e) => updateNode('label', e.target.value)}
        placeholder="Es: Chiama API esterna"
      />
    </Form.Item>
    <Form.Item label="URL">
      <Input
        value={node.data.url}
        onChange={(e) => updateNode('url', e.target.value)}
        placeholder="https://api.example.com/endpoint"
      />
    </Form.Item>
    <Form.Item label="Metodo">
      <Select
        value={node.data.method}
        onChange={(v) => updateNode('method', v)}
      >
        {methodOptions.map(m => <Option key={m} value={m}>{m}</Option>)}
      </Select>
    </Form.Item>
    <Divider />
    <Button danger block icon={<DeleteOutlined />} onClick={onDelete}>
      Elimina nodo
    </Button>
  </Form>
);

const WorkflowPropertiesPanel = () => {
  const { selectedNode, updateNodeData, deleteNode } = useWorkflowBuilderStore();

  if (!selectedNode) {
    return (
      <div style={{ padding: 16 }}>
        <Empty
          description="Seleziona un nodo per modificare le proprietà"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      </div>
    );
  }

  const nodeType = selectedNode.type;
  const updateNode = (key, value) => {
    updateNodeData(selectedNode.id, { [key]: value });
  };
  const handleDelete = () => {
    deleteNode(selectedNode.id);
  };

  const renderProperties = () => {
    switch (nodeType) {
      case 'trigger':
        return <TriggerProperties node={selectedNode} updateNode={updateNode} onDelete={handleDelete} />;
      case 'condition':
        return <ConditionProperties node={selectedNode} updateNode={updateNode} onDelete={handleDelete} />;
      case 'action':
        return <ActionProperties node={selectedNode} updateNode={updateNode} onDelete={handleDelete} />;
      case 'notification':
        return <NotificationProperties node={selectedNode} updateNode={updateNode} onDelete={handleDelete} />;
      case 'delay':
        return <DelayProperties node={selectedNode} updateNode={updateNode} onDelete={handleDelete} />;
      case 'webhook':
        return <WebhookProperties node={selectedNode} updateNode={updateNode} onDelete={handleDelete} />;
      default:
        return <Empty description="Tipo nodo non supportato" />;
    }
  };

  return (
    <div>
      <div style={{ padding: '12px 16px', borderBottom: '1px solid #f0f0f0' }}>
        <strong>{nodeTypeLabels[nodeType] || 'Nodo'}</strong>
      </div>
      <div style={{ padding: 16 }}>
        {renderProperties()}
      </div>
    </div>
  );
};

export default WorkflowPropertiesPanel;
