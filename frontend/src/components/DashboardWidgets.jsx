import React, { useEffect, useState } from 'react';
import { apiFetch } from '../utils';

function DashboardWidgets({ modelName }) {
  const [widgets, setWidgets] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadWidgets = async () => {
      try {
        // 1. Recupera i metadati
        const metaRes = await apiFetch(`/data/${modelName}/meta`);
        if (metaRes.status === 404) return;
        if (!metaRes.ok) throw new Error("Failed to load widget metadata");
        
        const meta = await metaRes.json();
        
        // 2. Determina la modalità: "Righe" (KPI definiti come record) o "Colonne" (KPI come campi di un record)
        // La modalità "Righe" è quella usata da seed_kpi.py (campi: label, value, trend, color, icon)
        const hasLabel = meta.fields.find(f => f.name === 'label');
        const hasValue = meta.fields.find(f => f.name === 'value');

        if (hasLabel && hasValue) {
            // Modalità Righe: ogni record è un widget
            const dataRes = await apiFetch(`/data/${modelName}?per_page=20`);
            if (!dataRes.ok) throw new Error("Failed to load widget data");
            const data = await dataRes.json();
            setWidgets(data);
        } else {
            // Modalità Colonne: un record contiene tutti i KPI (es. summary fields)
            const numericFields = meta.fields.filter(f => ['integer', 'float', 'currency', 'summary', 'formula'].includes(f.type));
            const dataRes = await apiFetch(`/data/${modelName}?per_page=1`);
            if (!dataRes.ok) throw new Error("Failed to load widget data");
            const data = await dataRes.json();
            
            if (data.length > 0) {
                const row = data[0];
                const mappedWidgets = numericFields.map(f => ({
                    id: f.name,
                    label: f.title,
                    value: row[f.name] !== null ? (
                        f.type === 'currency' 
                        ? Number(row[f.name]).toLocaleString('it-IT', { style: 'currency', currency: 'EUR' }) 
                        : Number(row[f.name]).toLocaleString()
                    ) : '-',
                    color: 'primary',
                    icon: null,
                    trend: null
                }));
                setWidgets(mappedWidgets);
            }
        }
      } catch (e) {
        console.error("Dashboard widget error:", e);
        setError(e.message);
      }
    };

    loadWidgets();
  }, [modelName]);

  if (error || widgets.length === 0) return null;

  return (
    <div className="row mb-4">
      {widgets.map((widget, idx) => (
        <div key={widget.id || idx} className="col-md-3 mb-3">
          <div className={`card shadow-sm border-start border-4 border-${widget.color || 'primary'} h-100`}>
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-center mb-2">
                 <h6 className="text-uppercase text-muted small mb-0">{widget.label}</h6>
                 {widget.icon && <i className={`bi bi-${widget.icon} text-${widget.color || 'primary'} fs-4`}></i>}
              </div>
              <h3 className="mb-0">{widget.value}</h3>
              {widget.trend && (
                  <div className={`small mt-2 ${widget.trend.includes('-') ? 'text-danger' : 'text-success'}`}>
                      {widget.trend} <span className="text-muted"> vs mese prec.</span>
                  </div>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

export default DashboardWidgets;