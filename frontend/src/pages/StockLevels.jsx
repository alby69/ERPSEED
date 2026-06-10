import React, { useState, useEffect, useCallback } from 'react';
import { Card, Table, Input, Select, Space, Tag, message } from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import { apiFetch } from '@/utils';
import { useColumnManagerWithDrawer } from '@/hooks/useColumnManager';
import Layout from '../components/Layout';
import ColumnSettingsButton from '@/components/ColumnSettingsButton';

const StockLevels = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [products, setProducts] = useState([]);
    const [locations, setLocations] = useState([]);
    const [search, setSearch] = useState('');
    const [locationFilter, setLocationFilter] = useState(null);

    const fetchData = useCallback(async () => {
        setLoading(true);
        try {
            const res = await apiFetch('/inventory/stock');
            if (res.ok) setData(await res.json());
        } catch { message.error('Error loading stock levels'); }
        finally { setLoading(false); }
    }, []);

    const fetchLookups = useCallback(async () => {
        try {
            const [pRes, lRes] = await Promise.all([
                apiFetch('/api/v1/products?per_page=500'),
                apiFetch('/inventory/locations'),
            ]);
            if (pRes.ok) { const j = await pRes.json(); setProducts(j.items || []); }
            if (lRes.ok) setLocations(await lRes.json());
        } catch {}
    }, []);

    useEffect(() => { fetchData(); fetchLookups(); }, [fetchData, fetchLookups]);

    const getProductName = (id) => {
        const p = products.find(x => x.id === id);
        return p ? `${p.code || ''} - ${p.name}` : `ID: ${id}`;
    };

    const filtered = data.filter(item => {
        if (search) {
            const name = getProductName(item.product_id).toLowerCase();
            if (!name.includes(search.toLowerCase())) return false;
        }
        if (locationFilter && item.location_id !== locationFilter) return false;
        return true;
    });

    const rawColumns = [
        { title: 'Prodotto', dataIndex: 'product_id', key: 'product_id', render: (id) => getProductName(id) },
        { title: 'Ubicazione', dataIndex: 'location_id', key: 'location_id', render: (id) => { const l = locations.find(x => x.id === id); return l ? l.name : `ID: ${id}`; } },
        { title: 'Quantità', dataIndex: 'quantity', key: 'quantity', render: (v) => <span style={{ fontWeight: 600, fontSize: 16 }}>{v || 0}</span> },
        { title: 'Prenotata', dataIndex: 'reserved_quantity', key: 'reserved_quantity', render: (v) => v || 0 },
        { title: 'Disponibile', dataIndex: 'available_quantity', key: 'available_quantity', render: (v, r) => {
            const avail = v ?? (r.quantity || 0) - (r.reserved_quantity || 0);
            const color = avail <= 0 ? 'red' : avail < 10 ? 'orange' : 'green';
            return <Tag color={color}>{avail}</Tag>;
        }},
        { title: 'Livello Riordino', dataIndex: 'reorder_level', key: 'reorder_level', render: (v) => v || '-' },
        { title: 'Ultima Rilevazione', dataIndex: 'last_counted_at', key: 'last_counted_at', render: (v) => v ? new Date(v).toLocaleDateString() : '-' },
    ];

    const colManager = useColumnManagerWithDrawer('stock_levels', rawColumns);

    return (
        <Layout>
            <div style={{ padding: 24 }}>
                <Card title="Magazzino (Giacenze)" extra={<ColumnSettingsButton manager={colManager} />}>
                    <Space style={{ marginBottom: 16 }}>
                        <Input placeholder="Cerca prodotto..." prefix={<SearchOutlined />} value={search} onChange={(e) => setSearch(e.target.value)} style={{ width: 300 }} allowClear />
                        <Select allowClear placeholder="Filtra ubicazione" style={{ width: 200 }} value={locationFilter} onChange={setLocationFilter}
                            options={locations.map(l => ({ value: l.id, label: l.name }))} />
                    </Space>
                    <Table dataSource={filtered} columns={colManager.processedColumns} rowKey={(r) => `${r.product_id}-${r.location_id}`} loading={loading} />
                </Card>
            </div>
        </Layout>
    );
};

export default StockLevels;
