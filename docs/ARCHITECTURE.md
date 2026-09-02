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
├── extensions.py            # Flask extensions initialization
├── schemas.py               # Marshmallow schemas
├── container.py            # Dependency Injection container
├── run.py                   # Entry point
│
├── models/                  # DATABASE MODELS (spacchettato)
│   ├── __init__.py
│   ├── base.py             # BaseModel con soft delete
│   ├── user.py             # User model
│   ├── project.py          # Project model
│   ├── product.py          # Product model
│   ├── sales.py            # SalesOrder, SalesOrderLine
│   ├── purchase.py         # PurchaseOrder, PurchaseOrderLine
│   ├── ai.py              # AIConversation
│   ├── chart.py            # ChartLibraryConfig
│   ├── user_role.py       # UserRole
│   ├── tax.py             # TaxRate
│   ├── uom.py             # UnitOfMeasure
│   ├── pricing.py         # PriceList, PriceListItem
│   ├── movement_reason.py # MovementReason
│   ├── goods_receipt.py   # GoodsReceipt, GoodsReceiptLine
│   ├── maturity.py        # Maturity
│   ├── crm.py             # Lead, Opportunity
│   ├── contract.py        # Contract
│   ├── manufacturing.py   # BillOfMaterial, BOMLine, WorkCycle, WorkPhase, ProductionOrder, ProductionOrderMaterial
│   ├── project_management.py # BusinessProject, Timesheet, TimesheetLine
│   ├── report.py          # Report, ReportExecution
│   ├── vat.py             # VatRegisterEntry, VatLiquidation, IntrastatDeclaration
│   ├── riba.py            # RiBa, RiBaItem
│   ├── lot.py             # Lot, SerialNumber
│   ├── purchase_request.py # PurchaseRequest, RFQ, SupplierQuotation (con linee)
│   ├── mrp.py             # MRPRun, MRPSuggestion
│   ├── workflow.py        # Workflow, WorkflowStep, WorkflowExecution
│   ├── webhook.py         # WebhookEndpoint, WebhookDelivery, WebhookEvent
│   └── system/            # System models
│       ├── sys_model.py   # SysModel
│       ├── sys_field.py   # SysField
│       ├── sys_view.py    # SysView
│       ├── sys_component.py
│       ├── sys_action.py
│       ├── sys_chart.py
│       ├── sys_dashboard.py
│       └── sys_model_version.py
│
├── routes/                  # API ROUTES
│   ├── __init__.py
│   ├── projects.py
│   ├── dashboard.py
│   ├── analytics.py
│   ├── dynamic.py          # Dynamic CRUD API
│   ├── workflows.py
│   ├── webhooks.py
│   ├── templates.py
│   ├── visual_builder.py
│   ├── versioning.py
│   ├── debugging.py
│   └── gdo.py             # GDO Reconciliation
│
├── services/                # BUSINESS LOGIC
│   ├── __init__.py
│   ├── base.py            # BaseService
│   ├── workflow_service.py
│   ├── webhook_service.py
│   ├── workflow_executor.py
│   ├── dynamic_api_service.py
│   ├── project_service.py
│   ├── user_service.py
│   ├── template_service.py
│   ├── versioning_service.py
│   ├── file_processing_service.py
│   ├── gdo_reconciliation_service.py
│   ├── gdo_excel_reporter.py
│   └── generic_service.py
│
├── cli/                     # CLI SCRIPTS
│   ├── create_admin.py
│   ├── create_default_project.py
│   ├── setup_database.py
│   ├── reset_db.py
│   ├── register_gdo_module.py
│   ├── test_container.py
│   └── create_tenant.py
│
├── seeds/                   # DATABASE SEEDS
│   ├── initial.py          # Admin user + tenant
│   ├── comuni.py          # Italian geographic data
│   ├── metadata.py         # SysComponent, SysAction
│   ├── kpi.py             # Dashboard KPI
│   └── gdo_models.py       # GDO template
│
├── core/                    # CORE SYSTEM
│   ├── api/               # Core API endpoints
│   │   ├── auth.py        # Login, Register, JWT
│   │   ├── tenant.py       # Tenant management
│   │   ├── modules.py     # Module system
│   │   ├── system.py      # System config
│   │   ├── pdf.py         # PDF generation
│   │   ├── test_runner.py  # Test execution
│   │   ├── custom_modules.py
│   │   ├── module_api.py
│   │   └── import_export.py
│   ├── models/            # Core models
│   │   ├── base.py
│   │   ├── tenant.py
│   │   ├── tenant_member.py
│   │   ├── audit.py
│   │   ├── module.py
│   │   ├── module_definition.py
│   │   ├── modulo.py
│   │   ├── tenant_module.py
│   │   └── test_models.py
│   ├── services/          # Core services
│   │   ├── auth_service.py
│   │   ├── auth/
│   │   ├── tenant_service.py
│   │   ├── tenant/
│   │   ├── module_service.py
│   │   ├── permission_service.py
│   │   ├── query_filter.py
│   │   ├── import_export_service.py
│   │   ├── pdf_service.py
│   │   └── test_engine.py
│   └── middleware/         # Middleware
│       ├── tenant_middleware.py
│       └── module_middleware.py
│
├── modules/                 # MODULI APPLICATIVI
│   ├── entities/           # Anagrafiche (Vision Archetypes)
│   │   ├── soggetto.py    #   Soggetto (Cliente/Fornitore)
│   │   ├── ruolo.py
│   │   ├── indirizzo.py
│   │   ├── indirizzo_geografico.py
│   │   ├── contatto.py
│   │   ├── comune.py
│   │   ├── routes.py      #   CRUD: soggetti, ruoli, indirizzi, contatti
│   │   ├── comuni_routes.py  # CRUD: comuni, regioni, province
│   │   └── schemas.py
│   ├── products/           # Prodotti (CQRS)
│   │   ├── service_api.py #   Entry point (execute command)
│   │   ├── api/rest_api.py #   REST CRUD
│   │   ├── domain/        #   Product, ProductCreatedEvent
│   │   ├── application/   #   Handlers, Commands, Queries
│   │   └── infrastructure/ #   ProductRepository
│   ├── sales/              # Vendite (CQRS)
│   │   └── (same CQRS structure)
│   ├── purchases/          # Acquisti (CQRS)
│   │   └── (same CQRS structure)
│   ├── analytics/          # Dashboard e KPI
│   │   └── api/rest_api.py, dashboard_api.py
│   ├── automation/         # Workflow e Webhook
│   │   └── api/workflows_api.py, webhooks_api.py
│   ├── ai/                 # AI Assistant
│   │   ├── service.py, api.py, context.py
│   │   ├── tool_registry.py, tool_executors.py
│   │   └── adapters/ (openai, anthropic, ollama, openrouter)
│   ├── builder/            # No-Code Builder (CQRS)
│   │   └── application/, domain/, api.py
│   ├── dynamic_api/        # Dynamic CRUD engine
│   │   └── api/routes/, services/field_validator, query_builder, result_processor
│   ├── gdo/                # GDO Reconciliation
│   │   └── services/
│   ├── projects/           # Progetti (CQRS)
│   │   └── api/rest_api.py, application/, service.py
│   ├── users/              # Utenti (CQRS)
│   │   └── api/rest_api.py, application/, service.py
│   ├── system_tools/       # Template, Versioning, Debug
│   │   └── api/templates_api.py, versioning_api.py, gdo_api.py
│   ├── tax/                # Aliquote IVA (CQRS)
│   ├── product_categories/ # Categorie Prodotto
│   ├── uom/                # Unità di Misura
│   ├── pricing/            # Listini Prezzo
│   ├── invoicing/          # Fatturazione Vendita (CQRS)
│   ├── inventory/          # Magazzino (movimenti + causali)
│   ├── goods_receipt/      # DDT Entrata Merci
│   ├── maturities/         # Scadenzario
│   ├── crm/                # CRM (Lead + Opportunità)
│   ├── contracts/          # Contratti
│   ├── manufacturing/      # Produzione (BOM, Cicli, ODP)
│   ├── project_management/ # Timesheet + Budget Commessa
│   ├── report_designer/    # Report Designer
│   ├── vat/                # Registri IVA + Intrastat
│   ├── riba/               # Ri.Ba. (Ricevute Bancarie)
│   ├── lot/                # Lotti e Serial Number
│   ├── purchase_requests/  # Richieste Acquisto + RFQ
│   └── mrp/                # MRP (Material Requirements Planning)
│
├── plugins/                # PLUGIN SYSTEM
│   ├── base.py
│   ├── registry.py
│   ├── accounting/
│   ├── hr/
│   └── inventory/
│
├── shared/                 # SHARED UTILITIES
│   ├── events/
│   │   ├── event_bus.py
│   │   ├── event.py
│   │   └── system_events.py
│   ├── utils/
│   │   ├── audit.py
│   │   ├── filters.py
│   │   └── pagination.py
│   ├── interfaces/
│   └── exceptions/
│
├── composition/            # COMPOSITION SYSTEM
├── orm/                    # ORM ENHANCEMENTS
├── view_renderer/          # VIEW RENDERING
│
├── docs/                   # DOCUMENTATION
├── tests/                  # TEST SUITE
└── translations/           # i18n
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

### Field Types

| Type | Database | Validation |
|------|----------|------------|
| `string` | VARCHAR | max_length |
| `integer` | INTEGER | min, max |
| `float` | FLOAT | min, max |
| `boolean` | BOOLEAN | - |
| `date` | DATE | - |
| `datetime` | DATETIME | - |
| `select` | ENUM / VARCHAR | options[] |
| `relation` | FOREIGN KEY | target_model |
| `file` | VARCHAR (path) | allowed_extensions |
| `richtext` | TEXT | - |
| `currency` | DECIMAL | - |

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
