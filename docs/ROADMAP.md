# ERPSEED Roadmap di Sviluppo

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

**Problema Risolto:**
- Unificato `BaseModel` in `backend/core/models/base.py` con supporto soft delete.
- `backend/models/base.py` funge da proxy per compatibilità.

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

## 📦 Fase 3: Nuove Features & Agentificazione (MEDIO-LUNGO TERMINE)

### Obiettivo: Espandere funzionalità e integrare AgentMesh

| # | Feature | Priorità | Complessità | Stato |
|---|---------|----------|------------|-------|
| 3.1 | Batch Import/Export UI | 🟢 MEDIA | Media | ✅ PARZIALE |
| 3.2 | Workflow Visual Editor | 🟢 MEDIA | Alta | ✅ COMPLETATO |
| 3.3 | Dashboard Builder | 🟢 MEDIA | Media | ✅ COMPLETATO |
| 3.4 | AgentMesh Integration | 🔴 CRITICA | Alta | ✅ COMPLETATO (Base) |
| 3.5 | Capability Discovery | 🟡 ALTA | Media | ✅ COMPLETATO |
| 3.6 | Multi-language Support | 🟢 MEDIA | Media | ✅ COMPLETATO |

### Dettagli Fase 3
#### 3.1 - Batch Import/Export
- Implementata logica di Export in `DynamicApiService`. Endpoint `/export` aggiunto a `dynamic_io.py`.

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
│   ├── ✅ Batch Export logic
│   ├── ✅ Product Detail page & CRUD routes
│   ├── ✅ Dashboard Builder
│   ├── ✅ AgentMesh Core (Capability Registry)
│   └── ✅ Capability Discovery Endpoint
├── Fase 4: Security & Performance
│   ├── ✅ API Versioning (v1)
│   └── ✅ Tenant middleware JWT fallback fix
└── Bug fixes
    ├── ✅ Entity blueprint URL alignment (/api/v1 instead of /api/v1/entities/{name})
    ├── ✅ Products API (GetProductCommand entity_id field)
    ├── ✅ Seed script (user.tenant_id assignment)
    └── ✅ apiClient JSON body serialization

### PR Guidelines

1. **Test coverage** - Nuove features richiedono test
2. **DRY** - Evitare duplicazione codice
3. **KISS** - Mantenere funzioni semplici (<100 righe target)
4. **Documentazione** - Aggiornare docs se necessario

---

> **Nota:** Parallelamente a questa roadmap di qualità, tutti i 24 blocchi ERP del [Piano di Implementazione](IMPLEMENTATION_PLAN.md) sono stati completati (modelli, API, frontend). Vedi [API.md](API.md) per la lista completa degli endpoint.

---

## Appendice — Guida al Refactoring per Sviluppatori

Quando si modifica un modulo esistente:
1. **Verificare il BaseModel**: Assicurarsi di importare da `backend.core.models.base` (non `backend.models.base`).
2. **Usare BaseService**: Se il servizio fa CRUD semplice, non riscrivere i metodi, usa quelli ereditati da `backend.core.services.base.BaseService`.
3. **Disaccoppiamento**: Non importare servizi direttamente se possibile; usare il pattern `ServiceProxy` o l'iniezione tramite container.
4. **Schema unico**: Usare `backend.core.schemas.dynamic_schemas` per centralizzare gli schemi Marshmallow delle API dinamiche.

---

*Ultimo aggiornamento: 2026-06-10*
