import { useEffect, useState, useRef } from 'react';
import { useNavigate, useOutletContext, useLocation } from 'react-router-dom';
import { message } from 'antd';
import Layout from './Layout';
import SearchBar from './SearchBar';
import Pagination from './Pagination';
import DataTable from './DataTable';
import FormLines from './FormLines';
import KanbanView from './KanbanView';
import TableSearch from './TableSearch';
import { apiFetch, getNestedValue } from '../utils';
import { useCrudData } from '../hooks/useCrudData.js';

const evaluateFormula = (formula, data) => {
  try {
    // Sostituisce {var} con data['var'] per l'eval sicuro
    const expression = formula.replace(/{(\w+)}/g, "data['$1']");
    const func = new Function('data', `try { return ${expression}; } catch(e) { return ''; }`);
    return func(data);
  } catch (e) {
    return '';
  }
};

const TagInput = ({ value = [], onChange, disabled }) => {
  const [input, setInput] = useState('');

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      if (input.trim()) {
        onChange([...(value || []), input.trim()]);
        setInput('');
      }
    }
  };

  const removeTag = (index) => {
    onChange(value.filter((_, i) => i !== index));
  };

  return (
    <div className="border p-2 rounded bg-white">
      <div className="d-flex flex-wrap gap-1 mb-2">
        {(value || []).map((tag, i) => (
          <span key={i} className="badge bg-primary d-flex align-items-center">
            {tag}
            {!disabled && <button type="button" className="btn-close btn-close-white ms-2" style={{ fontSize: '0.5em' }} onClick={() => removeTag(i)}></button>}
          </span>
        ))}
      </div>
      {!disabled && <input type="text" className="form-control form-control-sm" placeholder="Type and press Enter..." value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={handleKeyDown} />}
    </div>
  );
};

function GenericCrudPage({ pageTitle, apiPath, columns, formFields, filterTabs, defaultView = 'table', defaultSort, enableDateFilter = false, kanbanConfig, embedded = false }) {
  const navigate = useNavigate();
  const location = useLocation();
  const outletContext = useOutletContext() || {};
  const { projectTitle, projectId } = outletContext;
  const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');

  // Build breadcrumbs
  const breadcrumbs = [
    { title: <a onClick={() => navigate('/projects')}>Progetti</a> },
  ];
  if (projectTitle) {
    breadcrumbs.push({ title: <a onClick={() => navigate(`/projects/${projectId}`)}>{projectTitle}</a> });
  }
  breadcrumbs.push({ title: pageTitle });

  // Check if we should render without internal layout (when embedded in ProjectLayout)
  const renderWithoutLayout = embedded || (projectId && location.pathname.startsWith('/projects/'));

  // Integrazione Custom Hook useCrudData
  const {
    data,
    loading,
    error: hookError,
    pagination,
    sort,
    filters,
    searchField,
    searchValue,
    setPage,
    setSort,
    setFilters,
    setSearch,
    clearSearch,
    createItem,
    updateItem,
    deleteItem,
    bulkDeleteItem,
    refresh
  } = useCrudData(apiPath, { initialPerPage: 10, initialSort: defaultSort });

  // Stato locale per UI
  const [searchTerm, setSearchTerm] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [errors, setErrors] = useState({});
  const [dynamicOptions, setDynamicOptions] = useState({});
  const [dateFilters, setDateFilters] = useState({ from: '', to: '' });
  const [selectedIds, setSelectedIds] = useState([]);
  const [activeTab, setActiveTab] = useState(0);
  const [viewMode, setViewMode] = useState(defaultView);
  const fileInputRef = useRef(null);

  // Inizializza formData
  const initialFormData = formFields.reduce((acc, field) => {
    acc[field.name] = field.defaultValue !== undefined ? field.defaultValue : '';
    if (field.type === 'checkbox') acc[field.name] = field.defaultValue || false;
    if (field.type === 'lines') acc[field.name] = [];
    if (field.type === 'tags') acc[field.name] = [];
    return acc;
  }, {});

  const [formData, setFormData] = useState(initialFormData);

  useEffect(() => {
    if (!token) {
      navigate('/login');
    }
  }, [token, navigate]);

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

  // Inizializza i filtri del primo tab al montaggio
  useEffect(() => {
    if (filterTabs && filterTabs.length > 0) {
      const defaultFilters = filterTabs[0].filters || {};
      setFilters(prev => ({ ...prev, ...defaultFilters }));
    }
  }, []); // Esegui solo al mount

  const handleTabChange = (index) => {
    setActiveTab(index);
    const tabFilters = filterTabs[index].filters || {};

    // Ricostruisce i filtri mantenendo ricerca e date, ma sostituendo i filtri del tab
    const newFilters = {
        q: searchTerm,
        date_from: dateFilters.from,
        date_to: dateFilters.to,
        ...tabFilters
    };

    setFilters(newFilters);
    setPage(1); // Reset a pagina 1 quando cambia il filtro principale
  };

  const handleSearch = (term) => {
    setSearchTerm(term);
    setFilters({ ...filters, q: term });
  };

  const handlePageChange = (page) => {
    setPage(page);
  };

  const handleSort = (key) => {
    const currentField = sort.field;
    const currentOrder = sort.order;
    if (currentField === key) {
      setSort({ field: key, order: currentOrder === 'asc' ? 'desc' : 'asc' });
    } else {
      setSort({ field: key, order: 'asc' });
    }
  };

  const handleSearchField = (field, value) => {
    setSearch(field, value);
  };

  const handleSearchClear = () => {
    clearSearch();
  };

  const handleGlobalSearch = (term) => {
    setFilters(prev => ({ ...prev, q: term }));
  };

  const handleDateFilterChange = (key, value) => {
    const newDates = { ...dateFilters, [key]: value };
    setDateFilters(newDates);
    setFilters(prev => ({
      ...prev,
      date_from: newDates.from,
      date_to: newDates.to
    }));
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked, files } = e.target;
    let val;
    if (type === 'checkbox') val = checked;
    else if (type === 'file') val = files[0];
    else val = value;

    setFormData(prev => {
      const newData = { ...prev, [name]: val };

      // Ricalcola campi calculated
      formFields.forEach(field => {
        if (field.formula && field.readOnly) { // Assumiamo che i campi con formula nel form siano calculated
           newData[field.name] = evaluateFormula(field.formula, newData);
        }
      });
      return newData;
    });
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

      if (field.type === 'tags') {
         // Assicura che sia un array
         if (!Array.isArray(val)) val = [];
      }

      newFormData[field.name] = val;
    });

    // Calcolo iniziale dei campi calculated
    formFields.forEach(field => {
      if (field.formula && field.readOnly) {
         newFormData[field.name] = evaluateFormula(field.formula, newFormData);
      }
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
    if (!window.confirm("Are you sure you want to delete this item?")) return;

    try {
      await deleteItem(id);
      message.success("Item deleted successfully");
    } catch (err) {
      message.error(err.message || "Error during deletion");
    }
  };

  const handleClone = async (item) => {
    if (!window.confirm("Do you want to duplicate this item?")) return;

    try {
      const res = await apiFetch(`${apiPath}/${item.id}/clone`, {
        method: 'POST'
      });
      if (res.ok) {
        message.success("Item duplicated successfully");
        refresh();
      } else {
        message.error("Error during duplication");
      }
    } catch (err) {
      console.error(err);
      message.error("Connection error");
    }
  };

  const handleKanbanStatusChange = async (itemId, newStatus) => {
    try {
      await updateItem(itemId, { [kanbanConfig.statusField]: newStatus });
      message.success("Status updated");
      refresh(); // Refresh data from server
    } catch (err) {
      message.error("Failed to update status.");
    }
  };

  const handleSelectAll = (e) => {
    if (e.target.checked) {
      setSelectedIds(data.map(item => item.id));
    } else {
      setSelectedIds([]);
    }
  };

  const handleSelectRow = (id) => {
    setSelectedIds(prev =>
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    );
  };

  const handleBulkDelete = async () => {
    if (selectedIds.length === 0) return;
    if (!window.confirm(`Are you sure you want to delete ${selectedIds.length} items?`)) return;

    try {
      await bulkDeleteItem(selectedIds);
      message.success(`${selectedIds.length} items deleted`);
      setSelectedIds([]); // Clear selection after deletion
    } catch (err) {
      message.error(err.message || "Error during bulk deletion");
    }
  };

  const isFieldRequired = (field, currentFormData) => {
    // Static requirement from DB
    if (field.required) {
        return true;
    }
    // Conditional requirement from Builder options
    if (field.optionsConfig?.requirement?.field) {
        const depField = field.optionsConfig.requirement.field;
        const depValue = field.optionsConfig.requirement.value;
        if (String(currentFormData[depField]) === String(depValue)) {
            return true;
        }
    }
    return false;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const newErrors = {};
    // Client-side validation
    formFields.forEach(field => {
      const required = isFieldRequired(field, formData);
      const value = formData[field.name];

      if (required && (value === null || value === undefined || value === '')) {
        newErrors[field.name] = 'This field is required.';
      } else if (field.validationRegex && value) {
        try {
          if (!new RegExp(field.validationRegex).test(String(value))) {
            newErrors[field.name] = field.validationMessage || 'Invalid format';
          }
        } catch (e) {
          console.warn(`Invalid regex for field ${field.name}:`, e);
        }
      }
    });

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setErrors({});

    const hasFile = formFields.some(f => f.type === 'file');
    let payload;

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
      payload = formDataObj;
    } else {
      payload = formData;
    }

    try {
      if (editingId) {
        await updateItem(editingId, payload);
      } else {
        await createItem(payload);
      }
      setShowModal(false);
      message.success("Saved successfully");
    } catch (err) {
      message.error(err.message || "Error during save");
    }
  };

  const handleExport = async () => {
    const params = new URLSearchParams();
    // Usa i filtri attuali del hook
    Object.keys(filters).forEach(key => {
      if (filters[key]) params.append(key, filters[key]);
    });
    if (sort.field) {
      params.append('sort_by', sort.field);
      params.append('sort_order', sort.order);
    }

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
        message.success("Export successful");
      } else {
        message.error("Error during export");
      }
    } catch (err) {
      console.error(err);
      message.error("Connection error during export");
    }
  };

  const handleImportClick = () => {
    fileInputRef.current.click();
  };

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await apiFetch(`${apiPath}/import`, {
        method: 'POST',
        body: formData
      });

      const result = await res.json();
      if (res.ok) {
        let msg = result.message;
        if (result.errors && result.errors.length > 0) {
            msg += "\n\nErrors:\n" + result.errors.slice(0, 10).join("\n");
            if (result.errors.length > 10) msg += `\n...and ${result.errors.length - 10} more.`;
        }
        message.info(msg);
        refresh();
      } else {
        message.error(result.message || "Import failed");
      }
    } catch (err) {
      console.error(err);
      message.error("Import error");
    } finally {
      e.target.value = null;
    }
  };

  const renderField = (field) => {
    const isReadOnly = field.readOnly || (field.readOnlyOnEdit && editingId);
    const required = isFieldRequired(field, formData);

    if (field.type === 'file') {
      return (
        <div>
          <input
            type="file"
            className={`form-control ${errors[field.name] ? 'is-invalid' : ''}`}
            name={field.name}
            onChange={handleInputChange} // Obbligatorio solo in creazione
            required={required && !editingId}
            disabled={isReadOnly}
          />
          {editingId && typeof formData[field.name] === 'string' && formData[field.name] && (
             <div className="form-text text-muted">Current file: {formData[field.name]}</div>
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

    if (field.type === 'tags') {
      return (
        <TagInput
          value={formData[field.name]}
          onChange={(newTags) => setFormData(prev => ({ ...prev, [field.name]: newTags }))}
          disabled={isReadOnly}
        />
      );
    }

    const commonProps = {
      className: `form-control ${errors[field.name] ? 'is-invalid' : ''}`,
      name: field.name,
      value: formData[field.name],
      onChange: handleInputChange,
      required: required,
      disabled: isReadOnly
    };

    if (field.type === 'select') {
      const options = field.options || dynamicOptions[field.name] || [];
      return (
        <select className="form-select" {...commonProps}>
          <option value="">Select...</option>
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
          <label className="form-check-label">
            {field.label}{required && <span className="text-danger ms-1">*</span>}
            {field.tooltip && (
              <i className="bi bi-info-circle ms-2 text-muted" title={field.tooltip} style={{ cursor: 'help' }}></i>
            )}
          </label>
        </div>
      );
    }

    return <input type={field.type || 'text'} {...commonProps} />;
  };

  const renderContent = () => (
    <>
    <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>{pageTitle}</h2>
        {selectedIds.length > 0 ? (
          <div className="d-flex gap-2">
            <button className="btn btn-danger" onClick={handleBulkDelete}>
              Delete Selected ({selectedIds.length})
            </button>
            <button className="btn btn-secondary" onClick={() => setSelectedIds([])}>
              Cancel
            </button>
          </div>
        ) : (
          <div className="d-flex gap-2">
            {/* View Mode Toggles */}
            <div className="btn-group me-2">
              <button
                className={`btn btn-outline-secondary ${viewMode === 'table' ? 'active' : ''}`}
                onClick={() => setViewMode('table')}
                title="Table View"
              >
                <i className="bi bi-list"></i>
              </button>
              <button
                className={`btn btn-outline-secondary ${viewMode === 'card' ? 'active' : ''}`}
                onClick={() => setViewMode('card')}
                title="Grid View"
              >
                <i className="bi bi-grid"></i>
            </button>
            {kanbanConfig &&
              <button
                className={`btn btn-outline-secondary ${viewMode === 'kanban' ? 'active' : ''}`}
                onClick={() => setViewMode('kanban')}
                title="Kanban View">
                <i className="bi bi-kanban"></i>
              </button>
            }
            </div>
            {enableDateFilter && (
              <div className="d-flex gap-1">
                <input
                  type="date"
                  className="form-control"
                  value={dateFilters.from}
                  onChange={(e) => handleDateFilterChange('from', e.target.value)}
                  title="Start Date"
                />
                <input
                  type="date"
                  className="form-control"
                  value={dateFilters.to}
                  onChange={(e) => handleDateFilterChange('to', e.target.value)}
                  title="End Date"
                />
              </div>
            )}
            <SearchBar onSearch={handleSearch} />
            <input
              type="file"
              ref={fileInputRef}
              style={{display: 'none'}}
              accept=".csv"
              onChange={handleFileChange}
            />
            <button className="btn btn-outline-primary" onClick={handleImportClick}>Import CSV</button>
            <button className="btn btn-outline-success" onClick={handleExport}>CSV</button>
            <button className="btn btn-primary" onClick={openNewModal}>New</button>
          </div>
        )}
      </div>

      {/* Filter Tabs */}
      {filterTabs && filterTabs.length > 0 && (
        <ul className="nav nav-tabs mb-3">
          {filterTabs.map((tab, idx) => (
            <li className="nav-item" key={idx}>
              <button
                className={`nav-link ${activeTab === idx ? 'active' : ''}`}
                onClick={() => handleTabChange(idx)}
                type="button"
                style={{ cursor: 'pointer' }}
              >
                {tab.label}
              </button>
            </li>
          ))}
        </ul>
      )}

      {loading && <div className="text-center my-2 text-muted">Loading...</div>}
      {hookError && <div className="alert alert-danger">{hookError}</div>}

      {viewMode === 'table' ? (
        <div>
          <div className="mb-3">
            <TableSearch
              columns={columns}
              searchField={searchField}
              searchValue={searchValue}
              searchTerm={filters.q || ''}
              globalSearchValue={filters.q || ''}
              onSearchFieldChange={handleSearchField}
              onSearchValueChange={(val) => handleSearchField(searchField, val)}
              onSearchSubmit={() => {}}
              onClearSearch={handleSearchClear}
              onGlobalSearch={handleGlobalSearch}
            />
          </div>
          <DataTable
          columns={columns}
          data={data}
          onEdit={handleEdit}
          onDelete={handleDelete}
          actions={(row) => (
            <button
              className="btn btn-sm btn-outline-secondary me-2"
              onClick={() => handleClone(row)}
title="Duplicate"
            >
              <i className="bi bi-files"></i>
            </button>
          )}
          sortConfig={{ key: sort.field, direction: sort.order }}
          onSort={handleSort}
          selectable={true}
          selectedIds={selectedIds}
          onSelectAll={handleSelectAll}
          onSelectRow={handleSelectRow}
        />
        </div>
      ) : (
        <div className="row g-3">
          {data.map(row => (
            <div key={row.id} className="col-md-6 col-lg-4">
              <div className={`card h-100 shadow-sm ${selectedIds.includes(row.id) ? 'border-primary' : ''}`}>
                <div className="card-body">
                  <div className="d-flex justify-content-between mb-3">
                    <input
                      type="checkbox"
                      className="form-check-input"
                      checked={selectedIds.includes(row.id)}
                      onChange={() => handleSelectRow(row.id)}
                    />
                    <div className="d-flex gap-1">
                      <button className="btn btn-sm btn-outline-secondary" onClick={() => handleClone(row)} title="Duplica"><i className="bi bi-files"></i></button>
                      <button className="btn btn-sm btn-outline-primary" onClick={() => handleEdit(row)}><i className="bi bi-pencil"></i></button>
                      <button className="btn btn-sm btn-outline-danger" onClick={() => handleDelete(row.id)}><i className="bi bi-trash"></i></button>
                    </div>
                  </div>
                  {columns.map((col, index) => (
                    <div key={index} className="mb-2">
                      <strong className="d-block small text-muted">{col.header}</strong>
                      <div className="text-truncate">
                        {col.render ? col.render(row) : (col.accessor ? getNestedValue(row, col.accessor) : '')}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
          {data.length === 0 && <div className="col-12 text-center text-muted py-5">No data found.</div>}
        </div>
      )}

      <Pagination
        currentPage={pagination.page}
        totalPages={pagination.totalPages}
        onPageChange={handlePageChange}
      />

      {showModal && (
        <div className="modal fade show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">{editingId ? 'Edit' : 'New'} {pageTitle}</h5>
                <button type="button" className="btn-close" onClick={() => setShowModal(false)}></button>
              </div>
              <div className="modal-body">
                <form onSubmit={handleSubmit}>
                  <div className="row">
                    {formFields.map(field => {
                      // Check Visibility
                      let isVisible = true;
                      if (field.optionsConfig && field.optionsConfig.visibility && field.optionsConfig.visibility.field) {
                         const depField = field.optionsConfig.visibility.field;
                         const depValue = field.optionsConfig.visibility.value;
                         // Confronto stringa per sicurezza (gestisce numeri e stringhe)
                         if (String(formData[depField]) !== String(depValue)) {
                           isVisible = false;
                         }
                      }

                      if (!isVisible) return null;

                      return (
                        <div className={field.colClass || "col-12 mb-3"} key={field.name}>
                          {field.type !== 'checkbox' && (
                            <label className="form-label">
                              {field.label}{isFieldRequired(field, formData) && <span className="text-danger ms-1">*</span>}
                              {field.tooltip && (
                                <i className="bi bi-info-circle ms-2 text-muted" title={field.tooltip} style={{ cursor: 'help' }}></i>
                              )}
                            </label>
                          )}
                          {renderField(field)}
                          {errors[field.name] && <div className="invalid-feedback d-block">{errors[field.name]}</div>}
                        </div>
                      );
                    })}
                  </div>
                  <div className="d-flex justify-content-end gap-2 mt-3">
                    <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                    <button type="submit" className="btn btn-primary">Save</button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );

  if (renderWithoutLayout) {
    return renderContent();
  }

  return (
    <Layout breadcrumbs={breadcrumbs}>
      {renderContent()}
    </Layout>
  );
}

export default GenericCrudPage;