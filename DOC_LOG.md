# Documentation Overhaul Log

## [2026-06-11] Consolidamento e pulizia documentazione (docs/ overhaul)
- **Spostamento codice sorgente**: Spostato `docs/service.py` in `backend/modules/logistics/service.py` e rimossi i file Python orfani `docs/service.py` e `docs/api.py`.
- **Nuovo GETTING_STARTED.md**: Creato `docs/GETTING_STARTED.md` unificando setup Docker, setup locale e variabili d'ambiente. Eliminato `docs/QUICKSTART.md`.
- **Riorganizzazione DEVELOPER_GUIDE.md**: Spostate le sezioni di setup duplicate in `GETTING_STARTED.md` e aggiunta la sezione `## Convenzioni di Refactoring`.
- **Consolidamento Roadmap e Implementation Plan**: Spostate le appendici duplicate da `IMPLEMENTATION_PLAN.md` e `ROADMAP.md` a `DEVELOPER_GUIDE.md`. Chiarita la titolarità: `IMPLEMENTATION_PLAN.md` per i blocchi funzionali ERP, `ROADMAP.md` per la qualità del codice (KISS/DRY).
- **Consolidamento AgentMesh**: Uniti `AGENTMESH_DESIGN.md` e `AGENTMESH_INTEGRATION.md` nel nuovo `docs/AGENTMESH.md`. Eliminati i due file precedenti.
- **Unificazione Tutorial Fleet**: Fusi `TUTORIAL_FLEET_CLI.md` e `TUTORIAL_FLEET.md` in un unico `TUTORIAL_FLEET.md` con sezioni GUI e CLI e indice di navigazione iniziale. Eliminato `TUTORIAL_FLEET_CLI.md`.
- **Aggiornamento Strategia Branch**: Aggiornato `BRANCH_STRATEGY.md` indicando la unificazione su `main` e la gestione tramite feature branch.
- **Rimozione Archivio e README ridondanti**: Eliminata interamente la cartella `docs/archive/` (contenuto già confluito in roadmap e plan) ed eliminato `docs/README.md`.
- **Aggiornamento Indice e Links**: Riscritto `docs/INDEX.md` per mappare esattamente i 13 file attivi. Aggiornati i link in root `README.md` (puntatori da `backend/docs/` corretti in `docs/`).
- **Verifica finale**: Verificato con script automatizzato che 100% dei link Markdown interni siano validi (0 link rotti). Ridotto il numero di file `.md` in `docs/` da 19 a 13 attivi.

## [2026-06-09] Refactoring documentazione
- Creata `backend/docs/INDEX.md`: indice master che categorizza tutti i 21 documenti per area (overview, guides, api, tutorials, implementation, archive)
- Unificati duplicati: ERP_BLOCKS_ANALYSIS → fuso in IMPLEMENTATION_PLAN come Appendice A; ROADMAP_ANALYSIS → fuso in ROADMAP come Appendice
- Archiviati: QUESTIONS.md, ROADMAP_ANALYSIS.md, ERP_BLOCKS_ANALYSIS.md in `archive/`
- Sostituito `frontend/README.md` (placeholder Vite) con README specifico progetto
- Sostituito `requirements.txt` root con symlink a `backend/requirements.txt`
- Aggiornati: root README.md, backend/docs/README.md (indice sintetico con rinvio a INDEX.md)
- Verifica finale backend: 16/16 test passano; frontend lint: 0 errori

## [2026-06-10] Personalizza Colonne su tutte le pagine
- Creata `useColumnManagerWithDrawer` hook (convenience wrapper con drawer state)
- Creato `ColumnSettingsButton` componente (pulsante + drawer in unico componente)
- Refactoring IndirizziPage per usare i nuovi helper
- Aggiunta personalizzazione colonne a tutte le 44 pagine con tabelle
- Pages DRY: hook e componente condivisi, ogni pagina chiama 1 hook + 1 componente
- Escluse DashboardBuilder (tabelle dinamiche) e ModuleAppPage (tabelle da metadata)

## [2026-06-10] Aggiornamento documentazione — Soggetti form tab merge
- Uniti tab "Dati Principali" e "Dati Anagrafici" in unico tab "Dati Anagrafici" nel form Soggetto
- Aggiunti campi Cognome e Ragione Sociale al tab unificato
- Aggiornati tab di dettaglio (detailTabItems) per coerenza
- Rimossi 2 tab obsoleti: form ora ha 3 tab (Dati Anagrafici, Contatti, Ruoli)

## [2026-06-10] Aggiornamento documentazione — Indirizzi/Via/Logistica
- Aggiunto modello `Via` (cache locale strade per comune) con campi `comune_id`/`via_id` su `Indirizzo`
- Aggiunta API `GET /api/v1/vie/` con ricerca cache + Nominatim fallback; API `POST /api/v1/vie/bulk` per pre-caricamento
- Refactoring UX IndirizziPage: selezione città → autocomplete via → numero civico
- DistanceCalculator: mostra città di partenza/arrivo nei risultati
- Sidebar: spostato "Calcolo Distanze" (Logistica) dentro "Geografia"
- Aggiornati: README.md, API.md, ROADMAP.md, DEVELOPER_GUIDE.md, IMPLEMENTATION_PLAN.md, INDEX.md, tutorials/indirizzi.md
- docs synced with implementation

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
