import React, { useState, useEffect, useCallback } from 'react';
import {
  Card, Table, Button, Modal, Form, Input, Select, Tag, Space, message, Popconfirm, Typography, Row, Col, InputNumber
} from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, EnvironmentOutlined } from '@ant-design/icons';
import { apiFetch } from '@/utils';

const { Option } = Select;

const IndirizziPage = () => {
  const [indirizzi, setIndirizzi] = useState([]);
  const [soggetti, setSoggetti] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingIndirizzo, setEditingIndirizzo] = useState(null);
  const [form] = Form.useForm();

  const fetchIndirizzi = useCallback(async () => {
    setLoading(true);
    try {
      const response = await apiFetch('/indirizzi');
      if (response.ok) {
        const data = await response.json();
        setIndirizzi(data);
      }
    } catch (error) {
      message.error('Errore nel caricamento degli indirizzi');
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchSoggetti = useCallback(async () => {
    try {
      const response = await apiFetch('/soggetti');
      if (response.ok) {
        const data = await response.json();
        setSoggetti(data);
      }
    } catch (error) {
      console.error('Errore nel caricamento dei soggetti:', error);
    }
  }, []);

  useEffect(() => {
    fetchIndirizzi();
    fetchSoggetti();
  }, [fetchIndirizzi, fetchSoggetti]);

  const handleCreate = () => {
    setEditingIndirizzo(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record) => {
    setEditingIndirizzo(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  const handleDelete = async (id) => {
    try {
      const response = await apiFetch(`/indirizzi/${id}`, { method: 'DELETE' });
      if (response.ok) {
        message.success('Indirizzo eliminato');
        fetchIndirizzi();
      } else {
        message.error('Errore nell\'eliminazione');
      }
    } catch (error) {
      message.error('Errore nell\'eliminazione');
    }
  };

  const handleSubmit = async (values) => {
    try {
      const url = editingIndirizzo ? `/indirizzi/${editingIndirizzo.id}` : '/indirizzi';
      const method = editingIndirizzo ? 'PUT' : 'POST';

      const response = await apiFetch(url, {
        method,
        body: JSON.stringify(values)
      });

      if (response.ok) {
        message.success(editingIndirizzo ? 'Indirizzo aggiornato' : 'Indirizzo creato');
        setModalVisible(false);
        fetchIndirizzi();
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
      'residenza': 'blue',
      'sede_legale': 'green',
      'magazzino': 'orange',
      'fatturazione': 'purple',
      'consegue': 'cyan'
    };
    return <Tag color={colors[tipo] || 'default'}>{tipo}</Tag>;
  };

  const columns = [
    {
      title: 'Soggetto',
      dataIndex: ['soggetto', 'nome'],
      key: 'soggetto',
    },
    {
      title: 'Tipo',
      dataIndex: 'tipo',
      key: 'tipo',
      render: (tipo) => getTipoTag(tipo),
    },
    {
      title: 'Indirizzo',
      key: 'indirizzo',
      render: (_, record) => (
        <span>
          {record.via}, {record.numero_civico}<br />
          {record.cap} {record.città} ({record.provincia})
        </span>
      ),
    },
    {
      title: 'Nazione',
      dataIndex: 'nazione',
      key: 'nazione',
    },
    {
      title: 'Coordinate',
      key: 'coordinate',
      render: (_, record) => (
        record.latitudine && record.longitudine ? (
          <Tag>{record.latitudine}, {record.longitudine}</Tag>
        ) : '-'
      ),
    },
    {
      title: 'Preferito',
      dataIndex: 'is_preferred',
      key: 'is_preferred',
      render: (val) => val ? <Tag color="gold">Preferito</Tag> : null,
    },
    {
      title: 'Azioni',
      key: 'azioni',
      width: 120,
      render: (_, record) => (
        <Space>
          <Button type="text" icon={<EditOutlined />} onClick={() => handleEdit(record)} />
          <Popconfirm title="Confermi l'eliminazione?" onConfirm={() => handleDelete(record.id)}>
            <Button type="text" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const soggettoOptions = soggetti.map(s => (
    <Option key={s.id} value={s.id}>{s.nome}</Option>
  ));

  return (
    <div style={{ padding: '24px' }}>
      <Card
        title={
          <Space>
            <EnvironmentOutlined />
            <span>Gestione Indirizzi</span>
          </Space>
        }
        extra={
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            Nuovo Indirizzo
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={indirizzi}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Modal
        title={editingIndirizzo ? 'Modifica Indirizzo' : 'Nuovo Indirizzo'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item name="soggetto_id" label="Soggetto" rules={[{ required: true }]}>
            <Select showSearch placeholder="Cerca soggetto">
              {soggettoOptions}
            </Select>
          </Form.Item>
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="tipo" label="Tipo" rules={[{ required: true }]}>
                <Select>
                  <Option value="residenza">Residenza</Option>
                  <Option value="sede_legale">Sede Legale</Option>
                  <Option value="magazzino">Magazzino</Option>
                  <Option value="fatturazione">Fatturazione</Option>
                  <Option value="consegna">Consegna</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="is_preferred" label="Indirizzo Preferito" valuePropName="checked">
                <Select defaultValue={false}>
                  <Option value={true}>Sì</Option>
                  <Option value={false}>No</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="via" label="Via / Piazza" rules={[{ required: true }]}>
            <Input />
          </Form.Item>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="numero_civico" label="N. Civico">
                <Input />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="cap" label="CAP">
                <Input />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="provincia" label="Provincia">
                <Input />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="città" label="Città" rules={[{ required: true }]}>
                <Input />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="nazione" label="Nazione" initialValue="Italia">
                <Input />
              </Form.Item>
            </Col>
          </Row>

          <Divider>Geolocalizzazione</Divider>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="latitudine" label="Latitudine">
                <InputNumber step={0.000001} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="longitudine" label="Longitudine">
                <InputNumber step={0.000001} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingIndirizzo ? 'Aggiorna' : 'Crea'}
              </Button>
              <Button onClick={() => setModalVisible(false)}>Annulla</Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default IndirizziPage;
