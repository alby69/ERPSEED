import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useCrudData } from '../hooks/useCrudData';
import { Layout, DataTable, Pagination, SearchBar } from '../components';

function Sales() {
  const navigate = useNavigate();
  const { data, loading, error, pagination, setPage, setFilters, setSort, sort } = useCrudData('/sales-orders');

  const currencyFormatter = new Intl.NumberFormat('it-IT', { style: 'currency', currency: 'EUR' });

  const columns = [
    { accessor: 'id', header: 'ID', sortField: 'id' },
    { accessor: 'party.name', header: 'Customer', sortField: 'party.name' },
    { accessor: 'order_date', header: 'Order Date', render: (row) => new Date(row.order_date).toLocaleDateString(), sortField: 'order_date' },
    { accessor: 'total_amount', header: 'Total', render: (row) => currencyFormatter.format(row.total_amount), sortField: 'total_amount' },
    { accessor: 'status', header: 'Status', sortField: 'status' },
  ];
  
  const handleEdit = (item) => {
    navigate(`/sales/${item.id}`);
  };

  const handleNew = () => {
    navigate('/sales/new'); // Rotta per creare un nuovo ordine
  };

  return (
    <Layout>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Sales Orders</h2>
        <div className="d-flex align-items-center gap-2">
          <SearchBar onSearch={(term) => setFilters({ q: term })} />
          <button className="btn btn-primary" onClick={handleNew}>New Order</button>
        </div>
      </div>

      {loading && <div className="text-center">Loading...</div>}
      {error && <div className="alert alert-danger">{error}</div>}
      
      <DataTable
        columns={columns}
        data={data}
        onEdit={handleEdit} // Passa la funzione di navigazione
        onDelete={null} // La cancellazione avverrà nella pagina di dettaglio
        sortConfig={{ key: sort.field, direction: sort.order }}
        onSort={(field) => setSort(field)}
      />
      
      <Pagination
        currentPage={pagination.page}
        totalPages={pagination.totalPages}
        onPageChange={(page) => setPage(page)}
      />
    </Layout>
  );
}

export default Sales;