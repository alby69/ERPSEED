function DataTable({ columns, data, onEdit, onDelete, sortConfig, onSort }) {
  // Funzione helper per accedere a proprietà annidate (es. "supplier.name")
  const getNestedValue = (obj, path) => {
    if (!path) return '';
    return path.split('.').reduce((acc, part) => acc && acc[part], obj);
  };

  return (
    <div className="card shadow-sm">
      <div className="card-body p-0">
        <table className="table table-hover mb-0">
          <thead className="table-light">
            <tr>
              {columns.map((col, index) => (
                <th 
                  key={index} 
                  onClick={() => col.accessor && onSort && onSort(col.accessor)}
                  style={{ cursor: col.accessor ? 'pointer' : 'default', userSelect: 'none' }}
                >
                  <div className="d-flex align-items-center gap-1">
                    {col.header}
                    {sortConfig && sortConfig.key === col.accessor && (
                      <span className="small text-muted">
                        {sortConfig.direction === 'asc' ? ' ▲' : ' ▼'}
                      </span>
                    )}
                  </div>
                </th>
              ))}
              {(onEdit || onDelete) && <th style={{ width: '150px' }}>Azioni</th>}
            </tr>
          </thead>
          <tbody>
            {data.map((row) => (
              <tr key={row.id}>
                {columns.map((col, index) => (
                  <td key={index}>
                    {/* Se c'è una funzione render personalizzata usala, altrimenti mostra il valore diretto */}
                    {col.render 
                      ? col.render(row) 
                      : (col.accessor ? getNestedValue(row, col.accessor) : '')}
                  </td>
                ))}
                {(onEdit || onDelete) && (
                  <td>
                    {onEdit && (
                      <button 
                        className="btn btn-sm btn-outline-primary me-2" 
                        onClick={() => onEdit(row)}
                      >
                        Modifica
                      </button>
                    )}
                    {onDelete && (
                      <button 
                        className="btn btn-sm btn-outline-danger" 
                        onClick={() => onDelete(row.id)}
                      >
                        Elimina
                      </button>
                    )}
                  </td>
                )}
              </tr>
            ))}
            {data.length === 0 && (
              <tr>
                <td colSpan={columns.length + (onEdit || onDelete ? 1 : 0)} className="text-center py-4 text-muted">
                  Nessun dato trovato.
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