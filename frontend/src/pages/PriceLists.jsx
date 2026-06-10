import React, { useState, useEffect, useCallback } from 'react';
import { Card, Table, Button, Modal, Form, Input, InputNumber, Switch, Select, Space, Tag, Popconfirm, message, Tabs, Divider } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, DollarOutlined } from '@ant-design/icons';
import { apiFetch } from '@/utils';
import { useColumnManagerWithDrawer } from '@/hooks/useColumnManager';
import ColumnSettingsButton from '@/components/ColumnSettingsButton';

const PriceListItems = ({ listId, visible, onClose }) => {
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(false);
    const [products, setProducts] = useState([]);
    const [addModalVisible, setAddModalVisible] = useState(false);
    const [editingItem, setEditingItem] = useState(null);
    const [form] = Form.useForm();

    const fetchItems = useCallback(async () => {
        if (!listId) return;
        setLoading(true);
        try {
            const res = await apiFetch(`/api/v1/price-lists/${listId}/items`);
            if (res.ok) setItems(await res.json());
        } catch { message.error('Error loading items'); }
        finally { setLoading(false); }
    }, [listId]);

    const fetchProducts = useCallback(async () => {
        try {
            const res = await apiFetch('/api/v1/products?per_page=200');
            if (res.ok) {
                const data = await res.json();
                setProducts(data.items || []);
            }
        } catch {}
    }, []);

    useEffect(() => { if (visible) { fetchItems(); fetchProducts(); } }, [visible, fetchItems, fetchProducts]);

    const handleSubmit = async () => {
        try {
            const values = await form.validateFields();
            let res;
            if (editingItem) {
                res = await apiFetch(`/api/v1/price-lists/${listId}/items/${editingItem.id}`, { method: 'PUT', body: JSON.stringify(values) });
            } else {
                res = await apiFetch(`/api/v1/price-lists/${listId}/items`, { method: 'POST', body: JSON.stringify(values) });
            }
            if (res.ok) {
                message.success(editingItem ? 'Item updated' : 'Item added');
                setAddModalVisible(false); form.resetFields(); setEditingItem(null); fetchItems();
            } else {
                const err = await res.json();
                message.error(err.message || 'Operation failed');
            }
        } catch (err) {
            if (err.errorFields) return;
            message.error('Validation failed');
        }
    };

    const handleDelete = async (itemId) => {
        try {
            const res = await apiFetch(`/api/v1/price-lists/${listId}/items/${itemId}`, { method: 'DELETE' });
            if (res.ok) { message.success('Item removed'); fetchItems(); }
        } catch { message.error('Error deleting item'); }
    };

    const columns = [
        { title: 'Prodotto', dataIndex: 'product_id', key: 'product_id', render: (pid) => { const p = products.find(pr => pr.id === pid); return p ? `${p.code} - ${p.name}` : `ID: ${pid}`; } },
        { title: 'Prezzo', dataIndex: 'price', key: 'price', render: (v) => `€ ${v?.toFixed(2)}` },
        { title: 'Sconto Max %', dataIndex: 'max_discount', key: 'max_discount', render: (v) => v ? `${v}%` : '-' },
        { title: 'Q.tà Minima', dataIndex: 'min_quantity', key: 'min_quantity', render: (v) => v || '-' },
        { title: 'Azioni', key: 'actions', render: (_, r) => (
            <Space>
                <Button type="link" icon={<EditOutlined />} onClick={() => { setEditingItem(r); form.setFieldsValue(r); setAddModalVisible(true); }} />
                <Popconfirm title="Rimuovere questo item?" onConfirm={() => handleDelete(r.id)}>
                    <Button type="link" danger icon={<DeleteOutlined />} />
                </Popconfirm>
            </Space>
        )},
    ];

    return (
        <Modal title="Prezzi di Listino" open={visible} onCancel={onClose} footer={null} width={800}>
            <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditingItem(null); form.resetFields(); setAddModalVisible(true); }} style={{ marginBottom: 16 }}>Aggiungi Prodotto</Button>
            <Table dataSource={items} columns={columns} rowKey="id" loading={loading} size="small" />
            <Modal title={editingItem ? 'Modifica Prezzo' : 'Aggiungi Prodotto al Listino'} open={addModalVisible}
                onOk={handleSubmit} onCancel={() => { setAddModalVisible(false); form.resetFields(); setEditingItem(null); }}
                okText="Salva" cancelText="Annulla">
                <Form form={form} layout="vertical">
                    {!editingItem && (
                        <Form.Item name="product_id" label="Prodotto" rules={[{ required: true }]}>
                            <Select showSearch placeholder="Seleziona prodotto" optionFilterProp="label"
                                options={products.filter(p => !items.find(i => i.product_id === p.id)).map(p => ({ value: p.id, label: `${p.code || ''} - ${p.name}` }))} />
                        </Form.Item>
                    )}
                    <Form.Item name="price" label="Prezzo" rules={[{ required: true }]}>
                        <InputNumber min={0} step={0.01} prefix="€" style={{ width: '100%' }} />
                    </Form.Item>
                    <Form.Item name="max_discount" label="Sconto Massimo %">
                        <InputNumber min={0} max={100} step={0.5} style={{ width: '100%' }} />
                    </Form.Item>
                    <Form.Item name="min_quantity" label="Quantità Minima">
                        <InputNumber min={0} step={1} style={{ width: '100%' }} />
                    </Form.Item>
                </Form>
            </Modal>
        </Modal>
    );
};

export default function PriceLists() {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [modalVisible, setModalVisible] = useState(false);
    const [itemsModalVisible, setItemsModalVisible] = useState(false);
    const [selectedListId, setSelectedListId] = useState(null);
    const [editingRecord, setEditingRecord] = useState(null);
    const [form] = Form.useForm();

    const fetchData = useCallback(async () => {
        setLoading(true);
        try {
            const res = await apiFetch('/api/v1/price-lists');
            if (res.ok) setData(await res.json());
        } catch { message.error('Error loading price lists'); }
        finally { setLoading(false); }
    }, []);

    useEffect(() => { fetchData(); }, [fetchData]);

    const handleSubmit = async () => {
        try {
            const values = await form.validateFields();
            let res;
            if (editingRecord) {
                res = await apiFetch(`/api/v1/price-lists/${editingRecord.id}`, { method: 'PUT', body: JSON.stringify(values) });
            } else {
                res = await apiFetch('/api/v1/price-lists', { method: 'POST', body: JSON.stringify(values) });
            }
            if (res.ok) {
                message.success(editingRecord ? 'Updated' : 'Created');
                setModalVisible(false); form.resetFields(); setEditingRecord(null); fetchData();
            } else {
                const err = await res.json();
                message.error(err.message || 'Operation failed');
            }
        } catch (err) {
            if (err.errorFields) return;
            message.error('Validation failed');
        }
    };

    const handleDelete = async (id) => {
        try {
            const res = await apiFetch(`/api/v1/price-lists/${id}`, { method: 'DELETE' });
            if (res.ok) { message.success('Deleted'); fetchData(); }
        } catch { message.error('Error deleting'); }
    };

    const rawColumns = [
        { title: 'Codice', dataIndex: 'code', key: 'code', width: 120 },
        { title: 'Nome', dataIndex: 'name', key: 'name' },
        { title: 'Valuta', dataIndex: 'currency', key: 'currency', width: 80 },
        { title: 'Prodotti', dataIndex: 'items_count', key: 'items_count', width: 100 },
        { title: 'Attivo', dataIndex: 'is_active', key: 'is_active', width: 80, render: (v) => <Tag color={v ? 'green' : 'red'}>{v ? 'Sì' : 'No'}</Tag> },
        { title: 'Azioni', key: 'actions', width: 200, render: (_, r) => (
            <Space>
                <Button type="link" icon={<DollarOutlined />} onClick={() => { setSelectedListId(r.id); setItemsModalVisible(true); }}>Prezzi</Button>
                <Button type="link" icon={<EditOutlined />} onClick={() => { setEditingRecord(r); form.setFieldsValue(r); setModalVisible(true); }} />
                <Popconfirm title="Eliminare listino?" onConfirm={() => handleDelete(r.id)}>
                    <Button type="link" danger icon={<DeleteOutlined />} />
                </Popconfirm>
            </Space>
        )},
    ];

    const colManager = useColumnManagerWithDrawer('pricelists', rawColumns);

    return (
        <div style={{ padding: 24 }}>
            <Card title="Listini Prezzo" extra={<Space><ColumnSettingsButton manager={colManager} /><Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditingRecord(null); form.resetFields(); setModalVisible(true); }}>Nuovo Listino</Button></Space>}>
                <Table dataSource={data} columns={colManager.processedColumns} rowKey="id" loading={loading} />
            </Card>
            <Modal title={editingRecord ? 'Modifica Listino' : 'Nuovo Listino'} open={modalVisible}
                onOk={handleSubmit} onCancel={() => { setModalVisible(false); form.resetFields(); setEditingRecord(null); }}
                okText="Salva" cancelText="Annulla">
                <Form form={form} layout="vertical">
                    <Form.Item name="code" label="Codice" rules={[{ required: true }]}><Input placeholder="es. LISTINO_BASE" /></Form.Item>
                    <Form.Item name="name" label="Nome" rules={[{ required: true }]}><Input placeholder="es. Listino Base" /></Form.Item>
                    <Form.Item name="currency" label="Valuta"><Input placeholder="EUR" /></Form.Item>
                    <Form.Item name="description" label="Descrizione"><Input.TextArea rows={2} /></Form.Item>
                    <Form.Item name="is_active" label="Attivo" valuePropName="checked"><Switch defaultChecked /></Form.Item>
                </Form>
            </Modal>
            <PriceListItems listId={selectedListId} visible={itemsModalVisible} onClose={() => { setItemsModalVisible(false); setSelectedListId(null); fetchData(); }} />
        </div>
    );
};
