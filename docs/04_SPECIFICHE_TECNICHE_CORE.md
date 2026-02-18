# ERPaaS - Specifiche Tecniche Modulo Core

## Documento #04 - Implementazione Multi-Tenant e Servizi Base

---

## 1. Panoramica Architetturale

### 1.1 Obiettivi del Modulo Core

Il modulo Core fornisce le fondamenta per l'intera piattaforma FlaskERP:

| Obiettivo | Descrizione |
|-----------|-------------|
| **Multi-Tenant** | Isolamento dati tra clienti/tenant |
| **Autenticazione** | JWT con supporto multi-tenant |
| **Autorizzazione** | Ruoli e permessi granulari |
| **Audit** | Tracciamento operazioni |
| **API Base** | Endpoints CRUD comuni |

### 1.2 Schema Multi-Tenant

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TENANT ISOLATION MODEL                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌──────────┐     ┌──────────┐     ┌──────────┐                 │
│   │ Tenant 1 │     │ Tenant 2 │     │ Tenant N │                 │
│   │  (Azienda│     │  (Azienda│     │  (Azienda│                 │
│   │   Alpha)  │     │   Beta)  │     │  Gamma)  │                 │
│   └─────┬─────┘     └─────┬─────┘     └─────┬─────┘                 │
│         │                  │                  │                       │
│    ┌────┴────┐       ┌────┴────┐       ┌────┴────┐                 │
│    │ Users   │       │ Users   │       │ Users   │                 │
│    │ (admin) │       │ (mario) │       │ (luca)  │                 │
│    └─────────┘       └─────────┘       └─────────┘                 │
│                                                                     │
│    ┌──────────────────────────────────────────────────────────┐     │
│    │               SHARED DATABASE (PostgreSQL)               │     │
│    │  ┌────────────┐  ┌────────────┐  ┌────────────┐        │     │
│    │  │ tenants    │  │ users      │  │ parties    │        │     │
│    │  │ (id=1)     │  │ (tenant_id)│  │ (tenant_id)│        │     │
│    │  │            │  │            │  │            │        │     │
│    │  └────────────┘  └────────────┘  └────────────┘        │     │
│    └──────────────────────────────────────────────────────────┘     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Modelli Database

### 2.1 BaseModel Aggiornato

File: `backend/core/models/base.py`

```python
"""
BaseModel con supporto multi-tenant.
Tutti i modelli del sistema erediteranno da questa classe.
"""
from datetime import datetime
from backend.extensions import db
from flask import g


class TenantMixin:
    """Mixin per aggiungere supporto multi-tenant."""
    
    tenant_id = db.Column(
        db.Integer, 
        db.ForeignKey('tenants.id'), 
        nullable=False,
        index=True
    )
    
    @declared_attr
    def tenant(cls):
        return db.relationship('Tenant', backref=cls.__tablename__)


class BaseModel(db.Model):
    """
    Classe base per tutti i modelli del sistema.
    Include:
    - ID univoco
    - Timestamp creazione/modifica
    - Supporto multi-tenant
    """
    __abstract__ = True
    
    # Campi comuni a tutti i modelli
    id = db.Column(db.Integer, primary_key=True)
    
    # Timestamp automatici
    created_at = db.Column(
        db.DateTime, 
        default=datetime.utcnow,
        nullable=False
    )
    updated_at = db.Column(
        db.DateTime, 
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # Soft delete
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)
    
    @property
    def is_deleted(self):
        return self.deleted_at is not None
    
    def soft_delete(self):
        """Soft delete - marca come eliminato senza rimuovere."""
        self.deleted_at = datetime.utcnow()
        db.session.add(self)
    
    def restore(self):
        """Ripristina record soft-deleted."""
        self.deleted_at = None
        db.session.add(self)
    
    def to_dict(self, exclude=None):
        """Converti modello in dizionario."""
        exclude = exclude or []
        result = {}
        for col in self.__table__.columns:
            if col.name in exclude:
                continue
            value = getattr(self, col.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[col.name] = value
        return result


class TimestampMixin:
    """Mixin per timestamp opzionali."""
    
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    @declared_attr
    def created_by(cls):
        return db.relationship('User', foreign_keys=[cls.created_by_id])
    
    @declared_attr
    def updated_by(cls):
        return db.relationship('User', foreign_keys=[cls.updated_by_id])
```

### 2.2 Modello Tenant

File: `backend/core/models/tenant.py`

```python
"""
Modello Tenant - Rappresenta un'azienda/cliente.
"""
from datetime import datetime
from backend.extensions import db
from .base import BaseModel


class Tenant(BaseModel):
    """
    Tenant - Entità aziendale che utilizza il sistema.
    Ogni tenant ha:
    - Utenti dedicati
    - Dati isolati
    - Configurazione personalizzata
    """
    __tablename__ = 'tenants'
    
    # Identificazione
    name = db.Column(db.String(150), nullable=False, index=True)
    slug = db.Column(db.String(80), unique=True, nullable=False, index=True)
    
    # Contatti
    email = db.Column(db.String(120))
    phone = db.Column(db.String(50))
    website = db.Column(db.String(255))
    
    # Indirizzo
    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(2), default='IT')
    
    # Configurazione
    timezone = db.Column(db.String(50), default='Europe/Rome')
    locale = db.Column(db.String(5), default='it_IT')
    currency = db.Column(db.String(3), default='EUR')
    
    # Piano/Abbonamento
    plan = db.Column(db.String(50), default='starter')
    plan_expires_at = db.Column(db.DateTime)
    max_users = db.Column(db.Integer, default=3)
    max_storage_mb = db.Column(db.Integer, default=1024)
    
    # Stato
    is_active = db.Column(db.Boolean, default=True)
    
    # Branding
    logo = db.Column(db.String(255))
    primary_color = db.Column(db.String(7), default='#3498db')
    
    # Relazioni
    users = db.relationship('User', back_populates='tenant', lazy='dynamic')
    
    def __repr__(self):
        return f'<Tenant {self.slug}>'
    
    @property
    def is_plan_expired(self):
        if self.plan_expires_at is None:
            return False
        return datetime.utcnow() > self.plan_expires_at
    
    def can_add_user(self):
        """Verifica se si possono aggiungere altri utenti."""
        return self.users.count() < self.max_users
    
    def can_use_storage(self, bytes_used):
        """Verifica se c'è spazio storage disponibile."""
        max_bytes = self.max_storage_mb * 1024 * 1024
        return bytes_used < max_bytes
```

### 2.3 Modello User Aggiornato

File: `backend/core/models/user.py`

```python
"""
Modello User con supporto multi-tenant.
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from backend.extensions import db
from .base import BaseModel


class User(BaseModel):
    """
    Utente del sistema.
    Ogni utente appartiene a un tenant.
    """
    __tablename__ = 'users'
    
    # Identificazione tenant
    tenant_id = db.Column(
        db.Integer, 
        db.ForeignKey('tenants.id'), 
        nullable=False,
        index=True
    )
    
    # Credenziali
    email = db.Column(db.String(120), nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Profilo
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    avatar = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    
    # Ruolo nel tenant
    role = db.Column(
        db.String(50), 
        nullable=False, 
        default='user'
    )
    
    # Stato
    is_active = db.Column(db.Boolean, default=True)
    is_primary = db.Column(db.Boolean, default=False, comment="Owner/admin principale")
    force_password_change = db.Column(db.Boolean, default=False)
    
    # Ultimo accesso
    last_login_at = db.Column(db.DateTime)
    login_count = db.Column(db.Integer, default=0)
    
    # Token reset password
    password_reset_token = db.Column(db.String(255))
    password_reset_expires = db.Column(db.DateTime)
    
    # Relazioni
    tenant = db.relationship('Tenant', back_populates='users')
    
    # Indici per performance
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'email', name='uix_tenant_email'),
        db.Index('ix_user_email_lower', db.func.lower(email)),
    )
    
    def __repr__(self):
        return f'<User {self.email}@{self.tenant.slug}>'
    
    @property
    def full_name(self):
        return f"{self.first_name or ''} {self.last_name or ''}".strip() or self.email
    
    def set_password(self, password):
        """Imposta password con hash."""
        self.password_hash = generate_password_hash(password)
        self.force_password_change = False
        self.password_reset_token = None
        self.password_reset_expires = None
    
    def check_password(self, password):
        """Verifica password."""
        return check_password_hash(self.password_hash, password)
    
    def record_login(self):
        """Registra accesso utente."""
        self.last_login_at = datetime.utcnow()
        self.login_count += 1
    
    def to_dict(self, include_email=True):
        """Serializza utente."""
        data = super().to_dict()
        if not include_email:
            data.pop('email', None)
        data['full_name'] = self.full_name
        data.pop('password_hash', None)
        data.pop('password_reset_token', None)
        return data


class UserRole(BaseModel):
    """
    Ruoli personalizzati per tenant.
    """
    __tablename__ = 'user_roles'
    
    tenant_id = db.Column(
        db.Integer, 
        db.ForeignKey('tenants.id'), 
        nullable=False,
        index=True
    )
    
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255))
    permissions = db.Column(db.Text, comment="JSON array of permissions")
    is_default = db.Column(db.Boolean, default=False)
    
    tenant = db.relationship('Tenant')
    users = db.relationship('User', back_populates='custom_role')
    
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'name', name='uix_tenant_role_name'),
    )


# Aggiungi campo ruolo personalizzato al modello User
User.custom_role_id = db.Column(db.Integer, db.ForeignKey('user_roles.id'))
User.custom_role = db.relationship('UserRole', back_populates='users')
```

### 2.4 Modello Audit Log

File: `backend/core/models/audit.py`

```python
"""
Modello per tracciamento operazioni (Audit Log).
"""
from datetime import datetime
from backend.extensions import db
from .base import BaseModel


class AuditLog(BaseModel):
    """
    Log di tutte le operazioni nel sistema.
    Fondamentale per:
    - Sicurezza
    - Compliance (GDPR)
    - Debug
    - Analytics
    """
    __tablename__ = 'audit_logs'
    
    tenant_id = db.Column(
        db.Integer, 
        db.ForeignKey('tenants.id'), 
        nullable=False,
        index=True
    )
    
    # Chi ha eseguito l'azione
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Dettagli azione
    action = db.Column(
        db.String(50), 
        nullable=False,
        index=True
    )
    resource_type = db.Column(db.String(50), nullable=False, index=True)
    resource_id = db.Column(db.Integer, nullable=True)
    
    # Dati modificati
    changes = db.Column(db.Text, comment="JSON con le modifiche")
    old_values = db.Column(db.Text)
    new_values = db.Column(db.Text)
    
    # Contesto
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    endpoint = db.Column(db.String(255))
    method = db.Column(db.String(10))
    
    # Risultato
    status = db.Column(db.String(20), default='success')  # success, failure
    error_message = db.Column(db.Text)
    
    # Relazioni
    tenant = db.relationship('Tenant')
    user = db.relationship('User')
    
    # Indici
    __table_args__ = (
        db.Index('ix_audit_tenant_created', 'tenant_id', 'created_at'),
        db.Index('ix_audit_user_created', 'user_id', 'created_at'),
    )
    
    # Azioni predefinite
    ACTION_CREATE = 'create'
    ACTION_UPDATE = 'update'
    ACTION_DELETE = 'delete'
    ACTION_LOGIN = 'login'
    ACTION_LOGOUT = 'logout'
    ACTION_PASSWORD_CHANGE = 'password_change'
    ACTION_EXPORT = 'export'
    ACTION_IMPORT = 'import'
    
    @staticmethod
    def log_create(user_id, tenant_id, resource_type, resource_id, new_values=None):
        """Log creazione record."""
        log = AuditLog(
            user_id=user_id,
            tenant_id=tenant_id,
            action=AuditLog.ACTION_CREATE,
            resource_type=resource_type,
            resource_id=resource_id,
            new_values=new_values,
            status='success'
        )
        db.session.add(log)
        return log
    
    @staticmethod
    def log_update(user_id, tenant_id, resource_type, resource_id, old_values, new_values):
        """Log aggiornamento record."""
        import json
        log = AuditLog(
            user_id=user_id,
            tenant_id=tenant_id,
            action=AuditLog.ACTION_UPDATE,
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=json.dumps(old_values),
            new_values=json.dumps(new_values),
            changes=json.dumps(AuditLog._compute_changes(old_values, new_values)),
            status='success'
        )
        db.session.add(log)
        return log
    
    @staticmethod
    def _compute_changes(old, new):
        """Calcola differenze tra vecchi e nuovi valori."""
        import json
        changes = {}
        old_dict = json.loads(old) if isinstance(old, str) else old or {}
        new_dict = json.loads(new) if isinstance(new, str) else new or {}
        
        for key in set(list(old_dict.keys()) + list(new_dict.keys())):
            old_val = old_dict.get(key)
            new_val = new_dict.get(key)
            if old_val != new_val:
                changes[key] = {'old': old_val, 'new': new_val}
        return changes
```

---

## 3. Gestione Tenant Context

### 3.1 Tenant Context Manager

File: `backend/core/services/tenant_context.py`

```python
"""
Gestione del contesto tenant per ogni richiesta.
"""
from flask import g, request
from functools import wraps
from backend.core.models.tenant import Tenant


class TenantContext:
    """
    Gestisce il contesto del tenant per la richiesta corrente.
    Utilizza Flask g per storage thread-safe.
    """
    
    TENANT_KEY = 'current_tenant'
    USER_KEY = 'current_user'
    
    @classmethod
    def get_tenant(cls):
        """Ottieni tenant corrente."""
        return getattr(g, cls.TENANT_KEY, None)
    
    @classmethod
    def set_tenant(cls, tenant):
        """Imposta tenant corrente."""
        g[cls.TENANT_KEY] = tenant
    
    @classmethod
    def get_user(cls):
        """Ottieni utente corrente."""
        return getattr(g, cls.USER_KEY, None)
    
    @classmethod
    def set_user(cls, user):
        """Imposta utente corrente."""
        g[cls.USER_KEY] = user
    
    @classmethod
    def get_tenant_id(cls):
        """Ottieni ID tenant corrente."""
        tenant = cls.get_tenant()
        return tenant.id if tenant else None
    
    @classmethod
    def clear(cls):
        """Pulisci contesto."""
        g.pop(cls.TENANT_KEY, None)
        g.pop(cls.USER_KEY, None)


def tenant_required(f):
    """
    Decoratore che richiede un tenant valido.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if not TenantContext.get_tenant():
            from flask import abort
            abort(403, description="Tenant not found")
        return f(*args, **kwargs)
    return decorated


def get_current_tenant():
    """
    Helper per ottenere tenant corrente.
    """
    return TenantContext.get_tenant()


def get_current_user():
    """
    Helper per ottenere utente corrente.
    """
    return TenantContext.get_user()


def get_current_tenant_id():
    """
    Helper per ottenere ID tenant corrente.
    """
    return TenantContext.get_tenant_id()
```

### 3.2 Tenant Middleware

File: `backend/core/middleware/tenant_middleware.py`

```python
"""
Middleware per impostare il contesto tenant ad ogni richiesta.
"""
from flask import request, g
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from backend.core.models import Tenant, User
from backend.core.services.tenant_context import TenantContext
from backend.extensions import db


class TenantMiddleware:
    """
    Middleware che:
    1. Estrae il tenant dalla richiesta
    2. Imposta il contesto tenant
    3. Filtira automaticamente le query
    """
    
    @staticmethod
    def init_app(app):
        """Registra il middleware nell'app Flask."""
        app.before_request(TenantMiddleware._before_request)
        app.after_request(TenantMiddleware._after_request)
    
    @staticmethod
    def _before_request():
        """Esegui prima di ogni richiesta."""
        # Pulisci contesto precedente
        TenantContext.clear()
        
        # Estrai tenant
        tenant = TenantMiddleware._extract_tenant()
        if tenant:
            TenantContext.set_tenant(tenant)
            
            # Estrai utente se autenticato
            user = TenantMiddleware._extract_user()
            if user:
                TenantContext.set_user(user)
    
    @staticmethod
    def _extract_tenant():
        """
        Estrai tenant da diverse fonti:
        1. Header X-Tenant-ID
        2. Subdomain
        3. JWT token
        """
        # Metodo 1: Header esplicito (per API)
        tenant_id = request.headers.get('X-Tenant-ID')
        if tenant_id:
            try:
                tenant_id = int(tenant_id)
                return Tenant.query.filter_by(id=tenant_id, is_active=True).first()
            except ValueError:
                pass
        
        # Metodo 2: Subdomain (per UI)
        host = request.host
        if '.' in host and not host.startswith('localhost'):
            subdomain = host.split('.')[0]
            if subdomain not in ('www', 'api', 'admin'):
                return Tenant.query.filter_by(slug=subdomain, is_active=True).first()
        
        # Metodo 3: Da JWT se l'utente è loggato
        try:
            if verify_jwt_in_request(optional=True):
                user_id = get_jwt_identity()
                if user_id:
                    user = User.query.get(user_id)
                    if user:
                        return user.tenant
        except Exception:
            pass
        
        return None
    
    @staticmethod
    def _extract_user():
        """Estrai utente corrente dal JWT."""
        try:
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
            if user_id:
                return User.query.get(int(user_id))
        except Exception:
            pass
        return None
    
    @staticmethod
    def _after_request(response):
        """Esegui dopo ogni richiesta."""
        # Aggiungi header con info tenant (debug)
        tenant = TenantContext.get_tenant()
        if tenant:
            response.headers['X-Tenant-ID'] = str(tenant.id)
            response.headers['X-Tenant-Slug'] = tenant.slug
        return response
```

---

## 4. Autenticazione e Autorizzazione

### 4.1 Auth Service

File: `backend/core/services/auth_service.py`

```python
"""
Servizio di autenticazione con supporto multi-tenant.
"""
from datetime import datetime, timedelta
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token,
    get_jwt_identity,
    get_jwt
)
from backend.extensions import db
from backend.core.models.user import User
from backend.core.models.tenant import Tenant
from backend.core.models.audit import AuditLog
import secrets


class AuthService:
    """Servizio per gestione autenticazione."""
    
    @staticmethod
    def login(email, password, tenant_id=None):
        """
        Effettua login utente.
        
        Args:
            email: Email utente
            password: Password in chiaro
            tenant_id: ID tenant (opzionale)
            
        Returns:
            dict: {access_token, refresh_token, user}
            
        Raises:
            ValueError: Credenziali non valide
        """
        email = email.lower().strip()
        
        # Costruisci query
        query = User.query.filter(db.func.lower(User.email) == email)
        
        # Se specificato, verifica tenant
        if tenant_id:
            query = query.filter_by(tenant_id=tenant_id)
        
        user = query.first()
        
        # Verifica credenziali
        if not user or not user.check_password(password):
            raise ValueError("Email o password non validi")
        
        if not user.is_active:
            raise ValueError("Account disattivato")
        
        # Verifica tenant attivo
        if not user.tenant.is_active:
            raise ValueError("Tenant disattivato")
        
        # Registra accesso
        user.record_login()
        db.session.commit()
        
        # Log azione
        AuditLog.log_create(
            user_id=user.id,
            tenant_id=user.tenant_id,
            resource_type='user',
            resource_id=user.id,
            new_values={'action': 'login'}
        )
        
        # Genera token
        access_token = AuthService._create_access_token(user)
        refresh_token = create_refresh_token(identity=str(user.id))
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }
    
    @staticmethod
    def _create_access_token(user):
        """Crea access token con claims personalizzati."""
        additional_claims = {
            'role': user.role,
            'tenant_id': user.tenant_id,
            'email': user.email,
            'is_primary': user.is_primary
        }
        return create_access_token(
            identity=str(user.id),
            additional_claims=additional_claims
        )
    
    @staticmethod
    def refresh_token():
        """
        Refresh dello access token.
        """
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.is_active:
            raise ValueError("Utente non valido")
        
        return {
            'access_token': AuthService._create_access_token(user)
        }
    
    @staticmethod
    def register(email, password, first_name, last_name, tenant_name, tenant_slug):
        """
        Registra nuovo tenant + utente admin.
        
        Args:
            email: Email admin
            password: Password
            first_name: Nome admin
            last_name: Cognome admin
            tenant_name: Nome azienda
            tenant_slug: Slug per URL
            
        Returns:
            dict: {access_token, refresh_token, user, tenant}
        """
        # Valida slug
        if Tenant.query.filter_by(slug=tenant_slug).first():
            raise ValueError("Slug già in uso")
        
        # Crea tenant
        tenant = Tenant(
            name=tenant_name,
            slug=tenant_slug,
            is_primary=True
        )
        db.session.add(tenant)
        db.session.flush()  # Per ottenere ID
        
        # Crea utente admin
        user = User(
            tenant_id=tenant.id,
            email=email.lower(),
            first_name=first_name,
            last_name=last_name,
            role='admin',
            is_primary=True
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        # Genera token
        access_token = AuthService._create_access_token(user)
        refresh_token = create_refresh_token(identity=str(user.id))
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict(),
            'tenant': tenant.to_dict()
        }
    
    @staticmethod
    def request_password_reset(email):
        """
        Richiede reset password.
        
        Args:
            email: Email utente
            
        Returns:
            dict: {reset_token} (da inviare via email)
        """
        user = User.query.filter_by(email=email.lower()).first()
        if not user:
            return {'success': True}  # Non rivelare se email esiste
        
        # Genera token
        reset_token = secrets.token_urlsafe(32)
        user.password_reset_token = reset_token
        user.password_reset_expires = datetime.utcnow() + timedelta(hours=24)
        
        db.session.commit()
        
        # TODO: Invia email con reset_token
        
        return {
            'reset_token': reset_token,
            'expires': user.password_reset_expires
        }
    
    @staticmethod
    def reset_password(token, new_password):
        """
        Reset password con token.
        """
        user = User.query.filter_by(password_reset_token=token).first()
        
        if not user:
            raise ValueError("Token non valido")
        
        if user.password_reset_expires < datetime.utcnow():
            raise ValueError("Token scaduto")
        
        user.set_password(new_password)
        db.session.commit()
        
        return {'success': True}
```

### 4.2 Permission System

File: `backend/core/services/permission_service.py`

```python
"""
Sistema di permessi e autorizzazione.
"""
from functools import wraps
from flask import abort
from flask_jwt_extended import get_jwt


class Permission:
    """Costanti permessi."""
    
    # Utenti
    MANAGE_USERS = 'manage_users'
    VIEW_USERS = 'view_users'
    
    # Tenant
    MANAGE_TENANT = 'manage_tenant'
    
    # Dati
    VIEW_ALL = 'view_all'
    EDIT_ALL = 'edit_all'
    DELETE_ALL = 'delete_all'
    
    # Moduli
    VIEW_ACCOUNTING = 'view_accounting'
    MANAGE_ACCOUNTING = 'manage_accounting'
    VIEW_INVENTORY = 'view_inventory'
    MANAGE_INVENTORY = 'manage_inventory'
    VIEW_SALES = 'view_sales'
    MANAGE_SALES = 'manage_sales'


# Ruoli predefiniti con permessi
DEFAULT_ROLES = {
    'admin': [
        Permission.MANAGE_USERS,
        Permission.VIEW_USERS,
        Permission.MANAGE_TENANT,
        Permission.VIEW_ALL,
        Permission.EDIT_ALL,
        Permission.DELETE_ALL,
    ],
    'manager': [
        Permission.VIEW_ALL,
        Permission.EDIT_ALL,
    ],
    'user': [],
    'viewer': [
        Permission.VIEW_ALL,
    ]
}


class PermissionService:
    """Servizio per gestione permessi."""
    
    @staticmethod
    def has_permission(user, permission):
        """
        Verifica se utente ha un permesso.
        
        Args:
            user: Istanza User
            permission: String permesso
            
        Returns:
            bool
        """
        # Admin ha tutti i permessi
        if user.role == 'admin':
            return True
        
        # Admin tenant ha tutti i permessi
        if user.is_primary:
            return True
        
        # Verifica ruolo personalizzato
        if user.custom_role:
            import json
            permissions = json.loads(user.custom_role.permissions or '[]')
            return permission in permissions
        
        # Verifica ruolo default
        role_permissions = DEFAULT_ROLES.get(user.role, [])
        return permission in role_permissions
    
    @staticmethod
    def require_permission(permission):
        """
        Decoratore per richiedere permesso.
        """
        def decorator(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                from flask_jwt_extended import get_jwt_identity
                from backend.core.models.user import User
                
                user_id = get_jwt_identity()
                user = User.query.get(user_id)
                
                if not user or not PermissionService.has_permission(user, permission):
                    abort(403, description="Permission denied")
                
                return f(*args, **kwargs)
            return decorated
        return decorator
```

---

## 5. Filtri Automatici Multi-Tenant

### 5.1 Query Filter

File: `backend/core/services/query_filter.py`

```python
"""
Filtri automatici per query multi-tenant.
"""
from flask import g
from sqlalchemy import event
from sqlalchemy.orm import Query
from backend.core.services.tenant_context import TenantContext


class TenantQueryFilter:
    """
    Filtra automaticamente tutte le query per tenant.
    Si applica a tutti i modelli che ereditano da BaseModel.
    """
    
    @staticmethod
    def init_app(app):
        """Registra eventi SQLAlchemy."""
        event.listen(
            Query, 
            'before_compile', 
            TenantQueryFilter._add_tenant_filter
        )
    
    @staticmethod
    def _add_tenant_filter(query):
        """
        Aggiunge filtro tenant a tutte le query.
        """
        tenant_id = TenantContext.get_tenant_id()
        
        # Se non c'è tenant, non filtrare (per operazioni sistema)
        if tenant_id is None:
            return
        
        # Ignora modelli senza tenant_id (sistema)
        for entity in query._entities):
            if hasattr(entity, 'tenant_id'):
                # Applica filtro tenant
                query = query.filter(entity.tenant_id == tenant_id)
        
        return query


class SoftDeleteFilter:
    """
    Filtra automaticamente i record soft-deleted.
    """
    
    @staticmethod
    def init_app(app):
        event.listen(
            Query,
            'before_compile',
            SoftDeleteFilter._add_soft_delete_filter
        )
    
    @staticmethod
    def _add_soft_delete_filter(query):
        """Aggiunge filtro per escludere soft-deleted."""
        for entity in query._entities:
            if hasattr(entity, 'deleted_at'):
                query = query.filter(entity.deleted_at == None)
        return query
```

---

## 6. API Endpoints

### 6.1 Auth API

File: `backend/core/api/auth.py`

```python
"""
API per autenticazione.
"""
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.user import User
from ..models.tenant import Tenant
from ..services.auth_service import AuthService
from ..services.tenant_context import TenantContext
from ...extensions import db
from ...schemas import (
    LoginSchema, 
    AuthResponseSchema,
    RegisterSchema,
    UserSchema,
    PasswordResetRequestSchema,
    PasswordResetSchema
)

auth_bp = Blueprint('auth', __name__, description='Authentication')


@auth_bp.route('/login')
class Login(MethodView):
    @auth_bp.arguments(LoginSchema)
    @auth_bp.response(200, AuthResponseSchema)
    def post(self, data):
        """Effettua login."""
        try:
            result = AuthService.login(
                email=data['email'],
                password=data['password'],
                tenant_id=data.get('tenant_id')
            )
            return result
        except ValueError as e:
            abort(401, message=str(e))


@auth_bp.route('/register')
class Register(MethodView):
    @auth_bp.arguments(RegisterSchema)
    @auth_bp.response(201, AuthResponseSchema)
    def post(self, data):
        """Registra nuovo tenant e utente admin."""
        try:
            result = AuthService.register(
                email=data['email'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                tenant_name=data['tenant_name'],
                tenant_slug=data['tenant_slug']
            )
            return result
        except ValueError as e:
            abort(400, message=str(e))


@auth_bp.route('/me')
class CurrentUser(MethodView):
    @auth_bp.doc(security=[{"bearerAuth": []}])
    @jwt_required()
    @auth_bp.response(200, UserSchema)
    def get(self):
        """Ottieni utente corrente."""
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            abort(404, message="Utente non trovato")
        return user.to_dict()


@auth_bp.route('/refresh')
class Refresh(MethodView):
    @auth_bp.doc(security=[{"bearerAuth": []}])
    @jwt_required(refresh=True)
    @auth_bp.response(200)
    def post(self):
        """Refresh token."""
        try:
            return AuthService.refresh_token()
        except ValueError as e:
            abort(401, message=str(e))


@auth_bp.route('/password/reset')
class PasswordResetRequest(MethodView):
    @auth_bp.arguments(PasswordResetRequestSchema)
    @auth_bp.response(200)
    def post(self, data):
        """Richiedi reset password."""
        return AuthService.request_password_reset(data['email'])


@auth_bp.route('/password/reset/confirm')
class PasswordResetConfirm(MethodView):
    @auth_bp.arguments(PasswordResetSchema)
    @auth_bp.response(200)
    def post(self, data):
        """Conferma reset password."""
        try:
            AuthService.reset_password(data['token'], data['new_password'])
            return {'message': 'Password resettata con successo'}
        except ValueError as e:
            abort(400, message=str(e))
```

### 6.2 Tenant API

File: `backend/core/api/tenant.py`

```python
"""
API per gestione tenant.
"""
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt
from ..models.tenant import Tenant
from ..models.user import User
from ..services.permission_service import Permission, PermissionService
from ...extensions import db

tenant_bp = Blueprint('tenant', __name__, description='Tenant Management')


@tenant_bp.route('/')
class TenantResource(MethodView):
    @tenant_bp.doc(security=[{"bearerAuth": []}])
    @jwt_required()
    @tenant_bp.response(200)
    def get(self):
        """Ottieni info tenant corrente."""
        tenant = TenantContext.get_tenant()
        if not tenant:
            abort(404)
        return tenant.to_dict()
    
    @tenant_bp.doc(security=[{"bearerAuth": []}])
    @jwt_required()
    @PermissionService.require_permission(Permission.MANAGE_TENANT)
    @tenant_bp.arguments(TenantUpdateSchema)
    @tenant_bp.response(200)
    def put(self, data):
        """Aggiorna tenant."""
        tenant = TenantContext.get_tenant()
        
        for key, value in data.items():
            setattr(tenant, key, value)
        
        db.session.commit()
        return tenant.to_dict()


@tenant_bp.route('/users')
class TenantUsers(MethodView):
    @tenant_bp.doc(security=[{"bearerAuth": []}])
    @jwt_required()
    @tenant_bp.response(200)
    def get(self):
        """Lista utenti tenant."""
        tenant_id = TenantContext.get_tenant_id()
        users = User.query.filter_by(tenant_id=tenant_id).all()
        return [u.to_dict() for u in users]
    
    @tenant_bp.doc(security=[{"bearerAuth": []}])
    @jwt_required()
    @PermissionService.require_permission(Permission.MANAGE_USERS)
    @tenant_bp.arguments(UserCreateSchema)
    @tenant_bp.response(201)
    def post(self, data):
        """Crea nuovo utente nel tenant."""
        tenant = TenantContext.get_tenant()
        
        if not tenant.can_add_user():
            abort(400, message="Limite utenti raggiunto")
        
        user = User(
            tenant_id=tenant.id,
            email=data['email'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            role=data.get('role', 'user')
        )
        user.set_password(data.get('password', 'changeme123'))
        
        db.session.add(user)
        db.session.commit()
        
        return user.to_dict()
```

---

## 7. Database Migration

### 7.1 Migration Iniziale

File: `migrations/versions/xxx_add_tenant_support.py`

```python
"""Add multi-tenant support

Revision ID: xxx
Revises: 
Create Date: 2026-02-18
"""
from alembic import op
import sqlalchemy as sa

revision = 'xxx'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 1. Crea tabella tenants
    op.create_table(
        'tenants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('slug', sa.String(length=80), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('website', sa.String(length=255), nullable=True),
        sa.Column('address', sa.String(length=255), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('postal_code', sa.String(length=20), nullable=True),
        sa.Column('country', sa.String(length=2), nullable=True),
        sa.Column('timezone', sa.String(length=50), nullable=True),
        sa.Column('locale', sa.String(length=5), nullable=True),
        sa.Column('currency', sa.String(length=3), nullable=True),
        sa.Column('plan', sa.String(length=50), nullable=True),
        sa.Column('plan_expires_at', sa.DateTime(), nullable=True),
        sa.Column('max_users', sa.Integer(), nullable=True),
        sa.Column('max_storage_mb', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('logo', sa.String(length=255), nullable=True),
        sa.Column('primary_color', sa.String(length=7), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_index('ix_tenants_name', 'tenants', ['name'])
    op.create_index('ix_tenants_slug', 'tenants', ['slug'])
    
    # 2. Aggiungi tenant_id a users
    op.add_column('users', sa.Column('tenant_id', sa.Integer(), nullable=True))
    op.create_index('ix_users_tenant_id', 'users', ['tenant_id'])
    op.create_unique_constraint('uix_tenant_email', 'users', ['tenant_id', 'email'])
    
    # 3. Crea tabella audit_logs
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=False),
        sa.Column('resource_id', sa.Integer(), nullable=True),
        sa.Column('changes', sa.Text(), nullable=True),
        sa.Column('old_values', sa.Text(), nullable=True),
        sa.Column('new_values', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('endpoint', sa.String(length=255), nullable=True),
        sa.Column('method', sa.String(length=10), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )
    op.create_index('ix_audit_tenant_created', 'audit_logs', ['tenant_id', 'created_at'])


def downgrade():
    op.drop_table('audit_logs')
    op.drop_column('users', 'tenant_id')
    op.drop_table('tenants')
```

---

## 8. Configurazione

### 8.1 Configurazione Base

File: `app/config.py`

```python
"""
Configurazione applicazione con supporto multi-tenant.
"""
import os
from datetime import timedelta


class Config:
    """Configurazione base."""
    
    # Secret keys
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-prod'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-change-in-prod'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }
    
    # JWT
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=60)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # Cache
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Upload
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/tmp/flaskerp/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Multi-tenant
    TENANT_DEFAULT_PLAN = 'starter'
    TENANT_MAX_USERS = {
        'starter': 3,
        'business': 10,
        'professional': 25,
        'enterprise': None  # Illimitato
    }
    
    # API
    API_TITLE = 'FlaskERP API'
    API_VERSION = 'v1'
    OPENAPI_VERSION = '3.0.2'
    OPENAPI_URL_PREFIX = '/'
    
    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')


class DevelopmentConfig(Config):
    """Configurazione sviluppo."""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Configurazione produzione."""
    DEBUG = False
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # Sicurezza produzione
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'


class TestingConfig(Config):
    """Configurazione test."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
```

---

## 9. Inizializzazione App

### 9.1 App Factory Aggiornata

File: `app/__init__.py`

```python
"""
Fabbrica applicazione Flask con multi-tenant.
"""
from flask import Flask
from flask_smorest import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_caching import Cache
from flask_migrate import Migrate
from app.config import config
from app.extensions import db


def create_app(config_name=None):
    """Crea e configura l'applicazione Flask."""
    
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Inizializza estensioni
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)
    cache = Cache(app)
    api = Api(app)
    CORS(app)
    
    # Importa modelli
    from backend.core.models.base import BaseModel
    from backend.core.models.tenant import Tenant
    from backend.core.models.user import User, UserRole
    from backend.core.models.audit import AuditLog
    
    # Registra middleware tenant
    from backend.core.middleware.tenant_middleware import TenantMiddleware
    TenantMiddleware.init_app(app)
    
    # Registra blueprint API
    from backend.core.api.auth import auth_bp
    api.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    
    from backend.core.api.tenant import tenant_bp
    api.register_blueprint(tenant_bp, url_prefix='/api/v1/tenant')
    
    # Health check
    @app.route('/health')
    def health():
        return {'status': 'ok', 'tenant': TenantContext.get_tenant_id()}
    
    @app.route('/')
    def index():
        return {'message': 'FlaskERP API', 'version': 'v1'}
    
    return app
```

---

## 10. Checklist Implementazione

### Fase 1: Modelli (Giorni 1-2)

- [ ] Aggiornare BaseModel con tenant_id
- [ ] Creare modello Tenant
- [ ] Aggiornare modello User con tenant_id
- [ ] Creare modello AuditLog
- [ ] Creare migration

### Fase 2: Autenticazione (Giorni 3-4)

- [ ] Aggiornare AuthService per multi-tenant
- [ ] Modificare JWT per includere tenant_id
- [ ] Implementare sistema permessi
- [ ] Aggiornare API auth

### Fase 3: Middleware (Giorno 5)

- [ ] Implementare TenantContext
- [ ] Creare TenantMiddleware
- [ ] Implementare query filter
- [ ] Testare integrazione

### Fase 4: Testing (Giorno 6)

- [ ] Test unitari modelli
- [ ] Test autenticazione
- [ ] Test multi-tenant isolation
- [ ] Test permission system

---

## 11. Prossimo Step

Dopo aver implementato il Core:

1. **Modulo Parties**: Anagrafiche clienti/fornitori
2. **Modulo Products**: Catalogo prodotti
3. **Modulo Sales**: Ordini cliente

---

*Documento generato il 18 Febbraio 2026*
*Progetto: FlaskERP ERPaaS Platform*
*Documento #04 - Specifiche Tecniche Modulo Core*
