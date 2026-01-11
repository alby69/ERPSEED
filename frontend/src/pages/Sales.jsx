import { GenericCrudPage } from '../components';
import { apiFetch } from '../utils';

function Sales() {
  const currencyFormatter = new Intl.NumberFormat('it-IT', { style: 'currency', currency: 'EUR' });

  const handlePrintPdf = async (id) => {
    try {
      const res = await apiFetch(`/sales/${id}/pdf`);
      
      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        window.open(url, '_blank'); // Apre il PDF in una nuova scheda
      } else {
        alert("Errore nella generazione del PDF");
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Colonne della tabella principale (Lista Ordini)
  const columns = [
    { header: 'Numero', accessor: 'number' },
    { 
      header: 'Data', 
      accessor: 'date',
      render: (row) => row.date ? new Date(row.date).toLocaleDateString() : ''
    },
    { header: 'Cliente', accessor: 'customer.name' }, // Accesso semantico
    { 
      header: 'Totale', 
      accessor: 'total_amount',
      render: (row) => currencyFormatter.format(row.total_amount || 0)
    },
    { 
      header: 'Stato', 
      accessor: 'status',
      render: (row) => (
        <span className={`badge ${row.status === 'confirmed' ? 'bg-success' : 'bg-secondary'}`}>
          {row.status}
        </span>
      )
    },
    {
      header: 'Stampa',
      render: (row) => (
        <button 
          className="btn btn-sm btn-outline-dark" 
          onClick={() => handlePrintPdf(row.id)}
          title="Stampa PDF"
        >
          🖨️ PDF
        </button>
      )
    }
  ];

  // Configurazione del Form (Testata + Righe)
  const formFields = [
    { name: 'number', label: 'Numero Ordine', required: true },
    { name: 'date', label: 'Data', type: 'date', required: true },
    { 
      name: 'customer_id', 
      label: 'Cliente', 
      type: 'select', 
      apiUrl: '/parties?type=company', 
      valueKey: 'id', 
      labelKey: 'name',
      required: true
    },
    { 
      name: 'status', 
      label: 'Stato', 
      type: 'select', 
      options: [
        { value: 'draft', label: 'Bozza' },
        { value: 'confirmed', label: 'Confermato' },
        { value: 'done', label: 'Completato' }
      ],
      defaultValue: 'draft'
    },
    
    // Configurazione Master-Detail (Righe Ordine)
    { 
      name: 'lines', 
      type: 'lines', 
      label: 'Prodotti',
      // Colonne della tabellina interna
      columns: [
        { header: 'Prodotto', accessor: 'product_id' },
        { header: 'Q.tà', accessor: 'quantity' },
        { header: 'Prezzo', accessor: 'unit_price', render: r => currencyFormatter.format(r.unit_price) },
        { header: 'Totale', accessor: 'total', render: r => currencyFormatter.format(r.total || 0) }
      ],
      // Campi del form inline
      fields: [
        { 
          name: 'product_id', 
          label: 'Prodotto', 
          type: 'select', 
          apiUrl: '/products', 
          valueKey: 'id', 
          labelKey: 'name', 
          colClass: 'col-md-5' 
        },
        { name: 'quantity', label: 'Quantità', type: 'number', defaultValue: 1, colClass: 'col-md-2' },
        { name: 'unit_price', label: 'Prezzo', type: 'number', colClass: 'col-md-2' },
        { name: 'total', label: 'Totale', type: 'number', readOnly: true, colClass: 'col-md-3' }
      ],
      // Logica di calcolo automatica
      compute: (row, options) => {
        if (row.product_id && options && options.product_id) {
           const product = options.product_id.find(p => String(p.id) === String(row.product_id));
           if (product && (!row.unit_price || row.unit_price == 0)) {
               row.unit_price = product.price;
           }
        }
        const qty = parseFloat(row.quantity) || 0;
        const price = parseFloat(row.unit_price) || 0;
        row.total = (qty * price).toFixed(2);
        return row;
      }
    }
  ];

  return (
    <GenericCrudPage 
      pageTitle="Ordini di Vendita" 
      apiPath="/sales" 
      columns={columns} 
      formFields={formFields} 
    />
  );
}

export default Sales;