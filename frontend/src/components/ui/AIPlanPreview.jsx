/**
 * AI Plan Preview Component
 *
 * Displays a structured list of actions proposed by the AI
 */

import React from 'react';
import {
  List,
  Tag,
  Typography,
  Space,
  Card,
  Divider,
  Collapse
} from 'antd';
import {
  DatabaseOutlined,
  PlusOutlined,
  LayoutOutlined,
  NodeIndexOutlined,
  FieldStringOutlined,
  CheckCircleOutlined
} from '@ant-design/icons';

const { Text, Title, Paragraph } = Typography;
const { Panel } = Collapse;

const AIPlanPreview = ({ plan = [] }) => {
  if (!plan || plan.length === 0) {
    return <Text type="secondary">Nessun piano di esecuzione disponibile.</Text>;
  }

  const getActionIcon = (action) => {
    switch (action) {
      case 'create_model': return <DatabaseOutlined style={{ color: '#1890ff' }} />;
      case 'add_field': return <FieldStringOutlined style={{ color: '#52c41a' }} />;
      case 'create_view': return <LayoutOutlined style={{ color: '#fa8c16' }} />;
      case 'create_workflow': return <NodeIndexOutlined style={{ color: '#722ed1' }} />;
      default: return <PlusOutlined />;
    }
  };

  const getActionColor = (action) => {
    switch (action) {
      case 'create_model': return 'blue';
      case 'add_field': return 'green';
      case 'create_view': return 'orange';
      case 'create_workflow': return 'purple';
      default: return 'default';
    }
  };

  return (
    <div className="ai-plan-preview">
      <Title level={5}>Piano di Implementazione Suggerito</Title>
      <Paragraph type="secondary">
        L'AI ha elaborato i seguenti passaggi per soddisfare la tua richiesta:
      </Paragraph>

      <List
        itemLayout="horizontal"
        dataSource={plan}
        renderItem={(item, index) => (
          <List.Item>
            <List.Item.Meta
              avatar={getActionIcon(item.action)}
              title={
                <Space>
                  <Text strong>{item.description}</Text>
                  <Tag color={getActionColor(item.action)}>{item.action.replace('_', ' ')}</Tag>
                </Space>
              }
              description={
                <div>
                  <Text type="secondary" style={{ fontSize: 12 }}>Target: {item.target}</Text>
                  {item.details && Object.keys(item.details).length > 0 && (
                    <Collapse ghost size="small" style={{ marginTop: 4 }}>
                      <Panel header="Dettagli tecnici" key="1" style={{ fontSize: 11 }}>
                        <pre style={{ margin: 0, fontSize: 10 }}>
                          {JSON.stringify(item.details, null, 2)}
                        </pre>
                      </Panel>
                    </Collapse>
                  )}
                </div>
              }
            />
          </List.Item>
        )}
      />

      <Divider style={{ margin: '12px 0' }} />
      <Space>
        <CheckCircleOutlined style={{ color: '#52c41a' }} />
        <Text type="secondary" style={{ fontSize: 12 }}>
          Rivedi i passaggi sopra. Cliccando su "Applica", queste modifiche verranno eseguite sul database.
        </Text>
      </Space>
    </div>
  );
};

export default AIPlanPreview;
