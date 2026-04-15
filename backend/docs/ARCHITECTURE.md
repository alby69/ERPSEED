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
├── entities/               # VISION ARCHETYPES
│   ├── __init__.py
│   ├── soggetto.py        # Soggetto (Cliente/Fornitore)
│   ├── ruolo.py
│   ├── indirizzo.py
│   ├── indirizzo_geografico.py
│   ├── contatto.py
│   ├── routes.py
│   ├── comuni_routes.py
│   └── schemas.py
│
├── ai/                     # AI ASSISTANT (Legacy)
│   ├── __init__.py
│   ├── service.py         # AIService (800+ lines)
│   ├── api.py
│   ├── context.py
│   ├── tool_registry.py
│   ├── tool_executors.py
│   ├── test_generator.py
│   └── adapters/
│
├── ai_service/             # AI SERVICE (CQRS Pattern)
│   ├── __init__.py
│   ├── application/       # CQRS Application Layer
│   │   ├── commands.py     # Command definitions
│   │   ├── queries.py     # Query definitions
│   │   ├── handlers.py    # Command handlers
│   │   └── query_handlers.py
│   ├── domain/            # Domain Layer
│   │   ├── services/
│   │   │   ├── chat_service.py   # ChatService
│   │   │   └── tool_service.py   # ToolService
│   │   └── ports/
│   │       ├── llm_port.py
│   │       └── vectorstore_port.py
│   └── infrastructure/    # Infrastructure Layer
│       ├── adapters/
│       │   ├── base_adapter.py
│       │   ├── openai_adapter.py
│       │   ├── anthropic_adapter.py
│       │   ├── ollama_adapter.py
│       │   └── openrouter_adapter.py
│       └── factory.py     # AdapterFactory
│
├── builder_service/        # BUILDER (CQRS Pattern)
│   ├── __init__.py
│   ├── api.py
│   ├── container.py
│   ├── application/
│   │   ├── commands/
│   │   └── handlers/
│   ├── domain/
│   │   └── models/
│   └── infrastructure/
│       ├── persistence/
│       └── repositories/
│
├── products_service/       # PRODUCTS (CQRS)
├── sales_service/          # SALES (CQRS)
├── purchases_service/       # PURCHASES (CQRS)
├── analytics_service/       # ANALYTICS (CQRS)
│
├── builder/                # LEGACY BUILDER (deprecated)
│   ├── models.py
│   ├── api.py
│   ├── cli.py
│   └── generator.py
│
├── marketplace/            # MARKETPLACE
│   ├── models.py
│   └── api.py
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

### Schema Isolation

```
PostgreSQL
├── schema: tenant_1
│   ├── users
│   ├── projects
│   └── sys_models_*
└── schema: tenant_2
    ├── users
    ├── projects
    └── sys_models_*
```

### Middleware Flow

```
Request → TenantMiddleware → Extract Tenant ID → Set Context → Route Handler
```

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

```
Trigger (event/time) → Workflow Definition → Steps Execution
                                              ├── Step 1
                                              ├── Step 2
                                              └── Step 3
```

## Dynamic Builder (No-Code)

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

*Ultimo aggiornamento: 2026-03-18*
