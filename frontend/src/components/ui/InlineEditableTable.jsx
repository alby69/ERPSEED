import React, { useEffect, useRef } from 'react';
import { Table, InputNumber, Input, Button, Popconfirm, Space, Typography, Card } from 'antd';
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons';
import { z } from 'zod';
import { useForm, useFieldArray, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import ProductLookupInput from './ProductLookupInput';

const { Text } = Typography;

// Zod schema for individual order line item
export const orderLineSchema = z.object({
  id: z.any().optional(),
  product_id: z.number().nullable().optional(),
  description: z.string().optional(),
  quantity: z.number().min(0, 'La quantità non può essere negativa'),
  unit_price: z.number().min(0, 'Il prezzo unitario non può essere negativo'),
  discount_percent: z.number().min(0, 'Sconto minimo 0%').max(100, 'Sconto massimo 100%'),
  tax_id: z.number().nullable().optional(),
  total_price: z.number().optional()
});

// Zod schema for lines container form
export const orderLinesFormSchema = z.object({
  lines: z.array(orderLineSchema)
});

/**
 * InlineEditableTable Component
 *
 * Provides high-performance inline editing for order lines (quantity, unit_price, discount_percent, description)
 * powered by React Hook Form & Zod schema validation.
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
  const initialLines = Array.isArray(value) ? value : [];
  const isLocalChangeRef = useRef(false);

  const { control, watch, setValue, reset, formState: { errors } } = useForm({
    resolver: zodResolver(orderLinesFormSchema),
    defaultValues: { lines: initialLines },
    mode: 'onChange'
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'lines'
  });

  // Only reset form state when value changes externally, not on local edits
  useEffect(() => {
    if (isLocalChangeRef.current) {
      isLocalChangeRef.current = false;
      return;
    }
    reset({ lines: Array.isArray(value) ? value : [] });
  }, [value, reset]);

  const watchedLines = watch('lines') || [];

  const notifyChange = (updatedLines) => {
    isLocalChangeRef.current = true;
    if (onChange) {
      onChange(updatedLines);
    }
  };

  const handleLineFieldChange = (index, field, newVal) => {
    const currentLine = watchedLines[index] || {};
    const updatedLine = { ...currentLine, [field]: newVal };

    if (['quantity', 'unit_price', 'discount_percent'].includes(field)) {
      const qty = Number(updatedLine.quantity || 0);
      const price = Number(updatedLine.unit_price || 0);
      const discount = Number(updatedLine.discount_percent || 0);
      const discountFactor = Math.max(0, 1 - discount / 100);
      updatedLine.total_price = Number((qty * price * discountFactor).toFixed(2));
    }

    const newLines = watchedLines.map((line, i) => (i === index ? updatedLine : line));
    setValue(`lines.${index}`, updatedLine);
    notifyChange(newLines);
  };

  const handleProductSelect = (index, product) => {
    const currentLine = watchedLines[index] || {};
    let updatedLine;

    if (!product) {
      updatedLine = {
        ...currentLine,
        product_id: null,
        description: '',
        unit_price: 0,
        total_price: 0
      };
    } else {
      const qty = Number(currentLine.quantity || 1);
      const price = Number(product.price || product.unit_price || 0);
      const discount = Number(currentLine.discount_percent || 0);
      const discountFactor = Math.max(0, 1 - discount / 100);

      updatedLine = {
        ...currentLine,
        product_id: product.id,
        description: currentLine.description || product.name || product.description || '',
        quantity: qty,
        unit_price: price,
        total_price: Number((qty * price * discountFactor).toFixed(2))
      };
    }

    const newLines = watchedLines.map((line, i) => (i === index ? updatedLine : line));
    setValue(`lines.${index}`, updatedLine);
    notifyChange(newLines);
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
    append(newLine);
    const updated = [...watchedLines, newLine];
    notifyChange(updated);
  };

  const handleDeleteLine = (index) => {
    remove(index);
    const updated = watchedLines.filter((_, i) => i !== index);
    notifyChange(updated);
  };

  const subtotal = watchedLines.reduce((acc, l) => acc + (Number(l?.quantity || 0) * Number(l?.unit_price || 0)), 0);
  const grandTotal = watchedLines.reduce((acc, l) => acc + Number(l?.total_price || 0), 0);
  const totalDiscountAmount = subtotal - grandTotal;

  // Use fields from useFieldArray for stable key identity
  const dataSource = fields.map((fieldItem, index) => ({
    ...fieldItem,
    ...(watchedLines[index] || {})
  }));

  const columns = [
    {
      title: 'Prodotto',
      dataIndex: 'product_id',
      key: 'product_id',
      width: '28%',
      render: (val, record, index) => (
        <Controller
          name={`lines.${index}.product_id`}
          control={control}
          render={({ field }) => (
            <ProductLookupInput
              value={field.value}
              onChange={(newVal) => handleLineFieldChange(index, 'product_id', newVal)}
              onSelectProduct={(prod) => handleProductSelect(index, prod)}
              disabled={disabled}
            />
          )}
        />
      )
    },
    {
      title: 'Descrizione',
      dataIndex: 'description',
      key: 'description',
      width: '24%',
      render: (val, record, index) => (
        <Controller
          name={`lines.${index}.description`}
          control={control}
          render={({ field }) => (
            <div>
              <Input
                value={field.value || ''}
                onChange={(e) => handleLineFieldChange(index, 'description', e.target.value)}
                placeholder="Descrizione riga..."
                disabled={disabled}
                status={errors?.lines?.[index]?.description ? 'error' : ''}
              />
              {errors?.lines?.[index]?.description && (
                <Text type="danger" style={{ fontSize: 11 }}>
                  {errors.lines[index].description.message}
                </Text>
              )}
            </div>
          )}
        />
      )
    },
    {
      title: 'Quantità',
      dataIndex: 'quantity',
      key: 'quantity',
      width: '12%',
      render: (val, record, index) => (
        <Controller
          name={`lines.${index}.quantity`}
          control={control}
          render={({ field }) => (
            <div>
              <InputNumber
                min={0}
                value={field.value}
                onChange={(newVal) => handleLineFieldChange(index, 'quantity', newVal)}
                style={{ width: '100%' }}
                disabled={disabled}
                status={errors?.lines?.[index]?.quantity ? 'error' : ''}
              />
              {errors?.lines?.[index]?.quantity && (
                <Text type="danger" style={{ fontSize: 11 }}>
                  {errors.lines[index].quantity.message}
                </Text>
              )}
            </div>
          )}
        />
      )
    },
    {
      title: 'Prezzo Unitario',
      dataIndex: 'unit_price',
      key: 'unit_price',
      width: '14%',
      render: (val, record, index) => (
        <Controller
          name={`lines.${index}.unit_price`}
          control={control}
          render={({ field }) => (
            <div>
              <InputNumber
                min={0}
                step={0.01}
                value={field.value}
                onChange={(newVal) => handleLineFieldChange(index, 'unit_price', newVal)}
                formatter={v => `${v} €`}
                parser={v => v.replace(' €', '')}
                style={{ width: '100%' }}
                disabled={disabled}
                status={errors?.lines?.[index]?.unit_price ? 'error' : ''}
              />
              {errors?.lines?.[index]?.unit_price && (
                <Text type="danger" style={{ fontSize: 11 }}>
                  {errors.lines[index].unit_price.message}
                </Text>
              )}
            </div>
          )}
        />
      )
    },
    {
      title: 'Sconto %',
      dataIndex: 'discount_percent',
      key: 'discount_percent',
      width: '10%',
      render: (val, record, index) => (
        <Controller
          name={`lines.${index}.discount_percent`}
          control={control}
          render={({ field }) => (
            <div>
              <InputNumber
                min={0}
                max={100}
                value={field.value}
                onChange={(newVal) => handleLineFieldChange(index, 'discount_percent', newVal)}
                formatter={v => `${v}%`}
                parser={v => v.replace('%', '')}
                style={{ width: '100%' }}
                disabled={disabled}
                status={errors?.lines?.[index]?.discount_percent ? 'error' : ''}
              />
              {errors?.lines?.[index]?.discount_percent && (
                <Text type="danger" style={{ fontSize: 11 }}>
                  {errors.lines[index].discount_percent.message}
                </Text>
              )}
            </div>
          )}
        />
      )
    },
    {
      title: 'Totale',
      dataIndex: 'total_price',
      key: 'total_price',
      width: '12%',
      render: (val, record, index) => {
        const total = watchedLines[index]?.total_price ?? val;
        return (
          <Text strong style={{ color: '#1890ff' }}>
            € {(Number(total) || 0).toFixed(2)}
          </Text>
        );
      }
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
        dataSource={dataSource}
        columns={columns}
        rowKey={(record) => record.id}
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
