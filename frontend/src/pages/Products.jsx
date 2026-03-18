import React, { useState, useEffect } from 'react';
import { Table, Spin, Alert, Button, Typography, Space } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { apiClient } from './api';



function Products() {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [pagination, setPagination] = useState({
        current: 1,
        pageSize: 10,
        total: 0,
    });

    const navigate = useNavigate();

    const fetchProducts = async (page = 1, pageSize = 10) => {
        setLoading(true);
        setError(null);
        try {
            const data = await apiClient.get(`/api/v1/products?page=${page}&per_page=${pageSize}`);
            setProducts(data.items);
            setPagination({
                current: data.pagination.page,
                pageSize: data.pagination.per_page,
                total: data.pagination.total,
            });
        } catch (err) {
            setError(err.message || 'Failed to fetch products. The backend service might be down.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchProducts(pagination.current, pagination.pageSize);
    }, []); // Removed token dependency

    const handleTableChange = (pagination) => {
        fetchProducts(pagination.current, pagination.pageSize);
    };

    const columns = [
        { title: 'Name', dataIndex: 'name', key: 'name' },
        { title: 'Code', dataIndex: 'code', key: 'code' },
        { title: 'Unit Price', dataIndex: 'unit_price', key: 'unit_price', render: (price) => `$${(price || 0).toFixed(2)}` },
        { title: 'Stock', dataIndex: 'stock_quantity', key: 'stock_quantity' },
        {
            title: 'Actions',
            key: 'actions',
            render: (text, record) => (
                <span>
                    <Button type="link" onClick={() => navigate(`/products/${record.id}`)}>Edit</Button>
                    <Button type="link" danger>Delete</Button>
                </span>
            ),
        },
    ];

    if (loading && !error) {
        return <div className="p-5 text-center"><Spin size="large" /></div>;
    }

  return (
    <>
      <div style={{ padding: 24, background: '#fff', borderBottom: '1px solid #f0f0f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
            <Typography.Title level={4} style={{ margin: 0 }}>Products</Typography.Title>
            <Typography.Text type="secondary">Manage your product catalog</Typography.Text>
        </div>
        <Space>
            <Button key="1" type="primary" icon={<PlusOutlined />} onClick={() => navigate('/products/new')}>
                Create Product
            </Button>
        </Space>
      </div>
      <div style={{ padding: 24 }}>
        {error && <Alert message="Error" description={error} type="error" showIcon className="mb-4" />}
        <Table dataSource={products} columns={columns} rowKey="id" pagination={pagination} loading={loading} onChange={handleTableChange} />
      </div>
    </>
  );
}

export default Products;
