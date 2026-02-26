import { CaretUpOutlined, CaretDownOutlined } from '@ant-design/icons';

export function sortableColumn(title, dataIndex, sortField, sortOrder, onSort) {
  const isSorted = sortField === dataIndex;
  
  return {
    title: (
      <span 
        style={{ cursor: 'pointer' }} 
        onClick={() => onSort(dataIndex)}
        className="d-flex align-items-center gap-1"
      >
        {title}
        {isSorted ? (
          sortOrder === 'asc' ? 
            <CaretUpOutlined style={{ fontSize: 10 }} /> : 
            <CaretDownOutlined style={{ fontSize: 10 }} />
        ) : (
          <CaretUpOutlined style={{ fontSize: 10, opacity: 0.3 }} />
        )}
      </span>
    ),
    dataIndex,
    sorter: false,
  };
}

export default sortableColumn;
