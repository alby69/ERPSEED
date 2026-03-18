import React, { useState, useEffect, useCallback } from 'react';
import {
  Card, Table, Button, Modal, Form, Input, Select, Tag, Space, message, Popconfirm, Row, Col, InputNumber, Divider, AutoComplete
} from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, EnvironmentOutlined, SearchOutlined, AimOutlined, CaretUpOutlined, CaretDownOutlined } from '@ant-design/icons';
import { apiFetch } from '../utils';
import { useTableSort } from '../hooks/useTableSort';
import TableSearch from '../components/TableSearch';
import Layout from '../components/Layout';

const { Option } = Select;

const IndirizziPage = () => {
  const [soggetti, setSoggetti] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingIndirizzo, setEditingIndirizzo] = useState(null);
  const [form] = Form.useForm();

  const { 
    data: indirizzi, 
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
  } = useTableSort('/api/v1/indirizzi', { initialSortField: 'città', initialSortOrder: 'asc' });

  // Stati per selezione gerarchica
  const [regioni, setRegioni] = useState([]);
  const [province, setProvince] = useState([]);
  const [comuni, setComuni] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);

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

  const fetchRegioni = useCallback(async () => {
    try {
      const response = await apiFetch('/api/v1/comuni/regioni');
      if (response.ok) {
        const data = await response.json();
        setRegioni(data);
      }
    } catch (error) {
      console.error('Errore nel caricamento delle regioni:', error);
    }
  }, []);

  const fetchProvince = useCallback(async (regioneCodice) => {
    if (!regioneCodice) {
      setProvince([]);
      return;
    }
    try {
      const response = await apiFetch(`/api/v1/comuni/province?regione=${regioneCodice}`);
      if (response.ok) {
        const data = await response.json();
        setProvince(data);
      }
    } catch (error) {
      console.error('Errore nel caricamento delle province:', error);
    }
  }, []);

  const fetchComuni = useCallback(async (provinciaCodice) => {
    if (!provinciaCodice) {
      setComuni([]);
      return;
    }
    try {
      const response = await apiFetch(`/api/v1/comuni?provincia=${provinciaCodice}`);
      if (response.ok) {
        const data = await response.json();
        setComuni(data.items || []);
      }
    } catch (error) {
      console.error('Errore nel caricamento dei comuni:', error);
    }
  }, []);

  const cercaIndirizzo = useCallback(async (testo) => {
    if (!testo || testo.length < 2) {
      setSearchResults([]);
      return;
    }
    setSearchLoading(true);
    try {
      const response = await apiFetch(`/api/v1/comuni?q=${encodeURIComponent(testo)}`);
      if (response.ok) {
        const data = await response.json();
        setSearchResults(data.items || []);
      }
    } catch (error) {
      console.error('Errore nella ricerca:', error);
    } finally {
      setSearchLoading(false);
    }
  }, []);

  const geocodificaIndirizzo = async (values) => {
    const indirizzo = [
      values.via,
      values.numero_civico,
      values.città,
      values.provincia,
      values.nazione || 'Italia'
    ].filter(Boolean).join(', ');

    if (!indirizzo) {
      message.warning('Compila almeno via e città per geocodificare');
      return;
    }

    try {
      const response = await apiFetch(`/api/v1/indirizzi/geocodifica?indirizzo=${encodeURIComponent(indirizzo)}`);
      if (response.ok) {
        const data = await response.json();
        if (data.latitudine && data.longitudine) {
          form.setFieldsValue({
            latitudine: data.latitudine,
            longitudine: data.longitudine
          });
          message.success('Coordinate trovate automaticamente');
        } else {
          message.warning('Indirizzo non trovato, inserisci le coordinate manualmente');
        }
      } else {
        message.error('Geocodifica fallita');
      }
    } catch (error) {
      message.error('Errore nella geocodifica');
    }
  };

  useEffect(() => {
    fetchData();
    fetchSoggetti();
    fetchRegioni();
  }, [fetchData, fetchSoggetti, fetchRegioni]);

  const handleCreate = () => {
    setEditingIndirizzo(null);
    form.resetFields();
    form.setFieldsValue({ nazione: 'IT' });
    setProvince([]);
    setComuni([]);
    setModalVisible(true);
  };

  const handleEdit = (record) => {
    setEditingIndirizzo(record);
    form.setFieldsValue(record);
    // Carica province e comuni se presenti
    if (record.provincia) {
      fetchProvince(record.regione);
      fetchComuni(record.provincia);
    }
    setModalVisible(true);
  };

  const handleDelete = async (id) => {
    try {
      const response = await apiFetch(`/indirizzi/${id}`, { method: 'DELETE' });
      if (response.ok) {
        message.success('Indirizzo eliminato');
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
      const url = editingIndirizzo ? `/indirizzi/${editingIndirizzo.id}` : '/indirizzi';
      const method = editingIndirizzo ? 'PUT' : 'POST';

      const response = await apiFetch(url, {
        method,
        body: JSON.stringify(values)
      });

      if (response.ok) {
        message.success(editingIndirizzo ? 'Indirizzo aggiornato' : 'Indirizzo creato');
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

  const handleRegioneChange = (value) => {
    form.setFieldsValue({ provincia: undefined, città: undefined });
    setProvince([]);
    setComuni([]);
    fetchProvince(value);
  };

  const handleProvinciaChange = (value) => {
    form.setFieldsValue({ città: undefined });
    setComuni([]);
    fetchComuni(value);
  };

  const handleSearchSelect = (value, option) => {
    const comune = option.comuneData;
    if (comune) {
      form.setFieldsValue({
        città: comune.nome,
        cap: comune.CAP,
        provincia: comune.provincia,
        regione: comune.regione,  // Use codice regione directly
        latitudine: comune.latitudine,
        longitudine: comune.longitudine
      });
      // Load province for the selected region
      if (comune.provincia) {
        fetchProvince(comune.regione);
        setTimeout(() => fetchComuni(comune.provincia), 100);
      }
    }
  };

  const getTipoTag = (tipo) => {
    const colors = {
      'residenza': 'blue',
      'sede_legale': 'green',
      'magazzino': 'orange',
      'fatturazione': 'purple',
      'consegna': 'cyan'
    };
    return <Tag color={colors[tipo] || 'default'}>{tipo}</Tag>;
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
      title: sortableHeader('Tipo', 'tipo'),
      dataIndex: 'tipo',
      key: 'tipo',
      render: (tipo) => getTipoTag(tipo),
    },
    {
      title: sortableHeader('Città', 'città'),
      key: 'indirizzo',
      render: (_, record) => (
        <span>
          {record.denominazione}, {record.numero_civico}<br />
          {record.cap} {record.città} ({record.provincia})
        </span>
      ),
    },
    {
      title: sortableHeader('Nazione', 'nazione'),
      dataIndex: 'nazione',
      key: 'nazione',
    },
    {
      title: 'Coordinate',
      key: 'coordinate',
      render: (_, record) => (
        record.latitudine && record.longitudine ? (
          <Tag>{record.latitudine.toFixed(5)}, {record.longitudine.toFixed(5)}</Tag>
        ) : '-'
      ),
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
          dataSource={indirizzi}
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
        title={editingIndirizzo ? 'Modifica Indirizzo' : 'Nuovo Indirizzo'}
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
              <Form.Item name="is_preferred" label="Preferito" valuePropName="checked">
                <Select defaultValue={false}>
                  <Option value={true}>Sì</Option>
                  <Option value={false}>No</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Divider>Ricerca Automatica</Divider>
          
          <Form.Item label="Cerca indirizzo">
            <AutoComplete
              placeholder="Inizia a scrivere un indirizzo..."
              options={searchResults.map(r => ({
                value: r.display,
                comuneData: r
              }))}
              onSearch={cercaIndirizzo}
              onSelect={handleSearchSelect}
              loading={searchLoading}
              style={{ width: '100%' }}
            />
          </Form.Item>

          <Divider>Indirizzo</Divider>

          <Row gutter={16}>
            <Col span={24}>
              <Form.Item name="denominazione" label="Via / Piazza" rules={[{ required: true }]}>
                <Input placeholder="Via Roma, 1" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="numero_civico" label="N. Civico">
                <Input placeholder="1" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="cap" label="CAP">
                <Input placeholder="00100" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="nazione" label="Nazione" initialValue="IT">
                <Select>
                  <Option value="IT">Italia</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="regione" label="Regione">
                <Select 
                  placeholder="Seleziona regione"
                  onChange={handleRegioneChange}
                  showSearch
                  allowClear
                >
                  {regioni.map(r => (
                    <Option key={r.codice} value={r.codice}>{r.nome}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="provincia" label="Provincia">
                <Select 
                  placeholder="Seleziona provincia"
                  onChange={handleProvinciaChange}
                  showSearch
                  allowClear
                >
                  {province.map(p => (
                    <Option key={p.codice} value={p.codice}>{p.nome}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="città" label="Città" rules={[{ required: true }]}>
                <Select 
                  placeholder="Seleziona comune"
                  showSearch
                  allowClear
                >
                  {comuni.map(c => (
                    <Option key={c.codice} value={c.nome}>{c.nome}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Divider>
            <Space>
              <AimOutlined />
              Geolocalizzazione
            </Space>
          </Divider>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="latitudine" label="Latitudine">
                <InputNumber step={0.000001} style={{ width: '100%' }} placeholder="41.9028" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="longitudine" label="Longitudine">
                <InputNumber step={0.000001} style={{ width: '100%' }} placeholder="12.4964" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item>
            <Space>
              <Button 
                type="default" 
                icon={<SearchOutlined />}
                onClick={() => geocodificaIndirizzo(form.getFieldsValue())}
              >
                Trova Coordinate
              </Button>
              <Button type="primary" htmlType="submit">
                {editingIndirizzo ? 'Aggiorna' : 'Crea'}
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

export default IndirizziPage;
