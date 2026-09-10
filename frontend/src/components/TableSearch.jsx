import { Select, Input, Button, Space, Tooltip } from 'antd';
import { SearchOutlined, ClearOutlined } from '@ant-design/icons';

function TableSearch({
  columns = [],
  globalSearchValue,
  onSearchSubmit,
  onClearSearch,
  onGlobalSearch,
  filters = {},
  onFilterChange
}) {
  const filterColumns = columns.filter(col => col.filterType === 'select' && col.filterOptions);
  const hasActiveFilters = Object.values(filters).some(v => v?.length > 0) || globalSearchValue;

  return (
    <Space size="small" wrap>
      <Input.Search
        placeholder="Ricerca..."
        style={{ width: 250 }}
        value={globalSearchValue || ''}
        onChange={(e) => onGlobalSearch(e.target.value)}
        onSearch={onSearchSubmit}
        enterButton={<SearchOutlined />}
        allowClear
      />
      {filterColumns.map(col => {
        const fieldKey = col.key || (typeof col.dataIndex === 'string' ? col.dataIndex : col.dataIndex?.[0]);
        return (
          <Select
            key={fieldKey}
            mode="multiple"
            placeholder={col.title}
            style={{ minWidth: 180 }}
            maxTagCount={1}
            value={filters[fieldKey] || []}
            onChange={(values) => onFilterChange(fieldKey, values)}
            allowClear
            options={col.filterOptions}
          />
        );
      })}
      {hasActiveFilters && (
        <Tooltip title="Pulisci filtri">
          <Button
            icon={<ClearOutlined />}
            onClick={onClearSearch}
          />
        </Tooltip>
      )}
    </Space>
  );
}

export default TableSearch;
