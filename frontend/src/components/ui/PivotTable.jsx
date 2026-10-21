import React, { useState, useMemo } from 'react';
import { Table, Select, Flex, Card, Typography, Space } from 'antd';

const { Text } = Typography;

export default function PivotTable({
  data = [],
  rowFields = [],
  colFields = [],
  valField = '',
  aggFunc = 'sum', // 'sum', 'count', 'avg'
}) {
  const [selectedRowField, setSelectedRowField] = useState(rowFields[0] || '');
  const [selectedColField, setSelectedColField] = useState(colFields[0] || '');
  const [selectedValField, setSelectedValField] = useState(valField || '');

  const pivotData = useMemo(() => {
    if (!data.length || !selectedRowField || !selectedColField || !selectedValField) {
      return { columns: [], dataSource: [] };
    }

    const colKeys = Array.from(new Set(data.map((item) => String(item[selectedColField] ?? 'Altro')))).sort();
    const rowKeys = Array.from(new Set(data.map((item) => String(item[selectedRowField] ?? 'Altro')))).sort();

    const matrix = {};
    rowKeys.forEach((r) => {
      matrix[r] = {};
      colKeys.forEach((c) => {
        matrix[r][c] = [];
      });
    });

    data.forEach((item) => {
      const rVal = String(item[selectedRowField] ?? 'Altro');
      const cVal = String(item[selectedColField] ?? 'Altro');
      const val = Number(item[selectedValField]) || 0;
      if (matrix[rVal] && matrix[rVal][cVal]) {
        matrix[rVal][cVal].push(val);
      }
    });

    const columns = [
      {
        title: selectedRowField.toUpperCase(),
        dataIndex: 'rowKey',
        key: 'rowKey',
        fixed: 'left',
      },
      ...colKeys.map((c) => ({
        title: c,
        dataIndex: c,
        key: c,
        align: 'right',
        render: (val) => (val !== undefined ? val.toFixed(2) : '0.00'),
      })),
    ];

    const dataSource = rowKeys.map((r) => {
      const rowObj = { key: r, rowKey: r };
      colKeys.forEach((c) => {
        const arr = matrix[r][c];
        let computed = 0;
        if (arr.length > 0) {
          if (aggFunc === 'sum') computed = arr.reduce((a, b) => a + b, 0);
          else if (aggFunc === 'count') computed = arr.length;
          else if (aggFunc === 'avg') computed = arr.reduce((a, b) => a + b, 0) / arr.length;
        }
        rowObj[c] = computed;
      });
      return rowObj;
    });

    return { columns, dataSource };
  }, [data, selectedRowField, selectedColField, selectedValField, aggFunc]);

  return (
    <Card size="small" style={{ marginBottom: 16 }}>
      <Flex gap="middle" align="center" style={{ marginBottom: 16 }} wrap>
        <Space>
          <Text bold>Righe:</Text>
          <Select
            value={selectedRowField}
            onChange={setSelectedRowField}
            style={{ width: 150 }}
            options={rowFields.map((f) => ({ label: f, value: f }))}
          />
        </Space>
        <Space>
          <Text bold>Colonne:</Text>
          <Select
            value={selectedColField}
            onChange={setSelectedColField}
            style={{ width: 150 }}
            options={colFields.map((f) => ({ label: f, value: f }))}
          />
        </Space>
        <Space>
          <Text bold>Valore:</Text>
          <Select
            value={selectedValField}
            onChange={setSelectedValField}
            style={{ width: 150 }}
            options={(valField ? [valField] : rowFields).map((f) => ({ label: f, value: f }))}
          />
        </Space>
      </Flex>

      <Table
        columns={pivotData.columns}
        dataSource={pivotData.dataSource}
        pagination={false}
        size="small"
        scroll={{ x: 'max-content' }}
      />
    </Card>
  );
}
