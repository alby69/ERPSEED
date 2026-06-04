import { useState, useRef, useEffect } from 'react';
import { getNestedValue } from '@/utils';

export function ActionsMenu({ row, onEdit, onDelete, onClone }) {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    const handleClick = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  if (!onEdit && !onDelete && !onClone) return null;

  return (
    <div className="dropdown" ref={ref}>
      <button
        className="btn btn-sm btn-light border rounded-3 px-2"
        onClick={(e) => { e.stopPropagation(); setOpen(!open); }}
      >
        <i className="bi bi-three-dots-vertical"></i>
      </button>
      {open && (
        <ul className="dropdown-menu show position-absolute end-0 mt-1 shadow-sm" style={{ minWidth: '140px', zIndex: 1050 }}>
          {onClone && (
            <li>
              <button className="dropdown-item" onClick={(e) => { e.stopPropagation(); onClone(row); setOpen(false); }}>
                <i className="bi bi-files me-2"></i>Duplicate
              </button>
            </li>
          )}
          {onEdit && (
            <li>
              <button className="dropdown-item" onClick={(e) => { e.stopPropagation(); onEdit(row); setOpen(false); }}>
                <i className="bi bi-pencil me-2"></i>Edit
              </button>
            </li>
          )}
          {onDelete && (
            <li>
              <button className="dropdown-item text-danger" onClick={(e) => { e.stopPropagation(); onDelete(row.id); setOpen(false); }}>
                <i className="bi bi-trash me-2"></i>Delete
              </button>
            </li>
          )}
        </ul>
      )}
    </div>
  );
}

function DataTable({ columns, data, onEdit, onDelete, onClone, sortConfig, onSort, selectable, selectedIds, onSelectAll, onSelectRow }) {
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
              {(onEdit || onDelete || onClone) && <th style={{ width: '60px' }}>Azioni</th>}
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
                    {col.render
                      ? col.render(row)
                      : (() => {
                          const val = col.accessor ? getNestedValue(row, col.accessor) : '';
                          if (typeof val === 'object' && val !== null) return val.plate || val.title || val.name || val.id || JSON.stringify(val);
                          return val;
                        })()}
                  </td>
                ))}
                {(onEdit || onDelete || onClone) && (
                  <td className="text-center">
                    <ActionsMenu row={row} onEdit={onEdit} onDelete={onDelete} onClone={onClone} />
                  </td>
                )}
              </tr>
            ))}
            {data.length === 0 && (
              <tr>
                <td colSpan={columns.length + (onEdit || onDelete || onClone ? 1 : 0) + (selectable ? 1 : 0)} className="text-center py-4 text-muted">
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