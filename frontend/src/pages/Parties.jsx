import { GenericCrudPage } from '../components';

function Parties() {
  // Configurazione delle Colonne della Tabella
  const columns = [
    { header: 'Nome', accessor: 'name' },
    { 
      header: 'Tipo', 
      accessor: 'type', 
      render: (row) => (
        <span className={`badge ${row.type === 'company' ? 'bg-info' : 'bg-success'}`}>
          {row.type === 'company' ? 'Azienda' : 'Persona'}
        </span>
      )
    },
    { header: 'Email', accessor: 'email' },
    { header: 'P.IVA / C.F.', render: (row) => row.vat_number || row.fiscal_code }
  ];

  // Configurazione dei Campi del Form
  const formFields = [
    { name: 'name', label: 'Nome / Ragione Sociale', required: true },
    { 
      name: 'type', 
      label: 'Tipo', 
      type: 'select', 
      options: [{ value: 'company', label: 'Azienda' }, { value: 'person', label: 'Persona Fisica' }],
      defaultValue: 'company'
    },
    { name: 'email', label: 'Email', type: 'email' },
    { name: 'phone', label: 'Telefono' },
    { name: 'vat_number', label: 'Partita IVA', colClass: 'col-md-6' },
    { name: 'fiscal_code', label: 'Codice Fiscale', colClass: 'col-md-6' }
  ];

  const filterTabs = [
    { label: 'Tutti', filters: {} },
    { label: 'Aziende', filters: { type: 'company' } },
    { label: 'Persone', filters: { type: 'person' } }
  ];

  return (
    <GenericCrudPage 
      pageTitle="Anagrafiche" 
      apiPath="/parties" 
      columns={columns} 
      formFields={formFields} 
      filterTabs={filterTabs}
    />
  );
}

export default Parties;