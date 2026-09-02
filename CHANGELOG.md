# Changelog

All notable changes to the ERPSEED project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- GitHub Actions CI/CD pipeline workflow (`.github/workflows/ci.yml`) covering backend Pytest, frontend Vitest, and Lychee markdown link checking.
- `@playwright/test` dependency and `"test:e2e"` script in `frontend/package.json`.
- Capabilities API discovery endpoint documentation (`/api/v1/ai/capabilities`) and Purchase Returns endpoints (`/api/v1/purchase-returns`) in `docs/API.md`.
- Comprehensive business user operational guides for all 24 ERP modules in `docs/USER_MANUAL.md`.
- Column customization code examples (`useColumnManagerWithDrawer` and `ColumnSettingsButton`) in `docs/FRONTEND_GUIDE.md`.

### Changed
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
