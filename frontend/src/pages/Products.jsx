import { GenericCrudPage } from '../components';

function Products() {
  const currencyFormatter = new Intl.NumberFormat('it-IT', {
    style: 'currency',
    currency: 'EUR',
  });

  const columns = [
    { 
      header: 'Immagine', 
      render: (row) => (
        row.image ? (
          <img 
            src={`http://localhost:5000/uploads/${row.image}`} 
            alt={row.name} 
            style={{ width: '50px', height: '50px', objectFit: 'cover', borderRadius: '4px' }} 
          />
        ) : <span className="text-muted small">No img</span>
      )
    },
    { header: 'SKU', accessor: 'sku' },
    { header: 'Nome', accessor: 'name' },
    { 
      header: 'Prezzo', 
      accessor: 'price',
      render: (row) => row.price ? currencyFormatter.format(row.price) : ''
    },
    { header: 'Giacenza', accessor: 'stock_quantity' }
  ];

  const formFields = [
    { name: 'name', label: 'Nome Prodotto', required: true },
    { name: 'sku', label: 'Codice SKU', required: true },
    { name: 'price', label: 'Prezzo', type: 'number' },
    { name: 'stock_quantity', label: 'Giacenza Iniziale', type: 'number', defaultValue: 0 },
    { 
      name: 'supplier_id', 
      label: 'Fornitore', 
      type: 'select', 
      apiUrl: '/parties?type=company', 
      valueKey: 'id', 
      labelKey: 'name' 
    },
    { name: 'description', label: 'Descrizione', type: 'textarea' },
    { name: 'image', label: 'Immagine', type: 'file' }
  ];

  return (
    <GenericCrudPage 
      pageTitle="Prodotti" 
      apiPath="/products" 
      columns={columns} 
      formFields={formFields} 
    />
  );
}

export default Products;