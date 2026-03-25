import React from 'react';
import GenericCrudPage from '../components/GenericCrudPage';

function Users() {
  const columns = [
    { accessor: 'id', header: 'ID' },
    {
      header: 'Avatar',
      render: (row) => (
        <img
          src={row.avatar ? `http://localhost:5000/uploads/${row.avatar}` : `https://ui-avatars.com/api/?name=${row.first_name}+${row.last_name}&background=random`}
          alt="Avatar"
          style={{ width: '32px', height: '32px', objectFit: 'cover', borderRadius: '50%' }}
        />
      )
    },
    { accessor: 'email', header: 'Email' },
    { accessor: 'first_name', header: 'Nome' },
    { accessor: 'last_name', header: 'Cognome' },
    { accessor: 'role', header: 'Ruolo' },
    { accessor: 'is_active', header: 'Attivo', type: 'boolean' }
  ];

  const formFields = [
    { name: 'email', label: 'Email', type: 'email', required: true },
    { name: 'password', label: 'Password', type: 'password' },
    { name: 'first_name', label: 'Nome', type: 'text' },
    { name: 'last_name', label: 'Cognome', type: 'text' },
    { name: 'role', label: 'Ruolo', type: 'select', options: ['admin', 'user'] },
    { name: 'avatar', label: 'Avatar', type: 'file' },
    { name: 'is_active', label: 'Attivo', type: 'checkbox', defaultValue: true }
  ];

  return (
    <GenericCrudPage
      pageTitle="Gestione Utenti"
      apiPath="/users"
      columns={columns}
      formFields={formFields}
    />
  );
}

export default Users;