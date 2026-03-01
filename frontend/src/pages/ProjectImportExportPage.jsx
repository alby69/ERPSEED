import React, { useState, useEffect } from 'react';
import { Card, Button, Row, Col, Progress, message, Alert, List, Tag, Space, Divider } from 'antd';
import { 
  DownloadOutlined, 
  UploadOutlined, 
  DatabaseOutlined,
  BlockOutlined,
  SyncOutlined,
  AppstoreOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  InboxOutlined
} from '@ant-design/icons';
import { useParams } from 'react-router-dom';
import { apiFetch } from '../utils';
import { Layout } from '../components';
import { Upload } from 'antd';

const { Dragger } = Upload;

function ProjectImportExportPage() {
  const { projectId } = useParams();
  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [importing, setImporting] = useState(false);
  const [importResult, setImportResult] = useState(null);
  const [projectInfo, setProjectInfo] = useState(null);
  
  const pid = projectId || localStorage.getItem('currentProjectId') || 1;

  useEffect(() => {
    fetchProjectInfo();
  }, [pid]);

  const fetchProjectInfo = async () => {
    try {
      const response = await apiFetch(`/projects/${pid}`);
      if (response.ok) {
        const data = await response.json();
        setProjectInfo(data);
      }
    } catch (err) {
      console.error('Error fetching project info:', err);
    }
  };

  const handleExportFull = async () => {
    setExporting(true);
    setImportResult(null);
    try {
      const response = await apiFetch(`/api/v1/import-export/project/${pid}/export-full`);
      
      if (!response.ok) throw new Error('Export failed');
      
      const data = await response.json();
      
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `project_${projectInfo?.name || pid}_${new Date().toISOString().split('T')[0]}.json`;
      a.click();
      URL.revokeObjectURL(url);
      
      message.success('Progetto esportato con successo!');
    } catch (err) {
      message.error('Errore: ' + err.message);
    } finally {
      setExporting(false);
    }
  };

  const handleImportFull = async (file) => {
    setImporting(true);
    setImportResult(null);
    
    try {
      const text = await file.text();
      const data = JSON.parse(text);
      
      const response = await apiFetch(`/api/v1/import-export/project/${pid}/import-full`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.message || 'Import failed');
      }
      
      const result = await response.json();
      setImportResult(result);
      message.success('Import completato!');
    } catch (err) {
      message.error('Errore: ' + err.message);
      setImportResult({ error: err.message });
    } finally {
      setImporting(false);
    }
    
    return false;
  };

  const getResultStats = () => {
    if (!importResult || importResult.error) return null;
    
    const stats = {
      sysmodels: { success: 0, failed: 0 },
      blocks: { success: 0, failed: 0 },
      workflows: { success: 0, failed: 0 },
      modules: { success: 0, failed: 0 }
    };
    
    Object.keys(stats).forEach(key => {
      const items = importResult[key] || [];
      items.forEach(item => {
        if (item.error) stats[key].failed++;
        else stats[key].success++;
      });
    });
    
    return stats;
  };

  const stats = getResultStats();

  return (
    <Layout>
      <div style={{ padding: 24 }}>
        <Row gutter={[24, 24]}>
          <Col xs={24}>
            <Card
              title={<><DatabaseOutlined /> Import/Export Progetto</>}
              extra={
                <Button onClick={fetchProjectInfo}>
                  Aggiorna
                </Button>
              }
            >
              <Alert
                message="Backup Completo del Progetto"
                description="Esporta o importa tutti i componenti del progetto: Modelli, Blocchi, Workflow e Moduli."
                type="info"
                showIcon
                style={{ marginBottom: 24 }}
              />
              
              {projectInfo && (
                <div style={{ marginBottom: 24 }}>
                  <h4>Progetto: {projectInfo.name}</h4>
                  <p>{projectInfo.description || 'Nessuna descrizione'}</p>
                </div>
              )}
            </Card>
          </Col>

          <Col xs={24} md={12}>
            <Card
              title={<><DownloadOutlined /> Esporta Progetto</>}
              style={{ height: '100%' }}
            >
              <p>Esporta l'intero progetto in un file JSON che include:</p>
              <List
                size="small"
                dataSource={[
                  { icon: <DatabaseOutlined />, text: 'Modelli (SysModel)' },
                  { icon: <BlockOutlined />, text: 'Blocchi UI' },
                  { icon: <SyncOutlined />, text: 'Workflow' },
                  { icon: <AppstoreOutlined />, text: 'Moduli Personalizzati' }
                ]}
                renderItem={item => (
                  <List.Item>
                    <Space>
                      {item.icon}
                      {item.text}
                    </Space>
                  </List.Item>
                )}
              />
              <Divider />
              <Button 
                type="primary" 
                icon={<DownloadOutlined />} 
                onClick={handleExportFull}
                loading={exporting}
                block
              >
                Esporta Progetto Completo
              </Button>
            </Card>
          </Col>

          <Col xs={24} md={12}>
            <Card
              title={<><UploadOutlined /> Importa Progetto</>}
              style={{ height: '100%' }}
            >
              <p>Importa un progetto da file JSON. Attenzione: i componenti esistenti con lo stesso nome verranno sovrascritti.</p>
              <Dragger
                accept=".json"
                showUploadList={false}
                beforeUpload={handleImportFull}
                disabled={importing}
              >
                <p className="ant-upload-drag-icon">
                  <InboxOutlined />
                </p>
                <p className="ant-upload-text">Trascina il file JSON qui</p>
                <p className="ant-upload-hint">oppure clicca per selezionare il file di backup</p>
              </Dragger>
              {importing && (
                <div style={{ marginTop: 16, textAlign: 'center' }}>
                  <Progress type="circle" percent={100} status="active" />
                  <p>Importazione in corso...</p>
                </div>
              )}
            </Card>
          </Col>

          {importResult && (
            <Col xs={24}>
              <Card title="Risultato Importazione">
                {importResult.error ? (
                  <Alert
                    type="error"
                    message="Import Fallito"
                    description={importResult.error}
                    showIcon
                  />
                ) : stats && (
                  <>
                    <Row gutter={[16, 16]}>
                      <Col xs={12} sm={6}>
                        <Card size="small">
                          <div style={{ textAlign: 'center' }}>
                            <DatabaseOutlined style={{ fontSize: 24, color: '#1890ff' }} />
                            <div>Modelli</div>
                            <Tag color={stats.sysmodels.failed > 0 ? 'red' : 'green'}>
                              {stats.sysmodels.success} OK / {stats.sysmodels.failed} Errori
                            </Tag>
                          </div>
                        </Card>
                      </Col>
                      <Col xs={12} sm={6}>
                        <Card size="small">
                          <div style={{ textAlign: 'center' }}>
                            <BlockOutlined style={{ fontSize: 24, color: '#722ed1' }} />
                            <div>Blocchi</div>
                            <Tag color={stats.blocks.failed > 0 ? 'red' : 'green'}>
                              {stats.blocks.success} OK / {stats.blocks.failed} Errori
                            </Tag>
                          </div>
                        </Card>
                      </Col>
                      <Col xs={12} sm={6}>
                        <Card size="small">
                          <div style={{ textAlign: 'center' }}>
                            <SyncOutlined style={{ fontSize: 24, color: '#52c41a' }} />
                            <div>Workflow</div>
                            <Tag color={stats.workflows.failed > 0 ? 'red' : 'green'}>
                              {stats.workflows.success} OK / {stats.workflows.failed} Errori
                            </Tag>
                          </div>
                        </Card>
                      </Col>
                      <Col xs={12} sm={6}>
                        <Card size="small">
                          <div style={{ textAlign: 'center' }}>
                            <AppstoreOutlined style={{ fontSize: 24, color: '#fa8c16' }} />
                            <div>Moduli</div>
                            <Tag color={stats.modules.failed > 0 ? 'red' : 'green'}>
                              {stats.modules.success} OK / {stats.modules.failed} Errori
                            </Tag>
                          </div>
                        </Card>
                      </Col>
                    </Row>
                    
                    <Divider />
                    
                    <h5>Dettagli:</h5>
                    {Object.keys(stats).map(key => (
                      importResult[key]?.length > 0 && (
                        <div key={key} style={{ marginBottom: 8 }}>
                          <strong>{key.toUpperCase()}:</strong>
                          {importResult[key].map((item, idx) => (
                            <div key={idx} style={{ marginLeft: 16 }}>
                              {item.error ? (
                                <span style={{ color: 'red' }}>
                                  <CloseCircleOutlined /> {item.name || item.error}
                                </span>
                              ) : (
                                <span style={{ color: 'green' }}>
                                  <CheckCircleOutlined /> {item.name || item.action}
                                </span>
                              )}
                            </div>
                          ))}
                        </div>
                      )
                    ))}
                  </>
                )}
              </Card>
            </Col>
          )}
        </Row>
      </div>
    </Layout>
  );
}

export default ProjectImportExportPage;
