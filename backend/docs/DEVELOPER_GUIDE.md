# Developer Guide - ERPSEED Backend

## Setup Locale

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ (opzionale, SQLite per dev)
- Git
- Docker (opzionale)

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

### 4. Database

```bash
# Crea tabelle
flask db init
flask db migrate
flask db upgrade

# Seed dati iniziali (se disponibile)
flask seed
```

---

## Setup con Docker

### Avvio rapido

```bash
# Dalla root del repository (main branch)
docker compose up -d

# Oppure build manuale
cd backend
docker build -t erpseed-backend .
docker run -p 5002:5000 erpseed-backend
```

### Accedere ai container

```bash
# Backend shell
docker exec -it erpseed_backend sh

# Database shell
docker exec -it erpseed_db psql -U postgres -d flarkerp
```

---

## Struttura del Codice

### File Principali

```
backend/
├── __init__.py      # App factory (create_app)
├── run.py           # Entry point
├── extensions.py    # Flask extensions
├── models.py        # Modelli principali
└── ...
```

### Creare un Nuovo Modulo

#### 1. Definisci il Modello

```python
# myapp/models.py
from backend.extensions import db
from backend.core.models.base import BaseModel

class MyModel(BaseModel):
    __tablename__ = 'my_models'

    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True)

    # Relazioni
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref='my_models')
```

#### 2. Crea lo Schema Marshmallow

```python
# myapp/schemas.py
from marshmallow import Schema, fields

class MyModelSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()
    active = fields.Bool()
    created_at = fields.DateTime(dump_only=True)
```

#### 3. Crea l'API Blueprint

```python
# myapp/routes.py
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity

from .models import MyModel
from .schemas import MyModelSchema
from backend.extensions import db

blp = Blueprint('myapp', __name__, url_prefix='/myapp')

@blp.route('/')
class MyModelList(MethodView):
    @blp.arguments(MyModelSchema)
    @blp.response(201, MyModelSchema)
    @jwt_required()
    def post(self, data):
        model = MyModel(**data)
        db.session.add(model)
        db.session.commit()
        return model

    @blp.response(200, MyModelSchema(many=True))
    @jwt_required()
    def get(self):
        return MyModel.query.all()
```

#### 4. Registra il Blueprint

```python
# backend/__init__.py
from .myapp.routes import blp as myapp_blp

# Nella funzione create_app():
api.register_blueprint(myapp_blp)
```

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

### Flask Debug Toolbar

```python
# requirements.txt
flask-debugtoolbar

# app.py
from flask_debugtoolbar import DebugToolbarExtension
toolbar = DebugToolbarExtension(app)
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
| `JWT expired` | Refresh token o login novamente |

### Reset Database

```bash
# Reset completo (PERICOLOSO in produzione)
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

---

*Ultimo aggiornamento: 2026-03-18*
