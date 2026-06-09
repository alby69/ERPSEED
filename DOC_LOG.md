# Documentation Overhaul Log

## [2026-06-09] Refactoring documentazione
- Creata `backend/docs/INDEX.md`: indice master che categorizza tutti i 21 documenti per area (overview, guides, api, tutorials, implementation, archive)
- Unificati duplicati: ERP_BLOCKS_ANALYSIS → fuso in IMPLEMENTATION_PLAN come Appendice A; ROADMAP_ANALYSIS → fuso in ROADMAP come Appendice
- Archiviati: QUESTIONS.md, ROADMAP_ANALYSIS.md, ERP_BLOCKS_ANALYSIS.md in `archive/`
- Sostituito `frontend/README.md` (placeholder Vite) con README specifico progetto
- Sostituito `requirements.txt` root con symlink a `backend/requirements.txt`
- Aggiornati: root README.md, backend/docs/README.md (indice sintetico con rinvio a INDEX.md)
- Verifica finale backend: 16/16 test passano; frontend lint: 0 errori

## [2026-06-09] Verifica finale e aggiornamento avanzamento
- Eseguita verifica backend: 17/18 test passano (1 pre-esistente fallisce: test_dynamic_model_creation)
- Eseguito lint frontend: 9 nuove pagine pulite (0 errori, 0 warning)
- Backend: fixato import Invoice mancante in maturities/vat API, mappati campi su plugin Invoice
- Backend: tutti i modelli nuovi compilano senza errori
- Fixati 6 errori lint nelle pagine frontend (unused vars, empty catch)
- Rimosso duplicato Invoice model, riusato plugin accounting
- Documentazione aggiornata con risultati verifica

## [2026-04-23] Initial Setup
- Created branch `feature/documentation-refactor` from `main`.
- Initialized `DOC_LOG.md` and `QUESTIONS.md`.
- Started analysis of the project structure.
## [2026-04-23] Backend & Frontend Systematic Documentation
- Documented core backend components: Application Factory, BaseService, Utility module, DI Container, Tenant Middleware.
- Documented key backend models: User, Project, System (SysModel, SysField, etc.).
- Documented key frontend components: apiFetch utility, GenericCrudPage.

## [2026-04-23] Markdown Documentation Expansion
- Created `backend/docs/TUTORIAL_FLEET.md`: A step-by-step tutorial for building a Fleet Management project.
- Created `backend/docs/USER_MANUAL.md`: A high-level guide for non-technical users.
- Created `frontend/docs/FRONTEND_GUIDE.md`: Specific documentation for frontend developers.
