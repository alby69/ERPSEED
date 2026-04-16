import { useState, useEffect } from 'react';
import { apiFetch } from '../utils';

function FormLines({ name, value = [], onChange, columns, fields, compute }) {
  const [isEditing, setIsEditing] = useState(false);
  const [editingIndex, setEditingIndex] = useState(null);
  const [lineData, setLineData] = useState({});
  const [dynamicOptions, setDynamicOptions] = useState({});

  const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');

  // Inizializza i dati di una riga vuota
  const initialLineData = fields.reduce((acc, field) => {
    acc[field.name] = field.defaultValue !== undefined ? field.defaultValue : '';
    return acc;
  }, {});

  useEffect(() => {
    fields.forEach(field => {
      if (field.type === 'select' && field.apiUrl && !dynamicOptions[field.name]) {
        apiFetch(field.apiUrl)
        .then(res => res.json())
        .then(data => {
           const items = Array.isArray(data) ? data : (data.items || []);
           setDynamicOptions(prev => ({ ...prev, [field.name]: items }));
        })
        .catch(console.error);
      }
    });
  }, []);

  const handleAddNew = () => {
    setLineData(initialLineData);
    setEditingIndex(null);
    setIsEditing(true);
  };

  const handleEdit = (index) => {
    setLineData(value[index]);
    setEditingIndex(index);
    setIsEditing(true);
  };

  const handleDelete = (index) => {
    if (!confirm("Rimuovere questa riga?")) return;
    const newLines = value.filter((_, i) => i !== index);
    onChange({ target: { name, value: newLines } });
  };

  const handleCancel = () => {
    setIsEditing(false);
    setLineData({});
  };

  const handleSaveLine = () => {
    const newLines = [...value];
    if (editingIndex !== null) {
      newLines[editingIndex] = lineData;
    } else {
      newLines.push(lineData);
    }
    onChange({ target: { name, value: newLines } });
    setIsEditing(false);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;

    setLineData(prev => {
      let newData = { ...prev, [name]: value };

      // Se è stata passata una funzione di calcolo, eseguila
      if (compute) {
        // Passiamo anche dynamicOptions per permettere lookup (es. prezzo prodotto)
        newData = compute(newData, dynamicOptions);
      }

      return newData;
    });
  };

  const getOptionLabel = (fieldName, val) => {
    const options = dynamicOptions[fieldName];
    if (!options) return val;
    const fieldConfig = fields.find(f => f.name === fieldName);
    const valueKey = fieldConfig.valueKey || 'id';
    const labelKey = fieldConfig.labelKey || 'name';
    const option = options.find(o => String(o[valueKey]) === String(val));
    return option ? option[labelKey] : val;
  };

  return (
    <div className="border rounded p-2 mb-3 bg-white">
      <label className="form-label fw-bold">Righe Ordine</label>

      <table className="table table-sm table-striped mb-2">
        <thead>
          <tr>
            {columns.map((col, idx) => <th key={idx}>{col.header}</th>)}
            <th style={{ width: '100px' }}>Azioni</th>
          </tr>
        </thead>
        <tbody>
          {value.map((row, idx) => (
            <tr key={idx}>
              {columns.map((col, cIdx) => (
                <td key={cIdx}>
                  {col.render ? col.render(row) : (
                    fields.find(f => f.name === col.accessor && f.type === 'select')
                      ? getOptionLabel(col.accessor, row[col.accessor])
                      : row[col.accessor]
                  )}
                </td>
              ))}
              <td>
                <button type="button" className="btn btn-xs btn-link p-0 me-2" onClick={() => handleEdit(idx)}>Edit</button>
                <button type="button" className="btn btn-xs btn-link p-0 text-danger" onClick={() => handleDelete(idx)}>Remove</button>
              </td>
            </tr>
          ))}
          {value.length === 0 && <tr><td colSpan={columns.length + 1} className="text-center text-muted">No lines added</td></tr>}
        </tbody>
      </table>

      {isEditing ? (
        <div className="card card-body bg-light p-2">
          <div className="row g-2">
            {fields.map(field => (
              <div key={field.name} className={field.colClass || "col-md-4"}>
                <label className="form-label small mb-0">{field.label}</label>
                {field.type === 'select' ? (
                  <select
                    className="form-select form-select-sm"
                    name={field.name}
                    value={lineData[field.name]}
                    onChange={handleInputChange}
                    disabled={field.readOnly}
                  >
                    <option value="">Seleziona...</option>
                    {(dynamicOptions[field.name] || []).map(opt => {
                       const vKey = field.valueKey || 'id';
                       const lKey = field.labelKey || 'name';
                       return <option key={opt[vKey]} value={opt[vKey]}>{opt[lKey]}</option>
                    })}
                  </select>
                ) : (
                  <input
                    type={['integer', 'float', 'currency'].includes(field.type) ? 'number' : (field.type || 'text')}
                    className="form-control form-control-sm"
                    name={field.name}
                    value={lineData[field.name]}
                    onChange={handleInputChange}
                    disabled={field.readOnly}
                  />
                )}
              </div>
            ))}
          </div>
          <div className="mt-2 d-flex justify-content-end gap-2">
            <button type="button" className="btn btn-sm btn-secondary" onClick={handleCancel}>Annulla</button>
            <button type="button" className="btn btn-sm btn-success" onClick={handleSaveLine}>Conferma Riga</button>
          </div>
        </div>
      ) : (
        <button type="button" className="btn btn-sm btn-outline-primary" onClick={handleAddNew}>+ Aggiungi Riga</button>
      )}
    </div>
  );
}

export default FormLines;