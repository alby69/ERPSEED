import React, { useState, useEffect } from 'react';
import { apiFetch } from '../utils';

const FIELD_TYPES = [
  { value: 'string', label: 'String (Testo breve)' },
  { value: 'text', label: 'Text (Testo lungo)' },
  { value: 'integer', label: 'Integer (Numero intero)' },
  { value: 'float', label: 'Float (Numero decimale)' },
  { value: 'currency', label: 'Currency (Valuta)' },
  { value: 'boolean', label: 'Boolean (Vero/Falso)' },
  { value: 'date', label: 'Date (Data)' },
  { value: 'datetime', label: 'DateTime (Data e Ora)' },
  { value: 'tags', label: 'Tags (Etichette multiple)' },
  { value: 'color', label: 'Color (Selettore Colore)' },
  { value: 'select', label: 'Select (Menu a tendina)' },
  { value: 'relation', label: 'Relation (Relazione 1-a-N)' },
  { value: 'file', label: 'File (Allegato generico)' },
  { value: 'image', label: 'Image (Immagine)' },
  { value: 'formula', label: 'Formula (Campo calcolato)' },
  { value: 'summary', label: 'Summary (Campo di riepilogo)' },
  { value: 'calculated', label: 'Calculated (Frontend)' },
  { value: 'lookup', label: 'Lookup (Campo di ricerca)' },
  { value: 'lines', label: 'Master-Detail (Linee/Righe)' },
];

const AGGREGATION_FUNCTIONS = [
  { value: 'SUM', label: 'Somma (SUM)' },
  { value: 'AVG', label: 'Media (AVG)' },
  { value: 'COUNT', label: 'Conteggio (COUNT)' },
  { value: 'MIN', label: 'Minimo (MIN)' },
  { value: 'MAX', label: 'Massimo (MAX)' },
];

const NUMBER_FORMATS = [
  { value: '', label: 'Standard (es. 1.234,56)' },
  { value: 'currency_eur', label: 'Valuta (€ EUR)' },
  { value: 'currency_usd', label: 'Valuta ($ USD)' },
  { value: 'percent', label: 'Percentuale (0.1 -> 10%)' },
  { value: 'decimal_2', label: 'Decimale (2 cifre fisse)' },
  { value: 'progress', label: 'Progress Bar (0-100)' },
];

const BOOTSTRAP_COLORS = [
  { value: 'primary', label: 'Blu (Primary)' },
  { value: 'secondary', label: 'Grigio (Secondary)' },
  { value: 'success', label: 'Verde (Success)' },
  { value: 'danger', label: 'Rosso (Danger)' },
  { value: 'warning', label: 'Giallo (Warning)' },
  { value: 'info', label: 'Azzurro (Info)' },
  { value: 'light', label: 'Chiaro (Light)' },
  { value: 'dark', label: 'Scuro (Dark)' },
];

function SysFieldModal({ show, onClose, onSave, modelId, fieldToEdit }) {
  const getInitialState = () => ({
    name: '',
    title: '',
    type: 'string',
    required: false,
    is_unique: false,
    options: '',
    default_value: '',
    formula: '',
    summary_expression: '',
    validation_regex: '',
    validation_message: '',
    tooltip: '',
    model_id: modelId,
  });

  const [field, setField] = useState(getInitialState());
  const [sysModels, setSysModels] = useState([]);
  const [tagInput, setTagInput] = useState('');
  const [targetFields, setTargetFields] = useState([]);
  const [currentModelFields, setCurrentModelFields] = useState([]);

  useEffect(() => {
    if (show) {
      // Carica i modelli disponibili per le relazioni
      apiFetch('/sys-models')
        .then(res => res.ok ? res.json() : [])
        .then(data => setSysModels(data))
        .catch(err => console.error("Failed to load sys models", err));

      // Carica i campi del modello corrente per le dipendenze (visibilità)
      if (modelId) {
        apiFetch(`/sys-models/${modelId}`)
          .then(res => res.ok ? res.json() : {})
          .then(data => setCurrentModelFields(data.fields || []))
          .catch(err => console.error("Failed to load current model fields", err));
      }

      if (fieldToEdit) {
        // Popola il form per la modifica, assicurando che tutti i campi siano definiti
        const initialState = getInitialState();
        const editingState = {};
        for (const key in initialState) {
          editingState[key] = fieldToEdit[key] !== undefined && fieldToEdit[key] !== null ? fieldToEdit[key] : initialState[key];
        }
        setField(editingState);
      } else {
        // Resetta per un nuovo campo
        setField(getInitialState());
      }
    }
  }, [fieldToEdit, show, modelId]);

  const targetTable = (() => { try { return JSON.parse(field.options || '{}').target_table; } catch { return null; } })();

  useEffect(() => {
    if (field.type === 'summary' && targetTable) {
      apiFetch(`/data/${targetTable}/meta`)
        .then(res => res.ok ? res.json() : null)
        .then(data => {
          if (data && data.fields) {
            setTargetFields(data.fields.filter(f => ['integer', 'float'].includes(f.type)));
          }
        })
        .catch(err => console.error("Failed to load target fields", err));
    }
  }, [field.type, targetTable]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setField(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(field);
  };

  const handleAddTag = (e) => {
    e.preventDefault();
    if (!tagInput.trim()) return;
    
    let currentOptions = [];
    let currentMeta = {};

    try {
      const parsed = field.options ? JSON.parse(field.options) : [];
      if (Array.isArray(parsed)) {
        currentOptions = parsed;
      } else {
        currentOptions = parsed.values || [];
        currentMeta = { ...parsed };
        delete currentMeta.values;
      }
    } catch (e) {
      currentOptions = [];
    }

    const newOptions = [...currentOptions, tagInput.trim()];
    
    // Se ci sono metadati extra (es. visibility), salviamo come oggetto
    const payload = Object.keys(currentMeta).length > 0 
      ? { ...currentMeta, values: newOptions } 
      : newOptions;

    setField(prev => ({ ...prev, options: JSON.stringify(payload) }));
    setTagInput('');
  };

  const handleRemoveTag = (index) => {
    const parsed = JSON.parse(field.options || '[]');
    const currentOptions = Array.isArray(parsed) ? parsed : (parsed.values || []);
    const newOptions = currentOptions.filter((_, i) => i !== index);
    
    const payload = (!Array.isArray(parsed) && Object.keys(parsed).length > 1) // >1 perché values conta come 1
      ? { ...parsed, values: newOptions }
      : newOptions;

    setField(prev => ({ ...prev, options: JSON.stringify(payload) }));
  };

  if (!show) return null;

  const showOptions = ['select', 'relation', 'lookup', 'summary', 'lines'].includes(field.type);
  const showFormula = ['formula', 'calculated'].includes(field.type);
  const showSummary = field.type === 'summary';
  const showRegexValidation = ['string', 'text'].includes(field.type);

  return (
    <div className="modal fade show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
      <div className="modal-dialog modal-lg">
        <div className="modal-content">
          <form onSubmit={handleSubmit}>
            <div className="modal-header">
              <h5 className="modal-title">{fieldToEdit ? 'Edit Field' : 'Add New Field'}</h5>
              <button type="button" className="btn-close" onClick={onClose}></button>
            </div>
            <div className="modal-body">
              <div className="row">
                <div className="col-md-6 mb-3">
                  <label className="form-label">Field Name (es. `license_plate`)</label>
                  <input type="text" name="name" value={field.name} onChange={handleChange} className="form-control" required pattern="[a-z0-9_]+" title="Solo lettere minuscole, numeri e underscore." />
                </div>
                <div className="col-md-6 mb-3">
                  <label className="form-label">Field Title (es. `Targa`)</label>
                  <input type="text" name="title" value={field.title} onChange={handleChange} className="form-control" required />
                </div>
              </div>
              <div className="mb-3">
                <label className="form-label">Tooltip (Help Text)</label>
                <input type="text" name="tooltip" value={field.tooltip} onChange={handleChange} className="form-control" placeholder="Testo informativo che appare accanto all'etichetta" />
              </div>
              <div className="row">
                <div className="col-md-6 mb-3">
                  <label className="form-label">Type</label>
                  <select name="type" value={field.type} onChange={handleChange} className="form-select">
                    {FIELD_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
                  </select>
                </div>
                <div className="col-md-6 mb-3">
                  <label className="form-label">Default Value</label>
                  <input type="text" name="default_value" value={field.default_value} onChange={handleChange} className="form-control" />
                </div>
              </div>
              <div className="mb-3 d-flex gap-4">
                <div className="form-check">
                  <input type="checkbox" name="required" checked={field.required} onChange={handleChange} className="form-check-input" id="field-required" />
                  <label className="form-check-label" htmlFor="field-required">Required</label>
                </div>
                <div className="form-check">
                  <input type="checkbox" name="is_unique" checked={field.is_unique} onChange={handleChange} className="form-check-input" id="field-unique" />
                  <label className="form-check-label" htmlFor="field-unique">Unique</label>
                </div>
              </div>

              {showOptions && (
                <div className="mb-3">
                  <label className="form-label">{['relation', 'lines'].includes(field.type) ? 'Target Table' : field.type === 'select' ? 'Options (List)' : 'Options (JSON)'}</label>
                  {['relation', 'lines'].includes(field.type) ? (
                    <select 
                      className="form-select"
                      value={(() => {
                        try { return JSON.parse(field.options || '{}').target_table || ''; }
                        catch { return ''; }
                      })()}
                      onChange={(e) => setField(prev => ({
                        ...prev,
                        options: JSON.stringify({ ...JSON.parse(prev.options || '{}'), target_table: e.target.value })
                      }))}
                    >
                      <option value="">Select Table...</option>
                      {sysModels.map(m => (
                        <option key={m.id} value={m.name}>{m.title} ({m.name})</option>
                      ))}
                    </select>
                  ) : field.type === 'select' ? (
                    <div className="border p-3 rounded bg-light">
                      <div className="d-flex flex-wrap gap-2 mb-2">
                        {(() => {
                          try {
                            const parsed = field.options ? JSON.parse(field.options) : [];
                            const opts = Array.isArray(parsed) ? parsed : (parsed.values || []);
                            if (opts.length === 0) return <span className="text-muted small fst-italic">No options added yet.</span>;
                            return opts.map((opt, idx) => (
                              <span key={idx} className="badge bg-primary d-flex align-items-center gap-2">
                                {typeof opt === 'object' ? (opt.label || JSON.stringify(opt)) : opt}
                                <button type="button" className="btn-close btn-close-white" style={{ fontSize: '0.5em' }} onClick={() => handleRemoveTag(idx)}></button>
                              </span>
                            ));
                          } catch (e) {
                            return <span className="text-danger small">Invalid JSON in options. Clear to reset.</span>;
                          }
                        })()}
                      </div>
                      <div className="input-group">
                        <input type="text" className="form-control" placeholder="Type option and press Enter" value={tagInput} onChange={(e) => setTagInput(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter') handleAddTag(e); }} />
                        <button className="btn btn-outline-secondary" type="button" onClick={handleAddTag}>Add</button>
                      </div>
                    </div>
                  ) : (
                    <textarea name="options" value={field.options} onChange={handleChange} className="form-control" rows="3" placeholder='Es: ["Option 1", "Option 2"] o {"target_table": "users"}'></textarea>
                  )}
                </div>
              )}

              {field.type === 'select' && (
                <div className="border p-3 rounded mt-3 bg-light">
                  <h6 className="text-muted small fw-bold">Colori Badge (Opzionale)</h6>
                  <div className="row g-2">
                    {(() => {
                        try {
                            const parsed = field.options ? JSON.parse(field.options) : [];
                            const values = Array.isArray(parsed) ? parsed : (parsed.values || []);
                            const badgeColors = (Array.isArray(parsed) ? {} : parsed.badge_colors) || {};
                            
                            if (values.length === 0) return <div className="text-muted small">Aggiungi prima delle opzioni sopra.</div>;

                            return values.map((opt, idx) => {
                                const val = typeof opt === 'object' ? opt.value : opt;
                                const label = typeof opt === 'object' ? opt.label : opt;
                                return (
                                    <div key={idx} className="col-md-6 d-flex align-items-center gap-2">
                                        <span className="small text-truncate" style={{width: '100px'}} title={label}>{label}</span>
                                        <select 
                                            className="form-select form-select-sm"
                                            value={badgeColors[val] || ''}
                                            onChange={(e) => {
                                                const newColor = e.target.value;
                                                setField(prev => {
                                                    let opts = {};
                                                    try { opts = JSON.parse(prev.options || '{}'); } catch {}
                                                    if (Array.isArray(opts)) opts = { values: opts };
                                                    
                                                    if (!opts.badge_colors) opts.badge_colors = {};
                                                    if (newColor) opts.badge_colors[val] = newColor;
                                                    else delete opts.badge_colors[val];
                                                    
                                                    return { ...prev, options: JSON.stringify(opts) };
                                                });
                                            }}
                                        >
                                            <option value="">Nessuno (Testo)</option>
                                            {BOOTSTRAP_COLORS.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
                                        </select>
                                    </div>
                                );
                            });
                        } catch (e) { return null; }
                    })()}
                  </div>
                </div>
              )}

              {['integer', 'float', 'currency'].includes(field.type) && (
                <div className="mb-3 border p-3 rounded bg-light">
                  <label className="form-label fw-bold small">Formattazione Numerica</label>
                  <div className="row">
                    <div className="col-md-6">
                      <label className="form-label small">Formato</label>
                      <select 
                        className="form-select form-select-sm"
                        value={(() => { try { return JSON.parse(field.options || '{}').format || ''; } catch { return ''; } })()}
                        onChange={(e) => setField(prev => ({ ...prev, options: JSON.stringify({ ...JSON.parse(prev.options || '{}'), format: e.target.value }) }))}
                      >
                        {NUMBER_FORMATS.map(f => <option key={f.value} value={f.value}>{f.label}</option>)}
                      </select>
                    </div>
                    <div className="col-md-6">
                      <label className="form-label small">Suffisso Personalizzato</label>
                      <input 
                        type="text" 
                        className="form-control form-control-sm" 
                        placeholder="es. kg, m², pz"
                        value={(() => { try { return JSON.parse(field.options || '{}').suffix || ''; } catch { return ''; } })()}
                        onChange={(e) => setField(prev => ({ ...prev, options: JSON.stringify({ ...JSON.parse(prev.options || '{}'), suffix: e.target.value }) }))}
                      />
                    </div>
                  </div>
                </div>
              )}

              {['lines', 'summary'].includes(field.type) && (
                <div className="mb-3">
                  <label className="form-label">Foreign Key Field (nella tabella Detail)</label>
                  <input 
                    type="text" 
                    className="form-control" 
                    placeholder="es. invoice_id"
                    value={(() => { try { return JSON.parse(field.options || '{}').foreign_key || ''; } catch { return ''; } })()}
                    onChange={(e) => setField(prev => ({ ...prev, options: JSON.stringify({ ...JSON.parse(prev.options || '{}'), foreign_key: e.target.value }) }))}
                  />
                </div>
              )}

              {/* Conditional Visibility Section */}
              <div className="border p-3 rounded mt-3 bg-light">
                <h6 className="text-muted small fw-bold">Visibilità Condizionale</h6>
                <div className="row">
                  <div className="col-md-6">
                    <label className="form-label small">Mostra solo se il campo...</label>
                    <select 
                      className="form-select form-select-sm"
                      value={(() => { try { return JSON.parse(field.options || '{}').visibility?.field || ''; } catch { return ''; } })()}
                      onChange={(e) => {
                        const val = e.target.value;
                        setField(prev => {
                          let opts = {};
                          try { opts = JSON.parse(prev.options || '{}'); } catch {}
                          // Normalizza opts se era un array (vecchio select)
                          if (Array.isArray(opts)) opts = { values: opts };
                          
                          if (!opts.visibility) opts.visibility = {};
                          opts.visibility.field = val;
                          if (!val) delete opts.visibility; // Cleanup
                          return { ...prev, options: JSON.stringify(opts) };
                        });
                      }}
                    >
                      <option value="">-- Sempre Visibile --</option>
                      {currentModelFields.filter(f => f.name !== field.name).map(f => (
                        <option key={f.id} value={f.name}>{f.title} ({f.name})</option>
                      ))}
                    </select>
                  </div>
                  <div className="col-md-6">
                    <label className="form-label small">Ha valore...</label>
                    <input 
                      type="text" 
                      className="form-control form-control-sm"
                      placeholder="Valore esatto"
                      value={(() => { try { return JSON.parse(field.options || '{}').visibility?.value || ''; } catch { return ''; } })()}
                      onChange={(e) => {
                        const val = e.target.value;
                        setField(prev => {
                          let opts = {};
                          try { opts = JSON.parse(prev.options || '{}'); } catch {}
                          if (Array.isArray(opts)) opts = { values: opts };
                          
                          if (!opts.visibility) opts.visibility = {};
                          opts.visibility.value = val;
                          return { ...prev, options: JSON.stringify(opts) };
                        });
                      }}
                    />
                  </div>
                </div>
              </div>

              {/* Conditional Requirement Section */}
              <div className="border p-3 rounded mt-3">
                <h6 className="text-muted small fw-bold">Requisito Condizionale</h6>
                <div className="row">
                  <div className="col-md-6">
                    <label className="form-label small">Obbligatorio se il campo...</label>
                    <select 
                      className="form-select form-select-sm"
                      value={(() => { try { return JSON.parse(field.options || '{}').requirement?.field || ''; } catch { return ''; } })()}
                      onChange={(e) => {
                        const val = e.target.value;
                        setField(prev => {
                          let opts = {};
                          try { opts = JSON.parse(prev.options || '{}'); } catch {}
                          if (Array.isArray(opts)) opts = { values: opts };
                          
                          if (!opts.requirement) opts.requirement = {};
                          opts.requirement.field = val;
                          if (!val) delete opts.requirement; // Cleanup
                          return { ...prev, options: JSON.stringify(opts) };
                        });
                      }}
                    >
                      <option value="">-- Sempre (se spuntato sopra) --</option>
                      {currentModelFields.filter(f => f.name !== field.name).map(f => (
                        <option key={f.id} value={f.name}>{f.title} ({f.name})</option>
                      ))}
                    </select>
                  </div>
                  <div className="col-md-6">
                    <label className="form-label small">Ha valore...</label>
                    <input 
                      type="text" 
                      className="form-control form-control-sm"
                      placeholder="Valore esatto"
                      value={(() => { try { return JSON.parse(field.options || '{}').requirement?.value || ''; } catch { return ''; } })()}
                      onChange={(e) => {
                        const val = e.target.value;
                        setField(prev => {
                          let opts = {};
                          try { opts = JSON.parse(prev.options || '{}'); } catch {}
                          if (Array.isArray(opts)) opts = { values: opts };
                          
                          if (!opts.requirement) opts.requirement = {};
                          opts.requirement.value = val;
                          return { ...prev, options: JSON.stringify(opts) };
                        });
                      }}
                    />
                  </div>
                </div>
              </div>

              {showFormula && (
                <div className="mb-3">
                  <label className="form-label">Formula</label>
                  <input type="text" name="formula" value={field.formula} onChange={handleChange} className="form-control" placeholder={field.type === 'calculated' ? "Es: {firstName} + ' ' + {lastName}" : "Es: {quantity} * {price}"} />
                </div>
              )}

              {showSummary && (
                <div className="mb-3">
                  <label className="form-label">Configurazione Riepilogo</label>
                  <div className="d-flex gap-2">
                    <div style={{ flex: 1 }}>
                      <label className="form-label small text-muted">Funzione</label>
                      <select
                        className="form-select"
                        value={field.summary_expression ? field.summary_expression.match(/^(\w+)\(/)?.[1] || 'SUM' : 'SUM'}
                        onChange={(e) => {
                          const func = e.target.value;
                          const col = field.summary_expression ? field.summary_expression.match(/\((.*?)\)/)?.[1] || '' : '';
                          setField(prev => ({
                            ...prev,
                            summary_expression: col ? `${func}(${col})` : ''
                          }));
                        }}
                      >
                        {AGGREGATION_FUNCTIONS.map(f => (
                          <option key={f.value} value={f.value}>{f.label}</option>
                        ))}
                      </select>
                    </div>
                    <div style={{ flex: 2 }}>
                      <label className="form-label small text-muted">Campo Target</label>
                      <select 
                        className="form-select"
                        value={field.summary_expression ? field.summary_expression.match(/\((.*?)\)/)?.[1] || '' : ''}
                        onChange={(e) => {
                          const col = e.target.value;
                          const func = field.summary_expression ? field.summary_expression.match(/^(\w+)\(/)?.[1] || 'SUM' : 'SUM';
                          setField(prev => ({
                            ...prev,
                            summary_expression: col ? `${func}(${col})` : ''
                          }));
                        }}
                      >
                        <option value="">Seleziona un campo...</option>
                        <option value="id">ID (Primary Key)</option>
                        {targetFields.map(f => (
                          <option key={f.name} value={f.name}>{f.title} ({f.name})</option>
                        ))}
                      </select>
                    </div>
                  </div>
                  <div className="form-text mt-1">Espressione generata: {field.summary_expression}</div>
                </div>
              )}

              {field.type === 'color' && (
                <div className="form-text mb-3">Questo campo mostrerà un selettore di colore (Color Picker).</div>
              )}

              {showRegexValidation && (
                <div className="border p-3 rounded mt-3">
                  <h6 className="text-muted small">Custom Validation</h6>
                  <div className="mb-3">
                    <label className="form-label">Validation Regex</label>
                    <input type="text" name="validation_regex" value={field.validation_regex} onChange={handleChange} className="form-control" placeholder="es. ^[A-Z]{2}\d{3}[A-Z]{2}$" />
                  </div>
                  <div>
                    <label className="form-label">Validation Error Message</label>
                    <input type="text" name="validation_message" value={field.validation_message} onChange={handleChange} className="form-control" placeholder="es. Il formato della targa non è valido." />
                  </div>
                </div>
              )}

            </div>
            <div className="modal-footer">
              <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
              <button type="submit" className="btn btn-primary">Save Field</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default SysFieldModal;