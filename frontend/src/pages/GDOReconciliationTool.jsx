import React, { useState } from 'react';
import { Card, Upload, Button, Table, Space, Typography, Form, InputNumber, Select, message, Tabs, Statistic, Row, Col } from 'antd';
import { UploadOutlined, PlayCircleOutlined, DownloadOutlined, SaveOutlined } from '@ant-design/icons';
import { apiFetch } from '@/utils';
import { useParams } from 'react-router-dom';
import { Line, Pie } from '@ant-design/charts';

const { Title, Text } = Typography;

const GDOReconciliationTool = () => {
  const { projectId } = useParams();
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [config, setConfig] = useState({
    algorithm: 'progressive_balance',
    tolerance: 0.5,
    days_window: 5,
    column_mapping: {
      'Date': 'Data',
      'Debit': 'Dare',
      'Credit': 'Avere',
      'Data Valuta': 'Data Valuta'
    }
  });

  const handleUpload = (file) => {
    setFile(file);
    return false; // Prevent auto-upload
  };

  const runReconciliation = async () => {
    if (!file) {
      message.error('Carica un file prima di procedere');
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('config', JSON.stringify(config));

    try {
      const response = await apiFetch('/api/gdo/process', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      setResults(data);
      message.success('Riconciliazione completata');
    } catch (error) {
      console.error(error);
      message.error('Errore durante l\'elaborazione');
    } finally {
      setLoading(false);
    }
  };

  const downloadExcel = async () => {
    try {
      const response = await apiFetch('/api/gdo/export', {
        method: 'POST',
        body: JSON.stringify(results)
      });
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'Riconciliazione_GDO.xlsx';
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (error) {
      message.error('Errore durante il download');
    }
  };

  const saveResults = async () => {
    try {
      setLoading(true);
      const response = await apiFetch('/api/gdo/save', {
        method: 'POST',
        body: JSON.stringify({
          project_id: projectId,
          results: results,
          company_id: null // In a real app, let user select company
        })
      });

      if (response.ok) {
        message.success('Risultati salvati correttamente nel database');
      } else {
        throw new Error('Save failed');
      }
    } catch (error) {
      message.error('Errore durante il salvataggio');
    } finally {
      setLoading(false);
    }
  };

  // Format amount with thousands separator (point) and 2 decimal places (comma)
  const formatCurrency = (val) => {
    if (val == null || isNaN(val)) return '0,00';
    return val.toLocaleString('it-IT', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  };

  const formatCurrencyWithSymbol = (val) => {
    return `€ ${formatCurrency(val)}`;
  };

  const formatNumber = (val) => {
    if (val == null || isNaN(val)) return '0';
    return val.toLocaleString('it-IT');
  };

  const getDebitAmount = (record) => {
    const val = record?.Debit ?? record?.Dare;
    return formatCurrencyWithSymbol(val);
  };

  const getCreditAmountSimple = (record) => {
    const val = record?.Credit ?? record?.Avere;
    return formatCurrencyWithSymbol(val);
  };

  // Helper to get date (handles both Date and Data column names)
  const getDateValue = (record) => {
    return record?.Date ?? record?.Data ?? '-';
  };

  const getMatchColumns = [
    { title: 'Data Versamento', key: 'date', render: (_, record) => getDateValue(record?.credit) },
    { title: 'Importo Versato', key: 'credit', render: (_, record) => getCreditAmountSimple(record?.credit) },
    { title: 'Numero Incassi', dataIndex: 'debits', key: 'debits_count', render: (debits) => debits?.length || 0 },
    { title: 'Differenza', key: 'diff', render: (_, record) => formatCurrencyWithSymbol(record?.difference) },
    { title: 'Tipo', dataIndex: 'match_type', key: 'type' },
  ];

  const trendData = results?.stats?.monthly_trend?.flatMap(item => [
    { month: item.month, value: item.debit || 0, type: 'Incassi (Dare)' },
    { month: item.month, value: item.credit || 0, type: 'Versamenti (Avere)' }
  ]) || [];

  return (
    <div style={{ padding: '24px' }}>
      <Title level={2}>Tool Riconciliazione GDO</Title>

      <Row gutter={[16, 16]}>
        <Col span={8}>
          <Card title="Configurazione" size="small">
            <Form layout="vertical" initialValues={config} onValuesChange={(_, all) => setConfig(all)}>
              <Form.Item name="algorithm" label="Algoritmo">
                <Select options={[
                  { label: 'Progressive Balance', value: 'progressive_balance' },
                  { label: 'Subset Sum', value: 'subset_sum' }
                ]} />
              </Form.Item>
              <Form.Item name="tolerance" label="Tolleranza (€)">
                <InputNumber min={0} step={0.1} style={{ width: '100%' }} />
              </Form.Item>
              <Form.Item name="days_window" label="Finestra Temporale (Giorni)">
                <InputNumber min={1} style={{ width: '100%' }} />
              </Form.Item>
              <Space>
                <Upload beforeUpload={handleUpload} maxCount={1} showUploadList={!!file}>
                  <Button icon={<UploadOutlined />}>Scegli File</Button>
                </Upload>
                <Button type="primary" icon={<PlayCircleOutlined />} onClick={runReconciliation} loading={loading}>
                  Esegui
                </Button>
              </Space>
            </Form>
          </Card>
        </Col>

        {results && (
          <Col span={16}>
            <Row gutter={[16, 16]}>
              <Col span={8}>
                <Card>
                  <Statistic 
                    title="Incassi (€)" 
                    value={results.stats.total_debit || 0} 
                    precision={2} 
                    valueStyle={{ fontSize: '1.2em' }}
                    formatter={() => formatCurrencyWithSymbol(results.stats.total_debit)}
                  />
                  <div style={{ marginTop: 8, textAlign: 'center', color: '#888' }}>
                    Num: {formatNumber(results.stats.count_debit || 0)}
                  </div>
                </Card>
              </Col>
              <Col span={8}>
                <Card>
                  <Statistic 
                    title="Versamenti (€)" 
                    value={results.stats.total_credit || 0} 
                    precision={2} 
                    valueStyle={{ fontSize: '1.2em' }}
                    formatter={() => formatCurrencyWithSymbol(results.stats.total_credit)}
                  />
                  <div style={{ marginTop: 8, textAlign: 'center', color: '#888' }}>
                    Num: {formatNumber(results.stats.count_credit || 0)}
                  </div>
                </Card>
              </Col>
              <Col span={8}>
                <Card>
                  <Statistic 
                    title="Delta (€)" 
                    value={results.stats.total_difference || 0} 
                    precision={2} 
                    valueStyle={{ 
                      fontSize: '1.2em',
                      color: (results.stats.total_difference || 0) >= 0 ? '#3f9142' : '#cf1322'
                    }}
                    formatter={() => formatCurrencyWithSymbol(results.stats.total_difference)}
                  />
                  <div style={{ marginTop: 8, textAlign: 'center', color: '#888' }}>
                    Delta Num: {formatNumber((results.stats.count_debit || 0) - (results.stats.count_credit || 0))}
                  </div>
                </Card>
              </Col>
            </Row>
          </Col>
        )}
      </Row>

      {results && (
        <div style={{ marginTop: 24 }}>
          <Tabs defaultActiveKey="1" items={[
            {
              key: '1',
              label: 'Riconciliati',
              children: (
                <Row gutter={[16, 16]}>
                  <Col span={24}>
                    <Card title="Grafici">
                      <Row gutter={[16, 16]}>
                        <Col span={12}>
                          <Card title="Trend Mensile Incassi vs Versamenti" size="small">
                            <Line
                              data={trendData}
                              xField="month"
                              yField="value"
                              seriesField="type"
                              smooth
                              legend={{ position: 'top' }}
                            />
                          </Card>
                        </Col>
                        <Col span={12}>
                          <Card title="Distribuzione Match" size="small">
                            <Pie
                              data={results.matches.reduce((acc, curr) => {
                                const type = curr.match_type;
                                const existing = acc.find(i => i.type === type);
                                if (existing) existing.value++;
                                else acc.push({ type, value: 1 });
                                return acc;
                              }, [])}
                              angleField="value"
                              colorField="type"
                              radius={0.8}
                              label={false}
                              legend={{ position: 'bottom' }}
                            />
                          </Card>
                        </Col>
                      </Row>
                    </Card>
                  </Col>
                  <Col span={24}>
                    <Card title="Quadrature Trovate" style={{ marginTop: 16 }}>
                      <Table 
                        dataSource={results.matches} 
                        columns={getMatchColumns} 
                        rowKey={(record) => record.credit?.orig_index} 
                        pagination={{ pageSize: 10 }} 
                        size="small" 
                      />
                    </Card>
                  </Col>
                </Row>
              )
            },
            {
              key: '2',
              label: 'Non Riconciliati',
              children: (
                <Row gutter={[16, 16]}>
                  <Col span={12}>
                    <Card title="Incassi Non Riconciliati">
                      <Table 
                        dataSource={results.unreconciled_debit} 
                        columns={[
                          { title: 'Data', key: 'date', render: (_, record) => getDateValue(record) },
                          { title: 'Importo', key: 'amt', render: (_, record) => getDebitAmount(record) }
                        ]} 
                        rowKey={(record) => record.orig_index} 
                        pagination={{ pageSize: 10 }} 
                        size="small" 
                      />
                    </Card>
                  </Col>
                  <Col span={12}>
                    <Card title="Versamenti Non Riconciliati">
                      <Table 
                        dataSource={results.unreconciled_credit} 
                        columns={[
                          { title: 'Data', key: 'date', render: (_, record) => getDateValue(record) },
                          { title: 'Data Valuta', key: 'valuta', render: (_, record) => record?.['Data Valuta'] ?? '-' },
                          { title: 'Importo', key: 'amt', render: (_, record) => getCreditAmountSimple(record) }
                        ]} 
                        rowKey={(record) => record.orig_index} 
                        pagination={{ pageSize: 10 }} 
                        size="small" 
                      />
                    </Card>
                  </Col>
                </Row>
              )
            }
          ]} />
        </div>
      )}
    </div>
  );
};

export default GDOReconciliationTool;
