import React, { useState, useRef } from 'react';
import {
  Card,
  Upload,
  Button,
  Form,
  InputNumber,
  Select,
  Progress,
  Table,
  Tag,
  Typography,
  Space,
  Row,
  Col,
  Statistic,
  Alert,
  Tabs,
  message
} from 'antd';
import {
  InboxOutlined,
  PlayCircleOutlined,
  DownloadOutlined,
  CheckCircleOutlined,
  WarningOutlined,
  SettingOutlined,
  BarChartOutlined,
  FileExcelOutlined
} from '@ant-design/icons';
import { DEFAULT_PROFILES } from '../lib/cashrec/config';

const { Title, Text, Paragraph } = Typography;
const { Dragger } = Upload;

export default function CashRecTool() {
  const [file, setFile] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState('');
  const [results, setResults] = useState(null);
  const [reportBuffer, setReportBuffer] = useState(null);

  const [form] = Form.useForm();
  const workerRef = useRef(null);

  const handleProfileChange = (profileName) => {
    if (DEFAULT_PROFILES[profileName]) {
      form.setFieldsValue(DEFAULT_PROFILES[profileName]);
    }
  };

  const startReconciliation = async () => {
    try {
      const values = await form.validateFields();
      if (!file) {
        message.error('Seleziona un file (.xlsx, .xls, .csv) prima di avviare la riconciliazione.');
        return;
      }

      setProcessing(true);
      setProgress(5);
      setStatusMessage('Avvio elaborazione client-side...');
      setResults(null);
      setReportBuffer(null);

      const fileData = await file.arrayBuffer();

      // Create Web Worker
      const worker = new Worker(new URL('../lib/cashrec/worker.js', import.meta.url), { type: 'module' });
      workerRef.current = worker;

      worker.onmessage = (e) => {
        const { status, percent, message: msg, result, error } = e.data;
        if (status === 'progress') {
          setProgress(percent);
          setStatusMessage(msg);
        } else if (status === 'complete') {
          setProgress(100);
          setProcessing(false);
          setStatusMessage('Elaborazione completata con successo!');
          setResults(result);
          setReportBuffer(result.reportBuffer);
          message.success('Riconciliazione completata!');
          worker.terminate();
        } else if (status === 'error') {
          setProcessing(false);
          setStatusMessage(`Errore: ${error}`);
          message.error(`Errore durante la riconciliazione: ${error}`);
          worker.terminate();
        }
      };

      worker.onerror = (err) => {
        setProcessing(false);
        message.error(`Errore Web Worker: ${err.message}`);
        worker.terminate();
      };

      worker.postMessage({
        fileData,
        fileName: file.name,
        config: values
      }, [fileData]);

    } catch (err) {
      setProcessing(false);
      console.error(err);
    }
  };

  const handleDownloadReport = () => {
    if (!reportBuffer) return;
    const blob = new Blob([reportBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `CashRec_Report_${file ? file.name.split('.')[0] : 'session'}.xlsx`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const matchesColumns = [
    { title: 'ID Gruppo', dataIndex: 'group_id', key: 'group_id', render: (val) => <Tag color="blue">#{val}</Tag> },
    { title: 'Algoritmo', dataIndex: 'algorithm', key: 'algorithm' },
    { title: 'Anomalia', dataIndex: 'anomaly_type', key: 'anomaly_type', render: (val) => val ? <Tag color="red">{val}</Tag> : <Tag color="green">Nessuna</Tag> },
    { title: 'Differenza (€)', dataIndex: 'difference', key: 'difference', render: (val) => (val / 100).toFixed(2) }
  ];

  return (
    <div style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto' }}>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <div>
          <Title level={2}>
            <FileExcelOutlined style={{ marginRight: '12px', color: '#1890ff' }} />
            Riconciliazione Casse (CashRec)
          </Title>
          <Paragraph type="secondary">
            Strumento client-side ad alte prestazioni per la riconciliazione automatica di estratti conto e registri cassa.
          </Paragraph>
        </div>

        <Row gutter={[24, 24]}>
          <Col xs={24} lg={10}>
            <Card title="Carica File & Configurazioni" icon={<SettingOutlined />}>
              <Form
                form={form}
                layout="vertical"
                initialValues={{
                  profile: 'Operatore Punto Vendita (Default)',
                  algorithm: 'progressive_balance',
                  tolerance: 50.0,
                  days_window: 5,
                  search_direction: 'past_only'
                }}
              >
                <Form.Item label="Profilo Predefinito" name="profile">
                  <Select onChange={handleProfileChange}>
                    {Object.keys(DEFAULT_PROFILES).map((p) => (
                      <Select.Option key={p} value={p}>{p}</Select.Option>
                    ))}
                  </Select>
                </Form.Item>

                <Form.Item label="Algoritmo Riconciliazione" name="algorithm">
                  <Select>
                    <Select.Option value="progressive_balance">Progressive Balance (Saldo Progressivo)</Select.Option>
                    <Select.Option value="subset_sum">Subset Sum (Somma Combinatoria)</Select.Option>
                    <Select.Option value="greedy_amount_first">Greedy Amount First (Priorità Importo)</Select.Option>
                  </Select>
                </Form.Item>

                <Row gutter={16}>
                  <Col span={12}>
                    <Form.Item label="Tolleranza (€)" name="tolerance">
                      <InputNumber min={0} step={0.5} style={{ width: '100%' }} />
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item label="Finestra Giorni" name="days_window">
                      <InputNumber min={0} max={60} style={{ width: '100%' }} />
                    </Form.Item>
                  </Col>
                </Row>

                <Form.Item label="Direzione di Ricerca Temporale" name="search_direction">
                  <Select>
                    <Select.Option value="past_only">Solo Passato (Inclusa data rif.)</Select.Option>
                    <Select.Option value="future_only">Solo Futuro (Inclusa data rif.)</Select.Option>
                    <Select.Option value="both">Entrambe le Direzioni</Select.Option>
                  </Select>
                </Form.Item>

                <Form.Item label="File Dati (.xlsx, .xls, .csv)">
                  <Dragger
                    beforeUpload={(f) => {
                      setFile(f);
                      return false;
                    }}
                    maxCount={1}
                    onRemove={() => setFile(null)}
                  >
                    <p className="ant-upload-drag-icon">
                      <InboxOutlined />
                    </p>
                    <p className="ant-upload-text">Clicca o trascina il file qui</p>
                    <p className="ant-upload-hint">Supporta file Excel e CSV con intestazioni Data, Dare, Avere</p>
                  </Dragger>
                </Form.Item>

                <Button
                  type="primary"
                  icon={<PlayCircleOutlined />}
                  size="large"
                  block
                  loading={processing}
                  onClick={startReconciliation}
                >
                  Avvia Riconciliazione
                </Button>
              </Form>
            </Card>
          </Col>

          <Col xs={24} lg={14}>
            {processing && (
              <Card title="Avanzamento Elaborazione">
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Progress percent={progress} status="active" />
                  <Text type="secondary">{statusMessage}</Text>
                </Space>
              </Card>
            )}

            {results && (
              <Space direction="vertical" size="large" style={{ width: '100%' }}>
                <Card
                  title="Sintesi Risultati"
                  extra={
                    <Button
                      type="primary"
                      icon={<DownloadOutlined />}
                      onClick={handleDownloadReport}
                    >
                      Scarica Report Excel
                    </Button>
                  }
                >
                  <Row gutter={[16, 16]}>
                    <Col span={6}>
                      <Statistic title="Righe Totali" value={results.stats.total_rows} />
                    </Col>
                    <Col span={6}>
                      <Statistic title="Movimenti Dare" value={results.stats.debit_rows} />
                    </Col>
                    <Col span={6}>
                      <Statistic title="Movimenti Avere" value={results.stats.credit_rows} />
                    </Col>
                    <Col span={6}>
                      <Statistic
                        title="Match Trovati"
                        value={results.stats.matched_count}
                        valueStyle={{ color: '#3f8600' }}
                        prefix={<CheckCircleOutlined />}
                      />
                    </Col>
                  </Row>
                  {results.stats.total_anomalies > 0 && (
                    <Alert
                      message={`Rilevate ${results.stats.total_anomalies} anomalie o discrepanze.`}
                      type="warning"
                      showIcon
                      style={{ marginTop: '16px' }}
                    />
                  )}
                </Card>

                <Card title="Anteprima Match">
                  <Table
                    dataSource={results.matches}
                    columns={matchesColumns}
                    rowKey={(record, idx) => record.group_id || idx}
                    pagination={{ pageSize: 10 }}
                  />
                </Card>
              </Space>
            )}

            {!processing && !results && (
              <Card style={{ textAlign: 'center', padding: '40px 0' }}>
                <BarChartOutlined style={{ fontSize: '48px', color: '#ccc' }} />
                <Title level={4} style={{ color: '#888', marginTop: '16px' }}>
                  Nessuna elaborazione attiva
                </Title>
                <Text type="secondary">
                  Carica un file e clicca su "Avvia Riconciliazione" per visualizzare i risultati.
                </Text>
              </Card>
            )}
          </Col>
        </Row>
      </Space>
    </div>
  );
}
