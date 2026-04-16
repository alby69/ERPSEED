import { getNestedValue } from '@/utils';

function DataTable({ columns, data, onEdit, onDelete, actions, sortConfig, onSort, selectable, selectedIds, onSelectAll, onSelectRow }) {
  return (
    <div className="card shadow-sm">
      <div className="card-body p-0">
        <table className="table table-hover mb-0">
          <thead className="table-light">
            <tr>
              {selectable && (
                <th style={{ width: '40px' }}>
                  <input
                    type="checkbox"
                    className="form-check-input"
                    checked={data.length > 0 && selectedIds?.length === data.length}
                    onChange={onSelectAll}
                  />
                </th>
              )}
              {columns.map((col, index) => (
                <th
                  key={index}
                  onClick={() => (col.accessor || col.sortField) && onSort && onSort(col.sortField || col.accessor)}
                  style={{ cursor: (col.accessor || col.sortField) ? 'pointer' : 'default', userSelect: 'none' }}
                >
                  <div className="d-flex align-items-center gap-1">
                    {col.header}
                    {sortConfig && sortConfig.key === (col.sortField || col.accessor) && (
                      <span className="small text-muted">
                        {sortConfig.direction === 'asc' ? ' ▲' : ' ▼'}
                      </span>
                    )}
                  </div>
                </th>
              ))}
              {(onEdit || onDelete || actions) && <th style={{ width: '150px' }}>Azioni</th>}
            </tr>
          </thead>
          <tbody>
            {data.map((row) => (
              <tr key={row.id} className={selectable && selectedIds?.includes(row.id) ? 'table-active' : ''}>
                {selectable && (
                  <td>
                    <input
                      type="checkbox"
                      className="form-check-input"
                      checked={selectedIds?.includes(row.id)}
                      onChange={() => onSelectRow(row.id)}
                    />
                  </td>
                )}
                {columns.map((col, index) => (
                  <td key={index}>
                    {/* Se c'è una funzione render personalizzata usala, altrimenti mostra il valore diretto */}
                    {col.render
                      ? col.render(row)
                      : (col.accessor ? getNestedValue(row, col.accessor) : '')}
                  </td>
                ))}
                {(onEdit || onDelete || actions) && (
                  <td>
                    {actions && actions(row)}
                    {onEdit && (
                      <button
                        className="btn btn-sm btn-outline-primary me-2"
                        onClick={() => onEdit(row)}
                      >
                        Edit
                      </button>
                    )}
                    {onDelete && (
                      <button
                        className="btn btn-sm btn-outline-danger"
                        onClick={() => onDelete(row.id)}
                      >
                        Delete
                      </button>
                    )}
                  </td>
                )}
              </tr>
            ))}
            {data.length === 0 && (
              <tr>
                <td colSpan={columns.length + (onEdit || onDelete || actions ? 1 : 0) + (selectable ? 1 : 0)} className="text-center py-4 text-muted">
                  No data found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default DataTable;