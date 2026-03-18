import React, { useState, useEffect, useCallback } from 'react';
import {
  Card, Table, Button, Modal, Form, Input, Select, Tag, Space, message, Popconfirm, Typography, Row, Col
} from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, PhoneOutlined, MailOutlined, GlobalOutlined, CaretUpOutlined, CaretDownOutlined } from '@ant-design/icons';
import { apiFetch } from '../utils';
import { useTableSort } from '../hooks/useTableSort';
import TableSearch from '../components/TableSearch';
import Layout from '../components/Layout';

const { Option } = Select;

const ContattiPage = () => {
  const [soggetti, setSoggetti] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingContatto, setEditingContatto] = useState(null);
  const [form] = Form.useForm();

  const { 
    data: contatti, 
    loading, 
    pagination, 
    sortField, 
    sortOrder,
    searchField,
    searchValue,
    searchTerm,
    fetchData,
    handleSort,
    handlePageChange,
    handleSearchField,
    handleSearchSubmit,
    handleClearSearch,
    handleSearch
  } = useTableSort('/api/v1/contatti', { initialSortField: 'nome', initialSortOrder: 'asc' });

  const fetchSoggetti = useCallback(async () => {
    try {
      const response = await apiFetch('/api/v1/soggetti?per_page=1000');
      if (response.ok) {
        const data = await response.json();
        setSoggetti(Array.isArray(data) ? data : (data.items || []));
      }
    } catch (error) {
      console.error('Errore nel caricamento dei soggetti:', error);
    }
  }, []);

  useEffect(() => {
    fetchData();
    fetchSoggetti();
  }, [fetchData, fetchSoggetti]);

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
        fetchData();
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
        fetchData();
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

  const sortableHeader = (title, field) => (
    <span style={{ cursor: 'pointer' }} onClick={() => handleSort(field)}>
      {title}
      {sortField === field ? (
        sortOrder === 'asc' ? <CaretUpOutlined style={{ marginLeft: 4, fontSize: 10 }} /> : <CaretDownOutlined style={{ marginLeft: 4, fontSize: 10 }} />
      ) : (
        <CaretUpOutlined style={{ marginLeft: 4, fontSize: 10, opacity: 0.3 }} />
      )}
    </span>
  );

  const columns = [
    {
      title: sortableHeader('Soggetto', 'soggetto_id'),
      dataIndex: ['soggetto', 'nome'],
      key: 'soggetto',
    },
    {
      title: sortableHeader('Canale', 'canale'),
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
      title: sortableHeader('Valore', 'valore'),
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
      title: sortableHeader('Preferito', 'is_preferred'),
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
    <Layout>
      <div style={{ padding: '0' }}>
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
        <div className="mb-3">
          <TableSearch
            columns={columns}
            searchField={searchField}
            searchValue={searchValue}
            searchTerm={searchTerm}
            globalSearchValue={searchTerm}
            onSearchFieldChange={handleSearchField}
            onSearchValueChange={(val) => handleSearchField(searchField, val)}
            onSearchSubmit={handleSearchSubmit}
            onClearSearch={handleClearSearch}
            onGlobalSearch={handleSearch}
          />
        </div>
        <Table
          columns={columns}
          dataSource={contatti}
          rowKey="id"
          loading={loading}
          pagination={{ 
            current: pagination.page, 
            pageSize: pagination.perPage, 
            total: pagination.totalItems,
            onChange: handlePageChange,
            showSizeChanger: false
          }}
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
    </Layout>
  );
};

export default ContattiPage;
