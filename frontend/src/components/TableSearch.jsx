import { Select, Input, Button, Space } from 'antd';
import { SearchOutlined, ClearOutlined } from '@ant-design/icons';

function TableSearch({ 
  columns = [], 
  searchField, 
  searchValue, 
  searchTerm,
  onSearchFieldChange, 
  onSearchValueChange, 
  onSearchSubmit,
  onClearSearch,
  onGlobalSearch,
  globalSearchValue
}) {
  const searchableColumns = columns.filter(col => 
    col.dataIndex && col.searchable !== false
  );

  const showFieldSearch = searchField || searchValue;

  return (
    <Space size="small" wrap>
      <Select
        placeholder="Cerca per campo..."
        style={{ width: 150 }}
        value={searchField || null}
        allowClear
        onChange={(val) => onSearchFieldChange(val, searchValue)}
        options={searchableColumns.map(col => ({
          value: typeof col.dataIndex === 'string' ? col.dataIndex : col.dataIndex[0],
          label: col.title
        }))}
      />
      {searchField && (
        <Input.Search
          placeholder={`Cerca in ${searchField}...`}
          style={{ width: 200 }}
          value={searchValue}
          onChange={(e) => onSearchFieldChange(searchField, e.target.value)}
          onSearch={onSearchSubmit}
          enterButton
          allowClear
          onClear={() => onSearchFieldChange('', '')}
        />
      )}
      {(searchField || searchValue) && (
        <Button 
          icon={<ClearOutlined />} 
          onClick={onClearSearch}
          title="Pulisci ricerca"
        >
          Pulisci
        </Button>
      )}
      <span style={{ borderLeft: '1px solid #d9d9d9', margin: '0 8px', height: 24, display: 'inline-block' }} />
      <Input.Search
        placeholder="Ricerca globale..."
        style={{ width: 200 }}
        value={globalSearchValue}
        onChange={(e) => onGlobalSearch(e.target.value)}
        onSearch={onSearchSubmit}
        enterButton
        allowClear
      />
    </Space>
  );
}

export default TableSearch;
