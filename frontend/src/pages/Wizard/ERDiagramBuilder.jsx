import React, { useState } from 'react';
import { Card, Button, Drawer, Form, Input, Select, Table, Space, Tag, Typography, Modal, Progress, message } from 'antd';
import { PlusOutlined, EditOutlined, RocketOutlined, ArrowLeftOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { ReactFlow, Background, Controls, MiniMap, applyNodeChanges, applyEdgeChanges } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import { useWizardStore } from '../../stores/wizardStore';
import { apiFetch } from '../../utils';

const { Title, Text } = Typography;

const FIELD_TYPES = [
  { value: 'string', label: 'Testo Breve (String)' },
  { value: 'text', label: 'Testo Lume (Text)' },
  { value: 'integer', label: 'Numero Intero (Integer)' },
  { value: 'decimal', label: 'Importo / Decimale (Decimal)' },
  { value: 'boolean', label: 'Booleano (Sì/No)' },
  { value: 'date', label: 'Data (Date)' },
];

const ERDiagramBuilder = () => {
  const {
    nodes,
    edges,
    domainSpec,
    drawerOpen,
    selectedEntity,
    setNodes,
    setEdges,
    setDrawerOpen,
    setSelectedEntity,
    addCustomEntity,
    setCurrentStep,
    isProvisioning,
    setIsProvisioning,
    provisionProgress,
    provisionStatusText,
    setProvisionProgress,
  } = useWizardStore();

  const [addEntityModalOpen, setAddEntityModalOpen] = useState(false);
  const [entityForm] = Form.useForm();
  const [fieldForm] = Form.useForm();

  const onNodesChange = (changes) => {
    setNodes(applyNodeChanges(changes, nodes));
  };

  const onEdgesChange = (changes) => {
    setEdges(applyEdgeChanges(changes, edges));
  };

  const onNodeClick = (_, node) => {
    const entity = (domainSpec?.entities || []).find((e) => e.name === node.id);
    if (entity) {
      setSelectedEntity(entity);
      setDrawerOpen(true);
    }
  };

  const handleAddCustomEntity = (values) => {
    const newEntity = {
      name: values.name,
      table: values.table || values.name.toLowerCase() + 's',
      title: values.title || values.name,
      fields: [
        { name: 'code', type: 'string', title: 'Codice', required: true },
        { name: 'name', type: 'string', title: 'Nome', required: true },
      ],
    };
    addCustomEntity(newEntity);
    message.success(`Entità '${newEntity.title}' aggiunta con successo allo schema ER`);
    setAddEntityModalOpen(false);
    entityForm.resetFields();
  };

  const handleAddFieldToEntity = (values) => {
    if (!selectedEntity || !domainSpec) return;

    const newField = {
      name: values.name,
      type: values.type,
      title: values.title || values.name,
      required: !!values.required,
    };

    const updatedEntities = domainSpec.entities.map((e) => {
      if (e.name === selectedEntity.name) {
        return { ...e, fields: [...(e.fields || []), newField] };
      }
      return e;
    });

    const updatedSpec = { ...domainSpec, entities: updatedEntities };
    useWizardStore.getState().setDomainSpec(updatedSpec);

    setSelectedEntity({
      ...selectedEntity,
      fields: [...(selectedEntity.fields || []), newField],
    });

    fieldForm.resetFields();
    message.success('Campo aggiunto con successo');
  };

  const handleProvisionERP = async () => {
    setIsProvisioning(true);
    setProvisionProgress(10, 'Inizializzazione provisioning del dominio...');

    try {
      await new Promise((r) => setTimeout(r, 600));
      setProvisionProgress(35, 'Generazione modelli SQLAlchemy e metadati...');

      const payload = {
        project_id: 1,
        domain_spec: domainSpec,
      };

      const res = await apiFetch('/wizard/provision', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        throw new Error('Errore durante il provisioning');
      }

      setProvisionProgress(70, 'Registrazione moduli e migrazioni schema...');
      await new Promise((r) => setTimeout(r, 800));

      setProvisionProgress(100, 'Sistema ERP generato con successo!');
      message.success('ERP configurato ed operativo!');
      setCurrentStep(2);
    } catch (err) {
      console.error(err);
      message.error('Errore durante la creazione del sistema');
    } finally {
      setIsProvisioning(false);
    }
  };

  return (
    <div style={{ height: '75vh', display: 'flex', flexDirection: 'column' }}>
      <Card
        size="small"
        style={{ marginBottom: 12 }}
        bodyStyle={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
      >
        <Space>
          <Button icon={<ArrowLeftOutlined />} onClick={() => setCurrentStep(0)}>
            Torna al Questionnaire
          </Button>
          <Title level={4} style={{ margin: 0 }}>
            Visual Schema Builder (React Flow)
          </Title>
        </Space>

        <Space>
          <Button
            type="dashed"
            icon={<PlusOutlined />}
            onClick={() => setAddEntityModalOpen(true)}
          >
            Aggiungi Entità Personalizzata
          </Button>
          <Button
            type="primary"
            icon={<RocketOutlined />}
            size="large"
            loading={isProvisioning}
            onClick={handleProvisionERP}
            style={{ borderRadius: 6, backgroundColor: '#52c41a', borderColor: '#52c41a' }}
          >
            Genera Sistema ERP
          </Button>
        </Space>
      </Card>

      <div style={{ flex: 1, border: '1px solid #d9d9d9', borderRadius: 8, overflow: 'hidden' }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onNodeClick={onNodeClick}
          fitView
        >
          <Background color="#aaa" gap={16} />
          <Controls />
          <MiniMap />
        </ReactFlow>
      </div>

      {/* Drawer for Entity Field Editing */}
      <Drawer
        title={selectedEntity ? `Entità: ${selectedEntity.title} (${selectedEntity.name})` : 'Dettagli Entità'}
        width={480}
        onClose={() => setDrawerOpen(false)}
        open={drawerOpen}
      >
        {selectedEntity && (
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            <div>
              <Text type="secondary">Tabella Database: </Text>
              <Tag color="blue">{selectedEntity.table}</Tag>
            </div>

            <div>
              <Title level={5}>Campi Configurati</Title>
              <Table
                dataSource={selectedEntity.fields || []}
                rowKey="name"
                size="small"
                pagination={false}
                columns={[
                  { title: 'Nome', dataIndex: 'title', key: 'title' },
                  { title: 'Chiave', dataIndex: 'name', key: 'name', render: (t) => <code>{t}</code> },
                  { title: 'Tipo', dataIndex: 'type', key: 'type', render: (t) => <Tag>{t}</Tag> },
                ]}
              />
            </div>

            <Card size="small" title="Aggiungi Nuovo Campo">
              <Form form={fieldForm} layout="vertical" onFinish={handleAddFieldToEntity}>
                <Form.Item name="name" label="Nome Tecnico (snake_case)" rules={[{ required: true }]}>
                  <Input placeholder="es. targa, costo_orario" />
                </Form.Item>
                <Form.Item name="title" label="Label Visuale" rules={[{ required: true }]}>
                  <Input placeholder="es. Targa Veicolo" />
                </Form.Item>
                <Form.Item name="type" label="Tipo Dato" rules={[{ required: true }]}>
                  <Select options={FIELD_TYPES} />
                </Form.Item>
                <Button type="primary" htmlType="submit" icon={<PlusOutlined />} block>
                  Aggiungi Campo
                </Button>
              </Form>
            </Card>
          </Space>
        )}
      </Drawer>

      {/* Modal for Custom Entity */}
      <Modal
        title="Crea Entità Personalizzata"
        open={addEntityModalOpen}
        onCancel={() => setAddEntityModalOpen(false)}
        footer={null}
      >
        <Form form={entityForm} layout="vertical" onFinish={handleAddCustomEntity}>
          <Form.Item name="name" label="Nome Entità in Inglese (Singolare)" rules={[{ required: true }]}>
            <Input placeholder="es. Vehicle, RentalContract, MaintenanceLog" />
          </Form.Item>
          <Form.Item name="title" label="Titolo Visuale in Italiano" rules={[{ required: true }]}>
            <Input placeholder="es. Veicoli Aziendali, Contratti Noleggio" />
          </Form.Item>
          <Form.Item name="table" label="Nome Tabella DB (Plurale)">
            <Input placeholder="es. vehicles, rental_contracts (auto se vuoto)" />
          </Form.Item>
          <Button type="primary" htmlType="submit" block size="large">
            Crea Entità
          </Button>
        </Form>
      </Modal>

      {/* Provisioning Progress Overlay Modal */}
      <Modal
        open={isProvisioning || provisionProgress === 100}
        footer={null}
        closable={false}
        centered
      >
        <div style={{ textAlign: 'center', padding: '24px 0' }}>
          {provisionProgress === 100 ? (
            <CheckCircleOutlined style={{ fontSize: 48, color: '#52c41a', marginBottom: 16 }} />
          ) : (
            <RocketOutlined style={{ fontSize: 48, color: '#1890ff', marginBottom: 16 }} />
          )}

          <Title level={4}>
            {provisionProgress === 100 ? 'ERP Generato con Successo!' : 'Generazione ERP in corso...'}
          </Title>

          <Progress percent={provisionProgress} status={provisionProgress === 100 ? 'success' : 'active'} />

          <Text type="secondary" style={{ display: 'block', marginTop: 12 }}>
            {provisionStatusText}
          </Text>

          {provisionProgress === 100 && (
            <Button
              type="primary"
              size="large"
              style={{ marginTop: 24 }}
              onClick={() => {
                setProvisionProgress(0);
                window.location.href = '/dashboard';
              }}
            >
              Accedi al Tuo Nuovo ERP
            </Button>
          )}
        </div>
      </Modal>
    </div>
  );
};

export default ERDiagramBuilder;
