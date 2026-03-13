# ERPSeed Roadmap Completa

Questo documento raccoglie lo stato delle funzionalità, il piano di refactoring architetturale e la roadmap per gli sviluppi futuri.

---

# PARTE 1: Funzionalità Implementate

## ✅ Core System

| Componente            | Stato       | Data | Note                         |
| --------------------- | ----------- | ---- | ---------------------------- |
| Autenticazione JWT    | ✅ Completo | 2024 | Login, logout, refresh token |
| Multi-Progetto/Tenant | ✅ Completo | 2024 | Isolamento dati completo     |
| Gestione Utenti       | ✅ Completo | 2024 | Ruoli, permessi              |
| Modulo Sistema        | ✅ Completo | 2024 | Plugin, eventi               |
| Soft Delete           | ✅ Completo | 2024 | Cancellazione logica         |
| API RESTful           | ✅ Completo | 2024 | Flask-smorest + OpenAPI      |

---

## ✅ Builder (No-Code)

| Funzionalità                 | Stato       | Data     | Note                                   |
| ---------------------------- | ----------- | -------- | -------------------------------------- |
| Creazione modelli (SysModel) | ✅ Completo | 2024     | CRUD completo                          |
| Tipi campo base              | ✅ Completo | 2024     | string, number, date, boolean, etc     |
| Tipi campo avanzati          | ✅ Completo | 2024     | relation, calculated, summary          |
| Viste Kanban                 | ✅ Completo | 2024     | Drag & drop                            |
| Relazioni                    | ✅ Completo | 2024     | 1:N, N:N                               |
| Validazioni                  | ✅ Completo | 2024     | required, unique, regex                |
| Import/Export                | ✅ Completo | Feb 2026 | Toolbar, context menu, backup completo |
| Sync schema                  | ✅ Completo | 2024     | ALTER TABLE automatico                 |
| Block Builder (UI)          | ✅ Completo | Feb 2026 | Creazione Blocchi con VisualBuilder    |
| **Block Template**           | ✅ Completo | Mar 2026 | Block parametrici riutilizzabili       |

---

### 📋 Block Template - Opzioni Future

Se市场需求 (market requirements) lo richiede, queste opzioni estendono i Block Template:

| Opzione | Descrizione | Complessità |
| ------- | ----------- | ------------|
| **Opzione 2: Block Composition** | Lo stesso Block con config diverse nello stesso Modulo (slot-based) | Media |
| **Opzione 3: Marketplace-first** | Block pubblicati = Template globali disponibili per tutti i progetti | Bassa |

---

## ✅ AI Assistant

| Funzionalità                               | Stato       | Data     | Note                              |
| ------------------------------------------ | ----------- | -------- | --------------------------------- |
| Architettura base (service + API)          | ✅ Completo | Feb 2026 | backend/ai/service.py, api.py     |
| Integrazione LLM OpenRouter                | ✅ Completo | Feb 2026 | NVIDIA Nemotron, Qwen3, Anthropic |
| Integrazione Ollama locale                 | ✅ Completo | Feb 2026 | Per ambienti offline              |
| Generazione modelli da linguaggio naturale | ✅ Completo | Feb 2026 | Genera JSON config                |
| Interfaccia chat frontend                  | ✅ Completo | Feb 2026 | Modal con chat Ant Design         |
| Preview JSON modificabile                  | ✅ Completo | Feb 2026 | TextArea nel modal                |
| Applicazione config al DB                  | ✅ Completo | Feb 2026 | Crea modelli, campi, tabelle      |
| Test Generator                             | ✅ Completo | Feb 2026 | Genera test per modelli creati    |

### 📋 Da Implementare (AI)

| Funzionalità                  | Priorità | Note                          |
| ----------------------------- | -------- | ----------------------------- |
| Ripristino autenticazione JWT | Alta     | /api/ai/generate richiede fix |
| Suggerimenti intelligenti     | Bassa    | Analisi modelli esistenti     |
| Integrazione Workflow Builder | Bassa    | AI crea workflow              |

---

## ✅ Workflow Automation

| Funzionalità                     | Stato       | Data     | Note                                            |
| -------------------------------- | ----------- | -------- | ----------------------------------------------- |
| Workflow models                  | ✅ Completo | 2025     | Workflow, WorkflowStep, WorkflowExecution       |
| WorkflowService                  | ✅ Completo | 2025     | Esecuzione step, trigger event                  |
| API Routes                       | ✅ Completo | 2025     | CRUD workflow, test, executions                 |
| WorkflowsPage UI                 | ✅ Completo | 2025     | Lista, creazione, monitoraggio                  |
| Tipi step base                   | ✅ Completo | 2025     | condition, action, notification, delay, webhook |
| Workflow Builder visivo          | ✅ Completo | Feb 2026 | React Flow + Zustand + drag&drop                |
| Salvataggio/caricamento workflow | ✅ Completo | Feb 2026 | Persistenza completa                            |

### 📋 Da Implementare (Workflow)

| Funzionalità           | Priorità | Note                          |
| ---------------------- | -------- | ----------------------------- |
| Estendere tipi step    | Media    | sub_workflow, HTTP request    |
| Variabili di contesto  | Media    | {{user.name}}, {{date.today}} |
| Workflow asincroni     | Bassa    | Celery per delay lunghi       |
| Versionamento workflow | Bassa    | Cronologia modifiche          |

---

## ✅ Hook e Eventi

| Funzionalità          | Stato       | Data | Note                      |
| --------------------- | ----------- | ---- | ------------------------- |
| Hook Manager          | ✅ Completo | 2025 | Callback lifecycle entità |
| Event Bus (in-memory) | ✅ Completo | 2025 | Comunicazione asincrona   |
| Tipi hook base        | ✅ Completo | 2025 | Before/After CRUD         |
| Eventi sistema        | ✅ Completo | 2025 | entity.created, etc.      |

### 📋 Da Implementare (Hook/Eventi)

| Funzionalità             | Priorità | Note                               |
| ------------------------ | -------- | ---------------------------------- |
| Hook configurabili da UI | Bassa    | Simili ai workflow ma più semplici |
| Eventi custom            | Bassa    | Utenti definiscono eventi          |

---

## ✅ Moduli Personalizzati

| Funzionalità                           | Stato       | Data     | Note                              |
| -------------------------------------- | ----------- | -------- | --------------------------------- |
| Status su SysModel                     | ✅ Completo | Feb 2026 | draft/published                   |
| Tabella Module                         | ✅ Completo | 2024     | Già esistente                     |
| API CRUD per Module                    | ✅ Completo | 2024     | Già esistente                     |
| Filtro DynamicApiService per status    | ✅ Completo | Feb 2026 | Solo published                    |
| Filtro /projects/{id}/models per ruolo | ✅ Completo | Feb 2026 | Admin vs utenti                   |
| UI Lista Moduli nel Builder            | ✅ Completo | Feb 2026 | CustomModulesPage                 |
| Sistema test auto-generati             | ✅ Completo | Feb 2026 | CRUD, validation, FK, performance |
| Pubblicazione con regole               | ✅ Completo | Feb 2026 | Test + quality score >= 80%       |
| Dashboard App-Like                     | ✅ Completo | Feb 2026 | ModuleAppPage                     |
| Sistema API Ibrido                     | ✅ Completo | Feb 2026 | /api/modules/{module_name}/\*     |
| FK tra moduli                          | ✅ Completo | Feb 2026 | Campo relation con target_table   |
| Menu Builder > Moduli                  | ✅ Completo | Feb 2026 | Administration > Modules          |
| Migrazione/Backup dati                 | ✅ Completo | Feb 2026 | /backup endpoint                  |

---

## ✅ Marketplace

| Funzionalità          | Stato       | Data | Note                      |
| --------------------- | ----------- | ---- | ------------------------- |
| Pubblicazione Blocchi | ✅ Completo | 2024 | Con workflow approvazione |
| Installazione         | ✅ Completo | 2024 | Con un click              |
| Certificazione        | ✅ Completo | 2024 | Quality score >= 80%      |
| Recensioni            | ✅ Completo | 2024 | Rating e commenti         |

---

## ✅ Testing

| Funzionalità     | Stato       | Data     | Note               |
| ---------------- | ----------- | -------- | ------------------ |
| Test Runner UI   | ✅ Completo | 2024     | Interfaccia web    |
| Generazione Auto | ✅ Completo | Feb 2026 | Suite CRUD         |
| Esecuzione Test  | ✅ Completo | 2024     | Con risultati      |
| Quality Score    | ✅ Completo | 2024     | Calcolo automatico |

---

## ✅ Moduli ERP

### Contabilità 🟡

**Stato**: 75%

- [x] Piano dei conti
- [x] Prima nota
- [x] Partitario
- [x] Scritture automatiche (da movimenti)
- [ ] Bilancio (in corso)
- [ ] Fatturazione elettronica (SDI)

### Risorse Umane 🟡

**Stato**: 60%

- [x] Anagrafica dipendenti
- [x] Dipartimenti
- [x] Presenze
- [x] Richieste ferie
- [ ] Calcolo stipendi (in corso)
- [ ] Contratti

### Magazzino 🟡

**Stato**: 80%

- [x] Gestione ubicazioni
- [x] Movimenti di stock
- [x] Inventario
- [x] Prodotti con varianti

---

# PARTE 2: Piano di Refactoring Architetturale

## Premessa

Il progetto sta crescendo e diventa necessario disaccoppiare i componenti per:

1. **Manutenibilità**: Codice più testabile e mantenibile
2. **Scalabilità**: Possibilità di scalare componenti indipendentemente
3. **Futuri Microservizi**: Preparazione per split in servizi separati

## Obiettivo: Database Separati per Servizio

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         FLASKERP ORCHESTRATOR                           │
│  (Entry Point, Router, Event Bus, Service Locator)                     │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐
│   AUTH SERVICE    │   │   TENANT SERVICE  │   │  ENTITY SERVICE   │
│   (auth_db)       │   │   (tenant_db)    │   │   (entity_db)     │
└───────────────────┘   └───────────────────┘   └───────────────────┘
        │                           │                           │
        └───────────────────────────┼───────────────────────────┘
                                    │
                                    ▼
        ┌───────────────────────────────────────────────────────────┐
        │                   SHARED LAYER                            │
        │  (ORM, Utils, Exceptions, Interfaces, Event Bus)         │
        └───────────────────────────────────────────────────────────┘
```

## FASE 1: Infrastructure Layer (Shared)

### 1.1 Creare Pacchetto Shared

```
backend/shared/
├── orm/
│   ├── __init__.py
│   ├── fields.py          # Da backend/orm/fields.py
│   ├── relations.py       # Da backend/orm/relations.py
│   └── query.py           # Da backend/orm/query.py
├── utils/
│   ├── __init__.py
│   ├── pagination.py      # Da estrazione utils.py
│   ├── filters.py         # Da estrazione utils.py
│   └── audit.py           # Logica AuditLog
├── exceptions/
│   ├── __init__.py
│   └── flaskerp_exceptions.py
├── interfaces/
│   ├── __init__.py
│   ├── i_tenant_service.py
│   ├── i_auth_service.py
│   └── i_crud_service.py
└── events/
    ├── __init__.py
    ├── event.py           # DomainEvent dataclass
    └── event_bus.py       # In-memory event bus
```

### 1.2 Dependency Injection Container

```python
# backend/container.py
class ServiceContainer:
    """Container DI per servizi"""

    def register(self, name: str, factory: callable):
        """Registra un servizio"""

    def get(self, name: str):
        """Ottiene un servizio"""
```

### 📋 Task FASE 1

| Task | Descrizione                               | Priorità | Stato         |
| ---- | ----------------------------------------- | -------- | ------------- |
| T1.1 | Creare struttura `backend/shared/`        | Alta     | ✅ Completato |
| T1.2 | Spostare ORM fields in shared/orm/        | Alta     | ✅ Completato |
| T1.3 | Creare shared/utils/ con funzioni pure    | Alta     | ✅ Completato |
| T1.4 | Definire interfacce in shared/interfaces/ | Alta     | ✅ Completato |
| T1.5 | Implementare EventBus in-memory           | Alta     | ✅ Completato |
| T1.6 | Creare ServiceContainer                   | Alta     | ✅ Completato |
| T1.7 | Refactoring imports in tutti i moduli     | Alta     | ✅ Completato |

---

## FASE 2: AI Service Isolation

### 2.1 Struttura Target

```
ai_service/
├── api/
│   ├── __init__.py
│   └── endpoints.py       # Flask blueprint
├── domain/
│   ├── models/           # Conversation, Message
│   ├── ports/            # Interfacce astratte
│   │   ├── llm_port.py
│   │   └── vectorstore_port.py
│   └── services/
│       ├── chat_service.py
│       └── tool_service.py
├── adapters/
│   ├── openai.py
│   ├── anthropic.py
│   ├── ollama.py
│   └── openrouter.py
└── container.py
```

### 2.2 Ports & Adapters Pattern

```python
# ai_service/domain/ports/llm_port.py
class LLMPort(ABC):
    @abstractmethod
    async def chat(self, messages: list[dict]) -> str:
        pass
```

### 📋 Task FASE 2

| Task | Descrizione                                     | Priorità | Stato                      |
| ---- | ----------------------------------------------- | -------- | -------------------------- |
| T2.1 | Creare struttura ai_service/                    | Alta     | ✅ Completato              |
| T2.2 | Definire LLMPort interface                      | Alta     | ✅ Completato              |
| T2.3 | Implementare OpenAIAdapter                      | Alta     | ✅ Completato (OpenRouter) |
| T2.4 | Implementare AnthropicAdapter                   | Alta     | ✅ Completato              |
| T2.5 | Implementare OllamaAdapter                      | Alta     | ✅ Completato              |
| T2.6 | Refactoring ai/service.py verso nuova struttura | Alta     | ✅ Completato              |
| T2.7 | Integrare EventBus per eventi AI                | Media    | ✅ Completato              |

---

## FASE 3: Builder Service Isolation

### 3.1 Struttura Target

```
builder_service/
├── api/
│   └── blueprints.py
├── domain/
│   ├── entities/
│   │   ├── sys_model.py
│   │   ├── sys_field.py
│   │   ├── sys_view.py
│   │   └── sys_component.py
│   ├── repositories/      # Repository pattern
│   │   └── model_repository.py
│   └── events/
│       └── model_events.py
├── application/
│   ├── commands/
│   │   ├── create_model.py
│   │   ├── add_field.py
│   │   └── sync_schema.py
│   └── queries/
│       ├── get_model.py
│       └── list_models.py
├── infrastructure/
│   ├── persistence/      # SQLAlchemy repos
│   └── code_generator/
│       └── generator.py
└── container.py
```

### 3.2 Repository Pattern

```python
# builder_service/domain/repositories/model_repository.py
class ModelRepository(ABC):
    @abstractmethod
    def find_by_id(self, model_id: int) -> Optional[SysModel]:
        pass

    @abstractmethod
    def save(self, model: SysModel) -> SysModel:
        pass
```

### 📋 Task FASE 3

| Task | Descrizione                            | Priorità | Stato         |
| ---- | -------------------------------------- | -------- | ------------- |
| T3.1 | Creare struttura builder_service/      | Alta     | ✅ Completato |
| T3.2 | Definire ModelRepository interface     | Alta     | ✅ Completato |
| T3.3 | Implementare SQLAlchemyModelRepository | Alta     | ✅ Completato |
| T3.4 | Creare Command Handlers                | Alta     | ✅ Completato |
| T3.5 | Creare Query Handlers                  | Alta     | ✅ Completato |
| T3.6 | Refactoring builder/api.py             | Alta     | ✅ Completato |
| T3.7 | Integrare EventBus                     | Alta     | ✅ Completato |

---

## FASE 4: Event-Driven Communication

### 4.1 Event Bus Standard

```python
# shared/events/event_bus.py
class EventBus:
    def subscribe(self, event_type: str, handler: callable):
        """Sottoscrivi un handler a un tipo di evento"""

    def publish(self, event: DomainEvent):
        """Pubblica un evento a tutti gli sottoscrittori"""
```

### 4.2 Sostituire Import Diretti con Eventi

**PRIMA**:

```python
from backend.webhook_triggers import trigger_webhook
trigger_webhook("invoice.created", invoice)
```

**DOPO**:

```python
from shared.events import event_bus, DomainEvent
event_bus.publish(DomainEvent(
    event_type="invoice.created",
    payload={"invoice_id": invoice.id}
))
```

### 📋 Task FASE 4

| Task | Descrizione                           | Priorità | Stato         |
| ---- | ------------------------------------- | -------- | ------------- |
| T4.1 | Definire eventi standard del sistema  | Alta     | ✅ Completato |
| T4.2 | Migrare workflow → eventi             | Alta     | ✅ Completato |
| T4.3 | Migrare webhooks → eventi             | Alta     | ✅ Completato |
| T4.4 | Migrare plugins → eventi              | Alta     | ✅ Completato |
| T4.5 | Rimuovere import diretti cross-modulo | Alta     | ✅ Completato |

---

## FASE 5: Plugin System Isolation

### 5.1 Plugin Interface Standard

```python
# backend/plugin_system/interfaces.py
class Plugin(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        pass

    @abstractmethod
    def register(self, app, container):
        pass

    @abstractmethod
    def unregister(self, app):
        pass
```

### 5.2 Plugin Communication

```python
# plugins/inventory/plugin.py
class InventoryPlugin(Plugin):
    def register(self, app, container):
        event_bus.subscribe("invoice.created", self.on_invoice_created)

    def on_invoice_created(self, event):
        self.inventory_service.decrease_stock(event.payload)
```

### 📋 Task FASE 5

| Task | Descrizione                   | Priorità | Stato         |
| ---- | ----------------------------- | -------- | ------------- |
| T5.1 | Creare backend/plugin_system/ | Alta     | ✅ Completato |
| T5.2 | Definire Plugin interface     | Alta     | ✅ Completato |
| T5.3 | Implementare PluginManager    | Alta     | ✅ Completato |
| T5.4 | Refactoring plugins esistenti | Alta     | ✅ Completato |
| T5.5 | Sistema hot-reload plugin     | Media    | ✅ Completato |

---

## Timeline Riepilogativa

| Fase       | Descrizione                        | Durata Stimata | Stato         |
| ---------- | ---------------------------------- | -------------- | ------------- |
| **Fase 1** | Infrastructure Layer (shared/, DI) | 2-3 settimane  | ✅ Completato |
| **Fase 2** | AI Service isolation               | 2-3 settimane  | ✅ Completato |
| **FASE 3** | Builder Service isolation          | 3-4 settimane  | ✅ Completato |
| **Fase 4** | Event-Driven Communication         | 2-3 settimane  | ✅ Completato |
| **Fase 5** | Plugin System isolation            | 2-3 settimane  | ✅ Completato |

**Stato**: ✅ Refactoring Architetturale Completato (10 Marzo 2026)

---

## ⚠️ Da Implementare (Prossimi Passi)

### 1. Integrazione Servizi Orchestrator

- [x] Collegare EventBus globale all'applicazione Flask
- [x] Configurare ServiceContainer in app.py
- [x] Integrare PluginManager con Flask app

### 2. Migrazione Graduale

- [x] Aggiornare backend/orm/fields.py per usare shared/
- [x] Migrare ai/service.py verso ai_service/
- [x] Migrare builder_service.py verso builder_service/
- [x] Aggiornare imports in tutti i moduli

### 3. Testing

- [x] Aggiungere test per EventBus
- [x] Aggiungere test per ServiceContainer
- [x] Aggiungere test per PluginManager
- [ ] Verificare copertura >70%

### 4. Refactoring Aggiuntivo (Opzionale)

- [ ] Separare Auth Service in auth_service/
- [ ] Separare Tenant Service in tenant_service/
- [ ] Implementare database separati per servizi (vedi diagramma FASE 1)

---

## Metriche di Successo

| Metrica                     | Prima | Obiettivo |
| --------------------------- | ----- | --------- |
| Test coverage               | ~30%  | >70%      |
| Circular dependencies       | 50+   | 0         |
| Deploy indipendente servizi | No    | Sì        |
| Tempo boot applicazione     | 5s    | <2s       |

---

# PARTE 3: Roadmap Funzionalità Future

## Q2 2026

### Completamento Contabilità

- [ ] Bilancio
- [ ] Chiusure esercizio
- [ ] Integrazione SDI (fatturazione elettronica italiana)

### AI Assistant v1

- [ ] Fix autenticazione JWT
- [ ] Suggerimenti automatici basati su modelli esistenti

### CRM Module

- [ ] Pipeline commerciali
- [ ] Campagne
- [ ] Lead scoring

## Q3 2026

### Progetti e Task

- [ ] Gantt integrato
- [ ] Allocazione risorse
- [ ] Timeline

### Documentale

- [ ] Archiviazione
- [ ] Versioning
- [ ] Ricerca

## Q4 2026

### Helpdesk

- [ ] Ticket
- [ ] Knowledge base
- [ ] SLA

### Multi-company

- [ ] Consolidamento
- [ ] Reporting cross-company

### Reporting avanzato

- [ ] Designer grafico
- [ ] Dashboard custom

---

# PARTE 4: Dettagli Implementativi

## Riferimenti Codice

| Componente                  | Percorso                                              |
| --------------------------- | ----------------------------------------------------- |
| Core                        | `backend/core/`                                       |
| Builder                     | `backend/builder/`                                    |
| AI                          | `backend/ai/`                                         |
| **AI Service (nuovo)**      | `backend/ai_service/`                                 |
| **Builder Service (nuovo)** | `backend/builder_service/`                            |
| **Plugin System (nuovo)**   | `backend/plugin_system/`                              |
| **Shared (nuovo)**          | `backend/shared/`                                     |
| **Container DI**            | `backend/container.py`                                |
| Workflow                    | `backend/workflows.py`, `backend/workflow_service.py` |
| Plugins                     | `backend/plugins/`                                    |
| Marketplace                 | `backend/marketplace/`                                |
| Entities                    | `backend/entities/`                                   |

## Riferimenti Documentazione

| Documento                                                        | Descrizione                        |
| ---------------------------------------------------------------- | ---------------------------------- |
| [01_ARCHITETTURA.md](01_ARCHITETTURA.md)                         | Architettura generale              |
| [02_BUILDER.md](02_BUILDER.md)                                   | Guida al Builder                   |
| [13_ARCHITETTURA_DISTRIBUITA.md](13_ARCHITETTURA_DISTRIBUITA.md) | Analisi architetturale distribuita |

---

## Come Aggiornare Questo Documento

Quando implementi una nuova funzionalità:

1. Aggiungi la funzionalità nella sezione ✅ appropriata
2. Se è da fare, aggiungi in 📋 con priorità
3. Aggiorna la data
4. Sposta i task dalla Roadmap alle implementazioni

---

_Ultimo aggiornamento: 11 Marzo 2026 (Refactoring JWT/Tenant COMPLETATO - Fasi 1-5)_

---

# PARTE 5: Refactoring Autenticazione JWT e Tenant (Marzo 2026)

## 5.1 Problemi Identificati

### Classi Duplicate (RISOLTO)

| File | Classe | Stato |
|------|--------|-------|
| `backend/models.py:83` | `User` | ✅ Principale |
| `backend/core/models/user.py` | `User` | ✅ Eliminato |
| `backend/models.py` | `UserRole` | ✅ Spostato da user.py |
| `backend/models.py:345` | `AuditLog` (commentato) | ✅ Già commentato |

### Bug Critici (RISOLTI)

- ✅ **`tenant_service.py:201-204`**: Codice irraggiungibile - CORRETTO
- ✅ **`conftest.py:231`**: Usa endpoint `/login` legacy - CORRETTO
- ⚠️ **Test login**: Richiede test per validare
- ✅ **Due sistemi di autenticazione**: Unificato - ELIMINATO legacy

### Migrazioni Alembic (RISOLTO)

- ✅ Aggiunto `script_location` in `alembic.ini`

### Architettura Frammentata

- `TenantContext` usa `flask.g` (request-scoped) - fragile
- Query filter separati dal context
- Middleware duplica logica di estrazione tenant

---

## 5.2 Piano di Implementazione

### FASE 1: Pulizia Classi Duplicate ✅ PRIORITÀ ALTA

| Task | Descrizione | Stato |
|------|-------------|-------|
| T5.1.1 | Eliminare `backend/core/models/user.py` | ✅ Completato |
| T5.1.2 | Verificare imports in tutto il codebase | ✅ Completato |
| T5.1.3 | Rimuovere commenti AuditLog in `backend/models.py` | ✅ Spostato UserRole |

### FASE 2: Fix Bug Immediati ✅ PRIORITÀ ALTA

| Task | Descrizione | Stato |
|------|-------------|-------|
| T5.2.1 | Rimuovere codice irraggiungibile `tenant_service.py:201-204` | ✅ Completato |
| T5.2.2 | Correggere fixture `conftest.py` per `/api/v1/auth/login` | ✅ Completato |
| T5.2.3 | Aggiungere `script_location` a `alembic.ini` | ✅ Completato |

### FASE 3: Unificare Autenticazione ✅ PRIORITÀ MEDIA

| Task | Descrizione | Stato |
|------|-------------|-------|
| T5.3.1 | Mantenere SOLO `backend/core/api/auth.py` | ✅ Completato |
| T5.3.2 | Eliminare `backend/auth.py` completamente | ✅ Completato |
| T5.3.3 | Aggiornare endpoint frontend | ⏳ Da fare |

### FASE 4: Refactoring Tenant Isolation (Struttura DRY)

```
backend/core/services/
├── auth/
│   ├── auth_service.py      # Login, register, token
│   ├── jwt_service.py      # Gestione token JWT (NUOVO)
│   └── permission_service.py
├── tenant/
│   ├── tenant_service.py   # CRUD tenant
│   ├── tenant_context.py   # Request context
│   └── tenant_filter.py   # Query filtering
└── __init__.py
```

| Task | Descrizione | Stato |
|------|-------------|-------|
| T5.4.1 | Creare sottostruttura `backend/core/services/auth/` | ✅ Completato |
| T5.4.2 | Creare `jwt_service.py` dedicato | ✅ Completato |
| T5.4.3 | Unificare tenant_context + tenant_filter | ✅ Completato |
| T5.4.4 | Aggiornare container per nuovi servizi | ✅ Completato |

### FASE 5: Testabilità

| Task | Descrizione | Stato |
|------|-------------|-------|
| T5.5.1 | Creare interfacce per ogni servizio | ✅ Completato |
| T5.5.2 | Mock del TenantContext nei test | ✅ Completato |
| T5.5.3 | Test unitari per ogni servizio | ✅ Completato |

---

## 5.3 Pro e Contro

| Aspetto | Pro | Contro |
|---------|-----|--------|
| Eliminazione duplicati | Codice pulito, nessuna confusione | Rischio breaking se qualcosa dipende dalle classi duplicate |
| JWT unificato | Debug più semplice, un solo flusso | Richiede aggiornamento frontend |
| Tenant isolation centralizzata | Facile da testare e mantenere | Richiede riscrittura middleware |
| Service container | DI corretta, testabilità | Curva di apprendimento iniziale |

---

## 5.4 Principi KISS e DRY Applicati

- **KISS**: Ogni servizio fa una cosa sola
- **DRY**: Logica di autenticazione in un posto solo
- **Testability**: Ogni componente testabile separatamente
- **Incrementale**: Una fase rilasciabile alla volta

---

_Refactoring JWT/Tenant aggiunto: 11 Marzo 2026_

---

## 5.5 Sessione Corrente (11 Marzo 2026)

### Lavoro Completato

| Task | Descrizione | Stato |
|------|-------------|-------|
| T5.5.1 | Creare interfacce per ogni servizio | ✅ Completato |
| T5.5.2 | Mock del TenantContext nei test | ✅ Completato |
| T5.5.3 | Test unitari per ogni servizio | ✅ Completato (32 test) |
| T5.5.4 | Aggiornare endpoint frontend `/api/v1/auth/*` | ✅ Completato |
| T5.5.5 | Aggiungere breadcrumb labels per admin pages | ✅ Completato |
| T5.5.6 | Fix WorkflowsPage.jsx - aggiunto AppHeader | ✅ Completato |

### Errori 500 Rimanenti

| Endpoint | Problema | Possibile Causa | Stato |
|----------|----------|-----------------|-------|
| `/api/v1/modules` | 500 - `'dict' object has no attribute 'dump'` | `@blp.response` schema incompatible | ✅ Fixato |
| `/workflows/step-types` | 500 - `'dict' object has no attribute 'dump'` | Stessa causa | ✅ Fixato |
| `/api/v1/system/modules-info` | 500 | `@blp.response` schema mancante | ⚠️ Da verificare |

### Problemi Frontend

| Pagina | Problema | Possibile Causa |
|--------|----------|-----------------|
| Builder | Breadcrumb non visibile | Componente breadcrumb non renderizzato |
| BusinessRules | `projectId` = undefined (CORS) | Routing/navigation prop mancante |
| CustomModules | Internal Server Error | Da debuggare lato backend |

---

## 5.6 Analisi Problemi e Possibili Soluzioni

### Problema 1: Error 500 `'dict' object has no attribute 'dump'`

**Causa radice**: Quando un endpoint REST ritorna un dizionario (`{}`) ma il decorator `@blp.response(200, SchemaModel)` definisce uno schema che si aspetta un oggetto con metodo `.dump()`, si ottiene questo errore.

**Soluzione**: Rimuovere il parametro `schema` dal decorator `@blp.response` quando l'endpoint ritorna un dizionario plain.

```python
# SBAGLIATO
@blp.response(200, schema={"type": "object"})
def get_modules():
    return {"modules": [...]}

# CORRETTO
@blp.response(200)
def get_modules():
    return {"modules": [...]}
```

**File da verificare**:
- `backend/core/api/modules.py` - endpoint `/api/v1/modules`
- `backend/core/api/workflows.py` - endpoint `/workflows/step-types`

### Problema 2: Builder Breadcrumb

**Possibili cause**:
1. Il componente `Breadcrumb` non è incluso nel layout della pagina Builder
2. Il `projectId` non viene passato correttamente al breadcrumb
3. Lo stile CSS nasconde il breadcrumb

**Soluzione**: Verificare che `BuilderPage.jsx` includa il componente `AppHeader` con breadcrumb.

### Problema 3: BusinessRules `projectId` undefined

**Causa**: La pagina BusinessRules riceve `projectId` dalla URL params ma il routing non lo passa correttamente.

**Soluzione**: Verificare la configurazione delle route in `App.jsx` o `routes.js`.

### Problema 4: CustomModules Internal Server Error

**Causa**: Potrebbe essere un errore nel backend nella gestione del modulo custom.

**Soluzione**: Verificare i log del server e l'endpoint `/api/v1/modules`.

---

## 5.7 Prossimi Passi Consigliati

1. **Immediato**: Fix errori 500 sugli endpoint (10 minuti)
   - Verificare e correggere `@blp.response` in `modules.py` e `workflows.py`

2. **Breve termine**: Debug frontend
   - Verificare breadcrumb in BuilderPage
   - Correggere passaggio `projectId` in BusinessRules

3. **Medio termine**: CustomModules
   - Aggiungere logging per identificare l'errore esatto

---

_Analisi e piano: 11 Marzo 2026_
