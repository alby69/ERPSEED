# Architettura ERPSEED Backend

## Panoramica

ERPSEED è un sistema ERP modulare costruito con Flask. Utilizza un'architettura multi-tenant con supporto per:
- Creazione dinamica di modelli dati (No-Code Builder)
- Workflow automation
- Sistema webhook event-driven
- AI Assistant integrato

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
├── __init__.py           # App factory (create_app)
├── extensions.py         # Inizializzazione estensioni Flask
├── run.py                # Entry point
│
├── core/                 # CORE: Autenticazione, Tenant, Permessi
│   ├── api/             # API endpoints core
│   │   ├── auth.py      # Login, Register, JWT
│   │   ├── tenant.py    # Gestione tenant
│   │   ├── modules.py   # Moduli sistema
│   │   ├── system.py    # Configurazioni sistema
│   │   └── pdf.py      # Generazione PDF
│   ├── models/          # Modelli core
│   │   ├── base.py      # BaseModel con soft delete
│   │   ├── tenant.py    # Tenant, User, Role
│   │   ├── test_models.py
│   │   └── sys_*.py    # Modelli di sistema
│   ├── services/        # Servizi core
│   │   ├── auth_service.py
│   │   ├── tenant_service.py
│   │   └── query_filter.py
│   └── middleware/      # Middleware tenant
│
├── services/             # BUSINESS LOGIC
│   ├── base.py           # BaseService (pattern base)
│   ├── products_service/ # DDD: Products module
│   │   ├── models.py
│   │   ├── service.py
│   │   └── rest_api.py
│   ├── sales_service/    # DDD: Sales module
│   │   ├── models.py
│   │   ├── service.py
│   │   └── rest_api.py
│   └── dynamic_api_service.py  # Dynamic CRUD (945 lines - DA SPLITTARE)
│
├── builder/              # NO-CODE BUILDER
│   ├── models.py         # Archetype, Component, Block
│   ├── api.py           # Builder API
│   └── generator.py    # Code generation
│
├── entities/             # VISION ARCHETYPES
│   ├── soggetto.py      # Soggetto (Cliente/Fornitore)
│   ├── ruolo.py         # Ruolo
│   ├── indirizzo.py     # Indirizzo
│   └── contatto.py      # Contatto
│
├── webhook_*/             # WEBHOOK SYSTEM
│   ├── routes.py         # API endpoints
│   ├── service.py       # Logica business
│   └── models.py        # Webhook, Delivery
│
├── workflow_*/           # WORKFLOW ENGINE
│   ├── routes.py
│   ├── service.py
│   ├── executor.py      # Step execution
│   └── models.py
│
├── shared/               # SHARED UTILITIES
│   ├── events/          # Event bus
│   └── utils.py         # Helpers (log_audit, etc.)
│
├── plugin_system/        # PLUGIN ARCHITECTURE
│   ├── manager.py        # PluginManager
│   └── plugins/         # Plugin samples
│
├── ai/                   # AI ASSISTANT
│   └── api.py
│
├── marketplace/          # MARKETPLACE
│   └── api.py
│
├── analytics/            # ANALYTICS & DASHBOARD
│   ├── api.py
│   └── dashboard.py
│
├── commands/             # CLI COMMANDS
│   ├── seed_*.py        # Database seeding
│   └── setup_*.py      # Setup utilities
│
└── tests/                # TEST SUITE
```

## Pattern Architetturali

### 1. Service Layer Pattern (Nuovo - Consigliato)

```python
# services/products_service/service.py
class ProductService(BaseService):
    def __init__(self, db):
        super().__init__(db)
        self.model = Product
    
    def create(self, data):
        # Logica business
        return super().create(data)
    
    def calculate_price(self, product_id):
        # Logica specifica
        pass
```

### 2. Blueprint + Marshmallow (API REST)

```python
# routes.py
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required

blp = Blueprint('products', __name__, url_prefix='/products')

@blp.route('/')
@blp.arguments(ProductSchema)
@blp.response(ProductSchema)
@jwt_required()
def create_product(data):
    return product_service.create(data)
```

### 3. Dynamic API Pattern

Per il No-Code Builder, i modelli vengono creati runtime:

```python
# models.py (builder)
class SysModel(db.Model):
    name = db.Column(db.String(100))
    fields = db.relationship('SysField', back_populates='model')

class SysField(db.Model):
    name = db.Column(db.String(100))
    type = db.Column(db.String(50))  # string, integer, select, relation, etc.
```

## Multi-Tenancy

### Schema Isolation

```
┌─────────────────────────────────────┐
│           PostgreSQL                │
├─────────────────────────────────────┤
│  schema: tenant_1                   │
│  ├── users                          │
│  ├── projects                       │
│  └── sys_models_*                   │
├─────────────────────────────────────┤
│  schema: tenant_2                   │
│  ├── users                          │
│  ├── projects                       │
│  └── sys_models_*                   │
└─────────────────────────────────────┘
```

### Middleware Flow

```
Request → TenantMiddleware → Extract Tenant ID → Set Context → Route Handler
```

```python
# core/middleware/tenant_middleware.py
class TenantMiddleware:
    @staticmethod
    def process_request():
        tenant_id = request.headers.get('X-Tenant-ID')
        if tenant_id:
            set_current_tenant(tenant_id)
```

## Autenticazione JWT

```
┌──────────┐    ┌──────────┐    ┌──────────┐
│  Login   │───▶│  JWT     │───▶│  Access  │
│  POST    │    │  Token   │    │  Resource│
└──────────┘    └──────────┘    └──────────┘
   /api/v1/auth/login
```

### Token Flow

1. **Access Token**: Scade in 15 minuti
2. **Refresh Token**: Scade in 7 giorni
3. **Header**: `Authorization: Bearer <token>`

## Event System

```python
# shared/events/event_bus.py
class EventBus:
    def publish(self, event_name, data):
        for handler in self._handlers[event_name]:
            handler(data)
    
    def subscribe(self, event_name, handler):
        self._handlers[event_name].append(handler)

# Usage
event_bus.publish('user.created', {'user_id': 123})
```

## Plugin System

```
plugins/
├── my_plugin/
│   ├── __init__.py
│   ├── routes.py      # Blueprint routes
│   └── services.py    # Business logic
└── plugin.yml          # Metadata
```

```yaml
# plugin.yml
name: my_plugin
version: 1.0.0
routes:
  - /custom-endpoint
permissions:
  - read:users
  - write:projects
```

## Workflow Engine

```
Trigger (event/time) → Workflow Definition → Steps Execution
                                              ├── Step 1
                                              ├── Step 2 (depends on 1)
                                              └── Step 3
```

### Step Types

- **HTTP Request**: Chiamate a servizi esterni
- **Condition**: Branch logico
- **Notification**: Email/SMS/Webhook
- **Code**: Python custom logic

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
FLASK_DEBUG=1
```

### Database Connection

```python
# PostgreSQL (Produzione)
DATABASE_URL=postgresql://postgres:password@localhost:5432/erpseed

# SQLite (Sviluppo)
DATABASE_URL=sqlite:///data.db
```

## Error Handling

```python
# Standard error response
{
    "code": 404,
    "name": "Not Found",
    "description": "Resource not found"
}

# Validation error
{
    "message": "Validation error",
    "errors": {"field": ["Error message"]}
}
```

## Performance Considerations

1. **Pagination**: Tutti gli endpoint listano con paginazione
2. **Soft Delete**: Record eliminati non vengono rimossi fisicamente
3. **Caching**: Redis per sessioni e cache query
4. **Index**: Indici su campi foreign key e frequently queried

---

*Ultimo aggiornamento: 2026-03-18*
