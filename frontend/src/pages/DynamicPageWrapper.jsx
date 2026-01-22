import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { apiFetch } from '../utils';
import GenericCrudPage from '../components/GenericCrudPage';
import Layout from '../components/Layout';

// Funzione helper per valutare formule frontend
const evaluateFrontendFormula = (formula, row) => {
  try {
    const expression = formula.replace(/{(\w+)}/g, "data['$1'] || ''");
    const func = new Function('data', `try { return ${expression}; } catch(e) { return ''; }`);
    return func(row);
  } catch (e) {
    return '';
  }
};

function DynamicPageWrapper() {
  const { modelName } = useParams();
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchMetadata = async () => {
      try {
        setLoading(true);
        const response = await apiFetch(`/data/${modelName}/meta`);
        if (!response.ok) {
          throw new Error('Failed to load model metadata');
        }
        const model = await response.json();
        
        // Trasforma i campi del modello in configurazione per GenericCrudPage
        const columns = [];
        const formFields = [];

        // Ordina i campi per 'order'
        const sortedFields = (model.fields || []).sort((a, b) => a.order - b.order);

        sortedFields.forEach(field => {
          // Configurazione Colonne Tabella
          // Escludiamo campi "pesanti" o non visualizzabili facilmente dalla tabella di default
          if (!['file', 'image', 'formula', 'summary', 'calculated'].includes(field.type)) {
             const colConfig = {
               header: field.title || field.name
             };

             if (field.type === 'relation') {
               // Se è una relazione, l'API dinamica restituisce l'oggetto annidato (es. 'customer')
               // invece di 'customer_id'. Proviamo ad accedere a .name o .title
               const relationName = field.name.endsWith('_id') ? field.name.slice(0, -3) : field.name;
               colConfig.accessor = `${relationName}.name`; // Default a .name per ora
               colConfig.sortField = `${relationName}.name`; // Usa la notazione dot per ordinare per nome (es. customer.name)
             } else {
               colConfig.accessor = field.name;
               colConfig.sortField = field.name;

               if (field.type === 'boolean') {
                 colConfig.render = (row) => (
                   row[field.name] 
                     ? <span className="badge bg-success">Sì</span> 
                     : <span className="badge bg-secondary">No</span>
                 );
               }

               // Gestione Badge per Select
               if (field.type === 'select') {
                 try {
                   const opts = JSON.parse(field.options || '{}');
                   const badgeColors = opts.badge_colors || {};
                   
                   if (Object.keys(badgeColors).length > 0) {
                     colConfig.render = (row) => {
                       const val = row[field.name];
                       if (!val) return '';
                       
                       const color = badgeColors[val] || 'secondary';
                       
                       // Cerca la label corretta se le opzioni sono oggetti
                       let label = val;
                       const values = Array.isArray(opts) ? opts : (opts.values || []);
                       const option = values.find(o => (typeof o === 'object' ? o.value : o) === val);
                       if (option && typeof option === 'object' && option.label) {
                         label = option.label;
                       }

                       return <span className={`badge bg-${color}`}>{label}</span>;
                     };
                   }
                 } catch (e) {}
               }

               // Gestione Formattazione Numerica
               if (['integer', 'float', 'currency'].includes(field.type)) {
                 try {
                   const opts = JSON.parse(field.options || '{}');
                   
                   // Default currency formatting if type is currency and no specific format is chosen
                   if (field.type === 'currency' && !opts.format) {
                       opts.format = 'currency_eur';
                   }
                   
                   if (opts.format === 'progress') {
                     colConfig.render = (row) => {
                       const val = parseFloat(row[field.name]);
                       if (isNaN(val)) return '';
                       const percent = Math.min(Math.max(val, 0), 100);
                       
                       let bgClass = 'bg-primary';
                       if (percent >= 100) bgClass = 'bg-success';
                       else if (percent < 30) bgClass = 'bg-danger';
                       else if (percent < 70) bgClass = 'bg-warning';

                       return (
                         <div className="progress" style={{ height: '20px' }}>
                           <div className={`progress-bar ${bgClass}`} role="progressbar" style={{ width: `${percent}%` }}>
                             {Math.round(percent)}%
                           </div>
                         </div>
                       );
                     };
                   } else if (opts.format || opts.suffix) {
                     colConfig.render = (row) => {
                       const val = row[field.name];
                       if (val === null || val === undefined) return '';
                       
                       let formatted = val;
                       try {
                         if (opts.format === 'currency_eur') {
                           formatted = new Intl.NumberFormat('it-IT', { style: 'currency', currency: 'EUR' }).format(val);
                         } else if (opts.format === 'currency_usd') {
                           formatted = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val);
                         } else if (opts.format === 'percent') {
                           formatted = new Intl.NumberFormat('it-IT', { style: 'percent', minimumFractionDigits: 2 }).format(val);
                         } else if (opts.format === 'decimal_2') {
                           formatted = new Intl.NumberFormat('it-IT', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(val);
                         } else {
                           formatted = new Intl.NumberFormat('it-IT').format(val);
                         }
                       } catch (e) { formatted = val; }

                       if (opts.suffix && !['currency_eur', 'currency_usd', 'percent'].includes(opts.format)) {
                         formatted = `${formatted} ${opts.suffix}`;
                       }
                       return formatted;
                     };
                   }
                 } catch (e) {}
               }
             }
             
             if (field.type === 'tags') {
               colConfig.render = (row) => {
                 const val = row[field.name];
                 if (Array.isArray(val)) {
                   return val.map((t, i) => <span key={i} className="badge bg-secondary me-1">{t}</span>);
                 }
                 return '';
               };
             }

             columns.push(colConfig);
          } else if (field.type === 'image') {
             columns.push({
               header: field.title || field.name,
               render: (row) => row[field.name] ? (
                 <img 
                   src={`http://localhost:5000/uploads/${row[field.name]}`} 
                   alt={field.name} 
                   style={{ width: '40px', height: '40px', objectFit: 'cover', borderRadius: '4px' }} 
                 />
               ) : ''
             });
          } else if (field.type === 'calculated') {
             columns.push({
               header: field.title || field.name,
               render: (row) => evaluateFrontendFormula(field.formula, row)
             });
          }

          // Configurazione Campi Form
          // Ignoriamo campi calcolati in input (formula, summary, lookup)
          if (!['formula', 'summary', 'lookup'].includes(field.type)) {
            const formField = {
              name: field.name,
              label: field.title || field.name,
              type: field.type === 'string' ? 'text' : field.type, // Mappa 'string' a 'text' per HTML input
              required: field.required,
              defaultValue: field.default_value
            };

            if (field.type === 'calculated') {
              formField.type = 'text';
              formField.readOnly = true;
              formField.formula = field.formula;
            }

            // Gestione opzioni per Select
            if (field.type === 'select' && field.options) {
               try {
                 formField.options = JSON.parse(field.options);
               } catch (e) {
                 console.error("Error parsing options for field", field.name, e);
               }
            }
            
            // Gestione Relation (diventa una Select dinamica)
            if (field.type === 'relation' && field.options) {
              try {
                const opts = JSON.parse(field.options);
                if (opts.target_table) {
                  formField.type = 'select';
                  formField.apiUrl = `/data/${opts.target_table}`;
                  formField.valueKey = 'id';
                  // Cerchiamo di usare 'name' o 'title' come label se esistono, altrimenti id
                  // Nota: GenericCrudPage/FormLines dovrà essere abbastanza smart da gestire questo
                  // oppure l'API dinamica dovrebbe restituire un campo standard 'display_name'.
                  formField.labelKey = 'name'; 
                }
              } catch (e) {
                console.error("Error parsing relation options for field", field.name, e);
              }
            }

            formFields.push(formField);
          }
        });

        setConfig({
          pageTitle: model.title,
          apiPath: `/data/${model.name}`,
          columns,
          formFields
        });

      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchMetadata();
  }, [modelName]);

  if (loading) return <Layout><div>Loading dynamic model...</div></Layout>;
  if (error) return <Layout><div className="alert alert-danger">Error: {error}</div></Layout>;
  if (!config) return <Layout><div>Model configuration not found.</div></Layout>;

  return (
    <GenericCrudPage 
      pageTitle={config.pageTitle}
      apiPath={config.apiPath}
      columns={config.columns}
      formFields={config.formFields}
    />
  );
}

export default DynamicPageWrapper;