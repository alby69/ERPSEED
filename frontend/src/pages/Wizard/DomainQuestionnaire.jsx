import React from 'react';
import { Card, Form, Input, Switch, Button, Row, Col, Typography, Space, Divider } from 'antd';
import { ShopOutlined, AppstoreOutlined, ShoppingCartOutlined, ProjectOutlined, ArrowRightOutlined, RobotOutlined } from '@ant-design/icons';
import { useWizardStore } from '../../stores/wizardStore';
import { apiFetch } from '../../utils';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

const DomainQuestionnaire = () => {
  const {
    companyName,
    industry,
    hasInventory,
    hasPurchases,
    hasProjects,
    customDescription,
    setFormField,
    setCurrentStep,
    setDomainSpec,
    setNodes,
    setEdges,
    setIsAnalyzing,
    isAnalyzing
  } = useWizardStore();

  const handleAnalyze = async () => {
    setIsAnalyzing(true);
    try {
      const payload = {
        company_name: companyName,
        industry,
        has_inventory: hasInventory,
        has_purchases: hasPurchases,
        has_projects: hasProjects,
        custom_description: customDescription
      };

      const res = await apiFetch('/wizard/analyze-domain', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        throw new Error('Analisi del dominio fallita');
      }

      const spec = await res.json();
      setDomainSpec(spec);

      // Convert candidate entities into React Flow nodes and edges
      const entities = spec.entities || [];
      const nodes = entities.map((entity, index) => {
        const x = (index % 3) * 280 + 50;
        const y = Math.floor(index / 3) * 200 + 50;
        return {
          id: entity.name,
          type: 'default',
          data: {
            label: (
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontWeight: 'bold', fontSize: '15px' }}>{entity.title || entity.name}</div>
                <div style={{ fontSize: '12px', color: '#666' }}>
                  {entity.fields ? `${entity.fields.length} campi` : 'Entità'}
                </div>
              </div>
            )
          },
          position: { x, y },
          style: {
            background: '#ffffff',
            border: '2px solid #1890ff',
            borderRadius: '8px',
            padding: '12px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
            width: 220,
          }
        };
      });

      // Generate relationships as edges
      const edges = [];
      if (entities.some(e => e.name === 'Customer') && entities.some(e => e.name === 'Product')) {
        edges.push({
          id: 'e-customer-product',
          source: 'Customer',
          target: 'Product',
          label: 'Acquista (1:N)',
          animated: true,
          style: { stroke: '#1890ff' }
        });
      }

      setNodes(nodes);
      setEdges(edges);
      setCurrentStep(1); // Advance to ER Diagram step
    } catch (err) {
      console.error(err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <Card style={{ maxWidth: 900, margin: '0 auto', borderRadius: 12, boxShadow: '0 6px 16px rgba(0,0,0,0.06)' }}>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <div>
          <Title level={3} style={{ marginBottom: 4 }}>
            <ShopOutlined style={{ color: '#1890ff', marginRight: 8 }} />
            Domain Discovery: Inizia la configurazione del tuo ERP
          </Title>
          <Paragraph type="secondary">
            Rispondi a poche domande sul tuo modello di business. L'AI Assistant analizzerà le tue risposte ed elaborerà una struttura di database personalizzata.
          </Paragraph>
        </div>

        <Form layout="vertical">
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label="Nome Azienda / Organizzazione" required>
                <Input
                  prefix={<ShopOutlined />}
                  value={companyName}
                  onChange={(e) => setFormField('companyName', e.target.value)}
                  placeholder="Es. Acme S.r.l."
                  size="large"
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="Settore Principale" required>
                <Input
                  prefix={<AppstoreOutlined />}
                  value={industry}
                  onChange={(e) => setFormField('industry', e.target.value)}
                  placeholder="Es. Commercio, Logistica, Servizi..."
                  size="large"
                />
              </Form.Item>
            </Col>
          </Row>

          <Divider style={{ margin: '12px 0' }}>Moduli e Operazioni Aziendali</Divider>

          <Row gutter={[24, 16]}>
            <Col span={8}>
              <Card size="small" style={{ background: '#fafafa', borderColor: hasInventory ? '#1890ff' : '#d9d9d9' }}>
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Space style={{ justifyContent: 'space-between', width: '100%' }}>
                    <Text bold><AppstoreOutlined /> Gestione Magazzino</Text>
                    <Switch
                      checked={hasInventory}
                      onChange={(checked) => setFormField('hasInventory', checked)}
                    />
                  </Space>
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    Vendi o gestisci prodotti fisici che richiedono giacenze e movimentazioni.
                  </Text>
                </Space>
              </Card>
            </Col>

            <Col span={8}>
              <Card size="small" style={{ background: '#fafafa', borderColor: hasPurchases ? '#1890ff' : '#d9d9d9' }}>
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Space style={{ justifyContent: 'space-between', width: '100%' }}>
                    <Text bold><ShoppingCartOutlined /> Acquisti & Fornitori</Text>
                    <Switch
                      checked={hasPurchases}
                      onChange={(checked) => setFormField('hasPurchases', checked)}
                    />
                  </Space>
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    Acquisti merci o materie prime da fornitori con ordini d'acquisto.
                  </Text>
                </Space>
              </Card>
            </Col>

            <Col span={8}>
              <Card size="small" style={{ background: '#fafafa', borderColor: hasProjects ? '#1890ff' : '#d9d9d9' }}>
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Space style={{ justifyContent: 'space-between', width: '100%' }}>
                    <Text bold><ProjectOutlined /> Progetti & Timesheet</Text>
                    <Switch
                      checked={hasProjects}
                      onChange={(checked) => setFormField('hasProjects', checked)}
                    />
                  </Space>
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    Esegui servizi a consuntivo, commesse, contratti e tracciamento ore.
                  </Text>
                </Space>
              </Card>
            </Col>
          </Row>

          <Divider style={{ margin: '20px 0' }}>Requisiti Personalizzati (AI Assistant)</Divider>

          <Form.Item
            label={
              <Space>
                <RobotOutlined style={{ color: '#722ed1' }} />
                <Text bold>Qualcosa di unico nel tuo business?</Text>
              </Space>
            }
            help="Esempio: 'Ho una flotta di 15 furgoni che richiedono manutenzione', 'Gestisco contratti di noleggio a lungo termine', ecc."
          >
            <TextArea
              rows={4}
              value={customDescription}
              onChange={(e) => setFormField('customDescription', e.target.value)}
              placeholder="Descrivi in linguaggio naturale eventuali processi o entità speciali che vuoi che l'AI generi per te..."
            />
          </Form.Item>

          <div style={{ textAlign: 'right', marginTop: 24 }}>
            <Button
              type="primary"
              size="large"
              icon={isAnalyzing ? <RobotOutlined spin /> : <ArrowRightOutlined />}
              loading={isAnalyzing}
              onClick={handleAnalyze}
              style={{ borderRadius: 8, paddingLeft: 32, paddingRight: 32 }}
            >
              Genera Schema ER con AI
            </Button>
          </div>
        </Form>
      </Space>
    </Card>
  );
};

export default DomainQuestionnaire;
