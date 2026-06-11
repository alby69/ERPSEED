import React, { useState, useEffect, useCallback } from 'react';
import {
  Card, Table, Button, Modal, Form, Input, Select, Tabs, Tag, Space,
  message, Popconfirm, Row, Col, Divider, Descriptions, Typography, Spin
} from 'antd';
import {
  PlusOutlined, EditOutlined, DeleteOutlined, EyeOutlined,
  UserOutlined, HomeOutlined, PhoneOutlined, MailOutlined, CaretUpOutlined, CaretDownOutlined
} from '@ant-design/icons';
import { apiFetch } from '../utils';
import { useTableSort } from '../hooks/useTableSort';
import TableSearch from '../components/TableSearch';
import ColumnsControl from '../components/ColumnsControl';
import Layout from '../components/Layout';
import { useTranslation } from 'react-i18next';

const { Title, Text } = Typography;
const { Option } = Select;

export default function SoggettiPage() {
  const { t } = useTranslation();
  const [modalVisible, setModalVisible] = useState(false);
  const [editingSoggetto, setEditingSoggetto] = useState(null);
  const [selectedSoggetto, setSelectedSoggetto] = useState(null);
  const [detailVisible, setDetailVisible] = useState(false);
  const [ruoli, setRuoli] = useState([]);
  const [form] = Form.useForm();
  const [activeTab, setActiveTab] = useState('1');

  const {
    data: soggetti,
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
  } = useTableSort('/api/v1/soggetti', { initialSortField: 'nome', initialSortOrder: 'asc' });

  const fetchRuoli = useCallback(async () => {
    try {
      const response = await apiFetch('/api/v1/ruoli?per_page=100');
      if (response.ok) {
        const data = await response.json();
        setRuoli(Array.isArray(data) ? data : (data.items || []));
      }
    } catch (error) {
      console.error('Errore nel caricamento dei ruoli:', error);
    }
  }, []);

  useEffect(() => {
    const loadData = async () => {
      await fetchData();
      await fetchRuoli();
    };

    void loadData();
  }, [fetchData, fetchRuoli]);

  const handleCreate = () => {
    setEditingSoggetto(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record) => {
    setEditingSoggetto(record);
    const contatti = (record.contatti || []).map(sc => ({
      canale: sc.contatto?.canale,
      valore: sc.contatto?.valore,
      is_preferred: sc.contatto?.is_preferred,
      is_primary: sc.is_primary,
    }));
    if (record.email_principale && !contatti.some(c => c.canale === 'email' && c.valore === record.email_principale)) {
      contatti.push({ canale: 'email', valore: record.email_principale, is_preferred: true, is_primary: false });
    }
    if (record.telefono_principale && !contatti.some(c => c.canale === 'telefono' && c.valore === record.telefono_principale)) {
      contatti.push({ canale: 'telefono', valore: record.telefono_principale, is_preferred: false, is_primary: false });
    }
    if (record.website && !contatti.some(c => c.canale === 'sito_web' && c.valore === record.website)) {
      contatti.push({ canale: 'sito_web', valore: record.website, is_preferred: false, is_primary: false });
    }
    form.setFieldsValue({
      ...record,
      ruoli: record.ruoli?.map(r => r.id) || [],
      contatti,
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
        message.success(t('soggetti.deleted'));
        fetchData();
      } else {
        message.error(t('soggetti.deleteError'));
      }
    } catch {
      message.error(t('soggetti.deleteError'));
    }
  };

  const handleSubmit = async (values) => {
    try {
      const url = editingSoggetto ? `/soggetti/${editingSoggetto.id}` : '/soggetti';
      const method = editingSoggetto ? 'PUT' : 'POST';

      const payload = {
        ...values,
        ruoli: (values.ruoli || []).map(id => ({ ruolo_id: id })),
      };

      const response = await apiFetch(url, {
        method,
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        message.success(editingSoggetto ? t('soggetti.updated') : t('soggetti.created'));
        setModalVisible(false);
        fetchData();
      } else {
        const err = await response.json();
        console.error('Soggetto submit error:', err);
        console.error('Payload sent:', payload);
        const detail = err.errors?.json ? Object.entries(err.errors.json).map(([k, v]) => `${k}: ${v.join(', ')}`).join('; ') : err.message;
        message.error(detail || t('soggetti.saveError'));
      }
    } catch {
      message.error(t('soggetti.saveError'));
    }
  };

  const getTipoTag = (tipo) => {
    const colors = {
      'persona_fisica': 'blue',
      'persona_giuridica': 'green',
      'ente': 'purple'
    };
    const labels = {
      'persona_fisica': 'Persona Fisica',
      'persona_giuridica': 'Azienda',
      'ente': 'Ente'
    };
    return <Tag color={colors[tipo] || 'default'}>{labels[tipo] || tipo}</Tag>;
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

  const rawColumns = [
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
      title: sortableHeader('Tipo', 'tipo_soggetto'),
      dataIndex: 'tipo_soggetto',
      key: 'tipo_soggetto',
      render: (tipo) => getTipoTag(tipo),
    },
    {
      title: sortableHeader('Email', 'email_principale'),
      dataIndex: 'email_principale',
      key: 'email_principale',
    },
    {
      title: sortableHeader('Telefono', 'telefono_principale'),
      dataIndex: 'telefono_principale',
      key: 'telefono_principale',
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
      label: 'Dati Anagrafici',
      children: (
        <>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="nome" label="Nome" rules={[{ required: true }]}>
                <Input />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="cognome" label="Cognome">
                <Input />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={24}>
              <Form.Item name="ragione_sociale" label="Ragione Sociale">
                <Input />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="codice" label="Codice">
                <Input disabled />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="tipo_soggetto" label="Tipo" rules={[{ required: true }]}>
                <Select>
                  <Option value="persona_fisica">Persona Fisica</Option>
                  <Option value="persona_giuridica">Azienda</Option>
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
      key: '2',
      label: 'Contatti',
      children: (
        <Form.List name="contatti">
          {(fields, { add, remove }) => (
            <>
              {fields.map(({ key, name, ...rest }) => (
                <Row gutter={8} key={key} align="middle" style={{ marginBottom: 8 }}>
                  <Col span={7}>
                    <Form.Item {...rest} name={[name, 'canale']} rules={[{ required: true, message: 'Obbligatorio' }]} noStyle>
                      <Select placeholder="Canale" style={{ width: '100%' }}>
                        <Option value="email">Email</Option>
                        <Option value="telefono">Telefono</Option>
                        <Option value="cellulare">Cellulare</Option>
                        <Option value="sito_web">Sito Web</Option>
                        <Option value="fax">Fax</Option>
                        <Option value="whatsapp">WhatsApp</Option>
                        <Option value="skype">Skype</Option>
                        <Option value="telegram">Telegram</Option>
                        <Option value="altro">Altro</Option>
                      </Select>
                    </Form.Item>
                  </Col>
                  <Col span={10}>
                    <Form.Item {...rest} name={[name, 'valore']} rules={[{ required: true, message: 'Obbligatorio' }]} noStyle>
                      <Input placeholder="Valore" />
                    </Form.Item>
                  </Col>
                  <Col span={4}>
                    <Form.Item {...rest} name={[name, 'is_preferred']} noStyle>
                      <Select placeholder="Pref." style={{ width: '100%' }}>
                        <Option value={true}>Preferito</Option>
                        <Option value={false}>Normale</Option>
                      </Select>
                    </Form.Item>
                  </Col>
                  <Col span={3}>
                    <Button type="text" danger icon={<DeleteOutlined />} onClick={() => remove(name)} />
                  </Col>
                </Row>
              ))}
              <Form.Item>
                <Button type="dashed" onClick={() => add({ canale: 'email', is_preferred: false })} block icon={<PlusOutlined />}>
                  Aggiungi Contatto
                </Button>
              </Form.Item>
            </>
          )}
        </Form.List>
      ),
    },
    {
      key: '3',
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
      label: 'Dati Anagrafici',
      children: selectedSoggetto && (
        <Descriptions bordered column={2}>
          <Descriptions.Item label="Codice">{selectedSoggetto.codice}</Descriptions.Item>
          <Descriptions.Item label="Tipo">{getTipoTag(selectedSoggetto.tipo_soggetto)}</Descriptions.Item>
          <Descriptions.Item label="Nome">{selectedSoggetto.nome}</Descriptions.Item>
          <Descriptions.Item label="Cognome">{selectedSoggetto.cognome}</Descriptions.Item>
          <Descriptions.Item label="Ragione Sociale">{selectedSoggetto.ragione_sociale}</Descriptions.Item>
          <Descriptions.Item label="P.IVA">{selectedSoggetto.partita_iva}</Descriptions.Item>
          <Descriptions.Item label="C.F.">{selectedSoggetto.codice_fiscale}</Descriptions.Item>
          <Descriptions.Item label="Email">{selectedSoggetto.email_principale}</Descriptions.Item>
          <Descriptions.Item label="Telefono">{selectedSoggetto.telefono_principale}</Descriptions.Item>
          <Descriptions.Item label="Sito">{selectedSoggetto.website}</Descriptions.Item>
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
        <Table
          dataSource={selectedSoggetto.contatti}
          rowKey="id"
          pagination={false}
          size="small"
          columns={[
            { title: 'Canale', dataIndex: ['contatto', 'canale'], key: 'canale', render: (v) => <Tag color="blue">{v}</Tag> },
            { title: 'Valore', dataIndex: ['contatto', 'valore'], key: 'valore' },
            { title: 'Preferito', dataIndex: ['contatto', 'is_preferred'], key: 'is_preferred', render: (v) => v ? <Tag color="gold">Preferito</Tag> : null },
          ]}
        />
      ) : <Text type="secondary">Nessun contatto associato</Text>,
    },
  ];

  return (
    <Layout>
      <div style={{ padding: '0' }}>
        <ColumnsControl pageKey="soggetti" columns={rawColumns}>
          {({ columns, button }) => (
            <Card
              title={
                <Space>
                  <UserOutlined /> {t('soggetti.title')}
                  <span>{t('soggetti.title')}</span>
                </Space>
              }
              extra={
                <Space>
                  {button}
                  <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
                    {t('soggetti.new')}
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
                dataSource={soggetti}
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
          )}
        </ColumnsControl>

      <Modal
        title={editingSoggetto ? t('soggetti.edit') : t('soggetti.new')}
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
                {editingSoggetto ? t('common.edit') : t('common.add')}
              </Button>
              <Button onClick={() => setModalVisible(false)}>{t('common.cancel')}</Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title={`${t('soggetti.details')}: ${selectedSoggetto?.nome || ''}`}
        open={detailVisible}
        onCancel={() => setDetailVisible(false)}
        footer={[
          <Button key="edit" icon={<EditOutlined />} onClick={() => {
            setDetailVisible(false);
            handleEdit(selectedSoggetto);
          }}>
            {t('common.edit')}
          </Button>,
          <Button key="close" onClick={() => setDetailVisible(false)}>{t('common.close')}</Button>
        ]}
        width={800}
      >
        <Tabs activeKey={activeTab} items={detailTabItems} onChange={setActiveTab} />
      </Modal>
      </div>
    </Layout>
  );
};
