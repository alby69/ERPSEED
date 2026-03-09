# FlaskERP Roadmap Completa

Questo documento raccoglie lo stato delle funzionalità, il piano di refactoring architetturale e la roadmap per gli sviluppi futuri.

---

# PARTE 1: Funzionalità Implementate

## ✅ Core System

| Componente | Stato | Data | Note |
|-----------|-------|------|------|
| Autenticazione JWT | ✅ Completo | 2024 | Login, logout, refresh token |
| Multi-Progetto/Tenant | ✅ Completo | 2024 | Isolamento dati completo |
| Gestione Utenti | ✅ Completo | 2024 | Ruoli, permessi |
| Modulo Sistema | ✅ Completo | 2024 | Plugin, eventi |
| Soft Delete | ✅ Completo | 2024 | Cancellazione logica |
| API RESTful | ✅ Completo | 2024 | Flask-smorest + OpenAPI |

---

## ✅ Builder (No-Code)

| Funzionalità | Stato | Data | Note |
|-------------|-------|------|------|
| Creazione modelli (SysModel) | ✅ Completo | 2024 | CRUD completo |
| Tipi campo base | ✅ Completo | 2024 | string, number, date, boolean, etc |
| Tipi campo avanzati | ✅ Completo | 2024 | relation, calculated, summary |
| Viste Kanban | ✅ Completo | 2024 | Drag & drop |
| Relazioni | ✅ Completo | 2024 | 1:N, N:N |
| Validazioni | ✅ Completo | 2024 | required, unique, regex |
| Import/Export | ✅ Completo | Feb 2026 | Toolbar, context menu, backup completo |
| Sync schema | ✅ Completo | 2024 | ALTER TABLE automatico |

---

## ✅ AI Assistant

| Funzionalità | Stato | Data | Note |
|-------------|-------|------|------|
| Architettura base (service + API) | ✅ Completo | Feb 2026 | backend/ai/service.py, api.py |
| Integrazione LLM OpenRouter | ✅ Completo | Feb 2026 | NVIDIA Nemotron, Qwen3, Anthropic |
| Integrazione Ollama locale | ✅ Completo | Feb 2026 | Per ambienti offline |
| Generazione modelli da linguaggio naturale | ✅ Completo | Feb 2026 | Genera JSON config |
| Interfaccia chat frontend | ✅ Completo | Feb 2026 | Modal con chat Ant Design |
| Preview JSON modificabile | ✅ Completo | Feb 2026 | TextArea nel modal |
| Applicazione config al DB | ✅ Completo | Feb 2026 | Crea modelli, campi, tabelle |
| Test Generator | ✅ Completo | Feb 2026 | Genera test per modelli creati |

### 📋 Da Implementare (AI)

| Funzionalità | Priorità | Note |
|-------------|----------|------|
| Ripristino autenticazione JWT | Alta | /api/ai/generate richiede fix |
| Suggerimenti intelligenti | Bassa | Analisi modelli esistenti |
| Integrazione Workflow Builder | Bassa | AI crea workflow |

---

## ✅ Workflow Automation

| Funzionalità | Stato | Data | Note |
|-------------|-------|------|------|
| Workflow models | ✅ Completo | 2025 | Workflow, WorkflowStep, WorkflowExecution |
| WorkflowService | ✅ Completo | 2025 | Esecuzione step, trigger event |
| API Routes | ✅ Completo | 2025 | CRUD workflow, test, executions |
| WorkflowsPage UI | ✅ Completo | 2025 | Lista, creazione, monitoraggio |
| Tipi step base | ✅ Completo | 2025 | condition, action, notification, delay, webhook |
| Workflow Builder visivo | ✅ Completo | Feb 2026 | React Flow + Zustand + drag&drop |
| Salvataggio/caricamento workflow | ✅ Completo | Feb 2026 | Persistenza completa |

### 📋 Da Implementare (Workflow)

| Funzionalità | Priorità | Note |
|-------------|----------|------|
| Estendere tipi step | Media | sub_workflow, HTTP request |
| Variabili di contesto | Media | {{user.name}}, {{date.today}} |
| Workflow asincroni | Bassa | Celery per delay lunghi |
| Versionamento workflow | Bassa | Cronologia modifiche |

---

## ✅ Hook e Eventi

| Funzionalità | Stato | Data | Note |
|-------------|-------|------|------|
| Hook Manager | ✅ Completo | 2025 | Callback lifecycle entità |
| Event Bus (in-memory) | ✅ Completo | 2025 | Comunicazione asincrona |
| Tipi hook base | ✅ Completo | 2025 | Before/After CRUD |
| Eventi sistema | ✅ Completo | 2025 | entity.created, etc. |

### 📋 Da Implementare (Hook/Eventi)

| Funzionalità | Priorità | Note |
|-------------|----------|------|
| Hook configurabili da UI | Bassa | Simili ai workflow ma più semplici |
| Eventi custom | Bassa | Utenti definiscono eventi |

---

## ✅ Moduli Personalizzati

| Funzionalità | Stato | Data | Note |
|-------------|-------|------|------|
| Status su SysModel | ✅ Completo | Feb 2026 | draft/published |
| Tabella Module | ✅ Completo | 2024 | Già esistente |
| API CRUD per Module | ✅ Completo | 2024 | Già esistente |
| Filtro DynamicApiService per status | ✅ Completo | Feb 2026 | Solo published |
| Filtro /projects/{id}/models per ruolo | ✅ Completo | Feb 2026 | Admin vs utenti |
| UI Lista Moduli nel Builder | ✅ Completo | Feb 2026 | CustomModulesPage |
| Sistema test auto-generati | ✅ Completo | Feb 2026 | CRUD, validation, FK, performance |
| Pubblicazione con regole | ✅ Completo | Feb 2026 | Test + quality score >= 80% |
| Dashboard App-Like | ✅ Completo | Feb 2026 | ModuleAppPage |
| Sistema API Ibrido | ✅ Completo | Feb 2026 | /api/modules/{module_name}/* |
| FK tra moduli | ✅ Completo | Feb 2026 | Campo relation con target_table |
| Menu Builder > Moduli | ✅ Completo | Feb 2026 | Administration > Modules |
| Migrazione/Backup dati | ✅ Completo | Feb 2026 | /backup endpoint |

---

## ✅ Marketplace

| Funzionalità | Stato | Data | Note |
|-------------|-------|------|------|
| Pubblicazione Blocchi | ✅ Completo | 2024 | Con workflow approvazione |
| Installazione | ✅ Completo | 2024 | Con un click |
| Certificazione | ✅ Completo | 2024 | Quality score >= 80% |
| Recensioni | ✅ Completo | 2024 | Rating e commenti |

---

## ✅ Testing

| Funzionalità | Stato | Data | Note |
|-------------|-------|------|------|
| Test Runner UI | ✅ Completo | 2024 | Interfaccia web |
| Generazione Auto | ✅ Completo | Feb 2026 | Suite CRUD |
| Esecuzione Test | ✅ Completo | 2024 | Con risultati |
| Quality Score | ✅ Completo | 2024 | Calcolo automatico |

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

| Task | Descrizione | Priorità |
|------|-------------|----------|
| T1.1 | Creare struttura `backend/shared/` | Alta |
| T1.2 | Spostare ORM fields in shared/orm/ | Alta |
| T1.3 | Creare shared/utils/ con funzioni pure | Alta |
| T1.4 | Definire interfacce in shared/interfaces/ | Alta |
| T1.5 | Implementare EventBus in-memory | Alta |
| T1.6 | Creare ServiceContainer | Alta |
| T1.7 | Refactoring imports in tutti i moduli | Alta |

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

| Task | Descrizione | Priorità |
|------|-------------|----------|
| T2.1 | Creare struttura ai_service/ | Alta |
| T2.2 | Definire LLMPort interface | Alta |
| T2.3 | Implementare OpenAIAdapter | Alta |
| T2.4 | Implementare AnthropicAdapter | Alta |
| T2.5 | Implementare OllamaAdapter | Alta |
| T2.6 | Refactoring ai/service.py verso nuova struttura | Alta |
| T2.7 | Integrare EventBus per eventi AI | Media |

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

| Task | Descrizione | Priorità |
|------|-------------|----------|
| T3.1 | Creare struttura builder_service/ | Alta |
| T3.2 | Definire ModelRepository interface | Alta |
| T3.3 | Implementare SQLAlchemyModelRepository | Alta |
| T3.4 | Creare Command Handlers | Alta |
| T3.5 | Creare Query Handlers | Alta |
| T3.6 | Refactoring builder/api.py | Alta |
| T3.7 | Integrare EventBus | Alta |

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

| Task | Descrizione | Priorità |
|------|-------------|----------|
| T4.1 | Definire eventi standard del sistema | Alta |
| T4.2 | Migrare workflow → eventi | Alta |
| T4.3 | Migrare webhooks → eventi | Alta |
| T4.4 | Migrare plugins → eventi | Alta |
| T4.5 | Rimuovere import diretti cross-modulo | Alta |

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

| Task | Descrizione | Priorità |
|------|-------------|----------|
| T5.1 | Creare backend/plugin_system/ | Alta |
| T5.2 | Definire Plugin interface | Alta |
| T5.3 | Implementare PluginManager | Alta |
| T5.4 | Refactoring plugins esistenti | Alta |
| T5.5 | Sistema hot-reload plugin | Media |

---

## Timeline Riepilogativa

| Fase | Descrizione | Durata Stimata |
|------|-------------|----------------|
| **Fase 1** | Infrastructure Layer (shared/, DI) | 2-3 settimane |
| **Fase 2** | AI Service isolation | 2-3 settimane |
| **Fase 3** | Builder Service isolation | 3-4 settimane |
| **Fase 4** | Event-Driven Communication | 2-3 settimane |
| **Fase 5** | Plugin System isolation | 2-3 settimane |

**Totale**: ~12-16 settimane

---

## Metriche di Successo

| Metrica | Prima | Obiettivo |
|---------|-------|-----------|
| Test coverage | ~30% | >70% |
| Circular dependencies | 50+ | 0 |
| Deploy indipendente servizi | No | Sì |
| Tempo boot applicazione | 5s | <2s |

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

| Componente | Percorso |
|------------|----------|
| Core | `backend/core/` |
| Builder | `backend/builder/` |
| AI | `backend/ai/` |
| Workflow | `backend/workflows.py`, `backend/workflow_service.py` |
| Plugins | `backend/plugins/` |
| Marketplace | `backend/marketplace/` |
| Entities | `backend/entities/` |

## Riferimenti Documentazione

| Documento | Descrizione |
|-----------|-------------|
| [01_ARCHITETTURA.md](01_ARCHITETTURA.md) | Architettura generale |
| [02_BUILDER.md](02_BUILDER.md) | Guida al Builder |
| [13_ARCHITETTURA_DISTRIBUITA.md](13_ARCHITETTURA_DISTRIBUITA.md) | Analisi architetturale distribuita |

---

## Come Aggiornare Questo Documento

Quando implementi una nuova funzionalità:

1. Aggiungi la funzionalità nella sezione ✅ appropriata
2. Se è da fare, aggiungi in 📋 con priorità
3. Aggiorna la data
4. Sposta i task dalla Roadmap alle implementazioni

---

*Ultimo aggiornamento: 9 Marzo 2026*
