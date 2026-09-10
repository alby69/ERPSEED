# Frontend Developer Guide

## Tech Stack
- **Framework**: React 18/19
- **Build Tool**: Vite
- **UI Components**: Ant Design (`antd`)
- **Design Tokens & Themes**: `frontend/src/theme/tokens.js` + Ant Design `ConfigProvider`
- **Charting Standard**: `@ant-design/charts` (Primary standard for data visualizations)
- **State Management**: React Hooks + Context API + Zustand
- **API Communication**: Custom `apiFetch` utility with automatic JWT token management

## Getting Started
1. `cd frontend`
2. `npm install`
3. `npm run dev`

## Environment Variables
- `VITE_API_URL`: Base URL for backend API requests (default: `http://localhost:5000`). Configurable in `.env` or `.env.local`.

## Project Structure

```
frontend/src/
├── assets/                  # Immagini ed asset statici
├── components/              # COMPONENTI UI RIUTILIZZABILI
│   ├── archetypes/          #   Archetipi UI (FormArchetype, TableArchetype, GridArchetype, etc.)
│   ├── charts/              #   Componenti di charting (@ant-design/charts e adapter)
│   ├── core/                #   CommandPalette.jsx, ComponentRenderer, ArchetypeRegistry
│   ├── ui/                  #   InlineEditableTable.jsx, ProductLookupInput.jsx, AIAssistant, ImportExportToolbar
│   ├── workflow/            #   Nodi e proprietà per il Visual Workflow Builder
│   └── (root components)    #   GenericCrudPage, DataTable, ColumnSettingsButton, Sidebar, AppHeader, HelpDrawer, etc.
│
├── context/                 # Context Providers (AuthContext, ThemeContext, NotificationContext)
├── hooks/                   # Custom Hooks (useCommandPalette, useColumnManager, useResponsive, useCrudData)
├── lib/                     # Librerie e moduli frontend
│   └── cashrec/             #   Motore CashRec 100% client-side (engine, worker, parser, reporter)
├── locales/                 # Traduzioni i18n (it/translation.json, en/translation.json)
├── pages/                   # PAGINE APPLICATIVE (50+ pagine ERP, Dashboard, VisualBuilder, CashRecTool, etc.)
├── stores/                  # State management Zustand (workflowBuilderStore)
├── theme/                   # Token di design centralizzati (tokens.js)
├── utils/                   # Utility modulari (binding, dateUtils, exportUtils, sortable)
├── __tests__/               # Test unitari frontend (Vitest + React Testing Library)
├── App.jsx / ProjectLayout.jsx # Inizio applicazione e layout responsive principale
└── utils.js                 # Utility centralizzate (`apiFetch`, formattatori)
```

---

## Charting Library Standard

ERPSEED standardizes on **`@ant-design/charts`** as the primary charting library across all dashboards, reports, and analytics pages to ensure visual consistency and seamless integration with the Ant Design theme.

### Best Practices for Charts:
- **Primary Library**: Use `@ant-design/charts` for all new charts and dashboards (e.g., `Line`, `Bar`, `Pie`, `Column`, `Area`).
- **Legacy Adapters**: Legacy chart libraries (`ApexCharts`, `Chart.js`, `ECharts`) are kept solely for backward compatibility with existing user-generated chart templates and should not be used for new core features.

```jsx
import React from 'react';
import { Card } from 'antd';
import { Line } from '@ant-design/charts';

const SalesTrendChart = ({ data }) => {
  const config = {
    data,
    xField: 'date',
    yField: 'amount',
    point: { size: 5, shape: 'diamond' },
  };

  return (
    <Card title="Sales Trend">
      <Line {...config} />
    </Card>
  );
};

export default SalesTrendChart;
```

---

## Command Palette & Productive UX Shortcuts

ERPSEED include una **Global Command Palette** e scorciatoie da tastiera per un'esperienza ad alte prestazioni.

### 1. Command Palette (`Ctrl+K` / `Cmd+K`)
Il componente `<CommandPalette />` in `frontend/src/components/core/CommandPalette.jsx` è integrato nel `<ProjectLayout />` e gestito dallo stato dell'hook `useCommandPalette.js`.
- **Attivazione**: Premere `Ctrl+K` o `Cmd+K` da qualsiasi schermata dell'applicazione.
- **Funzionalità**:
  - Cerca istantaneamente tra le 50+ pagine della piattaforma ERP (Anagrafiche, Vendite, Acquisti, Magazzino, Contabilità, HR, Admin).
  - Offre azioni rapide (es. Nuovo Ordine, Apri AI Assistant, Cambia Tema/Lingua, Esegui CashRec).
  - Permette il filtraggio dinamico e la navigazione da tastiera (`Freccia Su/Giù` + `Invio`).

### 2. Global Keyboard Shortcuts
In `ProjectLayout.jsx` sono attivi gli event listener globali da tastiera:
- **`Ctrl+S` / `Cmd+S`**: Intercetta la combinazione di salvataggio ed esegue il submit del form attivo visibile nel DOM (modal, drawer o pagina corrente).
- **`Esc`**: Chiude automaticamente dialoghi, modal, drawer o la Command Palette se aperti.

---

## Responsive Viewport & Mobile Card View

ERPSEED gestisce il responsive design tramite l'hook `useResponsive()` (`frontend/src/hooks/useResponsive.js`).

- **Breakpoint Standard**: `lg` (992px) per la gestione della sidebar e del layout.
- **Mobile Card View**: In `<GenericCrudPage />`, quando `isMobile` è `true`, le tabelle dati vengono renderizzate automaticamente come griglie di `<Card>` espandibili, migliorando la fruibilità touchscreen.

```jsx
import useResponsive from '@/hooks/useResponsive';

const MobileAwareComponent = () => {
  const { isMobile, isTablet, isDesktop } = useResponsive();

  return (
    <div>
      {isMobile ? <MobileCardList /> : <DesktopDataTable />}
    </div>
  );
};
```

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

### 2. Document Line Editing (`InlineEditableTable` & `ProductLookupInput`)

Per la gestione avanzata di righe ordine di vendita e acquisto:

```jsx
import React, { useState } from 'react';
import InlineEditableTable from '@/components/ui/InlineEditableTable';
import ProductLookupInput from '@/components/ui/ProductLookupInput';

const OrderLineEditor = () => {
  const [lines, setLines] = useState([]);

  return (
    <InlineEditableTable
      value={lines}
      onChange={setLines}
      productLookupComponent={ProductLookupInput}
      currency="EUR"
    />
  );
};
```

### 3. Custom Table with Column Customization (`useColumnManagerWithDrawer` + `ColumnSettingsButton`)

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

### 4. API Requests with `apiFetch`

Always use `apiFetch` from `@/utils.js` instead of raw `fetch` or `axios`:

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
3. **Styling & Layout**: Use Ant Design layout components (`Space`, `Flex`, `Row`, `Col`) and central design tokens from `@/theme/tokens`.
4. **i18n Translations**: Use `useTranslation()` from `react-i18next` for user-visible strings.

---

## Testing
- **Unit & Component Tests**: `npm run test:run` (Vitest + React Testing Library)
- **Interactive Watch Mode**: `npm test`
- **E2E Tests**: `npm run test:e2e` (Playwright)

---

> Ultimo aggiornamento: 10 Settembre 2026 | [Torna all'Indice](INDEX.md)
