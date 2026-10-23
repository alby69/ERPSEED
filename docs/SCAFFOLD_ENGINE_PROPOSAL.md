# 🚀 [PROPOSTA ROADMAP] Sistema di Generazione "Schema-as-Code" (Template Componibili)

> **Destinatario**: `google-labs-jules[bot]` e Team di Sviluppo ERPSEED
> **Obiettivo**: Accelerare lo sviluppo di nuovi moduli ERP da zero trasformando descrizioni testuali dichiarative in artefatti di codice completi (DB, API, UI) tramite il pattern CQRS esistente.
> **Stato**: ✅ COMPLETATO (Fase 6 implementata integralmente)

---

## 1. Concetto Architetturale
Il sistema introduce un **Motore di Scaffolding CQRS**. Un template testuale (YAML/Markdown) non genera direttamente file, ma viene parsato in una serie di **Comandi di Dominio** che, eseguiti, materializzano gli oggetti nel sistema. Questo garantisce coerenza con l'architettura esistente (`backend/core/event_bus.py` e `modules/<nome>/service_api.py`).

### Flusso di Esecuzione
1. **Input**: Testo dichiarativo (es. `template_sales_order.yaml`).
2. **Parsing**: `TemplateParser` converte il testo in una lista di comandi.
3. **Dispatch**: I comandi vengono inviati al bus (`execute(command)`).
4. **Materializzazione**:
   - `RegisterEntityCommand` → Aggiorna `SysModel` (P0 ER Engine).
   - `ScaffoldBackendCommand` → Genera file `.py` (SQLAlchemy, Marshmallow, CQRS Handlers).
   - `ScaffoldFrontendCommand` → Genera file `.jsx` (Ant Design, riutilizzando `InlineEditableTable` e `ProductLookupInput`).
   - `GenerateMigrationCommand` → Prepara lo script Alembic.

---

## 2. Specifica della Sintassi del Template (DSL Ibrido)
I template devono essere componibili (ereditarietà) e leggibili.

```yaml
# Esempio: templates/sales_order.yaml
module: sales
entity: SalesOrder
extends: BaseDocument # Eredita: id, created_at, updated_at, created_by

metadata:
  label: "Ordine di Vendita"
  icon: "ShoppingCartOutlined"

fields:
  - name: order_number
    type: string
    constraints: [required, unique]
    ui: { label: "Numero Ordine", width: 150 }
  - name: order_date
    type: date
    default: now
    ui: { label: "Data Ordine" }
  - name: total_amount
    type: decimal
    ui: { label: "Totale", readonly: true }

relations:
  - name: customer
    target: entities.Subject
    type: many_to_one
    ui: { component: "ProductLookupInput", label: "Cliente" } # Riutilizzo componente esistente
  - name: lines
    target: sales.SalesOrderLine
    type: one_to_many
    cascade: all
    ui: { component: "InlineEditableTable", label: "Righe Ordine" } # Riutilizzo componente esistente

permissions:
  create: ["admin", "sales_manager"]
  read: ["admin", "sales_manager", "viewer"]
```

---

## 3. Fasi di Implementazione (Da aggiungere a ROADMAP.md)

### Fase 6.1: Core DSL Parser & Command Bus Integration (Settimane 1-2)
- [x] Creare `backend/core/scaffold/parser.py` per leggere template YAML/Markdown.
- [x] Definire le dataclass di comando in `backend/core/scaffold/commands.py`:
  - `RegisterEntityCommand(name, fields, relations)`
  - `ScaffoldBackendCommand(entity_name)`
  - `ScaffoldFrontendCommand(entity_name)`
  - `GenerateMigrationCommand(entity_name)`
- [x] Implementare gli handler/parser in `backend/core/scaffold/` che interagiscono con il bus ed il registro `SysModel`.

### Fase 6.2: Backend Scaffolding Engine (Settimane 3-4)
- [x] Creare template Jinja2 in `backend/core/scaffold/templates/backend/`:
  - `model.py.j2` (SQLAlchemy)
  - `schemas.py.j2` (Marshmallow)
  - `commands.py.j2` e `handlers.py.j2` (CQRS)
  - `rest_api.py.j2` (Flask-Smorest Blueprint)
- [x] Implementare la scrittura su disco e la generazione automatica via `CodeGenerator` in `backend/core/scaffold/generator.py`.

### Fase 6.3: Frontend Scaffolding Engine (Settimane 5-6)
- [x] Creare template Jinja2 in `backend/core/scaffold/templates/frontend/`:
  - `ListPage.jsx.j2` (con `GenericCrudPage` e tabelle dinamiche)
  - `FormPage.jsx.j2` (con componenti reattivi)
  - `api.js.j2` (Client API calls)
- [x] Garantire l'integrazione con il sistema di routing dinamico e la Command Palette (`Ctrl+K`).

### Fase 6.4: CLI Tool & API Endpoint (Settimane 7-8)
- [x] Esporre l'endpoint API: `POST /api/v1/builder/scaffold` in `backend/modules/builder/api.py`.
- [x] Creare funzione/comando CLI: `scaffold_from_yaml` in `backend/cli/scaffold.py`.
- [x] Aggiungere test di integrazione end-to-end (`backend/tests/test_scaffold_generator.py`).

---

## 4. Istruzioni Operative per Google Jules (`google-labs-jules[bot]`)
Per iniziare l'implementazione, procedi con la **Fase 6.1**. Esegui i seguenti step in modo atomico:

1. **Crea la struttura delle directory**:
   ```bash
   mkdir -p backend/core/scaffold/{templates/backend,templates/frontend}
   ```
2. **Implementa i Comandi CQRS**: Crea `backend/core/scaffold/commands.py` definendo `RegisterEntityCommand` e `ScaffoldBackendCommand` come dataclass.
3. **Implementa il Parser**: Crea `backend/core/scaffold/parser.py` utilizzando `PyYAML` per convertire un file `.yaml` in istanze dei comandi definiti al punto 2.
4. **Scrivi un Test Unitario**: Crea `tests/test_scaffold_parser.py` che verifica la corretta parsazione dell'esempio `sales_order.yaml` fornito sopra e l'emissione dei comandi corretti nel bus.
5. **Commit**: Usa il messaggio: `feat: implement Core Scaffold Parser and CQRS Commands for Schema-as-Code (Phase 6.1)`.

---

## 5. Criteri di Accettazione
- [ ] Il parser legge correttamente un template YAML valido e gestisce gli errori di sintassi con messaggi chiari.
- [ ] I comandi generati sono serializzabili e possono essere passati al `event_bus` esistente.
- [ ] Il sistema è estendibile: nuovi tipi di campo o componenti UI possono essere aggiunti al DSL senza riscrivere il parser centrale.
- [ ] La generazione rispetta le convenzioni KISS/DRY e lo stile di codice esistente (controllato via pre-commit hook).

---

> **Riferimenti Architetturali**:
> - `docs/IMPLEMENTATION_PLAN.md` (Primitivo P0: ER Engine `SysModel` + `SysField`)
> - `backend/core/event_bus.py` (Pattern di dispatching esistente)
> - `frontend/src/components/core/InlineEditableTable.jsx` (Componente UI target per il riutilizzo)

---

> Ultimo aggiornamento: 10 Settembre 2026 | [Torna all'Indice](INDEX.md)
