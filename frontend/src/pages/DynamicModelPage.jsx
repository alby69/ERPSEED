import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { apiFetch } from '../utils';
import GenericCrudPage from '../components/GenericCrudPage';
import Layout from '../components/Layout';

function DynamicModelPage() {
  const { projectId, modelName } = useParams();
  const [modelMeta, setModelMeta] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchMeta = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await apiFetch(`/projects/${projectId}/data/${modelName}/meta`);
        if (!response.ok) throw new Error('Failed to load model metadata');
        const data = await response.json();
        data.fields = data.fields || data.model_fields || [];

        // Se ci sono campi 'lines', carica i metadati dei modelli collegati
        const linesFields = data.fields.filter(f => f.type === 'lines');
        if (linesFields.length > 0) {
          await Promise.all(linesFields.map(async (field) => {
            try {
              const opts = JSON.parse(field.options);
              if (opts.target_table) {
                const detailRes = await apiFetch(`/projects/${projectId}/data/${opts.target_table}/meta`);
                if (detailRes.ok) {
                  const detailMeta = await detailRes.json();
                  detailMeta.fields = detailMeta.fields || detailMeta.model_fields || [];
                  // Arricchiamo il campo con i metadati del dettaglio per FormLines
                  field.columns = detailMeta.fields
                    .filter(f => f.name !== opts.foreign_key && f.name !== 'id') // Nascondi FK e ID
                    .sort((a, b) => (a.order || 0) - (b.order || 0))
                    .map(f => ({ key: f.name, label: f.title }));

                  field.fields = detailMeta.fields
                    .filter(f => f.name !== opts.foreign_key && f.name !== 'id')
                    .map(f => ({
                      name: f.name,
                      label: f.title,
                      type: f.type,
                      apiUrl: f.type === 'relation' && f.options ? `/projects/${projectId}/data/${JSON.parse(f.options).target_table}` : undefined,
                      valueKey: 'id', labelKey: 'name' // Default
                    }));
                }
              }
            } catch (e) { console.error("Error loading detail meta", e); }
          }));
        }

        setModelMeta(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    if (projectId && modelName) fetchMeta();
  }, [projectId, modelName]);

  if (loading) return <div className="p-5 text-center">Loading configuration...</div>;
  if (error) return <div className="alert alert-danger m-4">{error}</div>;
  if (!modelMeta) return <div className="alert alert-warning m-4">Model not found</div>;

  // Mappatura dei campi SysField -> GenericCrudPage fields
  const columns = modelMeta.fields
    .filter(f => f.type !== 'lines') // Non mostrare le linee nella tabella principale
    .sort((a, b) => (a.order || 0) - (b.order || 0))
    .map(f => ({
      accessor: f.name,
      header: f.title,
      type: f.type,
      render: f.type === 'boolean' ? (row) => (
        row[f.name]
          ? <span className="badge bg-success">Sì</span>
          : <span className="badge bg-secondary">No</span>
      ) : f.type === 'relation' ? (row) => {
        const val = row[f.name];
        if (!val) return '';
        if (typeof val === 'object') return val.plate || val.title || val.name || val.id || JSON.stringify(val);
        return val;
      } : undefined
    }));

  // Aggiunge colonna ID se non presente
  if (!columns.find(c => c.accessor === 'id')) {
    columns.unshift({ accessor: 'id', header: 'ID' });
  }

  const formFields = modelMeta.fields
    .sort((a, b) => (a.order || 0) - (b.order || 0))
    .map(f => {
      const fieldConfig = {
        name: f.name,
        label: f.title,
        type: f.type,
        required: f.required,
        readOnly: f.type === 'formula' || f.type === 'summary' || f.type === 'calculated',
        optionsConfig: f.options ? JSON.parse(f.options) : {}, // Passiamo la config raw per visibilità ecc.
        validationRegex: f.validation_regex,
        validationMessage: f.validation_message,
        tooltip: f.tooltip
      };

      // Mappatura tipi specifici per il form
      if (f.type === 'string') fieldConfig.type = 'text';
      if (f.type === 'integer' || f.type === 'float') fieldConfig.type = 'number';
      if (f.type === 'boolean') fieldConfig.type = 'checkbox';
      if (f.type === 'text') fieldConfig.type = 'textarea';
      if (f.type === 'color') fieldConfig.type = 'color';

      // Gestione Relazioni (Select dinamica)
      if (f.type === 'relation' && f.options) {
        try {
          const opts = JSON.parse(f.options);
          if (opts.target_table) {
            fieldConfig.type = 'select';
            fieldConfig.apiUrl = `/projects/${projectId}/data/${opts.target_table}`;
            if (opts.label_field) fieldConfig.labelKey = opts.label_field;
            if (opts.value_field) fieldConfig.valueKey = opts.value_field;
          }
        } catch (e) {
          console.error("Error parsing options for relation", f.name);
        }
      }

      // Gestione Select statica
      if (f.type === 'select' && f.options) {
        try {
           const parsed = JSON.parse(f.options);
           // Supporta sia array semplice ["A"] che oggetto { values: ["A"] }
           fieldConfig.options = Array.isArray(parsed) ? parsed : (parsed.values || []);
        } catch (e) {
           console.error("Error parsing options for select", f.name);
        }
      }

      // Gestione Lines (Master-Detail)
      if (f.type === 'lines') {
        fieldConfig.type = 'lines';
        fieldConfig.columns = f.columns || [];
        fieldConfig.fields = f.fields || [];
        try {
          const opts = JSON.parse(f.options || '{}');
          if (opts.target_table && opts.foreign_key) {
            fieldConfig.fetchUrl = `/projects/${projectId}/data/${opts.target_table}`;
            fieldConfig.filterField = opts.foreign_key;
          }
        } catch (e) {}
      }

      return fieldConfig;
    });

  // Configurazione per la vista Kanban
  let kanbanConfig = null;
  if (modelMeta.default_view === 'kanban' && modelMeta.kanban_status_field) {
    const statusField = modelMeta.fields.find(f => f.name === modelMeta.kanban_status_field);
    if (statusField && statusField.type === 'select' && statusField.options) {
      try {
        const opts = JSON.parse(statusField.options);
        kanbanConfig = {
          statusField: modelMeta.kanban_status_field,
          statusValues: Array.isArray(opts) ? opts : (opts.values || []),
          titleField: modelMeta.fields.find(f => f.name === 'name')?.name || 'id',
          descriptionField: modelMeta.fields.find(f => f.name === 'description')?.name,
          cardColorField: modelMeta.kanban_card_color_field,
          cardAvatarField: modelMeta.kanban_card_avatar_field,
          cardProgressField: modelMeta.kanban_card_progress_field,
          columnTotalField: modelMeta.kanban_column_total_field,
          fields: modelMeta.fields
        };
      } catch (e) { console.error("Could not parse Kanban status options", e); }
    }
  }

  return (
    <Layout>
    <GenericCrudPage
      pageTitle={modelMeta.title}
      apiPath={`/projects/${projectId}/data/${modelName}`}
      columns={columns}
      formFields={formFields}
      defaultView={modelMeta.default_view || 'table'}
      defaultSort={{ field: 'id', order: 'desc' }}
      enableDateFilter={true}
      kanbanConfig={kanbanConfig}
    />
    </Layout>
  );
}

export default DynamicModelPage;