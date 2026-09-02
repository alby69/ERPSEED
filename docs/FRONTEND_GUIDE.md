# Frontend Developer Guide

## Tech Stack
- **Framework**: React 18/19
- **Build Tool**: Vite
- **UI Components**: Ant Design (antd)
- **Styling**: Bootstrap 5 (standard classes) + Ant Design Themes
- **State Management**: React Hooks + Context API + Zustand
- **API Communication**: Custom `apiFetch` utility with automatic JWT token management

## Getting Started
1. `cd frontend`
2. `npm install`
3. `npm run dev`

## Environment Variables
- `VITE_API_URL`: Base URL for backend API requests (default: `http://localhost:5000`). Configurable in `.env` or `.env.local`.

## Project Structure
- `src/components`: Reusable UI components (`GenericCrudPage.jsx`, `ColumnSettingsButton.jsx`, `ComponentRenderer.jsx`).
- `src/pages`: Individual application pages (Anagrafiche, Products, Sales, Accounting, HR, etc.).
- `src/hooks`: Custom React hooks (`useColumnManagerWithDrawer.js`, `useCrudData.js`).
- `src/utils.js`: Centralized utility functions (`apiFetch`, date/currency formatters).
- `src/ProjectLayout.jsx`: Layout wrapper with AppHeader, Sidebar, and Breadcrumbs.

---

## Core Component Code Examples

### 1. Standard CRUD Page with `GenericCrudPage`

`GenericCrudPage` handles data fetching, search, pagination, modal forms, and column settings automatically:

```jsx
import React from 'react';
import GenericCrudPage from '@/components/GenericCrudPage';

const TaxRatesPage = () => {
  const columns = [
    { title: 'Codice', dataIndex: 'code', key: 'code', sorter: true },
    { title: 'Descrizione', dataIndex: 'name', key: 'name' },
    {
      title: 'Aliquota %',
      dataIndex: 'rate',
      key: 'rate',
      render: (val) => `${val}%`
    },
  ];

  const formFields = [
    { name: 'code', label: 'Codice Aliquota', type: 'text', required: true },
    { name: 'name', label: 'Descrizione', type: 'text', required: true },
    { name: 'rate', label: 'Aliquota (%)', type: 'number', required: true },
  ];

  return (
    <GenericCrudPage
      title="Aliquote IVA"
      pageKey="tax_rates_page"
      apiEndpoint="/api/v1/tax-rates"
      columns={columns}
      formFields={formFields}
      searchField="name"
    />
  );
};

export default TaxRatesPage;
```

### 2. Custom Table with Column Customization (`useColumnManagerWithDrawer` + `ColumnSettingsButton`)

For pages using custom `<Table>` layout, use `useColumnManagerWithDrawer` to manage column visibility and ordering with localStorage persistence:

```jsx
import React from 'react';
import { Card, Table } from 'antd';
import { useColumnManagerWithDrawer } from '@/hooks/useColumnManagerWithDrawer';
import ColumnSettingsButton from '@/components/ColumnSettingsButton';

const CustomAddressesPage = ({ data, loading }) => {
  const rawColumns = [
    { title: 'ID', dataIndex: 'id', key: 'id' },
    { title: 'Via/Piazza', dataIndex: 'street', key: 'street' },
    { title: 'Civico', dataIndex: 'number', key: 'number' },
    { title: 'Città', dataIndex: 'city', key: 'city' },
    { title: 'CAP', dataIndex: 'zip_code', key: 'zip_code' },
  ];

  // Initializes hook with page key and original column definitions
  const colManager = useColumnManagerWithDrawer('custom_addresses_page', rawColumns);

  return (
    <Card
      title="Elenco Indirizzi"
      extra={<ColumnSettingsButton manager={colManager} />}
    >
      <Table
        rowKey="id"
        loading={loading}
        dataSource={data}
        columns={colManager.processedColumns}
      />
    </Card>
  );
};

export default CustomAddressesPage;
```

### 3. API Requests with `apiFetch`

Always use `apiFetch` from `@/utils.js` instead of raw `fetch` or `axios`. It automatically injects `VITE_API_URL`, appends the `Authorization: Bearer <token>` header, handles 401 refresh tokens, and formats error messages:

```javascript
import { apiFetch } from '@/utils';
import { message } from 'antd';

async function fetchProducts() {
  try {
    const data = await apiFetch('/api/v1/products?page=1&per_page=20');
    return data.items;
  } catch (error) {
    message.error(`Errore nel caricamento prodotti: ${error.message}`);
  }
}
```

---

## Best Practices
1. **Reuse Components**: Prefer `GenericCrudPage` for standard tabular data.
2. **Column Settings**: Integrate `useColumnManagerWithDrawer` for custom tables to offer user preference persistence.
3. **Styling**: Combine Ant Design components with Bootstrap spacing utilities (`mb-3`, `d-flex`, `gap-2`).
4. **i18n Translations**: Use `useTranslation()` from `react-i18next` for user-visible strings.

---

## Testing
- **Unit & Component Tests**: `npm run test:run` (Vitest + React Testing Library)
- **Interactive Watch Mode**: `npm test`
- **E2E Tests**: `npm run test:e2e` (Playwright)
