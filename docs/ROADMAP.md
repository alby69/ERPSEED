# ERPSEED Roadmap di Sviluppo

> **Nota:** Questo documento definisce la roadmap di qualità del codice, refactoring e debito tecnico (Fasi 0-4 KISS/DRY e Piano UX/UI). Per lo stato di avanzamento dei blocchi funzionali ERP (acquisti, vendite, contabilità, etc.), consulta [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md).

---

## Panoramica

Questa roadmap definisce le priorità di sviluppo per ERPSEED, organizzate per fasi. L'obiettivo è migliorare la qualità del codice (KISS/DRY), stabilizzare le funzionalità esistenti e aggiungere nuove feature in modo ordinato.

---

## 🚨 Fase 0: Stabilizzazione Critica (IMMEDIATA)

### Obiettivo: Rendere il progetto avviabile e testabile

| # | Task | Priorità | Complessità | Stato |
|---|------|----------|------------|-------|
| 0.1 | Riempire `requirements.txt` | 🔴 CRITICA | Bassa | ✅ COMPLETATO |
| 0.2 | Fix BaseModel duplicati | 🔴 CRITICA | Media | ✅ COMPLETATO |
| 0.3 | Aggiungere test base | 🔴 CRITICA | Media | ✅ COMPLETATO |
| 0.4 | Documentazione API completa | 🔴 CRITICA | Media | ✅ COMPLETATO |

### Dettagli Fase 0

#### 0.2 - Consolidare BaseModel
- Unificato `BaseModel` in `backend/core/models/base.py` con supporto soft delete e utility `to_dict`.
- `backend/models/base.py` mantenuto come proxy per retrocompatibilità.

---

## 🔧 Fase 1: Refactoring DRY (CORTO TERMINE)

### Obiettivo: Eliminare duplicazioni e centralizzare logica

| # | Task | Priorità | Complessità | Stato |
|---|------|----------|------------|-------|
| 1.1 | Centralizzare `paginate()` | 🟡 ALTA | Bassa | ✅ COMPLETATO |
| 1.2 | Centralizzare `check_unique()` | 🟡 ALTA | Bassa | ✅ COMPLETATO |
| 1.3 | Utility `safe_json_parse()` | 🟡 ALTA | Bassa | ✅ COMPLETATO |
| 1.4 | Consolidare schemi Marshmallow | 🟡 ALTA | Media | ✅ COMPLETATO |

### Dettagli Fase 1

#### 1.4 - Schemi Marshmallow
- Creato `backend/core/schemas/dynamic_schemas.py` per centralizzare gli schemi delle API dinamiche.

---

## 🏗️ Fase 2: Refactoring KISS (MEDIO TERMINE)

### Obiettivo: Semplificare componenti complesse

| # | Task | Priorità | Complessità | Stato |
|---|------|----------|------------|-------|
| 2.1 | Split `DynamicApiService` (945 righe) | 🟡 ALTA | Alta | ✅ COMPLETATO |
| 2.2 | Split `dynamic_api.py` (8 classi) | 🟡 ALTA | Media | ✅ COMPLETATO |
| 2.3 | Standardizzare pattern Service | 🟡 ALTA | Media | ✅ COMPLETATO |
| 2.4 | Riorganizzare `__init__.py` | 🟢 MEDIA | Bassa | ✅ COMPLETATO |

### Dettagli Fase 2

#### 2.1 - Split DynamicApiService
- Scomposto in `FieldValidator`, `QueryBuilder` e `ResultProcessor` sotto `backend/modules/dynamic_api/services/dynamic/`.

#### 2.2 - Split dynamic_api.py
- Rotte spostate in `backend/modules/dynamic_api/api/routes/`.

---

## 🎨 Fase A — UX/UI: Fondamenta del Design System

### Obiettivo: Stabilire token unificati, deprecare il layout ibrido e consolidare la navigazione

| # | Task | Priorità | Complessità | Stato |
|---|------|----------|------------|-------|
| A.1 | Design Token Layer (`frontend/src/theme/tokens.js`) | 🟡 ALTA | Bassa | ✅ COMPLETATO |
| A.2 | Deprecazione Bootstrap nelle pagine target | 🟡 ALTA | Media | ✅ COMPLETATO |
| A.3 | Consolidamento navigazione / eliminazione dead code | 🟡 ALTA | Bassa | ✅ COMPLETATO |
| A.4 | Standardizzazione libreria di charting (`@ant-design/charts`) | 🟢 MEDIA | Bassa | ✅ COMPLETATO |

### Dettagli Fase A — UX/UI

#### A.1 - Design Token Layer
- Creato `frontend/src/theme/tokens.js` con definizioni centralizzate per colori, spaziature, tipografia e bordi.
- Aggiornato `ThemeContext.jsx` per esporre `tokens` unificati.

#### A.2 - Deprecazione Bootstrap
- Sostituite le utility Bootstrap (`d-flex`, `mb-3`, `gap-2`, `p-5`, `list-group`) con componenti layout Ant Design (`Flex`, `Space`, `Card`, `List`) in `Dashboard.jsx`, `Products.jsx`, `Sales.jsx`, `PurchaseOrders.jsx`, e `SoggettiPage.jsx`.

#### A.3 - Consolidamento Navigazione
- Rimosso il file vuoto `frontend/src/pages/Sidebar.jsx` e confermato `components/Sidebar.jsx` come navigazione principale.

#### A.4 - Charting Standard
- Documentato `@ant-design/charts` come libreria di charting primaria in `docs/FRONTEND_GUIDE.md`.

---

## 📱 Fase B — UX/UI: Responsive Design (Mobile/Tablet)

### Obiettivo: Garantire usabilità e navigazione fluida su dispositivi mobile e tablet

| # | Task | Priorità | Complessità | Stato |
|---|------|----------|------------|-------|
| B.1 | Breakpoint layout principale (`breakpoint="lg"`, `collapsedWidth="0"`) | 🔴 CRITICA | Bassa | ✅ COMPLETATO |
| B.2 | Hook `useResponsive()` per rilevamento viewport | 🟡 ALTA | Bassa | ✅ COMPLETATO |
| B.3 | Banner avviso "desktop-optimized" per builder visuali | 🟢 MEDIA | Bassa | ✅ COMPLETATO |

### Dettagli Fase B — UX/UI

#### B.1 & B.2 - Responsive Layout & Hook
- Implementato l'hook custom `useResponsive.js` con suite di test Vitest (`useResponsive.test.js`).
- Aggiornato `ProjectLayout.jsx` con breakpoint `lg` e `collapsedWidth="0"` per collassare automaticamente la sidebar su viewport ridotti.

#### B.3 - Banner per Visual Builders
- Aggiunto banner d'avviso `Alert` in `WorkflowBuilder.jsx`, `DashboardBuilder.jsx` e `RelationshipManagerPage.jsx` quando visualizzati su schermi mobile.

---

## 📦 Fase 3: Nuove Features & Agentificazione (MEDIO-LUNGO TERMINE)

### Obiettivo: Espandere funzionalità e integrare AgentMesh

| # | Feature | Priorità | Complessità | Stato |
|---|---------|----------|------------|-------|
| 3.1 | Batch Import/Export UI | 🟢 MEDIA | Media | ✅ COMPLETATO |
| 3.2 | Workflow Visual Editor | 🟢 MEDIA | Alta | ✅ COMPLETATO |
| 3.3 | Dashboard Builder | 🟢 MEDIA | Media | ✅ COMPLETATO |
| 3.4 | AgentMesh Integration | 🔴 CRITICA | Alta | ✅ COMPLETATO (Base) |
| 3.5 | Capability Discovery | 🟡 ALTA | Media | ✅ COMPLETATO |
| 3.6 | Multi-language Support | 🟢 MEDIA | Media | ✅ COMPLETATO |

### Dettagli Fase 3
#### 3.1 - Batch Import/Export
- Implementata logica di Export in `DynamicApiService`. Endpoint `/export` aggiunto a `dynamic_io.py` e interfaccia di import/export integrata in `ProjectImportExportPage.jsx`.

---

## 🔒 Fase 4: Security & Performance (ONGOING)

### Obiettivo: Migliorare sicurezza e performance

| # | Task | Priorità | Complessità | Stato |
|---|------|----------|------------|-------|
| 4.1 | Rate Limiting | 🟡 ALTA | Bassa | ✅ COMPLETATO |
| 4.2 | Input Sanitization | 🟡 ALTA | Media | ✅ COMPLETATO |
| 4.3 | Query Optimization | 🟡 ALTA | Media | ⏳ TODO |
| 4.4 | Redis Caching | 🟢 MEDIA | Media | ✅ COMPLETATO |
| 4.5 | API Versioning | 🟢 MEDIA | Bassa | ✅ COMPLETATO |

---

## 📋 Gantt Aggiornato

```
2026 Q1 (Gennaio - Marzo)
├── Fase 0: Stabilizzazione
│   ├── ✅ requirements.txt
│   ├── ✅ Documentazione
│   └── ✅ BaseModel
│
├── Fase 1: DRY Refactoring
│   ├── ✅ paginate utility
│   ├── ✅ check_unique utility
│   └── ✅ safe_json_parse
│
└── Fase 2: KISS Refactoring
    ├── ✅ Split DynamicApiService
    └── ✅ Standardize Services (BaseService)

2026 Q2 (Aprile - Giugno)
├── Fase 3: Nuove Features & Agentificazione
│   ├── ✅ Batch Export/Import logic & UI
│   ├── ✅ Product Detail page & CRUD routes
│   ├── ✅ Dashboard Builder
│   ├── ✅ AgentMesh Core (Capability Registry)
│   └── ✅ Capability Discovery Endpoint
├── Fase 4: Security & Performance
│   ├── ✅ API Versioning (v1)
│   └── ✅ Tenant middleware JWT fallback fix
├── Fase A: UX/UI Design System
│   ├── ✅ tokens.js & ThemeContext integration
│   ├── ✅ Bootstrap deprecation (top 5 pages)
│   ├── ✅ Navigation consolidation
│   └── ✅ Charting library standard (@ant-design/charts)
├── Fase B: UX/UI Responsive Design
│   ├── ✅ Responsive hook (useResponsive.js)
│   ├── ✅ Responsive ProjectLayout Sider (breakpoint="lg")
│   └── ✅ Visual builders mobile optimization banners
└── Bug fixes
    ├── ✅ Entity blueprint URL alignment (/api/v1 instead of /api/v1/entities/{name})
    ├── ✅ Products API (GetProductCommand entity_id field)
    ├── ✅ Seed script (user.tenant_id assignment)
    └── ✅ apiClient JSON body serialization
```

### PR Guidelines

1. **Test coverage** - Nuove features richiedono test
2. **DRY** - Evitare duplicazione codice
3. **KISS** - Mantenere funzioni semplici (<100 righe target)
4. **Documentazione** - Aggiornare docs se necessario

---

*Per la cronologia completa delle modifiche di questo documento, consulta la cronologia Git del repository.*
