# Changelog

All notable changes to the ERPSEED project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Global Command Palette**: Modal di comando globale (`frontend/src/components/core/CommandPalette.jsx` e `useCommandPalette.js`) attivabile con `Ctrl+K` / `Cmd+K` per navigazione immediata e azioni rapide su tutte le 50+ pagine della piattaforma.
- **Global Keyboard Shortcuts**: Scorciatoie produttive `Ctrl+S` / `Cmd+S` (salvataggio form/modal attivo) ed `Esc` (chiusura dialoghi e drawer).
- **Responsive Mobile Card View**: Conversione automatica delle tabelle in `<GenericCrudPage />` in griglie di `<Card>` espandibili quando `useResponsive().isMobile` è attivo (`<992px`).
- **Document Line Editing Components**: `InlineEditableTable.jsx` per l'editing delle righe ordine in tempo reale e `ProductLookupInput.jsx` per la ricerca articoli debounced con autocompletamento.
- **Enhanced Sales & Purchases Domain Models**: Estensione modelli e schemi di dominio per ordini di vendita ed acquisto con campi enterprise (`currency_id`, `pricelist_id`, `payment_term_id`, `billing_address_id`, `shipping_address_id`, `salesperson_id`, `buyer_id`, `customer_reference`, `supplier_reference`, `warehouse_id`, `landing_costs`, `tax_id` di riga, `discount_percent`, `uom_id`, `expected_delivery_date`).
- Responsive viewport hook (`frontend/src/hooks/useResponsive.js`) and unit test suite (`frontend/src/__tests__/useResponsive.test.js`).
- Mobile desktop-optimization alert banners for visual builders (`WorkflowBuilder.jsx`, `DashboardBuilder.jsx`, `RelationshipManagerPage.jsx`).
- Centralized UX/UI Design Token layer (`frontend/src/theme/tokens.js`) providing theme tokens for colors, spacing, radii, and typography.
- Unit tests for theme tokens and context (`frontend/src/__tests__/tokens.test.js`).
- Standardized `@ant-design/charts` primary charting library guidance in `docs/FRONTEND_GUIDE.md`.
- GitHub Actions CI/CD pipeline workflow (`.github/workflows/ci.yml`) covering backend Pytest, frontend Vitest, and Lychee markdown link checking.
- `@playwright/test` dependency and `"test:e2e"` script in `frontend/package.json`.
- Capabilities API discovery endpoint documentation (`/api/v1/ai/capabilities`) and Purchase Returns endpoints (`/api/v1/purchase-returns`) in `docs/API.md`.
- Comprehensive business user operational guides for all 24 ERP modules in `docs/USER_MANUAL.md`.
- Column customization code examples (`useColumnManagerWithDrawer` and `ColumnSettingsButton`) in `docs/FRONTEND_GUIDE.md`.

### Changed
- **Completamento Roadmap Q3-Q4 2026**: Raggiungimento del 100% degli obiettivi previsti in `docs/ROADMAP.md` (UX/UI Excellence, Command Palette, Shortcuts, Mobile Card View, Data Models, i18n).
- Configured responsive breakpoint (`lg`) and auto-collapse (`collapsedWidth="0"`) on `ProjectLayout.jsx` Sider for mobile/tablet navigation (<992px).
- Fixed template listing sorting in `TemplateService` to ensure deterministic ordering across all file systems.
- Refactored `Dashboard.jsx`, `Products.jsx`, `Sales.jsx`, `PurchaseOrders.jsx`, and `SoggettiPage.jsx` to replace Bootstrap utility classes with native Ant Design layout components (`Flex`, `Space`, `Card`, `List`).
- Removed unused empty file `frontend/src/pages/Sidebar.jsx`.
- Reconciled status of all 24 ERP blocks across `docs/IMPLEMENTATION_PLAN.md` to reflect completed implementations.
- Updated multi-tenancy documentation in `docs/ARCHITECTURE.md` to accurately represent Row-Level Isolation (`tenant_id` + `TenantFilter`) and documented `tenant_filter.py` as primary while `query_filter.py` is deprecated.
- Updated `docs/DEVELOPER_GUIDE.md` tutorial for creating new modules to enforce the CQRS pattern.
- Converted core architecture and dependency diagrams in `docs/ARCHITECTURE.md` and `docs/IMPLEMENTATION_PLAN.md` to GitHub-native Mermaid syntax.
- Standardized documentation metadata footers across `docs/`.

## [1.0.0] - 2026-06-11

### Added
- Completed all 24 vertical ERP blocks (Accounting, Invoicing, Purchases & Returns, Sales & CRM, Inventory, Manufacturing, HR Payroll & Training, Project Management, Analytics).
- Electronic invoicing XML generation (`FatturaElettronicaPA 1.2`).
- AgentMesh adapter gateway and capabilities registry for agentic ERP integration.
- Redis caching layer on high-traffic GET endpoints (Maturities, VAT, Inventory).
- Table column customization (`Personalizza Colonne`) across 44 UI pages.
