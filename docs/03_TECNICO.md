# FlaskERP - Tecnico

## Stack Tecnologico

| Componente | Tecnologia | Versione |
|------------|------------|----------|
| Framework | Flask | 2.x / 3.x |
| API | Flask-smorest | 0.40+ |
| ORM | SQLAlchemy + Flask-SQLAlchemy | 2.x |
| Database | PostgreSQL | 14+ |
| Migration | Flask-Migrate / Alembic | - |
| Serialization | Flask-Marshmallow | - |
| Auth | Flask-JWT-Extended | 4.x |
| Cache | Flask-Caching + Redis | - |
| Task Queue | Celery + Redis | 5.x |
| Frontend | React + Ant Design | 18.x |

---

## Multi-Tenant

### BaseModel

```python
class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### TenantContext

```python
class TenantContext:
    """Gestisce il contesto tenant per richiesta"""
    
    @staticmethod
    def get_current_tenant_id() -> int:
        # Estrae tenant_id dal JWT token
        return get_jwt_tenant_id()
    
    @staticmethod
    def set_tenant_id(tenant_id: int):
        # Imposta tenant_id nel contesto thread-local
        _thread_local.tenant_id = tenant_id
```

### TenantMiddleware

```python
class TenantMiddleware:
    """Middleware che estrae tenant da ogni richiesta"""
    
    def process_request(self, req):
        tenant_id = self._extract_tenant(req)
        TenantContext.set_tenant_id(tenant_id)
        req.tenant_id = tenant_id
```

---

## Modelli Core

### Tenant

```python
class Tenant(BaseModel):
    __tablename__ = 'tenants'
    
    nome = db.Column(db.String(200), nullable=False)
    subdomain = db.Column(db.String(50), unique=True)
    is_active = db.Column(db.Boolean, default=True)
    piano = db.Column(db.String(50), default='starter')
    
    utenti = db.relationship('User', back_populates='tenant')
```

### User

```python
class User(BaseModel):
    __tablename__ = 'users'
    
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(256))
    is_active = db.Column(db.Boolean, default=True)
    role = db.Column(db.String(20), default='user')
    
    tenant = db.relationship('Tenant', back_populates='utenti')
```

### AuditLog

```python
class AuditLog(BaseModel):
    __tablename__ = 'audit_logs'
    
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(50))  # create, update, delete
    entity_type = db.Column(db.String(50))
    entity_id = db.Column(db.Integer)
    changes = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
```

---

## Sistema Plugin

### BasePlugin

```python
class BasePlugin:
    name: str
    version: str
    description: str
    dependencies: List[str]
    
    def register(self, app, api, db): ...
    def install(self): ...
    def uninstall(self): ...
    def enable_for_tenant(self, tenant_id): ...
    def disable_for_tenant(self, tenant_id): ...
```

### PluginRegistry

```python
class PluginRegistry:
    @classmethod
    def register(cls, plugin_class): ...
    @classmethod
    def enable(cls, name, app, db, api): ...
    @classmethod
    def disable(cls, name): ...
    @classmethod
    def get(cls, name): ...
    @classmethod
    def list_enabled(cls): ...
```

---

## Sistema Moduli v2.0

### ModuleDefinition

```python
class ModuleDefinition(BaseModel):
    __tablename__ = 'module_definitions'
    
    codice = db.Column(db.String(50), unique=True)  # sales, inventory
    nome = db.Column(db.String(100))
    descrizione = db.Column(db.Text)
    versione = db.Column(db.String(20))
    categoria = db.Column(db.String(20))  # core, builtin, premium
    
    is_active = db.Column(db.Boolean, default=True)
    config = db.Column(db.JSON)
```

### TenantModule

```python
class TenantModule(BaseModel):
    __tablename__ = 'tenant_modules'
    
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('module_definitions.id'))
    is_enabled = db.Column(db.Boolean, default=False)
    config = db.Column(db.JSON)  # Configurazione specifica tenant
```

---

## Dynamic API

### Dynamic API Service

Genera automaticamente API REST da modelli definiti nel Builder:

```
Endpoint generati:
├── GET    /api/{model}           # Lista
├── GET    /api/{model}/{id}      # Dettaglio
├── POST   /api/{model}           # Crea
├── PUT    /api/{model}/{id}      # Aggiorna
├── DELETE /api/{model}/{id}      # Elimina
└── GET    /api/{model}/export   # Esporta
```

### SysModel

```python
class SysModel(BaseModel):
    __tablename__ = 'sys_models'
    
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    nome = db.Column(db.String(100))
    tabella = db.Column(db.String(100))
    descrizione = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    
    campi = db.relationship('SysField', back_populates='modello')
```

### SysField

```python
class SysField(BaseModel):
    __tablename__ = 'sys_fields'
    
    modello_id = db.Column(db.Integer, db.ForeignKey('sys_models.id'))
    nome = db.Column(db.String(100))
    tipo = db.Column(db.String(20))  # string, integer, date, relation, etc.
    label = db.Column(db.String(100))
    required = db.Column(db.Boolean, default=False)
    default_value = db.Column(db.String(255))
    opzioni = db.Column(db.JSON)  # Per select, relation
```

---

## Autenticazione JWT

```python
# Configurazione
JWT_ACCESS_TOKEN_EXPIRES = 15 minuti
JWT_REFRESH_TOKEN_EXPIRES = 30 giorni

# Endpoints
POST /api/v1/auth/login     # Login
POST /api/v1/auth/register  # Registrazione
POST /api/v1/auth/refresh   # Refresh token
POST /api/v1/auth/logout    # Logout
```

---

## Dipendenze Python

```
# Core
flask>=3.0.0
flask-sqlalchemy>=3.1.0
flask-migrate>=4.0.0
flask-smorest>=0.44.0
flask-marshmallow>=1.2.0
flask-jwt-extended>=4.6.0
flask-caching>=2.1.0

# Database
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
alembic>=1.13.0

# Tasks
celery>=5.3.0
redis>=5.0.0

# Utils
marshmallow-sqlalchemy>=0.29.0
python-dateutil>=2.8.0
gunicorn>=21.0.0
```

---

*Documento aggiornato: Febbraio 2026*
