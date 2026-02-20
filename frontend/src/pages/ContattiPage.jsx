import React, { useState, useEffect, useCallback } from 'react';
import {
  Card, Table, Button, Modal, Form, Input, Select, Tag, Space, message, Popconfirm, Typography, Row, Col
} from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, PhoneOutlined, MailOutlined, GlobalOutlined } from '@ant-design/icons';
import { apiFetch } from '@/utils';

const { Option } = Select;

const ContattiPage = () => {
  const [contatti, setContatti] = useState([]);
  const [soggetti, setSoggetti] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingContatto, setEditingContatto] = useState(null);
  const [form] = Form.useForm();

  const fetchContatti = useCallback(async () => {
    setLoading(true);
    try {
      const response = await apiFetch('/api/v1/contatti');
      if (response.ok) {
        const data = await response.json();
        setContatti(data);
      }
    } catch (error) {
      message.error('Errore nel caricamento dei contatti');
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchSoggetti = useCallback(async () => {
    try {
      const response = await apiFetch('/api/v1/soggetti');
      if (response.ok) {
        const data = await response.json();
        setSoggetti(data);
      }
    } catch (error) {
      console.error('Errore nel caricamento dei soggetti:', error);
    }
  }, []);

  useEffect(() => {
    fetchContatti();
    fetchSoggetti();
  }, [fetchContatti, fetchSoggetti]);

  const handleCreate = () => {
    setEditingContatto(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record) => {
    setEditingContatto(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  const handleDelete = async (id) => {
    try {
      const response = await apiFetch(`/contatti/${id}`, { method: 'DELETE' });
      if (response.ok) {
        message.success('Contatto eliminato');
        fetchContatti();
      } else {
        message.error('Errore nell\'eliminazione');
      }
    } catch (error) {
      message.error('Errore nell\'eliminazione');
    }
  };

  const handleSubmit = async (values) => {
    try {
      const url = editingContatto ? `/contatti/${editingContatto.id}` : '/contatti';
      const method = editingContatto ? 'PUT' : 'POST';

      const response = await apiFetch(url, {
        method,
        body: JSON.stringify(values)
      });

      if (response.ok) {
        message.success(editingContatto ? 'Contatto aggiornato' : 'Contatto creato');
        setModalVisible(false);
        fetchContatti();
      } else {
        const err = await response.json();
        message.error(err.message || 'Errore nel salvataggio');
      }
    } catch (error) {
      message.error('Errore nel salvataggio');
    }
  };

  const getCanaleIcon = (canale) => {
    const icons = {
      'email': <MailOutlined />,
      'telefono': <PhoneOutlined />,
      'cellulare': <PhoneOutlined />,
      'fax': <PhoneOutlined />,
      'whatsapp': <PhoneOutlined />,
      'skype': <GlobalOutlined />,
      'telegram': <GlobalOutlined />
    };
    return icons[canale] || <PhoneOutlined />;
  };

  const getCanaleTag = (canale) => {
    const colors = {
      'email': 'blue',
      'telefono': 'green',
      'cellulare': 'cyan',
      'fax': 'orange',
      'whatsapp': 'lime',
      'skype': 'blue',
      'telegram': 'blue'
    };
    return <Tag color={colors[canale] || 'default'}>{canale}</Tag>;
  };

  const columns = [
    {
      title: 'Soggetto',
      dataIndex: ['soggetto', 'nome'],
      key: 'soggetto',
    },
    {
      title: 'Canale',
      dataIndex: 'canale',
      key: 'canale',
      render: (canale) => (
        <Space>
          {getCanaleIcon(canale)}
          {getCanaleTag(canale)}
        </Space>
      ),
    },
    {
      title: 'Valore',
      dataIndex: 'valore',
      key: 'valore',
    },
    {
      title: 'Note',
      dataIndex: 'note',
      key: 'note',
      ellipsis: true,
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
            <PhoneOutlined />
            <span>Gestione Contatti</span>
          </Space>
        }
        extra={
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            Nuovo Contatto
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={contatti}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Modal
        title={editingContatto ? 'Modifica Contatto' : 'Nuovo Contatto'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
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
              <Form.Item name="canale" label="Canale" rules={[{ required: true }]}>
                <Select placeholder="Seleziona canale">
                  <Option value="email">Email</Option>
                  <Option value="telefono">Telefono</Option>
                  <Option value="cellulare">Cellulare</Option>
                  <Option value="fax">Fax</Option>
                  <Option value="whatsapp">WhatsApp</Option>
                  <Option value="skype">Skype</Option>
                  <Option value="telegram">Telegram</Option>
                  <Option value="altro">Altro</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="is_preferred" label="Contatto Preferito">
                <Select defaultValue={false}>
                  <Option value={true}>Sì</Option>
                  <Option value={false}>No</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="valore" label="Valore" rules={[{ required: true }]}>
            <Input placeholder="es. email@domain.com, +39 333 1234567" />
          </Form.Item>

          <Form.Item name="note" label="Note">
            <Input.TextArea rows={2} />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingContatto ? 'Aggiorna' : 'Crea'}
              </Button>
              <Button onClick={() => setModalVisible(false)}>Annulla</Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default ContattiPage;
