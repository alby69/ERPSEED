import React, { useState, useEffect, useCallback } from 'react';
import {
  Card, Table, Button, Modal, Form, Input, Select, Tag, Space, message, Popconfirm, Typography, Row, Col
} from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, CaretUpOutlined, CaretDownOutlined } from '@ant-design/icons';
import { apiFetch } from '../utils';
import { useTableSort } from '../hooks/useTableSort';
import TableSearch from '../components/TableSearch';
import Layout from '../components/Layout';

const { Title } = Typography;
const { Option } = Select;

const RuoliPage = () => {
  const [modalVisible, setModalVisible] = useState(false);
  const [editingRuolo, setEditingRuolo] = useState(null);
  const [form] = Form.useForm();

  const { 
    data: ruoli, 
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
  } = useTableSort('/api/v1/ruoli', { initialSortField: 'nome', initialSortOrder: 'asc' });

  const getStatoTag = (stato) => {
    const colors = {
      'attivo': 'green',
      'sospeso': 'orange',
      'terminato': 'red'
    };
    return <Tag color={colors[stato] || 'default'}>{stato}</Tag>;
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
      title: sortableHeader('Codice', 'codice'),
      dataIndex: 'codice',
      key: 'codice',
      width: 100,
    },
    {
      title: sortableHeader('Nome', 'nome'),
      dataIndex: 'nome',
      key: 'nome',
    },
    {
      title: sortableHeader('Descrizione', 'descrizione'),
      dataIndex: 'descrizione',
      key: 'descrizione',
    },
    {
      title: sortableHeader('Stato', 'stato'),
      dataIndex: 'stato',
      key: 'stato',
      render: (stato) => getStatoTag(stato),
    },
    {
      title: sortableHeader('Predefinito', 'predefinito'),
      dataIndex: 'predefinito',
      key: 'predefinito',
      render: (val) => val ? <Tag color="blue">Sì</Tag> : <Tag>No</Tag>,
    },
    {
      title: 'Azioni',
      key: 'azioni',
      width: 120,
      render: (_, record) => (
        <Space>
          <Button type="text" icon={<EditOutlined />} onClick={() => handleEdit(record)} />
          {!record.predefinito && (
            <Popconfirm title="Confermi l'eliminazione?" onConfirm={() => handleDelete(record.id)}>
              <Button type="text" danger icon={<DeleteOutlined />} />
            </Popconfirm>
          )}
        </Space>
      ),
    },
  ];

  const handleCreate = () => {
    setEditingRuolo(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record) => {
    setEditingRuolo(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  const handleDelete = async (id) => {
    try {
      const response = await apiFetch(`/ruoli/${id}`, { method: 'DELETE' });
      if (response.ok) {
        message.success('Ruolo eliminato');
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
      const url = editingRuolo ? `/ruoli/${editingRuolo.id}` : '/ruoli';
      const method = editingRuolo ? 'PUT' : 'POST';

      const response = await apiFetch(url, {
        method,
        body: JSON.stringify(values)
      });

      if (response.ok) {
        message.success(editingRuolo ? 'Ruolo aggiornato' : 'Ruolo creato');
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

  return (
    <Layout>
      <div style={{ padding: '0' }}>
        <Card
          title={
            <Space>
              <span>Gestione Ruoli</span>
            </Space>
          }
          extra={
            <Space>
              <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
                Nuovo Ruolo
              </Button>
          </Space>
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
          dataSource={ruoli}
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
        title={editingRuolo ? 'Modifica Ruolo' : 'Nuovo Ruolo'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="codice" label="Codice" rules={[{ required: true }]}>
                <Input />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="nome" label="Nome" rules={[{ required: true }]}>
                <Input />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="descrizione" label="Descrizione">
            <Input.TextArea rows={3} />
          </Form.Item>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="stato" label="Stato" initialValue="attivo">
                <Select>
                  <Option value="attivo">Attivo</Option>
                  <Option value="sospeso">Sospeso</Option>
                  <Option value="terminato">Terminato</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="predefinito" label="Predefinito" valuePropName="checked">
                <Select defaultValue={false}>
                  <Option value={true}>Sì</Option>
                  <Option value={false}>No</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="parametri" label="Parametri (JSON)">
            <Input.TextArea rows={4} placeholder='{"sconto_max": 10}' />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingRuolo ? 'Aggiorna' : 'Crea'}
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

export default RuoliPage;
