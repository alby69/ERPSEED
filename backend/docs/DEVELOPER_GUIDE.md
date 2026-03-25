# Developer Guide - ERPSEED Backend

## Setup Locale

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ (opzionale, SQLite per dev)
- Git

### 1. Clone e Installazione

```bash
# Clona il repository
git clone https://github.com/alby69/ERPSEED.git
cd ERPSEED/backend

# Crea virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Installa dipendenze
pip install -r requirements.txt
```

### 2. Configurazione

```bash
# Crea file .env
cat > .env << 'EOF'
DATABASE_URL=sqlite:///data.db
JWT_SECRET_KEY=your-super-secret-key-at-least-32-chars-long
SECRET_KEY=flask-secret-key-change-in-production
FLASK_ENV=development
FLASK_DEBUG=1
EOF
```

### 3. Avvio

```bash
# Modalità sviluppo
python run.py

# Oppure con Flask CLI
flask run --host=0.0.0.0 --port=5000
```

L'API sarà disponibile su `http://localhost:5000`
Swagger UI su `http://localhost:5000/swagger-ui`

---

## Architettura CQRS

### Struttura a 4 Livelli

```
┌──────────────────────────────────────────────────────┐
│  ENDPOINTS LAYER                                     │
│  endpoints/*.py                                      │
│  Riceve richieste HTTP, crea Command/Query objects  │
├──────────────────────────────────────────────────────┤
│  APPLICATION LAYER                                   │
│  application/*/commands/*.py                        │
│  application/*/handlers.py                          │
│  Orchestra la logica di business                    │
├──────────────────────────────────────────────────────┤
│  DOMAIN LAYER                                       │
│  domain/*/models.py (dataclass)                     │
│  domain/*/events.py                                 │
│  Definisce il dominio senza dipendenze              │
├──────────────────────────────────────────────────────┤
│  INFRASTRUCTURE LAYER                               │
│  infrastructure/*/models.py (SQLAlchemy)             │
│  infrastructure/*/repository.py                     │
│  Persiste i dati nel database                       │
└──────────────────────────────────────────────────────┘
```

### Regole Fondamentali

1. **Endpoint** → Crea Command/Query → Chiama Handler
2. **Handler** → Valida business rules → Usa Repository
3. **Repository** → Trasforma Domain ↔ Infrastructure → Database
4. **Domain** → Mai dipendenze da Flask/SQLAlchemy

---

## Creare un Nuovo Modulo CQRS

### 1. Definisci il Domain Model

```python
# domain/mymodule/models.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class MyEntity:
    id: Optional[int] = None
    name: str = ''
    description: Optional[str] = None
    tenant_id: Optional[int] = None

    def validate(self):
        if not self.name:
            raise ValueError("Name is required")
        return True
```

### 2. Definisci Domain Events

```python
# domain/mymodule/events.py
from dataclasses import dataclass
from datetime import datetime

@dataclass
class MyEntityCreatedEvent:
    entity_id: int
    name: str
    tenant_id: int
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
```

### 3. Crea SQLAlchemy Model

```python
# infrastructure/mymodule/models.py
from backend.extensions import db
from backend.core.models.base import BaseModel

class MyEntityModel(BaseModel):
    __tablename__ = 'my_entities'

    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'name', name='uix_tenant_name'),
    )
```

### 4. Crea Repository

```python
# infrastructure/mymodule/repository.py
from backend.extensions import db
from .models import MyEntityModel
from domain.mymodule.models import MyEntity

class MyEntityRepository:
    def create(self, entity: MyEntity) -> MyEntity:
        model = MyEntityModel(
            name=entity.name,
            description=entity.description,
            tenant_id=entity.tenant_id,
        )
        db.session.add(model)
        db.session.flush()
        return model

    def get_by_id(self, entity_id: int) -> MyEntity:
        model = MyEntityModel.query.get(entity_id)
        if model:
            return self.to_domain(model)
        return None

    def get_by_tenant(self, tenant_id: int, skip=0, limit=100):
        models = MyEntityModel.query.filter_by(tenant_id=tenant_id)\
            .offset(skip).limit(limit).all()
        return [self.to_domain(m) for m in models]

    def to_domain(self, model: MyEntityModel) -> MyEntity:
        return MyEntity(
            id=model.id,
            name=model.name,
            description=model.description,
            tenant_id=model.tenant_id,
        )

    def commit(self):
        db.session.commit()
```

### 5. Definisci Commands

```python
# application/mymodule/commands/__init__.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class CreateMyEntityCommand:
    tenant_id: int
    name: str
    description: Optional[str] = None

@dataclass
class UpdateMyEntityCommand:
    id: int
    tenant_id: int
    name: Optional[str] = None
    description: Optional[str] = None

@dataclass
class DeleteMyEntityCommand:
    id: int
    tenant_id: int
```

### 6. Crea Handler

```python
# application/mymodule/handlers.py
from .commands import CreateMyEntityCommand, UpdateMyEntityCommand, DeleteMyEntityCommand
from domain.mymodule.models import MyEntity
from infrastructure.mymodule.repository import MyEntityRepository

class MyEntityCommandHandler:
    def __init__(self):
        self.repository = MyEntityRepository()

    def handle_create(self, command: CreateMyEntityCommand) -> MyEntity:
        # Validazione
        existing = self.repository.get_by_name(command.tenant_id, command.name)
        if existing:
            raise ValueError(f"MyEntity with name {command.name} already exists")

        # Creazione
        entity = MyEntity(
            name=command.name,
            description=command.description,
            tenant_id=command.tenant_id,
        )

        result = self.repository.create(entity)
        self.repository.commit()

        return self.repository.get_by_id(result.id)

    def handle_update(self, command: UpdateMyEntityCommand) -> MyEntity:
        existing = self.repository.get_by_id(command.id)
        if not existing:
            raise ValueError(f"MyEntity {command.id} not found")

        if command.name and command.name != existing.name:
            dup = self.repository.get_by_name(command.tenant_id, command.name)
            if dup and dup.id != command.id:
                raise ValueError(f"MyEntity with name {command.name} already exists")

        # Aggiornamento diretto su DB per semplicità
        model = MyEntityModel.query.get(command.id)
        if command.name:
            model.name = command.name
        if command.description is not None:
            model.description = command.description

        self.repository.commit()
        return self.repository.get_by_id(command.id)

    def handle_delete(self, command: DeleteMyEntityCommand):
        existing = self.repository.get_by_id(command.id)
        if not existing:
            raise ValueError(f"MyEntity {command.id} not found")

        MyEntityModel.query.filter_by(id=command.id).delete()
        self.repository.commit()


class MyEntityQueryHandler:
    def __init__(self):
        self.repository = MyEntityRepository()

    def handle_get_by_id(self, entity_id: int, tenant_id: int):
        entity = self.repository.get_by_id(entity_id)
        if entity and entity.tenant_id != tenant_id:
            return None
        return entity

    def handle_get_all(self, tenant_id: int, skip=0, limit=100):
        return self.repository.get_by_tenant(tenant_id, skip, limit)
```

### 7. Crea Endpoint REST

```python
# endpoints/mymodule.py
from flask import Blueprint, request, jsonify
from flask.views import MethodView
from application.mymodule.handlers import MyEntityCommandHandler, MyEntityQueryHandler
from application.mymodule.commands import CreateMyEntityCommand, UpdateMyEntityCommand, DeleteMyEntityCommand

mymodule_bp = Blueprint('mymodule', __name__, url_prefix='/api/mymodule')

def _get_tenant_id():
    return request.headers.get('X-Tenant-ID', type=int) or 1

def _entity_to_dict(entity):
    if not entity:
        return None
    return {
        'id': entity.id,
        'name': entity.name,
        'description': entity.description,
    }

class MyEntityListView(MethodView):
    def get(self):
        tenant_id = _get_tenant_id()
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)

        handler = MyEntityQueryHandler()
        entities = handler.handle_get_all(tenant_id, skip, limit)
        return jsonify([_entity_to_dict(e) for e in entities])

    def post(self):
        tenant_id = _get_tenant_id()
        data = request.get_json()

        command = CreateMyEntityCommand(
            tenant_id=tenant_id,
            name=data['name'],
            description=data.get('description'),
        )

        handler = MyEntityCommandHandler()
        entity = handler.handle_create(command)
        return jsonify(_entity_to_dict(entity)), 201

class MyEntityDetailView(MethodView):
    def get(self, entity_id):
        tenant_id = _get_tenant_id()
        handler = MyEntityQueryHandler()
        entity = handler.handle_get_by_id(entity_id, tenant_id)
        if not entity:
            return jsonify({'error': 'Not found'}), 404
        return jsonify(_entity_to_dict(entity))

    def put(self, entity_id):
        tenant_id = _get_tenant_id()
        data = request.get_json()

        command = UpdateMyEntityCommand(
            id=entity_id,
            tenant_id=tenant_id,
            name=data.get('name'),
            description=data.get('description'),
        )

        handler = MyEntityCommandHandler()
        entity = handler.handle_update(command)
        return jsonify(_entity_to_dict(entity))

    def delete(self, entity_id):
        tenant_id = _get_tenant_id()
        command = DeleteMyEntityCommand(id=entity_id, tenant_id=tenant_id)
        handler = MyEntityCommandHandler()
        handler.handle_delete(command)
        return '', 204

mymodule_bp.add_url_rule('/', view_func=MyEntityListView.as_view('list'))
mymodule_bp.add_url_rule('/<int:entity_id>', view_func=MyEntityDetailView.as_view('detail'))
```

### 8. Registra il Blueprint

```python
# backend/__init__.py
from .endpoints.mymodule import mymodule_bp

# In create_app():
app.register_blueprint(mymodule_bp)
```

---

## Pattern e Best Practices

### 1. Trasformazione Domain <-> Model

```python
# Sempre nel Repository
class MyRepository:
    def to_domain(self, model) -> DomainModel:
        return DomainModel(
            id=model.id,
            field1=model.field1,
            # Mappa solo campi necessari
        )

    def to_model(self, domain) -> MyModel:
        return MyModel(
            id=domain.id,
            field1=domain.field1,
        )
```

### 2. Validazione nel Handler

```python
class MyHandler:
    def handle_create(self, command):
        # Validazioni di business
        if command.price < 0:
            raise ValueError("Price cannot be negative")

        # Verifica duplicati
        existing = self.repository.get_by_code(command.tenant_id, command.code)
        if existing:
            raise ValueError(f"Entity with code {command.code} already exists")

        # ...
```

### 3. Transazioni nel Handler

```python
class MyHandler:
    def handle_create(self, command):
        # Operazioni multiple
        entity = self.repository.create(domain_obj)
        self.repository.flush()  # Ottieni ID

        # Creazione entity correlate
        for item in command.items:
            self.item_repo.create(entity.id, item)

        # Commit atomico
        self.repository.commit()

        return entity
```

### 4. Multi-Tenancy

```python
# Sempre filtrare per tenant_id
class MyRepository:
    def get_by_tenant(self, tenant_id, skip=0, limit=100):
        return MyModel.query\
            .filter_by(tenant_id=tenant_id)\
            .offset(skip).limit(limit)\
            .all()

    def check_ownership(self, entity_id, tenant_id):
        return MyModel.query\
            .filter_by(id=entity_id, tenant_id=tenant_id)\
            .first() is not None
```

---

## Testing

### Setup Test con CQRS

```python
# tests/test_mymodule_cqrs.py
import pytest
import os
os.environ.setdefault('JWT_SECRET_KEY', 'test-secret-key-for-testing-purposes-only-12345')

from backend import create_app
from backend.extensions import db
from infrastructure.mymodule.models import MyEntityModel

@pytest.fixture
def app():
    app = create_app(db_url="sqlite:///:memory:")
    app.config["TESTING"] = True
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

class TestMyEntityCQRS:
    def test_create_entity(self, app):
        with app.app_context():
            from application.mymodule.handlers import MyEntityCommandHandler
            from application.mymodule.commands import CreateMyEntityCommand

            handler = MyEntityCommandHandler()
            command = CreateMyEntityCommand(
                tenant_id=1,
                name="Test Entity",
                description="A test entity"
            )

            entity = handler.handle_create(command)

            assert entity.id is not None
            assert entity.name == "Test Entity"

    def test_duplicate_validation(self, app):
        with app.app_context():
            from application.mymodule.handlers import MyEntityCommandHandler
            from application.mymodule.commands import CreateMyEntityCommand

            handler = MyEntityCommandHandler()
            command = CreateMyEntityCommand(
                tenant_id=1,
                name="Duplicate"
            )

            handler.handle_create(command)

            with pytest.raises(ValueError, match="already exists"):
                handler.handle_create(command)
```

### Esecuzione Test

```bash
# Tutti i test
pytest

# Test specifico modulo
pytest tests/test_mymodule_cqrs.py -v

# Con coverage
pytest --cov=backend --cov-report=html
```

---

## Debug

### Modalità Debug

```bash
export FLASK_DEBUG=1
export LOG_LEVEL=DEBUG
python run.py
```

### Logging

```python
import logging
logger = logging.getLogger(__name__)

class MyHandler:
    def handle_create(self, command):
        logger.debug(f"Creating entity: {command.name}")
        # ...
        logger.info(f"Entity created: {entity.id}")
```

---

## Database Migrations

### Creare Migrazione

```bash
flask db migrate -m "Add new field to my_entities"
```

### Seed Data

```python
# cli/seed_mymodule.py
import click
from flask.cli import with_appcontext

@click.command('seed:mymodule')
@with_appcontext
def seed_mymodule():
    from backend.extensions import db
    from infrastructure.mymodule.models import MyEntityModel

    entities = [
        {'name': 'Entity 1', 'tenant_id': 1},
        {'name': 'Entity 2', 'tenant_id': 1},
    ]

    for data in entities:
        entity = MyEntityModel(**data)
        db.session.add(entity)

    db.session.commit()
    click.echo('Seed complete!')
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
export JWT_SECRET_KEY=<strong-secret-at-least-32-chars>
export FLASK_ENV=production
```

---

## Troubleshooting

### Errori Comuni

| Problema | Soluzione |
|----------|-----------|
| `ModuleNotFoundError` | Verifica `PYTHONPATH` o usa virtualenv |
| `Database locked` | Riavvia server o usa PostgreSQL |
| `CORS error` | Aggiungi origine in `CORS()` config |
| `JWT expired` | Refresh token o login nuevamente |

### Reset Database

```bash
rm data.db
flask db upgrade
flask seed
```

---

## Risorse Utili

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Flask-Smorest](https://flask-smorest.readthedocs.io/)
- [SQLAlchemy](https://docs.sqlalchemy.org/)
- [Marshmallow](https://marshmallow.readthedocs.io/)
- [Flask-JWT-Extended](https://flask-jwt-extended.readthedocs.io/)
- [CQRS Pattern](https://martinfowler.com/bliki/CQRS.html)

---

*Ultimo aggiornamento: 2026-03-19*
