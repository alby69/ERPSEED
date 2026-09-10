# Architettura ERPSEED Backend

## Panoramica

ERPSEED è un sistema ERP modulare costruito con Flask. Utilizza un'architettura multi-tenant con supporto per:
- Creazione dinamica di modelli dati (No-Code Builder)
- Workflow automation
- Sistema webhook event-driven
- AI Assistant integrato con CQRS

## Stack Tecnologico

| Componente | Tecnologia |
|------------|-----------|
| Framework | Flask 3.x |
| ORM | SQLAlchemy + Flask-SQLAlchemy |
| API | Flask-Smorest (OpenAPI 3.0) |
| Auth | Flask-JWT-Extended (JWT) |
| Serializzazione | Marshmallow |
| Database | PostgreSQL / SQLite |
| Realtime | Flask-SocketIO |
| i18n | Flask-Babel |

## Struttura del Progetto

```
backend/
├── __init__.py              # App factory (create_app)
├── extensions.py            # Inizializzazione estensioni Flask
├── schemas.py               # Schemi Marshmallow centrali
├── container.py             # Iniezione dipendenze (Container)
├── models.py                # Proxy e relazioni modelli
├── utils.py                 # Utility condivise
├── webhooks.py / webhook_triggers.py  # Webhook triggers & handlers
│
├── models/                  # MODELLI DATABASE (SQLAlchemy)
│   ├── __init__.py
│   ├── base.py              # BaseModel con soft delete e to_dict
│   ├── user.py              # User, Role, UserRole
│   ├── project.py           # Project
│   ├── product.py           # Product
│   ├── sales.py             # SalesOrder, SalesOrderLine
│   ├── purchase.py          # PurchaseOrder, PurchaseOrderLine
│   ├── ai.py               # AIConversation
│   ├── chart.py             # ChartLibraryConfig
│   ├── tax.py              # TaxRate
│   ├── uom.py              # UnitOfMeasure
│   ├── pricing.py          # PriceList, PriceListItem
│   ├── movement_reason.py  # MovementReason
│   ├── goods_receipt.py    # GoodsReceipt, GoodsReceiptLine
│   ├── maturity.py         # Maturity
│   ├── crm.py              # Lead, Opportunity
│   ├── contract.py         # Contract
│   ├── manufacturing.py    # BillOfMaterial, WorkCycle, ProductionOrder
│   ├── project_management.py # BusinessProject, Timesheet
│   ├── report.py           # Report, ReportExecution
│   ├── vat.py              # VatRegisterEntry, VatLiquidation, IntrastatDeclaration
│   ├── riba.py             # RiBa, RiBaItem
│   ├── lot.py              # Lot, SerialNumber
│   ├── purchase_request.py  # PurchaseRequest, RFQ, SupplierQuotation
│   ├── mrp.py              # MRPRun, MRPSuggestion
│   ├── workflow.py         # Workflow, WorkflowStep, WorkflowExecution
│   ├── webhook.py          # WebhookEndpoint, WebhookDelivery, WebhookEvent
│   └── system.py           # SysModel, SysField, SysView, SysComponent, SysAction, SysChart, SysDashboard, SysModelVersion
│
├── services/                # SERVICE PROXIES (Lazy imports / backward compatibility)
│   ├── __init__.py          # ServiceProxy wrapper
│   ├── base.py
│   ├── builder_service.py
│   ├── dynamic_api_service.py
│   ├── file_processing_service.py
│   ├── generic_service.py
│   ├── geocoded_client.py
│   ├── logistics_service.py
│   ├── project_service.py
│   ├── template_service.py
│   ├── user_service.py
│   └── versioning_service.py
│
├── core/                    # CORE SYSTEM
│   ├── api/                # Endpoint API core (/api/v1/)
│   │   ├── auth.py         # Login, Register, JWT, Password reset
│   │   ├── tenant.py        # Gestione Tenant
│   │   ├── modules.py      # Gestione Moduli
│   │   ├── system.py       # Configurazione Sistema
│   │   ├── pdf.py          # Generazione PDF
│   │   ├── test_runner.py  # Esecuzione Test
│   │   ├── custom_modules.py
│   │   ├── module_api.py
│   │   └── import_export.py
│   ├── models/             # Modelli Core
│   │   ├── base.py
│   │   ├── tenant.py
│   │   ├── tenant_member.py
│   │   ├── audit.py
│   │   ├── module.py
│   │   ├── module_definition.py
│   │   ├── modulo.py
│   │   ├── tenant_module.py
│   │   └── test_models.py
│   ├── services/           # Servizi Core
│   │   ├── auth_service.py
│   │   ├── tenant_service.py
│   │   ├── module_service.py
│   │   ├── permission_service.py
│   │   ├── webhook_service.py
│   │   ├── import_export_service.py
│   │   ├── pdf_service.py
│   │   ├── file_processing_service.py
│   │   ├── test_engine.py
│   │   └── tenant/ (tenant_filter.py, tenant_context.py)
│   └── middleware/          # Middleware
│       ├── tenant_middleware.py
│       └── module_middleware.py
│
├── modules/                 # MODULI APPLICATIVI (CQRS & Domain Logic)
│   ├── ai/                 # Agent Gateway & AI Assistant (adapters, tool_registry, tool_executors)
│   ├── analytics/          # Dashboard, KPI & Analytics API
│   ├── automation/         # Workflow Engine & Webhook management
│   ├── builder/            # No-Code Builder (application, domain, api)
│   ├── contracts/          # Contratti
│   ├── crm/                # Lead & Opportunità
│   ├── dynamic_api/        # Dynamic CRUD engine (QueryBuilder, FieldValidator, ResultProcessor)
│   ├── entities/           # Anagrafiche: Soggetto, Ruolo, Indirizzo, Contatto, Comune, Via
│   ├── fattura_elettronica/# Generazione XML FatturaElettronicaPA 1.2
│   ├── geografia/          # Regioni, Province, Comuni, Nazioni
│   ├── goods_receipt/      # DDT Entrata Merci
│   ├── inventory/          # Giacenze, Movimenti & Causali
│   ├── invoicing/          # Fatturazione Vendita (CQRS)
│   ├── logistics/          # Servizi Logistici & Calcolo Percorsi
│   ├── lot/                # Lotti e Serial Number
│   ├── manufacturing/      # Produzione (BOM, Cicli, ODP)
│   ├── maturities/         # Scadenzario & Partite
│   ├── mrp/                # Material Requirements Planning
│   ├── pricing/            # Listini Prezzo
│   ├── product_categories/ # Categorie Prodotto
│   ├── products/           # Prodotti (CQRS)
│   ├── project_management/ # Timesheet & Budget Commessa
│   ├── projects/           # Progetti (CQRS)
│   ├── purchase_requests/  # Richieste d'Acquisto & RFQ
│   ├── purchase_returns/   # Resi Acquisti
│   ├── purchases/          # Ordini Acquisto (CQRS)
│   ├── relationship_manager/# Visual ER Relationship Manager
│   ├── report_designer/    # Report Designer & Esecuzione
│   ├── riba/               # Ricevute Bancarie (Ri.Ba.)
│   ├── sales/              # Ordini Vendita & Preventivi (CQRS)
│   ├── system_tools/       # Template, Versioning & System Debugging
│   ├── tax/                # Aliquote IVA (CQRS)
│   ├── uom/                # Unità di Misura
│   ├── users/              # Utenti & Ruoli (CQRS)
│   └── vat/                # Registri IVA & Intrastat
│
├── plugins/                # SYSTEM PLUGINS
│   ├── base.py             # BasePlugin class
│   ├── registry.py         # Plugin Registry
│   ├── accounting/         # Contabilità (Piano dei Conti, Prima Nota)
│   ├── hr/                 # Risorse Umane (Dipendenti, Presenze, Ferie, Payroll, Formazione)
│   └── inventory/          # Plugin Magazzino esteso
│
├── cli/                    # CLI SCRIPTS
│   ├── create_admin.py
│   ├── create_default_project.py
│   ├── create_tenant.py
│   ├── reset_db.py
│   ├── setup_database.py
│   └── test_container.py
│
├── seeds/                  # DATABASE SEEDS
│   ├── seed_initial.py     # Admin user + default tenant
│   ├── seed_comuni.py     # Anagrafica comuni italiani
│   ├── seed_metadata.py    # SysComponent, SysAction metadata
│   ├── seed_kpi.py         # KPI e dashboard iniziali
│   ├── enrich_comuni.py
│   └── comuni_istat.json
│
├── shared/                 # SHARED UTILITIES & EVENT BUS
│   ├── events/             # EventBus, Event, SystemEvents
│   ├── handlers/           # Event Handlers (Read Model Sync)
│   ├── utils/              # Audit, Filters, Pagination
│   ├── interfaces/         # ICrudService
│   └── exceptions/         # Excezioni Custom
│
├── tests/                  # SUITE TEST BACKEND (Pytest)
└── translations/           # File i18n (Flask-Babel)
```

## Pattern Architetturali

### 1. CQRS Pattern (Consigliato per nuovi moduli)

```
Command/Query → Handler → Service → Repository → Database
```

```python
# ai_service/application/commands.py
@dataclass
class SendMessageCommand:
    project_id: int
    user_id: int
    message: str

# ai_service/application/handlers.py
class SendMessageHandler:
    def handle(self, command: SendMessageCommand):
        # Process command
        return result
```

### 2. Service Layer Pattern

```python
# services/base.py
class BaseService:
    def __init__(self, db):
        self.db = db

    def create(self, data):
        # Business logic
        pass
```

### 3. Blueprint + Marshmallow (API REST)

```python
# routes/projects.py
blp = Blueprint('projects', __name__, url_prefix='/projects')

@blp.route('/')
@jwt_required()
def list_projects():
    return project_service.get_all()
```

### 4. Dynamic API Pattern

Per il No-Code Builder, i modelli vengono creati runtime:

```python
# models/system/sys_model.py
class SysModel(db.Model):
    name = db.Column(db.String(100))
    fields = db.relationship('SysField', back_populates='model')

class SysField(db.Model):
    name = db.Column(db.String(100))
    type = db.Column(db.String(50))
```

## Multi-Tenancy

### Row-Level Isolation

L'isolamento dei dati multi-tenant viene gestito a livello di riga (**Row-Level Isolation**) tramite la colonna `tenant_id` presente su tutti i modelli di dominio e un filtro automatico SQLAlchemy applicato a livello di query (`before_compile`).

```mermaid
flowchart TD
    Req[Incoming HTTP Request] --> TM[TenantMiddleware]
    TM -->|Extracts header / subdomain / JWT| TC[TenantContext]
    TC -->|Sets g.current_tenant| TF[TenantFilter]
    TF -->|SQLAlchemy before_compile| DB[(Database Query: WHERE tenant_id = tenant.id)]
```

> **Nota di architettura**: La logica di filtraggio automatico e contesto tenant è gestita centralmente da `backend/core/services/tenant/tenant_filter.py` (`TenantContext` e `TenantFilter`). Il file `backend/core/services/query_filter.py` è **deprecato** e sostituito da quest'ultimo.

### Middleware Flow

```
Request → TenantMiddleware → Extract Tenant (header X-Tenant-ID / subdomain / JWT) → Set TenantContext → Route Handler
```

Il middleware tenta 3 metodi in ordine:
1. **Header `X-Tenant-ID`** — esplicito, per API calls
2. **Subdomain** — per accessi via browser (es. `tenant1.erpseed.com`)
3. **JWT Token** — se l'utente è autenticato, usa `user.tenant` (fallback su `TenantMember`)

## Autenticazione JWT

```
Login → JWT Token → Access Resource
  POST    15min expiry    /api/*
```

## Event System

```python
# shared/events/event_bus.py
class EventBus:
    def publish(self, event_name, data):
        for handler in self._handlers[event_name]:
            handler(data)

    def subscribe(self, event_name, handler):
        self._handlers[event_name].append(handler)
```

## Plugin System

```python
# plugins/base.py
class BasePlugin:
    name: str
    enabled: bool = False

    def install(self):
        pass

    def uninstall(self):
        pass
```

## Workflow Engine

```mermaid
flowchart LR
    Trigger["Trigger (event/time)"] --> WorkflowDef["Workflow Definition"]
    WorkflowDef --> StepExec["Steps Execution"]
    StepExec --> Step1["Step 1: Action"]
    StepExec --> Step2["Step 2: Condition"]
    StepExec --> Step3["Step 3: Webhook/Notify"]
```

## Dynamic Builder (No-Code)

### Visual Relationship Manager
Consente la gestione visiva del modello Entity-Relationship (ER) tramite un'interfaccia a nodi (**XYFlow**), permettendo di:
- Visualizzare e mappare le relazioni tra modelli dinamici.
- Gestire graficamente chiavi esterne e vincoli di integrità.

> **Nota di architettura**: Il grafo ER visuale in Visual Relationship Manager (`/builder/relationships`) rappresenta esclusivamente le relazioni `relation` dirette (chiavi esterne fisiche) e non ancora i collegamenti derivati `lookup` (campi letti via JOIN) o `summary` (aggregati calcolati).

### Field Types

| Type | Database | Validation / Mechanics |
|------|----------|------------------------|
| `string` | VARCHAR | max_length, min_length |
| `text` | TEXT | max_length |
| `integer` | INTEGER | min, max |
| `float` | FLOAT | min, max |
| `boolean` | BOOLEAN | - |
| `date` | DATE | - |
| `datetime` | DATETIME | - |
| `select` | ENUM / VARCHAR | options[] |
| `relation` | FOREIGN KEY | target_table, label_field |
| `lookup` | VIRTUAL (JOIN) | local_key, remote_key, remote_field |
| `summary` | VIRTUAL (SUBQUERY) | summary_expression, foreign_key |
| `lines` | VIRTUAL (DETAIL) | target_table, foreign_key |
| `calculated` | VIRTUAL (EVAL) | formula |
| `file` | VARCHAR (path) | allowed_extensions |
| `image` | VARCHAR (path) | max_size_mb |
| `richtext` | TEXT | - |
| `currency` | DECIMAL | format, suffix |

## Configurazione

### Variabili d'Ambiente

```bash
DATABASE_URL=postgresql://user:pass@host:5432/dbname
JWT_SECRET_KEY=your-secret-key-min-32-chars
SECRET_KEY=flask-secret-key
FLASK_ENV=development
LLM_PROVIDER=openrouter  # Per AI
```

## Commit History

- `696fcf4` - refactor: Complete backend structure reorganization
- `2938e52` - feat: Add CQRS architecture to AI service

---

*Per la cronologia completa delle modifiche di questo documento, consulta la cronologia Git del repository.*

---

> Ultimo aggiornamento: 10 Settembre 2026 | [Torna all'Indice](INDEX.md)
