import React, { useState, useEffect } from 'react';
import { Table, Spin, Alert, Button, Tag, Typography, Space } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { apiClient } from './api';

function Sales() {
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 });

    const navigate = useNavigate();

    const fetchOrders = async (page = 1, pageSize = 10) => {
        setLoading(true);
        setError(null);
        try {
            const data = await apiClient.get(`/api/v1/sales/orders?page=${page}&per_page=${pageSize}`);
            setOrders(data.items);
            setPagination({
                current: data.pagination.page,
                pageSize: data.pagination.per_page,
                total: data.pagination.total,
            });
        } catch (err) {
            setError(err.message || 'Failed to fetch sales orders. The backend service might be down.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchOrders(pagination.current, pagination.pageSize);
    }, []); // Removed token dependency

    const handleTableChange = (pagination) => {
        fetchOrders(pagination.current, pagination.pageSize);
    };

    const getStatusColor = (status) => {
        const lowerStatus = status?.toLowerCase() || '';
        if (lowerStatus.includes('confirm')) return 'processing';
        if (lowerStatus.includes('complete')) return 'success';
        if (lowerStatus.includes('cancel')) return 'error';
        return 'default';
    };

    const columns = [
        { title: 'Order Number', dataIndex: 'order_number', key: 'order_number' },
        { title: 'Customer', dataIndex: 'customer_name', key: 'customer_name', render: (text, record) => record.customer?.name || 'N/A' },
        { title: 'Order Date', dataIndex: 'order_date', key: 'order_date', render: (date) => new Date(date).toLocaleDateString() },
        { title: 'Total', dataIndex: 'total_amount', key: 'total_amount', render: (amount) => `$${(amount || 0).toFixed(2)}` },
        { title: 'Status', dataIndex: 'status', key: 'status', render: (status) => <Tag color={getStatusColor(status)}>{status?.toUpperCase()}</Tag> },
        { title: 'Actions', key: 'actions', render: (text, record) => (<Button type="link" onClick={() => navigate(`/sales/${record.id}`)}>View Details</Button>) },
    ];

    if (loading && !error) {
        return <div className="p-5 text-center"><Spin size="large" /></div>;
    }

  return (
    <>
      <div style={{ padding: 24, background: '#fff', borderBottom: '1px solid #f0f0f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
            <Typography.Title level={4} style={{ margin: 0 }}>Sales Orders</Typography.Title>
            <Typography.Text type="secondary">Manage all sales orders</Typography.Text>
        </div>
        <Space>
            <Button key="1" type="primary" icon={<PlusOutlined />} onClick={() => navigate('/sales/new')}>
                New Sales Order
            </Button>
        </Space>
      </div>
      <div style={{ padding: 24 }}>
        {error && <Alert message="Error" description={error} type="error" showIcon className="mb-4" />}
        <Table dataSource={orders} columns={columns} rowKey="id" pagination={pagination} loading={loading} onChange={handleTableChange} />
      </div>
    </>
  );
}

export default Sales;
