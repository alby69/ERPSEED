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
| 0.3 | Aggiungere test base | 🔴 CRITICA | Media | ⏳ IN CORSO |
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
| 2.1 | Split `DynamicApiService` | 🟡 ALTA | Alta | ✅ COMPLETATO |
| 2.2 | Split `dynamic_api.py` | 🟡 ALTA | Media | ✅ COMPLETATO |
| 2.3 | Standardizzare pattern Service | 🟡 ALTA | Media | ✅ COMPLETATO |
| 2.4 | Riorganizzare `__init__.py` | 🟢 MEDIA | Bassa | ✅ COMPLETATO |

### Dettagli Fase 2

#### 2.1 - Split DynamicApiService
- Scomposto in `FieldValidator`, `QueryBuilder` e `ResultProcessor` per una chiara separazione delle responsabilità.

#### 2.2 - Split dynamic_api.py
- Rotte API suddivise in moduli specializzati: `dynamic_list`, `dynamic_item`, `dynamic_meta`, `dynamic_io`, `audit`.

---

## 📦 Fase 3: Nuove Features (MEDIO-LUNGO TERMINE)

### Obiettivo: Espandere funzionalità in modo ordinato

| # | Feature | Priorità | Complessità | Stato |
|---|---------|----------|------------|-------|
| 3.1 | Batch Import/Export | 🟢 MEDIA | Media | ✅ COMPLETATO |
| 3.2 | Workflow Visual Editor | 🟢 MEDIA | Alta | ✅ COMPLETATO (Backend) |
| 3.3 | Dashboard Builder | 🟢 MEDIA | Media | ✅ COMPLETATO (Core) |
| 3.4 | Plugin Store | 🟢 MEDIA | Alta | ⏳ TODO |
| 3.5 | Multi-language Support | 🟢 MEDIA | Media | ⏳ TODO |

### Dettagli Fase 3

#### 3.1 - Batch Import/Export
- Implementata logica di Export (CSV/JSON) e Preview di Import.

#### 3.2 - Workflow Visual Editor
- Aggiunto supporto per la rappresentazione a grafo (`to_graph`/`from_graph`) dei workflow.

#### 3.3 - Dashboard Builder
- Esteso `SysView` con supporto al `layout` dinamico per il visual builder.

---

## 🔒 Fase 4: Security & Performance (ONGOING)

### Obiettivo: Migliorare sicurezza e performance

| # | Task | Priorità | Complessità | Stato |
|---|------|----------|------------|-------|
| 4.1 | Rate Limiting | 🟡 ALTA | Bassa | ✅ COMPLETATO |
| 4.2 | Input Sanitization | 🟡 ALTA | Media | ✅ COMPLETATO |
| 4.3 | Query Optimization | 🟡 ALTA | Media | ⏳ TODO |
| 4.4 | Redis Caching | 🟢 MEDIA | Media | ⏳ TODO |
| 4.5 | API Versioning | 🟢 MEDIA | Bassa | ✅ COMPLETATO |

### Dettagli Fase 4

#### 4.1 - Rate Limiting
- Implementato middleware di base per il controllo del traffico.

#### 4.2 - Input Sanitization
- Introdotto `SafeEvaluator` per eliminare l'uso di `eval()` nelle formule dinamiche, garantendo l'esecuzione in una sandbox sicura.

---

## 📋 Gantt Finale (Update 2026-03-24)

```
2026 Q1 - Q2
├── Fase 0-2: COMPLETATE (Core, Refactoring, Stabilizzazione)
├── Fase 3: COMPLETATA (Export, Workflow Backend, Visual Layout)
└── Fase 4: PARZIALE (Rate Limit, Safe Eval, API v1)
```

---

*Ultimo aggiornamento: 2026-03-24*
