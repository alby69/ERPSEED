# Frontend Developer Guide

## Tech Stack
- **Framework**: React 18/19
- **Build Tool**: Vite + PWA (`vite-plugin-pwa`)
- **UI Components**: Ant Design (`antd`)
- **Design Tokens & Themes**: `frontend/src/theme/tokens.js` + Ant Design `ConfigProvider`
- **Charting Standard**: `@ant-design/charts` (Primary standard for data visualizations)
- **State Management**: TanStack Query (`@tanstack/react-query`) + React Hooks + Context API + Zustand
- **Forms & Validation**: React Hook Form + Zod (`zod`, `@hookform/resolvers/zod`)
- **API Communication**: Custom `apiFetch` utility integrated with TanStack Query and JWT token management

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
│   ├── ui/                  #   KanbanView.jsx, PivotTable.jsx, ContextualDrawer.jsx, KnowledgeDrawer.jsx, InlineEditableTable.jsx
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

## UI/UX Components & Advanced Views

### 1. Advanced Contextual Components
- **`KanbanView.jsx`**: Visualizzazione a colonne trascinabili/raggruppate per stati (CRM, progetti, ordini).
- **`PivotTable.jsx`**: Tabella pivot analitica per aggregazioni dinamiche su report e KPI.
- **`ContextualDrawer.jsx`**: Drawer laterale per ispezionare/modificare entità collegate senza abbandonare la vista attiva.
- **`KnowledgeDrawer.jsx`**: Pannello di aiuto e documentazione operativa contestuale alla pagina (accessibile tramite il pulsante `?` in `AppHeader`).

### 2. Field-Level RBAC & Dynamic Columns
`GenericCrudPage.jsx` interroga automaticamente `/api/v1/users/permissions` al caricamento e nasconde o maschera campi e colonne ristrette (`hidden_fields`, es. `cost_price`, `margin`) in base al ruolo dell'utente corrente.

### 3. Command Palette (`Ctrl+K` / `Cmd+K`)
Il componente `<CommandPalette />` (`frontend/src/components/core/CommandPalette.jsx`) esegue ricerche debounced verso `/api/v1/global/search?q=` consentendo la navigazione istantanea tra pagine e record.

---

## Charting Library Standard

ERPSEED standardizes on **`@ant-design/charts`** as the primary charting library across all dashboards, reports, and analytics pages to ensure visual consistency and seamless integration with the Ant Design theme.

---

## Responsive Viewport & Mobile Card View

ERPSEED gestisce il responsive design tramite l'hook `useResponsive()` (`frontend/src/hooks/useResponsive.js`).

- **Breakpoint Standard**: `lg` (992px) per la gestione della sidebar e del layout.
- **Mobile Card View**: In `<GenericCrudPage />`, quando `isMobile` è `true`, le tabelle dati vengono renderizzate automaticamente come griglie di `<Card>` espandibili con Skeleton Loading durante le fasi di fetching.

---

## Testing
- **Unit & Component Tests**: `npm --prefix frontend run test:run` (Vitest + React Testing Library)
- **E2E Tests**: `npm run test:e2e` (Playwright)

---

> Ultimo aggiornamento: 21 Ottobre 2026 | [Torna all'Indice](INDEX.md)
