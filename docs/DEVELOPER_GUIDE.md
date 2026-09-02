# Developer Guide - ERPSEED Backend

> Per l'installazione iniziale e il setup dell'ambiente (Docker o locale) vedi [GETTING_STARTED.md](GETTING_STARTED.md).

---

## Convenzioni di Refactoring

Quando si modifica un modulo esistente o se ne crea uno nuovo:
1. **Verificare il BaseModel**: Assicurarsi di importare da `backend.core.models.base` (non `backend.models.base`).
2. **Usare BaseService**: Se il servizio fa CRUD semplice, non riscrivere i metodi, usa quelli ereditati da `backend.core.services.base.BaseService`.
3. **Disaccoppiamento**: Non importare servizi direttamente se possibile; usare il pattern `ServiceProxy` o l'iniezione tramite container.
4. **Schema unico**: Usare `backend.core.schemas.dynamic_schemas` per centralizzare gli schemi Marshmallow delle API dinamiche.

---

## Struttura del Codice

### File Principali

```
backend/
├── __init__.py      # App factory (create_app)
├── run.py           # Entry point
├── extensions.py    # Flask extensions
├── models/          # Modelli SQLAlchemy
└── core/            # Componenti condivisi e base
```

### Creare un Nuovo Modulo

Tutti i nuovi moduli backend devono seguire l'architettura **CQRS (Command Query Responsibility Segregation)**, in modo da disaccoppiare logica di business, accesso ai dati ed esposizione API (necessaria anche per l'esposizione automatica come capability in AgentMesh).

#### 1. Struttura del Modulo CQRS

```
backend/modules/my_feature/
├── __init__.py                # Entry point del modulo / service proxy
├── api/
│   └── rest_api.py            # Flask-Smorest Blueprint
├── application/
│   ├── commands/              # Dataclass dei comandi (Create, Update, Delete)
│   ├── queries/               # Dataclass delle query (Get, List)
│   └── handlers.py            # Command/Query Handlers
├── domain/
│   └── models.py              # Modello di dominio / SQLAlchemy
└── infrastructure/
    └── repository.py          # SQLAlchemy Repository per accesso dati
```

#### 2. Modello di Dominio (`domain/models.py`)

```python
from backend.extensions import db
from backend.core.models.base import BaseModel

class FeatureItem(BaseModel):
    __tablename__ = 'feature_items'

    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
```

#### 3. Comandi e Handler (`application/`)

```python
# application/commands.py
from dataclasses import dataclass

@dataclass
class CreateFeatureItemCommand:
    name: str
    code: str
    tenant_id: int

# application/handlers.py
class CreateFeatureItemHandler:
    def __init__(self, repository):
        self.repository = repository

    def handle(self, command: CreateFeatureItemCommand):
        item = FeatureItem(
            name=command.name,
            code=command.code,
            tenant_id=command.tenant_id
        )
        return self.repository.save(item)
```

#### 4. REST API Blueprint (`api/rest_api.py`)

```python
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required
from backend.core.services.tenant import TenantContext

blp = Blueprint('feature_items', __name__, url_prefix='/api/v1/feature-items')

@blp.route('/')
class FeatureItemList(MethodView):
    @blp.response(200)
    @jwt_required()
    def get(self):
        tenant_id = TenantContext.get_tenant_id()
        return feature_service.list_items(tenant_id)

    @blp.arguments(FeatureItemSchema)
    @blp.response(201)
    @jwt_required()
    def post(self, data):
        data['tenant_id'] = TenantContext.get_tenant_id()
        command = CreateFeatureItemCommand(**data)
        return feature_service.execute_command(command)
```

> **Pattern Legacy**: Per manutenzione di moduli semplici esistenti, è accettabile l'uso diretto di Flask-Smorest Blueprint + MethodView + `db.session` senza il layer CQRS completo, ma il pattern CQRS sopra descritto è lo standard obbligatorio per tutti i nuovi moduli.

---

## Pattern e Best Practices

### 1. Service Layer

```python
# services/base.py
class BaseService:
    def __init__(self, db):
        self.db = db

    def create(self, model_class, data):
        instance = model_class(**data)
        self.db.session.add(instance)
        self.db.session.commit()
        return instance

    def get(self, model_class, id):
        return model_class.query.get_or_404(id)

    def paginate(self, query, page=1, per_page=20):
        return query.paginate(page=page, per_page=per_page, error_out=False)
```

### 2. Validazione

```python
from marshmallow import validates, ValidationError

class ProductSchema(Schema):
    price = fields.Float(required=True)

    @validates('price')
    def validate_price(self, value):
        if value < 0:
            raise ValidationError('Price must be positive')
```

### 3. Autorizzazione

```python
from flask_jwt_extended import jwt_required, get_jwt
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        claims = get_jwt()
        if claims.get('role') != 'admin':
            abort(403, message='Admin access required')
        return f(*args, **kwargs)
    return decorated_function
```

### 4. Middleware Personalizzato

```python
# core/middleware/my_middleware.py
class MyMiddleware:
    @staticmethod
    def process_request():
        # Logica middleware
        pass

    @staticmethod
    def process_response(response):
        # Modifica risposta
        return response
```

---

## Testing

### Esecuzione Test

```bash
# Tutti i test
pytest

# Con coverage
pytest --cov=. --cov-report=html

# Test specifico
pytest tests/test_auth.py -v

# Watch mode
pytest-watch
```

### Struttura Test

```python
# tests/test_auth.py
import pytest
from backend import create_app
from backend.extensions import db

@pytest.fixture
def app():
    app = create_app('sqlite:///:memory:')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_register(client):
    response = client.post('/api/v1/auth/register', json={
        'email': 'test@example.com',
        'password': 'Test123!',
        'first_name': 'Test',
        'last_name': 'User',
        'tenant_name': 'Test Company',
        'tenant_slug': 'test'
    })
    assert response.status_code == 201
```

### Mock External Services

```python
from unittest.mock import patch

@patch('requests.post')
def test_webhook(mock_post):
    mock_post.return_value.status_code = 200
    # ... test code
```

---

## Debug

### Modalità Debug

```bash
# Abilita debug dettagliato
export FLASK_DEBUG=1
export LOG_LEVEL=DEBUG
python run.py
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

def my_function():
    logger.debug("Debug info")
    logger.info("Info message")
    logger.warning("Warning")
    logger.error("Error occurred")
```

### Breakpoints

```python
# Usa pdb per debug
import pdb

def my_function():
    result = some_calculations()
    pdb.set_trace()  # Debug breakpoint
    return result
```

---

## Database Migrations

### Creare Migrazione

```bash
flask db migrate -m "Add phone field to users"
```

### Applicare Migrazioni

```bash
# Upgrade
flask db upgrade

# Downgrade
flask db downgrade
```

### Seed Data

```python
# commands/seed_users.py
import click
from flask.cli import with_appcontext

@click.command('seed:users')
@with_appcontext
def seed_users():
    from backend.extensions import db
    from backend.models import User

    users = [
        {'email': 'admin@test.com', 'first_name': 'Admin'},
    ]

    for data in users:
        user = User(**data)
        db.session.add(user)

    db.session.commit()
    click.echo('Users seeded!')
```

---

## Performance

### Query Optimization

```python
# Usa eager loading per evitare N+1
results = MyModel.query.options(
    db.joinedload(MyModel.related_model)
).all()

# Index su campi frequently queried
class MyModel(BaseModel):
    email = db.Column(db.String(255), index=True)
```

### Caching

```python
from flask_caching import Cache

cache = Cache(app)

@cache.cached(timeout=300)
def expensive_query():
    return MyModel.query.all()
```

---

## Deployment

### Produzione con Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5000 "backend:create_app()"
```

### Environment Variables

```bash
# Produzione
export DATABASE_URL=postgresql://user:pass@host:5432/prod
export JWT_SECRET_KEY=<strong-secret>
export FLASK_ENV=production
export FLASK_DEBUG=0
```

### Docker Production

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "backend:create_app()"]
```

---

## Troubleshooting

### Errori Comuni

| Problema | Soluzione |
|----------|-----------|
| `ModuleNotFoundError` | Verifica `PYTHONPATH` o usa virtualenv |
| `Database locked` | Riavvia server o usa PostgreSQL |
| `CORS error` | Aggiungi origine in `CORS()` config |
| `JWT expired` | Refresh token o login nuovamente |

---

## Risorse Utili

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Flask-Smorest](https://flask-smorest.readthedocs.io/)
- [SQLAlchemy](https://docs.sqlalchemy.org/)
- [Marshmallow](https://marshmallow.readthedocs.io/)
- [Flask-JWT-Extended](https://flask-jwt-extended.readthedocs.io/)

---

*Per la cronologia completa delle modifiche di questo documento, consulta la cronologia Git del repository.*
