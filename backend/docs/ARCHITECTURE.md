# Architettura ERPSEED Backend

## Panoramica

ERPSEED è un sistema ERP modulare costruito con Flask. Utilizza un'architettura **CQRS** (Command Query Responsibility Segregation) con supporto per:

- Creazione dinamica di modelli dati (No-Code Builder)
- Workflow automation
- Sistema webhook event-driven
- AI Assistant integrato
- Multi-tenancy completo

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

---

## Struttura del Progetto

```
backend/
├── __init__.py              # App factory (create_app)
├── extensions.py            # Flask extensions initialization
├── schemas.py               # Marshmallow schemas (legacy)
│
├── domain/                  # DOMAIN LAYER - Modelli puri
│   ├── entities/
│   │   ├── models.py       # Soggetto, Ruolo domain models
│   │   └── events.py       # Domain events
│   ├── marketplace/
│   │   ├── models.py       # Category, BlockListing, Review
│   │   └── events.py       # Domain events
│   └── products/
│       └── events.py       # Product events
│
├── application/             # APPLICATION LAYER - CQRS Commands/Queries
│   ├── entities/
│   │   ├── commands/       # CreateSoggettoCommand, UpdateRuoloCommand, etc.
│   │   ├── handlers.py     # SoggettoCommandHandler, RuoloQueryHandler
│   │   └── __init__.py
│   ├── marketplace/
│   │   ├── commands/
│   │   └── handlers.py
│   └── __init__.py
│
├── infrastructure/          # INFRASTRUCTURE LAYER - Persistence
│   ├── entities/
│   │   ├── models.py       # SQLAlchemy models (Soggetto, Ruolo, etc.)
│   │   └── repository.py   # SoggettoRepository, RuoloRepository
│   ├── marketplace/
│   │   ├── models.py       # SQLAlchemy models (Category, BlockListing)
│   │   └── repository.py   # CategoryRepository, ListingRepository
│   ├── builder/
│   │   └── models.py      # Archetype, Component, Block SQLAlchemy
│   ├── products/
│   │   └── repository.py
│   ├── container.py        # Dependency Injection
│   └── view_renderer/
│
├── endpoints/              # ENDPOINTS LAYER - REST API
│   ├── entities.py         # Soggetto, Ruolo, Indirizzo, Contatto APIs
│   ├── marketplace.py      # Category, Listing, Review APIs
│   ├── geographic.py       # Regioni, Province, Comuni, Geocoding
│   ├── products.py         # Product CRUD
│   ├── sales.py            # SalesOrder CRUD
│   ├── purchases.py        # PurchaseOrder CRUD
│   ├── builder.py          # Archetype, Component, Block APIs
│   ├── ai.py               # AI Assistant endpoints
│   ├── projects.py         # Project management
│   ├── users.py            # User management
│   ├── dashboard.py        # Dashboard APIs
│   ├── analytics.py        # Analytics APIs
│   ├── webhooks.py         # Webhook management
│   ├── workflows.py        # Workflow APIs
│   ├── visual_builder.py   # Visual Builder APIs
│   ├── templates.py        # Template management
│   ├── gdo.py              # GDO Reconciliation
│   └── dynamic.py          # Dynamic CRUD API
│
├── core/                   # CORE SYSTEM
│   ├── api/               # Core API endpoints
│   │   ├── auth.py        # Login, Register, JWT
│   │   ├── tenant.py       # Tenant management
│   │   ├── modules.py      # Module system
│   │   ├── system.py       # System config
│   │   ├── pdf.py          # PDF generation
│   │   └── test_runner.py   # Test execution
│   ├── models/            # Core models
│   │   ├── base.py        # BaseModel con soft delete
│   │   ├── tenant.py       # Tenant model
│   │   └── test_models.py  # Test models
│   ├── services/          # Core services
│   │   ├── auth_service.py
│   │   ├── tenant_service.py
│   │   └── query_filter.py # TenantQueryFilter
│   └── middleware/        # Middleware
│       └── tenant_middleware.py
│
├── models/                # LEGACY MODELS (deprecated)
│   ├── base.py
│   ├── user.py
│   ├── project.py
│   ├── product.py         # Product, ProductStock
│   ├── sales.py           # SalesOrder, SalesOrderLine
│   └── purchase.py        # PurchaseOrder, PurchaseOrderLine
│
├── services/              # LEGACY SERVICES (deprecated)
│   ├── base.py
│   ├── generic_service.py
│   └── template_service.py
│
├── shared/                # SHARED UTILITIES
│   ├── decorators.py       # @tenant_required, etc.
│   ├── events/
│   │   ├── event_bus.py   # EventBus singleton
│   │   ├── event.py       # Base event class
│   │   └── webhook_triggers.py
│   ├── utils/
│   │   ├── utils.py       # paginate, apply_filters, etc.
│   │   └── crud.py
│   ├── commands/           # Shared command types
│   ├── queries/            # Shared query types
│   └── handlers/            # Shared handler base classes
│
├── plugins/               # PLUGIN SYSTEM
│   ├── base.py            # BasePlugin class
│   ├── registry.py        # ModuleRegistry
│   ├── inventory/          # Inventory plugin
│   │   ├── models.py      # InventoryLocation, LocationStock, StockMovement
│   │   └── routes.py      # Inventory CRUD APIs
│   ├── accounting/         # Accounting plugin
│   └── hr/                # HR plugin
│
├── cli/                   # CLI SCRIPTS
├── seeds/                 # DATABASE SEEDS
├── tests/                 # TEST SUITE
└── translations/           # i18n
```

---

## Architettura CQRS

### Principi Fondamentali

Il backend ERPSEED utilizza il pattern **CQRS** (Command Query Responsibility Segregation) per separare le operazioni di lettura da quelle di scrittura.

### Flusso di una Richiesta

```
┌─────────────────────────────────────────────────────────────────────┐
│                        REQUEST ENTRY                                │
│                     POST /api/entities/soggetti                     │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     ENDPOINTS LAYER                                │
│                    endpoints/entities.py                            │
│  - Valida autenticazione (JWT)                                      │
│  - Estrae X-Tenant-ID dall'header                                  │
│  - Crea Command object                                             │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER                                 │
│              application/entities/handlers.py                       │
│  - SoggettoCommandHandler.handle_create()                          │
│  - Valida regole di business                                       │
│  - Coordina repository                                             │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  INFRASTRUCTURE LAYER                               │
│             infrastructure/entities/repository.py                     │
│  - Persiste/recupera dati dal database                             │
│  - db.session.flush() + db.session.commit()                         │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       DATABASE                                      │
│                    PostgreSQL/SQLite                                │
└─────────────────────────────────────────────────────────────────────┘
```

### Esempio: Creazione di un Soggetto

```python
# 1. ENDPOINT (endpoints/entities.py)
class SoggettoListView(MethodView):
    def post(self):
        tenant_id = _get_tenant_id()  # Estrae tenant da header

        command = CreateSoggettoCommand(
            tenant_id=tenant_id,
            codice=data['codice'],
            nome=data['nome'],
            # ...
        )

        handler = SoggettoCommandHandler()
        soggetto = handler.handle_create(command)
        return jsonify(_soggetto_to_dict(soggetto)), 201

# 2. COMMAND (application/entities/commands/__init__.py)
@dataclass
class CreateSoggettoCommand:
    tenant_id: int
    codice: str
    nome: str
    tipo_soggetto: str = 'persona_fisica'
    cognome: Optional[str] = None
    # ...

# 3. HANDLER (application/entities/handlers.py)
class SoggettoCommandHandler:
    def handle_create(self, command: CreateSoggettoCommand) -> Soggetto:
        # Validazione
        existing = self.repository.get_by_codice(command.tenant_id, command.codice)
        if existing:
            raise ValueError(f"Soggetto {command.codice} already exists")

        # Creazione dominio
        soggetto = Soggetto(
            codice=command.codice,
            nome=command.nome,
            # ...
        )

        # Persistenza
        result = self.repository.create(soggetto)
        db.session.commit()

        return self.repository.get_by_id(result.id)

# 4. REPOSITORY (infrastructure/entities/repository.py)
class SoggettoRepository:
    def create(self, soggetto: Soggetto) -> Soggetto:
        model = SoggettoModel(
            codice=soggetto.codice,
            nome=soggetto.nome,
            tenant_id=soggetto.tenant_id,
        )
        db.session.add(model)
        db.session.flush()  # Ottieni ID senza commit
        return model

    def commit(self):
        db.session.commit()
```

---

## Domain vs Infrastructure Models

### Domain Layer (`domain/`)

Contiene **modelli puri Python** (dataclass) che rappresentano il dominio senza dipendenze da framework:

```python
# domain/entities/models.py
@dataclass
class Soggetto:
    id: Optional[int] = None
    codice: str = ''
    nome: str = ''
    cognome: Optional[str] = None
    ragione_sociale: Optional[str] = None
    partita_iva: Optional[str] = None
    tenant_id: Optional[int] = None
    # ... solo dati, nessuna logica ORM
```

### Infrastructure Layer (`infrastructure/`)

Contiene i **modelli SQLAlchemy** che mappano alle tabelle del database:

```python
# infrastructure/entities/models.py
class Soggetto(BaseModel):
    __tablename__ = 'soggetti'

    codice = db.Column(db.String(50), nullable=False)
    nome = db.Column(db.String(200), nullable=False)
    cognome = db.Column(db.String(200))
    ragione_sociale = db.Column(db.String(200))
    partita_iva = db.Column(db.String(20))
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'))

    # Relazioni
    ruoli = db.relationship('SoggettoRuolo', back_populates='soggetto')
```

### Trasformazione Domain <-> Infrastructure

I Repository gestiscono la trasformazione:

```python
class SoggettoRepository:
    def to_domain(self, model: SoggettoModel) -> Soggetto:
        return Soggetto(
            id=model.id,
            codice=model.codice,
            nome=model.nome,
            # ...
        )

    def to_model(self, domain: Soggetto) -> SoggettoModel:
        return SoggettoModel(
            id=domain.id,
            codice=domain.codice,
            nome=domain.nome,
            # ...
        )
```

---

## Multi-Tenancy

### Schema di Isolamento

```
┌─────────────────────────────────────────────────┐
│              DATABASE                           │
├─────────────────────────────────────────────────┤
│  TENANT 1                                      │
│  ├── users (con tenant_id=1)                   │
│  ├── projects (con tenant_id=1)                │
│  ├── soggetti (con tenant_id=1)               │
│  └── sys_models_* (con tenant_id=1)           │
├─────────────────────────────────────────────────┤
│  TENANT 2                                      │
│  ├── users (con tenant_id=2)                   │
│  ├── projects (con tenant_id=2)                │
│  ├── soggetti (con tenant_id=2)               │
│  └── sys_models_* (con tenant_id=2)           │
└─────────────────────────────────────────────────┘
```

### Middleware Flow

```
Request → TenantMiddleware → Header X-Tenant-ID → Thread Local Context → Route Handler
```

```python
# core/middleware/tenant_middleware.py
class TenantMiddleware:
    @staticmethod
    def process_request():
        tenant_id = request.headers.get('X-Tenant-ID', type=int)
        if tenant_id:
            TenantContext.set_tenant_id(tenant_id)
```

---

## Event System

### Event Bus

```python
# shared/events/event_bus.py
class EventBus:
    _instance = None

    def publish(self, event_name: str, data: dict):
        for handler in self._handlers.get(event_name, []):
            handler(data)

    def subscribe(self, event_name: str, handler: callable):
        self._handlers.setdefault(event_name, []).append(handler)
```

### Domain Events

```python
# domain/entities/events.py
class SoggettoCreatedEvent:
    def __init__(self, soggetto_id: int, codice: str, tenant_id: int):
        self.soggetto_id = soggetto_id
        self.codice = codice
        self.tenant_id = tenant_id
        self.timestamp = datetime.utcnow()
```

---

## Plugin System

### Struttura Plugin

```
plugins/
├── base.py                 # BasePlugin astratta
├── registry.py             # ModuleRegistry
├── inventory/              # Plugin Inventario
│   ├── models.py          # InventoryLocation, LocationStock
│   └── routes.py          # CRUD APIs
├── accounting/             # Plugin Contabilità
└── hr/                    # Plugin Risorse Umane
```

### Ciclo di Vita Plugin

```python
# plugins/base.py
class BasePlugin:
    name: str = ""
    enabled: bool = False

    def install(self):
        """Called when plugin is enabled."""
        pass

    def uninstall(self):
        """Called when plugin is disabled."""
        pass

# plugins/registry.py
class ModuleRegistry:
    def enable(self, name: str, app=None, db=None, api=None):
        plugin = self._plugin_classes[name](app=app, db=db, api=api)
        plugin.install()
        self._plugins[name] = plugin
```

---

## API Endpoints

### Endpoint Base

```
http://localhost:5000/api/entities/soggetti
```

### Header Necessari

| Header | Valore | Descrizione |
|--------|--------|-------------|
| `Authorization` | `Bearer <jwt_token>` | Token JWT |
| `X-Tenant-ID` | `1` | ID Tenant (per API tenant-aware) |

### Risposte Standard

```json
// Successo (201 Created)
{
  "id": 1,
  "codice": "CLI001",
  "nome": "Mario",
  "cognome": "Rossi"
}

// Errore (404 Not Found)
{
  "error": "Soggetto not found"
}

// Errore Validazione (400)
{
  "message": "Validation error",
  "errors": {"codice": ["Missing data for required field."]}
}
```

---

## Configurazione

### Variabili d'Ambiente

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname
# oppure
DATABASE_URL=sqlite:///data.db

# JWT
JWT_SECRET_KEY=your-secret-key-at-least-32-chars-long

# Flask
FLASK_ENV=development
FLASK_DEBUG=1

# AI (opzionale)
LLM_PROVIDER=openrouter
OPENAI_API_KEY=sk-...
```

---

## Commit History Recenti

- `CQRS Migration` - Refactoring completo verso architettura CQRS
  - Nuova struttura: `domain/`, `application/`, `infrastructure/`, `endpoints/`
  - Migrazione Entities, Marketplace, Geographic routes
  - Eliminazione service wrapper deprecati

---

*Ultimo aggiornamento: 2026-03-19*
