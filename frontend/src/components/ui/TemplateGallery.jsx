/**
 * Template Gallery - Interface for selecting and installing starter templates
 */

import React, { useState, useEffect } from 'react';
import {
  Card,
  List,
  Button,
  Typography,
  Tag,
  Space,
  Modal,
  message,
  Empty,
  Spin,
  Tooltip
} from 'antd';
import {
  AppstoreAddOutlined,
  InfoCircleOutlined,
  RocketOutlined,
  CloudDownloadOutlined
} from '@ant-design/icons';
import { apiFetch } from '@/utils';

const { Title, Paragraph, Text } = Typography;

const TemplateGallery = ({ projectId, onInstalled }) => {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(false);
  const [installing, setInstalling] = useState(null);

  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    setLoading(true);
    try {
      const response = await apiFetch('/api/templates/');
      const data = await response.json();
      setTemplates(data);
    } catch (error) {
      console.error("Error fetching templates:", error);
      message.error("Impossibile caricare i template.");
    } finally {
      setLoading(false);
    }
  };

  const handleInstall = (templateId) => {
    Modal.confirm({
      title: 'Conferma Installazione',
      content: `Vuoi davvero installare questo template nel progetto corrente? Verranno creati nuovi modelli e viste.`,
      okText: 'Installa',
      cancelText: 'Annulla',
      onOk: async () => {
        setInstalling(templateId);
        try {
          const response = await apiFetch('/api/templates/install', {
            method: 'POST',
            body: JSON.stringify({
              template_id: templateId,
              project_id: parseInt(projectId)
            })
          });
          const result = await response.json();
          message.success(result.message);
          if (onInstalled) onInstalled(result);
        } catch (error) {
          message.error("Errore durante l'installazione del template.");
        } finally {
          setInstalling(null);
        }
      }
    });
  };

  if (loading) return <div style={{ textAlign: 'center', padding: 40 }}><Spin size="large" tip="Caricamento template..." /></div>;

  return (
    <div className="template-gallery">
      <div style={{ marginBottom: 24 }}>
        <Title level={4}><RocketOutlined /> Starter Templates</Title>
        <Paragraph type="secondary">
          Inizia velocemente con configurazioni predefinite per i casi d'uso più comuni.
        </Paragraph>
      </div>

      {templates.length === 0 ? (
        <Empty description="Nessun template disponibile." />
      ) : (
        <List
          grid={{ gutter: 16, xs: 1, sm: 1, md: 2, lg: 2, xl: 3, xxl: 3 }}
          dataSource={templates}
          renderItem={item => (
            <List.Item>
              <Card
                hoverable
                actions={[
                  <Button
                    type="primary"
                    icon={<CloudDownloadOutlined />}
                    loading={installing === item.id}
                    onClick={() => handleInstall(item.id)}
                    block
                  >
                    Installa Template
                  </Button>
                ]}
              >
                <Card.Meta
                  avatar={<AppstoreAddOutlined style={{ fontSize: 24, color: '#1677ff' }} />}
                  title={item.name}
                  description={
                    <div style={{ height: 100, overflow: 'hidden' }}>
                      <Paragraph ellipsis={{ rows: 2 }} style={{ marginBottom: 8 }}>
                        {item.description}
                      </Paragraph>
                      <Space wrap>
                        <Tag color="blue">{item.category}</Tag>
                        <Tooltip title={`${item.models_count} modelli e ${item.views_count} viste`}>
                          <Tag icon={<InfoCircleOutlined />}>{item.models_count} Entità</Tag>
                        </Tooltip>
                      </Space>
                    </div>
                  }
                />
              </Card>
            </List.Item>
          )}
        />
      )}
    </div>
  );
};

export default TemplateGallery;
