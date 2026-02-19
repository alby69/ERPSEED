import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Card, Table, Button, Modal, Form, Input, Select, Tabs, Tag, Space,
  message, Popconfirm, Row, Col, Divider, Descriptions, Typography, Spin
} from 'antd';
import {
  PlusOutlined, EditOutlined, DeleteOutlined, EyeOutlined,
  UserOutlined, HomeOutlined, PhoneOutlined, MailOutlined
} from '@ant-design/icons';
import { apiFetch } from '@/utils';

const { Title, Text } = Typography;
const { Option } = Select;

const SoggettiPage = () => {
  const [soggetti, setSoggetti] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingSoggetto, setEditingSoggetto] = useState(null);
  const [selectedSoggetto, setSelectedSoggetto] = useState(null);
  const [detailVisible, setDetailVisible] = useState(false);
  const [ruoli, setRuoli] = useState([]);
  const [form] = Form.useForm();
  const [activeTab, setActiveTab] = useState('1');

  const fetchSoggetti = useCallback(async () => {
    setLoading(true);
    try {
      const response = await apiFetch('/soggetti');
      if (response.ok) {
        const data = await response.json();
        setSoggetti(data);
      }
    } catch (error) {
      message.error('Errore nel caricamento dei soggetti');
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchRuoli = useCallback(async () => {
    try {
      const response = await apiFetch('/ruoli');
      if (response.ok) {
        const data = await response.json();
        setRuoli(data);
      }
    } catch (error) {
      console.error('Errore nel caricamento dei ruoli:', error);
    }
  }, []);

  useEffect(() => {
    fetchSoggetti();
    fetchRuoli();
  }, [fetchSoggetti, fetchRuoli]);

  const handleCreate = () => {
    setEditingSoggetto(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record) => {
    setEditingSoggetto(record);
    form.setFieldsValue({
      ...record,
      ruoli: record.ruoli?.map(r => r.id) || []
    });
    setModalVisible(true);
  };

  const handleView = async (record) => {
    setSelectedSoggetto(record);
    setDetailVisible(true);
    setActiveTab('1');
  };

  const handleDelete = async (id) => {
    try {
      const response = await apiFetch(`/soggetti/${id}`, { method: 'DELETE' });
      if (response.ok) {
        message.success('Soggetto eliminato');
        fetchSoggetti();
      } else {
        message.error('Errore nell\'eliminazione');
      }
    } catch (error) {
      message.error('Errore nell\'eliminazione');
    }
  };

  const handleSubmit = async (values) => {
    try {
      const url = editingSoggetto ? `/soggetti/${editingSoggetto.id}` : '/soggetti';
      const method = editingSoggetto ? 'PUT' : 'POST';

      const response = await apiFetch(url, {
        method,
        body: JSON.stringify(values)
      });

      if (response.ok) {
        message.success(editingSoggetto ? 'Soggetto aggiornato' : 'Soggetto creato');
        setModalVisible(false);
        fetchSoggetti();
      } else {
        const err = await response.json();
        message.error(err.message || 'Errore nel salvataggio');
      }
    } catch (error) {
      message.error('Errore nel salvataggio');
    }
  };

  const getTipoTag = (tipo) => {
    const colors = {
      'persona': 'blue',
      'azienda': 'green',
      'ente': 'purple'
    };
    const labels = {
      'persona': 'Persona Fisica',
      'azienda': 'Azienda',
      'ente': 'Ente'
    };
    return <Tag color={colors[tipo] || 'default'}>{labels[tipo] || tipo}</Tag>;
  };

  const columns = [
    {
      title: 'Codice',
      dataIndex: 'codice',
      key: 'codice',
      width: 100,
    },
    {
      title: 'Nome',
      dataIndex: 'nome',
      key: 'nome',
    },
    {
      title: 'Tipo',
      dataIndex: 'tipo',
      key: 'tipo',
      render: (tipo) => getTipoTag(tipo),
    },
    {
      title: 'Email',
      dataIndex: 'email',
      key: 'email',
    },
    {
      title: 'Telefono',
      dataIndex: 'telefono',
      key: 'telefono',
    },
    {
      title: 'Ruoli',
      dataIndex: 'ruoli',
      key: 'ruoli',
      render: (ruoli) => (
        <Space size={4}>
          {ruoli?.slice(0, 2).map((r, i) => (
            <Tag key={i} color="blue">{r.nome}</Tag>
          ))}
          {ruoli?.length > 2 && <Tag>+{ruoli.length - 2}</Tag>}
        </Space>
      ),
    },
    {
      title: 'Azioni',
      key: 'azioni',
      width: 150,
      render: (_, record) => (
        <Space>
          <Button type="text" icon={<EyeOutlined />} onClick={() => handleView(record)} />
          <Button type="text" icon={<EditOutlined />} onClick={() => handleEdit(record)} />
          <Popconfirm title="Confermi l'eliminazione?" onConfirm={() => handleDelete(record.id)}>
            <Button type="text" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const ruoloOptions = ruoli.map(r => (
    <Option key={r.id} value={r.id}>{r.nome}</Option>
  ));

  const tabItems = [
    {
      key: '1',
      label: 'Dati Principali',
      children: (
        <Form.Item name="nome" label="Nome / Ragione Sociale" rules={[{ required: true }]}>
          <Input />
        </Form.Item>
      ),
    },
    {
      key: '2',
      label: 'Dati Anagrafici',
      children: (
        <>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="codice" label="Codice">
                <Input disabled />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="tipo" label="Tipo" rules={[{ required: true }]}>
                <Select>
                  <Option value="persona">Persona Fisica</Option>
                  <Option value="azienda">Azienda</Option>
                  <Option value="ente">Ente</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="partita_iva" label="Partita IVA">
                <Input />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="codice_fiscale" label="Codice Fiscale">
                <Input />
              </Form.Item>
            </Col>
          </Row>
        </>
      ),
    },
    {
      key: '3',
      label: 'Contatti',
      children: (
        <>
          <Form.Item name="email" label="Email">
            <Input type="email" />
          </Form.Item>
          <Form.Item name="telefono" label="Telefono">
            <Input />
          </Form.Item>
          <Form.Item name="cellulare" label="Cellulare">
            <Input />
          </Form.Item>
          <Form.Item name="fax" label="Fax">
            <Input />
          </Form.Item>
          <Form.Item name="pec" label="PEC">
            <Input type="email" />
          </Form.Item>
          <Form.Item name="sitoweb" label="Sito Web">
            <Input />
          </Form.Item>
        </>
      ),
    },
    {
      key: '4',
      label: 'Ruoli',
      children: (
        <Form.Item name="ruoli" label="Assegna Ruoli">
          <Select mode="multiple" placeholder="Seleziona ruoli">
            {ruoloOptions}
          </Select>
        </Form.Item>
      ),
    },
  ];

  const detailTabItems = [
    {
      key: '1',
      label: 'Dati Principali',
      children: selectedSoggetto && (
        <Descriptions bordered column={2}>
          <Descriptions.Item label="Codice">{selectedSoggetto.codice}</Descriptions.Item>
          <Descriptions.Item label="Tipo">{getTipoTag(selectedSoggetto.tipo)}</Descriptions.Item>
          <Descriptions.Item label="Nome">{selectedSoggetto.nome}</Descriptions.Item>
          <Descriptions.Item label="Email">{selectedSoggetto.email}</Descriptions.Item>
          <Descriptions.Item label="Telefono">{selectedSoggetto.telefono}</Descriptions.Item>
          <Descriptions.Item label="Cellulare">{selectedSoggetto.cellulare}</Descriptions.Item>
          <Descriptions.Item label="P.IVA">{selectedSoggetto.partita_iva}</Descriptions.Item>
          <Descriptions.Item label="C.F.">{selectedSoggetto.codice_fiscale}</Descriptions.Item>
          <Descriptions.Item label="PEC">{selectedSoggetto.pec}</Descriptions.Item>
          <Descriptions.Item label="Sito">{selectedSoggetto.sitoweb}</Descriptions.Item>
        </Descriptions>
      ),
    },
    {
      key: '2',
      label: 'Ruoli',
      children: selectedSoggetto?.ruoli && (
        <Space wrap>
          {selectedSoggetto.ruoli.map((r, i) => (
            <Tag key={i} color="blue" style={{ padding: '8px 16px' }}>{r.nome}</Tag>
          ))}
        </Space>
      ),
    },
    {
      key: '3',
      label: 'Indirizzi',
      children: selectedSoggetto?.indirizzi?.length > 0 ? (
        <Row gutter={16}>
          {selectedSoggetto.indirizzi.map((ind, i) => (
            <Col span={12} key={i}>
              <Card size="small" title={ind.tipo || 'Indirizzo'}>
                <p>{ind.via}, {ind.città}</p>
                <p>{ind.cap} ({ind.provincia})</p>
                <p>{ind.nazione}</p>
              </Card>
            </Col>
          ))}
        </Row>
      ) : <Text type="secondary">Nessun indirizzo associato</Text>,
    },
    {
      key: '4',
      label: 'Contatti',
      children: selectedSoggetto?.contatti?.length > 0 ? (
        <Space direction="vertical">
          {selectedSoggetto.contatti.map((c, i) => (
            <Card key={i} size="small">
              <Tag color="blue">{c.canale}</Tag>: {c.valore}
            </Card>
          ))}
        </Space>
      ) : <Text type="secondary">Nessun contatto associato</Text>,
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Card
        title={
          <Space>
            <UserOutlined />
            <span>Anagrafiche (Soggetti)</span>
          </Space>
        }
        extra={
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            Nuovo Soggetto
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={soggetti}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Modal
        title={editingSoggetto ? 'Modifica Soggetto' : 'Nuovo Soggetto'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={700}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Tabs items={tabItems} />
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingSoggetto ? 'Aggiorna' : 'Crea'}
              </Button>
              <Button onClick={() => setModalVisible(false)}>Annulla</Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title={`Dettaglio: ${selectedSoggetto?.nome}`}
        open={detailVisible}
        onCancel={() => setDetailVisible(false)}
        footer={[
          <Button key="edit" icon={<EditOutlined />} onClick={() => {
            setDetailVisible(false);
            handleEdit(selectedSoggetto);
          }}>
            Modifica
          </Button>,
          <Button key="close" onClick={() => setDetailVisible(false)}>Chiudi</Button>
        ]}
        width={800}
      >
        <Tabs activeKey={activeTab} items={detailTabItems} onChange={setActiveTab} />
      </Modal>
    </div>
  );
};

export default SoggettiPage;
