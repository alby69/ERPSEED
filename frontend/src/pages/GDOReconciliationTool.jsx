import React, { useState } from 'react';
import { Card, Upload, Button, Table, Space, Typography, Form, InputNumber, Select, Switch, message, Tabs, Statistic, Row, Col } from 'antd';
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
    search_direction: 'past_only',
    enable_best_fit: true,
    enable_residual_recovery: true,
    valuta_date_column: 'Data Valuta',
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
        // Remove default JSON headers for multipart
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      }, true); // true to skip default JSON body stringify

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

  const matchColumns = [
    { title: 'Data Versamento', dataIndex: ['credit', 'analysis_date'], key: 'date' },
    { title: 'Importo Versato', dataIndex: ['credit', 'Credit'], key: 'credit', render: (val) => `€ ${(val / 100).toFixed(2)}` },
    { title: 'Numero Incassi', dataIndex: 'debits', key: 'debits_count', render: (debits) => debits.length },
    { title: 'Differenza', dataIndex: 'difference', key: 'diff', render: (val) => `€ ${(val / 100).toFixed(2)}` },
    { title: 'Tipo', dataIndex: 'match_type', key: 'type' },
  ];

  const trendData = results?.stats?.monthly_trend?.flatMap(item => [
    { month: item.month, value: item.debit, type: 'Incassi (Dare)' },
    { month: item.month, value: item.credit, type: 'Versamenti (Avere)' }
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
                  { label: 'Subset Sum', value: 'subset_sum' },
                  { label: 'Greedy Amount First', value: 'greedy_amount_first' }
                ]} />
              </Form.Item>
              <Form.Item name="search_direction" label="Direzione Ricerca">
                <Select options={[
                  { label: 'Solo Passato (D prima di A)', value: 'past_only' },
                  { label: 'Solo Futuro (A prima di D)', value: 'future_only' },
                  { label: 'Entrambe', value: 'both' }
                ]} />
              </Form.Item>
              <Form.Item name="tolerance" label="Tolleranza (€)">
                <InputNumber min={0} step={0.1} style={{ width: '100%' }} />
              </Form.Item>
              <Form.Item name="days_window" label="Finestra Temporale (Giorni)">
                <InputNumber min={1} style={{ width: '100%' }} />
              </Form.Item>
              <Form.Item name="enable_best_fit" label="Abilita Best Fit (Splitting)" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Form.Item name="enable_residual_recovery" label="Recupero Residui Intelligente" valuePropName="checked">
                <Switch />
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
              <Col span={6}>
                <Card><Statistic title="Copertura Incassi" value={results.stats.debit_coverage_perc} precision={1} suffix="%" /></Card>
              </Col>
              <Col span={6}>
                <Card><Statistic title="Copertura Versamenti" value={results.stats.credit_coverage_perc} precision={1} suffix="%" /></Card>
              </Col>
              <Col span={6}>
                <Card><Statistic title="Anomalie" value={results.stats.total_anomalies} valueStyle={{ color: results.stats.total_anomalies > 0 ? '#cf1322' : '#3f9142' }} /></Card>
              </Col>
              <Col span={6}>
                <Card>
                    <Space direction="vertical" style={{ width: '100%' }}>
                        <Button block icon={<DownloadOutlined />} onClick={downloadExcel}>Export Excel</Button>
                        <Button block type="dashed" icon={<SaveOutlined />} onClick={saveResults} loading={loading}>Salva</Button>
                    </Space>
                </Card>
              </Col>
            </Row>
          </Col>
        )}
      </Row>

      {results && (
        <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
            <Col span={12}>
                <Card title="Trend Mensile Incassi vs Versamenti">
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
                <Card title="Distribuzione Match">
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
                        label={{ type: 'outer' }}
                    />
                </Card>
            </Col>
        </Row>
      )}

      {results && (
        <div style={{ marginTop: 24 }}>
          <Tabs defaultActiveKey="1" items={[
            {
              key: '1',
              label: 'Quadrature Trovate',
              children: <Table dataSource={results.matches} columns={matchColumns} rowKey={(record) => record.credit.orig_index} size="small" />
            },
            {
              key: '2',
              label: 'Incassi Non Riconciliati',
              children: <Table dataSource={results.unreconciled_debit} columns={[
                { title: 'Data', dataIndex: 'Date', key: 'date' },
                { title: 'Importo', dataIndex: 'Debit', key: 'amt', render: (val) => `€ ${(val / 100).toFixed(2)}` }
              ]} size="small" />
            },
            {
                key: '3',
                label: 'Versamenti Non Riconciliati',
                children: <Table dataSource={results.unreconciled_credit} columns={[
                  { title: 'Data', dataIndex: 'Date', key: 'date' },
                  { title: 'Data Valuta', dataIndex: 'Data Valuta', key: 'valuta' },
                  { title: 'Importo', dataIndex: 'Credit', key: 'amt', render: (val) => `€ ${(val / 100).toFixed(2)}` }
                ]} size="small" />
              }
          ]} />
        </div>
      )}
    </div>
  );
};

export default GDOReconciliationTool;
