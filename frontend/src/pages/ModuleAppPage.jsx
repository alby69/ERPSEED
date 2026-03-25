import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Row, Col, Spin, message, Typography, Button, Menu, Tabs, Empty } from 'antd';
import { ArrowLeftOutlined, AppstoreOutlined, TableOutlined, FormOutlined, BarChartOutlined, HomeOutlined } from '@ant-design/icons';
import { apiFetch } from '../utils';
import { useTheme } from '../context';
import { StaticBlockRenderer } from '../components/BlockRenderer';

const { Title, Text } = Typography;

function ModuleAppPage() {
  const { projectId, moduleName } = useParams();
  const navigate = useNavigate();
  const { themeConfig } = useTheme();

  const [module, setModule] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [models, setModels] = useState([]);
  const [blocks, setBlocks] = useState([]);

  useEffect(() => {
    fetchModule();
  }, [projectId, moduleName]);

  const fetchModule = async () => {
    setLoading(true);
    try {
      const response = await apiFetch(`/api/v1/modules?project_id=${projectId}&search=${moduleName}`);
      const data = await response.json();

      if (data.modules && data.modules.length > 0) {
        const foundModule = data.modules[0];

        if (foundModule.status !== 'published') {
          message.error('Modulo non pubblicato');
          navigate(`/projects/${projectId}`);
          return;
        }

        setModule(foundModule);

        // Fetch full module details with relations
        const detailResponse = await apiFetch(`/api/v1/modules/${foundModule.id}`);
        const detailData = await detailResponse.json();

        // Get models from the module (as blocks)
        setModels(detailData.contained_models || detailData.models || []);

        // Also fetch blocks with their full details (including visual_builder_config)
        if (detailData.blocks && detailData.blocks.length > 0) {
          const blocksWithDetails = await Promise.all(
            detailData.blocks.map(async (block) => {
              try {
                const blockResponse = await apiFetch(`/api/blocks/${block.id}`);
                if (blockResponse.ok) {
                  return await blockResponse.json();
                }
              } catch (err) {
                console.error('Error fetching block details:', err);
              }
              return block;
            })
          );
          setBlocks(blocksWithDetails);
        } else {
          setBlocks([]);
        }
      } else {
        message.error('Modulo non trovato');
        navigate(`/projects/${projectId}`);
      }
    } catch (err) {
      message.error('Errore nel caricamento del modulo');
      navigate(`/projects/${projectId}`);
    } finally {
      setLoading(false);
    }
  };

  const renderOverview = () => {
    return (
      <div style={{ padding: '20px' }}>
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={8}>
            <Card bordered={false} style={{ background: themeConfig.primaryColor || '#1890ff', color: '#fff' }}>
              <div style={{ textAlign: 'center' }}>
                <Title level={2} style={{ color: '#fff', margin: 0 }}>{blocks.length}</Title>
                <Text style={{ color: 'rgba(255,255,255,0.8)' }}>Blocchi Layout</Text>
              </div>
            </Card>
          </Col>
          <Col xs={24} sm={8}>
            <Card bordered={false} style={{ background: '#52c41a', color: '#fff' }}>
              <div style={{ textAlign: 'center' }}>
                <Title level={2} style={{ color: '#fff', margin: 0 }}>{models.length}</Title>
                <Text style={{ color: 'rgba(255,255,255,0.8)' }}>Modelli Dati</Text>
              </div>
            </Card>
          </Col>
          <Col xs={24} sm={8}>
            <Card bordered={false} style={{ background: '#faad14', color: '#fff' }}>
              <div style={{ textAlign: 'center' }}>
                <Title level={2} style={{ color: '#fff', margin: 0 }}>v{module.version || '1.0'}</Title>
                <Text style={{ color: 'rgba(255,255,255,0.8)' }}>Versione</Text>
              </div>
            </Card>
          </Col>
        </Row>

        <Card title="Descrizione" style={{ marginTop: 20 }}>
          <Text>{module.description || 'Nessuna descrizione disponibile.'}</Text>
        </Card>

        {blocks.length > 0 ? (
          <Card title="Blocchi Layout" style={{ marginTop: 20 }}>
            <Row gutter={[16, 16]}>
              {blocks.map((block) => (
                <Col xs={24} sm={12} md={8} key={block.id}>
                  <Card
                    size="small"
                    hoverable
                    onClick={() => setActiveTab(`block-${block.id}`)}
                    style={{ borderColor: themeConfig.primaryColor }}
                  >
                    <Card.Meta
                      avatar={<AppstoreOutlined style={{ fontSize: 24, color: themeConfig.primaryColor }} />}
                      title={block.title || block.name}
                      description={block.description || (block.visual_builder_config ? 'Layout Visuale' : 'Block del modulo')}
                    />
                  </Card>
                </Col>
              ))}
            </Row>
          </Card>
        ) : (
          <Card style={{ marginTop: 20 }}>
            <Empty description="Nessun block configurato per questo modulo" />
          </Card>
        )}

        {models.length > 0 ? (
          <Card title="Modelli Dati" style={{ marginTop: 20 }}>
            <Row gutter={[16, 16]}>
              {models.map((model) => (
                <Col xs={24} sm={12} md={8} key={model.id}>
                  <Card
                    size="small"
                    hoverable
                    onClick={() => setActiveTab(`model-${model.id}`)}
                    style={{ borderColor: '#52c41a' }}
                  >
                    <Card.Meta
                      avatar={<TableOutlined style={{ fontSize: 24, color: '#52c41a' }} />}
                      title={model.title || model.name}
                      description={model.description || 'Modello dati'}
                    />
                  </Card>
                </Col>
              ))}
            </Row>
          </Card>
        ) : null}
      </div>
    );
  };

  const renderBlockContent = (block) => {
    // Check if block has VisualBuilder config
    if (block.visual_builder_config && block.visual_builder_config.length > 0) {
      return (
        <div style={{ padding: '20px', height: '100%' }}>
          <StaticBlockRenderer
            components={block.visual_builder_config}
            data={{}}
            projectId={projectId}
            onAction={(action, config, data) => {
              console.log('Block action:', action, config);
              message.info(`Azione: ${action}`);
            }}
          />
        </div>
      );
    }

    // Check if block has component IDs (legacy)
    if (block.components && block.components.length > 0) {
      return (
        <div style={{ padding: '20px' }}>
          <Card title="Componenti">
            {block.components.map(comp => (
              <Card key={comp.id} size="small" style={{ marginBottom: 8 }}>
                <strong>{comp.name}</strong>
                <p>{comp.archetype_name}</p>
              </Card>
            ))}
          </Card>
        </div>
      );
    }

    // Default: show placeholder
    return (
      <div style={{ padding: '20px' }}>
        <Card title={block.title || block.name}>
          <p>Accedi a questo block dal menu laterale o naviga verso i dati.</p>
          <Button
            type="primary"
            icon={<TableOutlined />}
            onClick={() => navigate(`/projects/${projectId}/data/${block.name}`)}
          >
            Apri {block.title || block.name}
          </Button>
        </Card>
      </div>
    );
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!module) {
    return null;
  }

  const menuItems = [
    {
      key: 'overview',
      icon: <HomeOutlined />,
      label: 'Panoramica',
    },
    ...blocks.map(block => ({
      key: `block-${block.id}`,
      icon: <AppstoreOutlined />,
      label: block.title || block.name,
    })),
    ...models.map(model => ({
      key: `model-${model.id}`,
      icon: <TableOutlined />,
      label: model.title || model.name,
    }))
  ];

  return (
    <div style={{ minHeight: '100vh', background: themeConfig.mode === 'dark' ? '#141414' : '#f5f5f5' }}>
      {/* Header App-Like */}
      <div
        style={{
          background: themeConfig.primaryColor || '#1890ff',
          color: '#fff',
          padding: '16px 24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <Button
            type="text"
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate(`/projects/${projectId}`)}
            style={{ color: '#fff' }}
          />
          <AppstoreOutlined style={{ fontSize: 24 }} />
          <div>
            <Title level={4} style={{ color: '#fff', margin: 0 }}>
              {module.title || module.name}
            </Title>
            <Text style={{ color: 'rgba(255,255,255,0.8)' }}>
              {module.category || 'Modulo Personalizzato'}
            </Text>
          </div>
        </div>
        <div>
          <Text style={{ color: 'rgba(255,255,255,0.8)' }}>
            v{module.version || '1.0'}
          </Text>
        </div>
      </div>

      <div style={{ display: 'flex', minHeight: 'calc(100vh - 70px)' }}>
        {/* Sidebar interna al modulo */}
        <div
          style={{
            width: 240,
            background: themeConfig.mode === 'dark' ? '#1f1f1f' : '#fff',
            borderRight: `1px solid ${themeConfig.mode === 'dark' ? '#303030' : '#f0f0f0'}`,
            padding: '16px 0'
          }}
        >
          <Menu
            mode="inline"
            selectedKeys={[activeTab]}
            onClick={({ key }) => setActiveTab(key)}
            style={{ borderRight: 0 }}
            items={menuItems}
          />
        </div>

        {/* Contenuto principale */}
        <div style={{ flex: 1, overflow: 'auto' }}>
          {activeTab === 'overview' ? renderOverview() : (
            <>
              {blocks.map(block =>
                activeTab === `block-${block.id}` ? renderBlockContent(block) : null
              )}
              {models.map(model =>
                activeTab === `model-${model.id}` ? (
                  <div key={model.id} style={{ padding: '20px' }}>
                    <Card title={model.title || model.name}>
                      <p>Accedi a questo modello dati.</p>
                      <Button
                        type="primary"
                        icon={<TableOutlined />}
                        onClick={() => navigate(`/projects/${projectId}/data/${model.name}`)}
                      >
                        Apri {model.title || model.name}
                      </Button>
                    </Card>
                  </div>
                ) : null
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default ModuleAppPage;
