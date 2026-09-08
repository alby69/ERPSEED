# Changelog

All notable changes to the ERPSEED project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Centralized UX/UI Design Token layer (`frontend/src/theme/tokens.js`) providing theme tokens for colors, spacing, radii, and typography.
- Unit tests for theme tokens and context (`frontend/src/__tests__/tokens.test.js`).
- Standardized `@ant-design/charts` primary charting library guidance in `docs/FRONTEND_GUIDE.md`.
- GitHub Actions CI/CD pipeline workflow (`.github/workflows/ci.yml`) covering backend Pytest, frontend Vitest, and Lychee markdown link checking.
- `@playwright/test` dependency and `"test:e2e"` script in `frontend/package.json`.
- Capabilities API discovery endpoint documentation (`/api/v1/ai/capabilities`) and Purchase Returns endpoints (`/api/v1/purchase-returns`) in `docs/API.md`.
- Comprehensive business user operational guides for all 24 ERP modules in `docs/USER_MANUAL.md`.
- Column customization code examples (`useColumnManagerWithDrawer` and `ColumnSettingsButton`) in `docs/FRONTEND_GUIDE.md`.

### Changed
- Refactored `Dashboard.jsx`, `Products.jsx`, `Sales.jsx`, `PurchaseOrders.jsx`, `SoggettiPage.jsx`, `ProjectDetail.jsx`, `SysChartBuilder.jsx`, `SysModelDetail.jsx`, `ResetPassword.jsx`, and `RuoliPage.jsx` to replace legacy Bootstrap utility classes with native Ant Design layout components (`Flex`, `Space`, `Card`, `List`, `Modal`, `Form`, `Input`, `Select`, `Breadcrumb`, `Avatar`, `Badge`, `Tag`, `Row`, `Col`).
- Removed unused empty file `frontend/src/pages/Sidebar.jsx`.
- Reconciled status of all 24 ERP blocks across `docs/IMPLEMENTATION_PLAN.md` and `docs/ROADMAP.md` to reflect completed implementations and Phase A Design System alignment.
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
