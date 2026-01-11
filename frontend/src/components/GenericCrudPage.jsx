import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from './Layout';
import SearchBar from './SearchBar';
import Pagination from './Pagination';
import DataTable from './DataTable';
import FormLines from './FormLines';
import { apiFetch } from '../utils';

function GenericCrudPage({ pageTitle, apiPath, columns, formFields }) {
  const [data, setData] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [errors, setErrors] = useState({});
  const [dynamicOptions, setDynamicOptions] = useState({});
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });
  const [dateFilters, setDateFilters] = useState({ from: '', to: '' });
  
  // Inizializza formData
  const initialFormData = formFields.reduce((acc, field) => {
    acc[field.name] = field.defaultValue !== undefined ? field.defaultValue : '';
    if (field.type === 'checkbox') acc[field.name] = field.defaultValue || false;
    if (field.type === 'lines') acc[field.name] = [];
    return acc;
  }, {});
  
  const [formData, setFormData] = useState(initialFormData);
  
  const navigate = useNavigate();
  const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');

  const fetchData = (query = '', page = 1, sort = sortConfig, dates = dateFilters) => {
    let url = `${apiPath}?page=${page}&per_page=10`;
    if (query) {
      url += `&q=${encodeURIComponent(query)}`;
    }
    if (sort.key) {
      url += `&sort_by=${sort.key}&sort_order=${sort.direction}`;
    }
    if (dates.from) {
      url += `&date_from=${dates.from}`;
    }
    if (dates.to) {
      url += `&date_to=${dates.to}`;
    }

    apiFetch(url)
    .then(res => {
      const pages = parseInt(res.headers.get('X-Pages')) || 1;
      setTotalPages(pages);
      return res.json().then(items => ({ items, pages }));
    })
    .then(result => {
      if (result && result.items) setData(result.items);
    })
    .catch(err => console.error(err));
  };

  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }
    fetchData(searchTerm, currentPage, sortConfig, dateFilters);
  }, [token, navigate, apiPath]);

  // Caricamento opzioni dinamiche per le select
  useEffect(() => {
    if (!token) return;

    formFields.forEach(field => {
      if (field.type === 'select' && field.apiUrl && !dynamicOptions[field.name] && !field.dependsOn) {
        apiFetch(field.apiUrl)
        .then(res => res.json())
        .then(data => {
           // Gestisce sia array diretto che formato paginato { items: [...] }
           const items = Array.isArray(data) ? data : (data.items || []);
           setDynamicOptions(prev => ({ ...prev, [field.name]: items }));
        })
        .catch(err => console.error(`Errore caricamento opzioni per ${field.name}:`, err));
      }
    });
  }, [formFields, token]);

  const handleSearch = (term) => {
    setSearchTerm(term);
    setCurrentPage(1);
    fetchData(term, 1, sortConfig, dateFilters);
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
    fetchData(searchTerm, page, sortConfig, dateFilters);
  };

  const handleSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
    fetchData(searchTerm, currentPage, { key, direction }, dateFilters);
  };

  const handleDateFilterChange = (key, value) => {
    const newDates = { ...dateFilters, [key]: value };
    setDateFilters(newDates);
    setCurrentPage(1);
    fetchData(searchTerm, 1, sortConfig, newDates);
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked, files } = e.target;
    let val;
    if (type === 'checkbox') val = checked;
    else if (type === 'file') val = files[0];
    else val = value;
    
    setFormData(prev => ({ ...prev, [name]: val }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: null }));
    }

    // Gestione dipendenze (Cascading Selects)
    formFields.forEach(field => {
      if (field.dependsOn === name) {
        // Reset del valore del campo figlio
        setFormData(prev => ({ ...prev, [field.name]: '' }));
        
        if (val) {
           const queryParam = field.paramName || name;
           apiFetch(`${field.apiUrl}?${queryParam}=${val}`)
           .then(res => res.json())
           .then(data => {
              const items = Array.isArray(data) ? data : (data.items || []);
              setDynamicOptions(prev => ({ ...prev, [field.name]: items }));
           })
           .catch(console.error);
        } else {
           setDynamicOptions(prev => ({ ...prev, [field.name]: [] }));
        }
      }
    });
  };

  const openNewModal = () => {
    setFormData(initialFormData);
    setEditingId(null);
    setErrors({});
    setShowModal(true);
    
    // Pulisce le opzioni dei campi dipendenti per il nuovo inserimento
    setDynamicOptions(prev => {
        const next = { ...prev };
        formFields.forEach(f => {
            if (f.dependsOn) next[f.name] = [];
        });
        return next;
    });
  };

  const handleEdit = (item) => {
    const newFormData = { ...initialFormData };
    formFields.forEach(field => {
      let val = item[field.name];
      if (val === null || val === undefined) val = '';
      
      // Gestione specifica per le date: estrai YYYY-MM-DD dall'ISO string
      if (field.type === 'date' && val && val.length >= 10) {
        val = val.substring(0, 10);
      }
      
      newFormData[field.name] = val;
    });
    
    setFormData(newFormData);
    setEditingId(item.id);
    setErrors({});
    setShowModal(true);

    // Carica opzioni per i campi dipendenti basandosi sui valori esistenti
    formFields.forEach(field => {
        if (field.dependsOn) {
            const parentValue = item[field.dependsOn];
            if (parentValue) {
                const queryParam = field.paramName || field.dependsOn;
                apiFetch(`${field.apiUrl}?${queryParam}=${parentValue}`)
                .then(res => res.json())
                .then(data => {
                    const items = Array.isArray(data) ? data : (data.items || []);
                    setDynamicOptions(prev => ({ ...prev, [field.name]: items }));
                })
                .catch(console.error);
            } else {
                setDynamicOptions(prev => ({ ...prev, [field.name]: [] }));
            }
        }
    });
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Sei sicuro di voler eliminare questo elemento?")) return;

    try {
      const res = await apiFetch(`${apiPath}/${id}`, {
        method: 'DELETE'
      });

      if (res.ok) {
        setData(data.filter(item => item.id !== id));
      } else {
        alert("Errore durante l'eliminazione");
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors({});

    const url = editingId 
      ? `${apiPath}/${editingId}` 
      : `${apiPath}`;
    const method = editingId ? 'PUT' : 'POST';

    const hasFile = formFields.some(f => f.type === 'file');
    let body;
    let headers = {};

    if (hasFile) {
      const formDataObj = new FormData();
      Object.keys(formData).forEach(key => {
        const val = formData[key];
        // Se è un file vero e proprio, lo aggiungiamo
        if (val instanceof File) {
          formDataObj.append(key, val);
        } else if (val !== null && val !== undefined && typeof val !== 'object') {
           // Aggiungiamo gli altri campi (escludendo eventuali oggetti/array non gestiti)
           // Nota: Se il campo è file ma il valore è una stringa (URL esistente), non lo rimandiamo
           const isFileField = formFields.find(f => f.name === key)?.type === 'file';
           if (!isFileField) {
             formDataObj.append(key, val);
           }
        }
      });
      body = formDataObj;
      // Non impostare Content-Type: il browser lo mette automatico con il boundary
    } else {
      headers['Content-Type'] = 'application/json';
      body = JSON.stringify(formData);
    }

    try {
      const res = await apiFetch(url, {
        method: method,
        headers: headers,
        body: body
      });

      if (res.ok) {
        const savedItem = await res.json();
        if (editingId) {
          setData(data.map(item => item.id === editingId ? savedItem : item));
        } else {
          setData([...data, savedItem]);
        }
        setShowModal(false);
      } else {
        const result = await res.json();
        if (res.status === 422 && result.errors && result.errors.json) {
          setErrors(result.errors.json);
        } else {
          alert(result.message || "Errore durante il salvataggio");
        }
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleExport = async () => {
    const params = new URLSearchParams();
    if (searchTerm) params.append('q', searchTerm);
    if (sortConfig.key) {
      params.append('sort_by', sortConfig.key);
      params.append('sort_order', sortConfig.direction);
    }
    if (dateFilters.from) params.append('date_from', dateFilters.from);
    if (dateFilters.to) params.append('date_to', dateFilters.to);

    try {
      const res = await apiFetch(`${apiPath}/export?${params.toString()}`);

      if (res.ok) {
        const blob = await res.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = `${pageTitle.toLowerCase().replace(/\s+/g, '_')}_export.csv`;
        document.body.appendChild(a);
        a.click();
        a.remove();
      } else {
        alert("Errore durante l'esportazione");
      }
    } catch (err) {
      console.error(err);
    }
  };

  const renderField = (field) => {
    const isReadOnly = field.readOnly || (field.readOnlyOnEdit && editingId);

    if (field.type === 'file') {
      return (
        <div>
          <input 
            type="file" 
            className={`form-control ${errors[field.name] ? 'is-invalid' : ''}`}
            name={field.name}
            onChange={handleInputChange}
            required={field.required && !editingId} // Obbligatorio solo in creazione
            disabled={isReadOnly}
          />
          {editingId && typeof formData[field.name] === 'string' && formData[field.name] && (
             <div className="form-text text-muted">File attuale: {formData[field.name]}</div>
          )}
        </div>
      );
    }

    if (field.type === 'lines') {
      return (
        <FormLines 
          name={field.name}
          value={formData[field.name]}
          onChange={handleInputChange}
          columns={field.columns}
          fields={field.fields}
          compute={field.compute}
        />
      );
    }

    const commonProps = {
      className: `form-control ${errors[field.name] ? 'is-invalid' : ''}`,
      name: field.name,
      value: formData[field.name],
      onChange: handleInputChange,
      required: field.required,
      disabled: isReadOnly
    };

    if (field.type === 'select') {
      const options = field.options || dynamicOptions[field.name] || [];
      return (
        <select className="form-select" {...commonProps}>
          <option value="">Seleziona...</option>
          {options.map(opt => {
            // Determina valore e etichetta: supporta config custom (valueKey/labelKey) o default (id/name o value/label)
            const value = field.valueKey ? opt[field.valueKey] : (opt.value !== undefined ? opt.value : opt.id);
            const label = field.labelKey ? opt[field.labelKey] : (opt.label !== undefined ? opt.label : opt.name);
            return <option key={value} value={value}>{label}</option>;
          })}
        </select>
      );
    }
    
    if (field.type === 'textarea') {
      return <textarea {...commonProps} rows="3" />;
    }

    if (field.type === 'checkbox') {
      return (
        <div className="form-check">
          <input 
            type="checkbox" 
            className="form-check-input"
            name={field.name}
            checked={formData[field.name]}
            onChange={handleInputChange}
            disabled={isReadOnly}
          />
          <label className="form-check-label">{field.label}</label>
        </div>
      );
    }

    return <input type={field.type || 'text'} {...commonProps} />;
  };

  return (
    <Layout>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>{pageTitle}</h2>
        <div className="d-flex gap-2">
          <div className="d-flex gap-1">
            <input 
              type="date" 
              className="form-control" 
              value={dateFilters.from} 
              onChange={(e) => handleDateFilterChange('from', e.target.value)}
              title="Data Inizio"
            />
            <input 
              type="date" 
              className="form-control" 
              value={dateFilters.to} 
              onChange={(e) => handleDateFilterChange('to', e.target.value)}
              title="Data Fine"
            />
          </div>
          <SearchBar onSearch={handleSearch} />
          <button className="btn btn-outline-success" onClick={handleExport}>CSV</button>
          <button className="btn btn-primary" onClick={openNewModal}>Nuovo</button>
        </div>
      </div>

      <DataTable 
        columns={columns} 
        data={data} 
        onEdit={handleEdit} 
        onDelete={handleDelete} 
        sortConfig={sortConfig}
        onSort={handleSort}
      />

      <Pagination 
        currentPage={currentPage} 
        totalPages={totalPages} 
        onPageChange={handlePageChange} 
      />

      {showModal && (
        <div className="modal fade show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">{editingId ? 'Modifica' : 'Nuovo'} {pageTitle}</h5>
                <button type="button" className="btn-close" onClick={() => setShowModal(false)}></button>
              </div>
              <div className="modal-body">
                <form onSubmit={handleSubmit}>
                  <div className="row">
                    {formFields.map(field => (
                      <div className={field.colClass || "col-12 mb-3"} key={field.name}>
                        {field.type !== 'checkbox' && <label className="form-label">{field.label}</label>}
                        {renderField(field)}
                        {errors[field.name] && <div className="invalid-feedback d-block">{errors[field.name]}</div>}
                      </div>
                    ))}
                  </div>
                  <div className="d-flex justify-content-end gap-2 mt-3">
                    <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Annulla</button>
                    <button type="submit" className="btn btn-primary">Salva</button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      )}
    </Layout>
  );
}

export default GenericCrudPage;