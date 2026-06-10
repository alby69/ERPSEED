import React, { useState, useEffect, useCallback } from 'react';
import {
  Card, Table, Button, Modal, Form, Input, Select, Tag, Space, message, Popconfirm, Row, Col, Divider, AutoComplete
} from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, EnvironmentOutlined, CaretUpOutlined, CaretDownOutlined, SettingOutlined } from '@ant-design/icons';
import { apiFetch } from '../utils';
import { useTableSort } from '../hooks/useTableSort';
import { useColumnManager } from '../hooks/useColumnManager';
import TableSearch from '../components/TableSearch';
import Layout from '../components/Layout';
import HelpDrawer from '@/components/HelpDrawer';
import ColumnSettingsDrawer from '@/components/ColumnSettingsDrawer';

const { Option } = Select;

export default function IndirizziPage() {
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

  const [columnSettingsOpen, setColumnSettingsOpen] = useState(false);

  // Stati per ricerca città e vie
  const [searchResults, setSearchResults] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [selectedComuneId, setSelectedComuneId] = useState(null);
  const [viaResults, setViaResults] = useState([]);
  const [viaLoading, setViaLoading] = useState(false);
  const [cittaText, setCittaText] = useState('');

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

  const cercaComuni = useCallback(async (testo) => {
    if (!testo) {
      setSearchResults([]);
      return;
    }
    setSearchLoading(true);
    try {
      const response = await apiFetch(`/api/v1/comuni?q=${encodeURIComponent(testo)}&per_page=20`);
      if (response.ok) {
        const data = await response.json();
        setSearchResults(Array.isArray(data) ? data : (data.items || []));
      }
    } catch (error) {
      console.error('Errore nella ricerca comuni:', error);
    } finally {
      setSearchLoading(false);
    }
  }, []);

  const cercaVia = useCallback(async (testo) => {
    if (!testo || testo.length < 2 || !selectedComuneId) {
      if (!testo || testo.length < 2) setViaResults([]);
      return;
    }
    setViaLoading(true);
    try {
      const response = await apiFetch(`/api/v1/vie/?comune_id=${selectedComuneId}&q=${encodeURIComponent(testo)}`);
      if (response.ok) {
        const data = await response.json();
        setViaResults(data || []);
      }
    } catch (error) {
      console.error('Errore nella ricerca vie:', error);
    } finally {
      setViaLoading(false);
    }
  }, [selectedComuneId]);

  useEffect(() => {
    fetchData();
    fetchSoggetti();
  }, [fetchData, fetchSoggetti]);

  const handleCreate = () => {
    setEditingIndirizzo(null);
    setSelectedComuneId(null);
    setViaResults([]);
    setCittaText('');
    setSearchResults([]);
    form.resetFields();
    form.setFieldsValue({ nazione: 'IT' });
    setModalVisible(true);
  };

  const handleEdit = (record) => {
    setEditingIndirizzo(record);
    setSelectedComuneId(record.comune_id || null);
    setViaResults([]);
    setCittaText(record.città || '');
    setSearchResults([]);
    form.setFieldsValue({
      ...record,
      cap: record.CAP,
    });
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

  const handleComuneSelect = (value, option) => {
    const comune = option.comuneData;
    if (comune) {
      setCittaText(comune.nome);
      form.setFieldsValue({
        città: comune.nome,
        comune_id: comune.id,
        cap: comune.cap,
        provincia: comune.codice_provincia,
        regione: comune.codice_regione,
        latitudine: comune.latitudine,
        longitudine: comune.longitudine,
        denominazione: undefined,
        via_id: undefined,
      });
      setSelectedComuneId(comune.id);
      setViaResults([]);
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

  const rawColumns = [
    {
      title: 'Cod. Soggetto',
      key: 'codice_soggetto',
      width: 100,
      render: (_, record) => record.soggetto?.codice || '-',
    },
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
      dataIndex: 'città',
      key: 'città',
    },
    {
      title: sortableHeader('Via', 'denominazione'),
      dataIndex: 'denominazione',
      key: 'via',
      render: (val) => val || '-',
    },
    {
      title: sortableHeader('Regione', 'regione'),
      dataIndex: 'regione_nome',
      key: 'regione',
      render: (val) => val || '-',
    },
    {
      title: sortableHeader('Provincia', 'provincia'),
      dataIndex: 'provincia_nome',
      key: 'provincia',
      render: (val) => val || '-',
    },
    {
      title: sortableHeader('Nazione', 'nazione'),
      dataIndex: 'nazione',
      key: 'nazione',
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

  const {
    processedColumns,
    allColumns,
    toggleColumn,
    moveColumn,
    resetColumns,
    hasChanges,
  } = useColumnManager('indirizzi', rawColumns);

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
              <HelpDrawer moduleName="indirizzi" moduleTitle="Guida Indirizzi" />
            </Space>
          }
          extra={
            <Space>
              <Button icon={<SettingOutlined />} onClick={() => setColumnSettingsOpen(true)}>
                Colonne
              </Button>
              <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
                Nuovo Indirizzo
              </Button>
            </Space>
          }
        >
        <div className="mb-3">
          <TableSearch
            columns={processedColumns}
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
          columns={processedColumns}
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
            <Select showSearch placeholder="Cerca soggetto" getPopupContainer={(trigger) => trigger.closest('.ant-modal-content') || document.body}>
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
                <Select>
                  <Option value={true}>Sì</Option>
                  <Option value={false}>No</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Divider>Città e Indirizzo</Divider>

          <Form.Item name="città" label="Città" rules={[{ required: true }]}>
            <AutoComplete
              value={cittaText}
              placeholder="Cerca città o comune..."
              onSearch={cercaComuni}
              onSelect={(value, option) => {
                handleComuneSelect(value, option);
              }}
              onChange={(value) => setCittaText(value)}
              notFoundContent={searchLoading ? "Ricerca in corso..." : "Nessun comune trovato"}
              getPopupContainer={(trigger) => trigger.closest('.ant-modal-content') || document.body}
              options={searchResults.map(r => ({
                value: r.nome,
                label: `${r.nome} (${r.codice_provincia})`,
                comuneData: r
              }))}
            />
          </Form.Item>

          <Row gutter={16}>
            <Col span={16}>
          <Form.Item name="denominazione" label="Via / Piazza">
            <Select
              showSearch
              placeholder={selectedComuneId ? "Inizia a digitare il nome della via..." : "Seleziona prima una città"}
              loading={viaLoading}
              onSearch={cercaVia}
              onSelect={(value) => {
                const found = viaResults.find(r => r.nome === value);
                if (found) form.setFieldsValue({ denominazione: value, via_id: found.id });
              }}
              filterOption={false}
              notFoundContent={null}
              disabled={!selectedComuneId}
              getPopupContainer={(trigger) => trigger.closest('.ant-modal-content') || document.body}
              options={viaResults.map(r => ({ value: r.nome, label: r.nome }))}
            />
          </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="numero_civico" label="N. Civico">
                <Input placeholder="1" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="cap" hidden><Input /></Form.Item>
          <Form.Item name="nazione" hidden initialValue="IT"><Input /></Form.Item>
          <Form.Item name="regione" hidden><Input /></Form.Item>
          <Form.Item name="provincia" hidden><Input /></Form.Item>
          <Form.Item name="comune_id" hidden><Input /></Form.Item>
          <Form.Item name="via_id" hidden><Input /></Form.Item>
          <Form.Item name="latitudine" hidden><Input /></Form.Item>
          <Form.Item name="longitudine" hidden><Input /></Form.Item>

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

      <ColumnSettingsDrawer
        open={columnSettingsOpen}
        onClose={() => setColumnSettingsOpen(false)}
        columns={allColumns}
        onToggle={toggleColumn}
        onMoveUp={(key) => moveColumn(key, -1)}
        onMoveDown={(key) => moveColumn(key, 1)}
        onReset={resetColumns}
        hasChanges={hasChanges}
      />
      </div>
    </Layout>
  );
};
