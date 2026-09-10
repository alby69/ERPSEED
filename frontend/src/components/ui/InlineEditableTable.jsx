import React from 'react';
import { Table, InputNumber, Input, Button, Popconfirm, Space, Typography, Card } from 'antd';
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons';
import ProductLookupInput from './ProductLookupInput';

const { Text } = Typography;

/**
 * InlineEditableTable Component
 *
 * Provides inline editing for order lines (quantity, unit_price, discount_percent, description).
 *
 * @param {Array} value - Array of line items
 * @param {function} onChange - Callback when lines are updated
 * @param {boolean} disabled - Disable editing
 * @param {string} currency - Currency symbol/code (default: 'EUR')
 */
const InlineEditableTable = ({
    value = [],
    onChange,
    disabled = false,
    currency = 'EUR'
}) => {
    const lines = Array.isArray(value) ? value : [];

    const handleLineChange = (index, field, val) => {
        const updated = lines.map((line, i) => {
            if (i !== index) return line;
            const newOrderLine = { ...line, [field]: val };

            if (['quantity', 'unit_price', 'discount_percent'].includes(field)) {
                const qty = Number(newOrderLine.quantity || 0);
                const price = Number(newOrderLine.unit_price || 0);
                const discount = Number(newOrderLine.discount_percent || 0);
                const discountFactor = Math.max(0, 1 - discount / 100);
                newOrderLine.total_price = Number((qty * price * discountFactor).toFixed(2));
            }
            return newOrderLine;
        });

        if (onChange) onChange(updated);
    };

    const handleProductSelect = (index, product) => {
        const updated = lines.map((line, i) => {
            if (i !== index) return line;
            if (!product) {
                return {
                    ...line,
                    product_id: null,
                    description: '',
                    unit_price: 0,
                    total_price: 0
                };
            }

            const qty = Number(line.quantity || 1);
            const price = Number(product.price || product.unit_price || 0);
            const discount = Number(line.discount_percent || 0);
            const discountFactor = Math.max(0, 1 - discount / 100);

            return {
                ...line,
                product_id: product.id,
                description: line.description || product.name || product.description || '',
                quantity: qty,
                unit_price: price,
                total_price: Number((qty * price * discountFactor).toFixed(2))
            };
        });

        if (onChange) onChange(updated);
    };

    const handleAddLine = () => {
        const newLine = {
            id: Date.now(),
            product_id: null,
            description: '',
            quantity: 1,
            unit_price: 0,
            discount_percent: 0,
            tax_id: null,
            total_price: 0
        };
        if (onChange) onChange([...lines, newLine]);
    };

    const handleDeleteLine = (index) => {
        const updated = lines.filter((_, i) => i !== index);
        if (onChange) onChange(updated);
    };

    const subtotal = lines.reduce((acc, l) => acc + (Number(l.quantity || 0) * Number(l.unit_price || 0)), 0);
    const grandTotal = lines.reduce((acc, l) => acc + Number(l.total_price || 0), 0);
    const totalDiscountAmount = subtotal - grandTotal;

    const columns = [
        {
            title: 'Prodotto',
            dataIndex: 'product_id',
            key: 'product_id',
            width: '28%',
            render: (val, record, index) => (
                <ProductLookupInput
                    value={val}
                    onChange={(newVal) => handleLineChange(index, 'product_id', newVal)}
                    onSelectProduct={(prod) => handleProductSelect(index, prod)}
                    disabled={disabled}
                />
            )
        },
        {
            title: 'Descrizione',
            dataIndex: 'description',
            key: 'description',
            width: '24%',
            render: (val, record, index) => (
                <Input
                    value={val}
                    onChange={(e) => handleLineChange(index, 'description', e.target.value)}
                    placeholder="Descrizione riga..."
                    disabled={disabled}
                />
            )
        },
        {
            title: 'Quantità',
            dataIndex: 'quantity',
            key: 'quantity',
            width: '12%',
            render: (val, record, index) => (
                <InputNumber
                    min={0}
                    value={val}
                    onChange={(newVal) => handleLineChange(index, 'quantity', newVal)}
                    style={{ width: '100%' }}
                    disabled={disabled}
                />
            )
        },
        {
            title: 'Prezzo Unitario',
            dataIndex: 'unit_price',
            key: 'unit_price',
            width: '14%',
            render: (val, record, index) => (
                <InputNumber
                    min={0}
                    step={0.01}
                    value={val}
                    onChange={(newVal) => handleLineChange(index, 'unit_price', newVal)}
                    formatter={v => `${v} €`}
                    parser={v => v.replace(' €', '')}
                    style={{ width: '100%' }}
                    disabled={disabled}
                />
            )
        },
        {
            title: 'Sconto %',
            dataIndex: 'discount_percent',
            key: 'discount_percent',
            width: '10%',
            render: (val, record, index) => (
                <InputNumber
                    min={0}
                    max={100}
                    value={val}
                    onChange={(newVal) => handleLineChange(index, 'discount_percent', newVal)}
                    formatter={v => `${v}%`}
                    parser={v => v.replace('%', '')}
                    style={{ width: '100%' }}
                    disabled={disabled}
                />
            )
        },
        {
            title: 'Totale',
            dataIndex: 'total_price',
            key: 'total_price',
            width: '12%',
            render: (val) => (
                <Text strong style={{ color: '#1890ff' }}>
                    € {(Number(val) || 0).toFixed(2)}
                </Text>
            )
        },
        {
            title: '',
            key: 'action',
            width: '5%',
            render: (_, record, index) => !disabled && (
                <Popconfirm title="Rimuovere riga?" onConfirm={() => handleDeleteLine(index)} okText="Sì" cancelText="No">
                    <Button type="text" danger icon={<DeleteOutlined />} />
                </Popconfirm>
            )
        }
    ];

    return (
        <Card size="small" style={{ marginTop: 12 }}>
            <Table
                dataSource={lines}
                columns={columns}
                rowKey={(record, index) => record.id || index}
                pagination={false}
                size="small"
                bordered
                footer={() => (
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        {!disabled ? (
                            <Button type="dashed" onClick={handleAddLine} icon={<PlusOutlined />}>
                                Aggiungi Riga
                            </Button>
                        ) : <div />}
                        <Space size="large">
                            <Text type="secondary">Subtotale: € {subtotal.toFixed(2)}</Text>
                            {totalDiscountAmount > 0 && (
                                <Text type="danger">Sconto Totale: -€ {totalDiscountAmount.toFixed(2)}</Text>
                            )}
                            <Text strong style={{ fontSize: 16 }}>
                                Totale Ordine ({currency}): € {grandTotal.toFixed(2)}
                            </Text>
                        </Space>
                    </div>
                )}
            />
        </Card>
    );
};

export default InlineEditableTable;
