import React from 'react';
import { Card, Steps, Typography } from 'antd';
import { ShopOutlined, NodeIndexOutlined, CheckCircleOutlined } from '@ant-design/icons';
import Layout from '../../components/Layout';
import DomainQuestionnaire from './DomainQuestionnaire';
import ERDiagramBuilder from './ERDiagramBuilder';
import { useWizardStore } from '../../stores/wizardStore';

const { Title, Paragraph } = Typography;

const WizardPage = () => {
  const { currentStep } = useWizardStore();

  const steps = [
    {
      title: 'Domain Discovery',
      description: 'Questionario Intelligente',
      icon: <ShopOutlined />,
    },
    {
      title: 'ER Schema Visual Builder',
      description: 'Modella Entità & Relazioni',
      icon: <NodeIndexOutlined />,
    },
    {
      title: 'ERP Generato',
      description: 'Sistema Pronto all\'Uso',
      icon: <CheckCircleOutlined />,
    },
  ];

  return (
    <Layout>
      <div style={{ padding: '24px', maxWidth: 1200, margin: '0 auto' }}>
        <Card style={{ marginBottom: 24, borderRadius: 12 }}>
          <Steps current={currentStep} items={steps} />
        </Card>

        {currentStep === 0 && <DomainQuestionnaire />}
        {currentStep === 1 && <ERDiagramBuilder />}
        {currentStep === 2 && (
          <Card style={{ textAlign: 'center', padding: '40px', borderRadius: 12 }}>
            <CheckCircleOutlined style={{ fontSize: 64, color: '#52c41a', marginBottom: 16 }} />
            <Title level={2}>Complimenti! Il tuo ERP è pronto</Title>
            <Paragraph type="secondary" style={{ fontSize: 16 }}>
              I modelli, i servizi e la struttura del database sono stati provisionati con successo.
            </Paragraph>
          </Card>
        )}
      </div>
    </Layout>
  );
};

export default WizardPage;
