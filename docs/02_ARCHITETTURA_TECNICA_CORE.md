# ERPaaS - Architettura Tecnica: FlaskERP Core

## Documento #02 - Analisi Architetturale

---

## 1. Panoramica dell'Architettura Attuale

### 1.1 Stack Tecnologico

Il progetto attuale utilizza le seguenti tecnologie:

| Componente | Tecnologia | Versione |
|------------|------------|-----------|
| Framework | Flask | 2.x |
| API | Flask-smorest | 0.40+ |
| ORM | SQLAlchemy + Flask-SQLAlchemy | - |
| Database | PostgreSQL | 14+ |
| Migration | Flask-Migrate | - |
| Serialization | Flask-Marshmallow | - |
| Auth | Flask-JWT-Extended | - |
| WebSocket | Flask-SocketIO | - |
| Frontend | Non specificato | - |

### 1.2 Struttura delle Directory

```
flaskERP/
├── app/                    # Configurazione app Flask
│   ├── __init__.py
│   ├── config.py          # Configurazione base
│   ├── extensions.py      # Estensioni Flask
│   └── resources/         # Resource API (se presenti)
├── backend/
│   ├── __init__.py
│   ├── models.py          # Modelli database
│   ├── extensions.py      # Estensioni condivise
│   ├── auth.py            # Autenticazione
│   ├── decorators.py      # Decoratori
│   ├── crud.py           # Operazioni CRUD base
│   ├── plugins/           # Sistema a plugin
│   │   ├── base.py       # Classe base BasePlugin
│   │   ├── registry.py   # PluginRegistry
│   │   ├── accounting/   # Plugin contabilità
│   │   └── hr/           # Plugin HR
│   ├── services/         # Servizi business logic
│   │   ├── base.py
│   │   ├── user_service.py
│   │   ├── builder_service.py
│   │   ├── project_service.py
│   │   └── dynamic_api_service.py
│   └── workflows/         # Gestione workflow
├── frontend/              # Frontend (non dettagliato)
├── migrations/           # Database migrations
├── tests/                # Test unitari
├── docs/                 # Documentazione
└── run.py                # Entry point
```

---

## 2. Analisi dei Componenti Core

### 2.1 Sistema di Autenticazione

**File**: `backend/auth.py`

Il sistema attuale utilizza **JWT (JSON Web Tokens)** per l'autenticazione:

```
Componenti:
├── JWT_ACCESS_TOKEN_EXPIRES = 15 minuti
├── JWT_REFRESH_TOKEN_EXPIRES = 30 giorni
└── Sistema password con hash (werkzeug.security)
```

**Flusso di autenticazione**:

```
1. Utente invia credenziali (email/password)
2. Server valida e genera JWT token
3. Token incluso in ogni richiesta header
4. Token validato ad ogni richiesta protetta
```

**Criticità identificate**:
- Nessun supporto OAuth2/Social login
- Token di accesso molto brevi (15 min) potrebbero causare UX problemi
- Refresh token memorizzato lato client senza rotazione

---

### 2.2 Modelli Database

**File**: `backend/models.py`

#### Modelli Core

| Modello | Tabella | Descrizione |
|---------|---------|-------------|
| `BaseModel` | - | Classe base con id, created_at, updated_at |
| `User` | users | Utenti del sistema |
| `Project` | projects | Progetti/istanze ERP |
| `SysModel` | sys_models | Modelli dinamici (tabelle) |
| `SysField` | sys_fields | Campi dinamici (colonne) |
| `Party` | parties | Anagrafiche (clienti/fornitori) |
| `Product` | products | Prodotti/Servizi |
| `SalesOrder` | sales_orders | Ordini cliente |
| `SalesOrderLine` | sales_order_lines | Righe ordine |
| `AuditLog` | audit_logs | Log azioni utenti |
| `SysChart` | sys_charts | Configurazione grafici |
| `SysDashboard` | sys_dashboards | Dashboard |

#### Relazioni tra Modelli

```
User (1) ──────< Project (N)
    │
    └────< ProjectMembers (N:N) >──── Project

Project (1) ──< SysModel (N)
    │
    └────< SysField (N)

Party (1) ──< SalesOrder (N)
    │
    └────< SalesOrderLine (N)
              │
              └────> Product (N)
```

---

### 2.3 Sistema a Plugin

**Files**: `backend/plugins/base.py`, `backend/plugins/registry.py`

Il progetto implementa un **sistema a plugin** per estendere le funzionalità:

#### Architettura Plugin

```
BasePlugin
├── name: str
├── version: str
├── description: str
├── dependencies: List[str]
├── register() [abstract]
├── init_db() [abstract]
├── install()
├── uninstall()
├── before_request()
└── after_request()

PluginRegistry
├── register(plugin_class)
├── enable(name, app, db, api)
├── disable(name)
├── get(name)
├── get_enabled()
├── discover_plugins(plugins_dir)
└── list_plugins()
```

#### Plugin Esistenti

| Plugin | Percorso | Stato |
|--------|----------|-------|
| Accounting | `backend/plugins/accounting/` | Implementato |
| HR | `backend/plugins/hr/` | Implementato |

#### Vantaggi dell'architettura plugin

1. **Separazione responsabilità**: Ogni plugin è un modulo indipendente
2. **Estensibilità**: Nuovi moduli senza modificare il core
3. **Riusabilità**: Plugin installabili/disinstallabili a runtime
4. **Isolamento errori**: Problemi in un plugin non crashano l'app

---

### 2.4 Builder Service

**File**: `backend/services/builder_service.py`

Il Builder Service gestisce la creazione dinamica di entità:

#### Funzionalità

- Creazione modelli dinamici (SysModel)
- Definizione campi con tipi diversi
- Configurazione relazioni tra entità
- Gestione permessi e ACL

#### Tipi di Campo Supportati

| Tipo | Descrizione |
|------|-------------|
| string | Testo breve |
| text | Testo lungo |
| integer | Numero intero |
| float | Numero decimale |
| boolean | Vero/Falso |
| date | Data |
| datetime | Data e ora |
| select | Menu a tendina |
| relation | Relazione ad altro modello |

---

### 2.5 Dynamic API Service

**File**: `backend/services/dynamic_api_service.py`

Genera automaticamente API REST basate sui modelli dinamici:

```
Endpoint generati automaticamente:
├── GET    /api/{model}           # Lista records
├── GET    /api/{model}/{id}     # Singolo record
├── POST   /api/{model}           # Crea record
├── PUT    /api/{model}/{id}     # Aggiorna record
├── DELETE /api/{model}/{id}      # Elimina record
└── GET    /api/{model}/export   # Esporta dati
```

---

## 3. Punti di Forza dell'Architettura Attuale

### 3.1 Pro

| Aspetto | Descrizione |
|---------|-------------|
| **Plugin System** | Architettura ben progettata per estensioni |
| **Dynamic Builder** | Sistema per creare entità a runtime |
| **JWT Auth** | Sicuro e scalabile |
| **Audit Log** | Tracciamento azioni utente |
| **Multi-tenant Ready** | BaseModel + Project supportano multi-tenant |

---

## 4. Criticità e Raccomandazioni

### 4.1 Criticità Identificate

| # | Problema | Impatto | Priorità |
|---|----------|---------|----------|
| 1 | Nessun multi-tenant reale | Dati non isolati | Alta |
| 2 | Frontend non definito | Non chiaro come proceedere | Alta |
| 3 | Test coverage bassa | Rischio regressioni | Media |
| 4 | Configurazione rigida | Non parametrizzabile per SaaS | Alta |
| 5 | Cache assente | Performance scarse | Media |
| 6 | Celery/Queue non presente | Async task non gestiti | Media |

---

### 4.2 Raccomandazioni Immediate

#### A. Implementare Multi-Tenant

Aggiungere `tenant_id` a tutti i modelli:

```python
class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
```

#### B. Aggiungere Sistema di Caching

```python
# extensions.py
from flask_caching import Cache

cache = Cache()

# config.py
CACHE_TYPE = "redis"
CACHE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
```

#### C. Aggiungere Task Queue

```python
# Per operazioni asincrone
# extensions.py
from celery import Celery

def make_celery(app):
    celery = Celery(app.import_name)
    celery.conf.update(app.config)
    return celery
```

#### D. Configurazione Centralizzata

Spostare configurazione in `config.yaml` o variabili d'ambiente:

```yaml
# config.yaml
database:
  host: ${DB_HOST}
  port: 5432
  name: ${DB_NAME}

redis:
  host: ${REDIS_HOST}
  port: 6379

security:
  jwt_secret: ${JWT_SECRET}
  jwt_algorithm: HS256
```

---

## 5. Architettura Proposta per FlaskERP Core

### 5.1 Diagramma Architetturale

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND LAYER                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  Web App    │  │  Mobile     │  │  API Docs   │             │
│  │  (React)    │  │  (Expo)     │  │  (Swagger)  │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
└─────────┼────────────────┼────────────────┼────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API GATEWAY LAYER                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Flask + Flask-smorest (REST)               │   │
│  │  • Rate Limiting    • Request Validation               │   │
│  │  • Auth Middleware   • CORS                             │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BUSINESS LOGIC LAYER                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Auth Service │  │User Service  │  │Builder Svc   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │Project Svc   │  │Plugin Svc    │  │Workflow Svc  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  PostgreSQL  │  │    Redis     │  │     S3       │          │
│  │  (Primary)   │  │   (Cache)    │  │   (Files)    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

---

### 5.2 Schema Multi-Tenant

```
┌─────────────────────────────────────────────────────────────┐
│                      TENANT ISOLATION                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  tenant_id: 1           tenant_id: 2           tenant_id:N │
│  ┌───────────┐          ┌───────────┐          ┌───────────┐│
│  │  Schema   │          │  Schema   │          │  Schema   ││
│  │  tenant1  │          │  tenant2  │          │  tenantN  ││
│  └───────────┘          └───────────┘          └───────────┘│
│        │                      │                      │        │
│        ▼                      ▼                      ▼        │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              PostgreSQL Database Cluster                │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

### 5.3 Struttura Package Proposta

```
flaskERP/
├── app/
│   ├── __init__.py           # Fabbrica applicazione
│   ├── config.py             # Configurazione
│   └── extensions.py        # Estensioni
├── core/
│   ├── models/               # Modelli database condivisi
│   │   ├── __init__.py
│   │   ├── base.py          # BaseModel + TenantMixin
│   │   ├── user.py
│   │   ├── tenant.py
│   │   └── audit.py
│   ├── services/            # Servizi core
│   │   ├── auth_service.py
│   │   ├── tenant_service.py
│   │   └── cache_service.py
│   ├── api/                 # API routes core
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── tenants.py
│   └── utils/               # Utility condivise
│       ├── security.py
│       └── validators.py
├── modules/                 # Moduli applicativi
│   ├── base.py             # Classe base modulo
│   ├── registry.py         # Registry moduli
│   ├── parties/            # Anagrafiche
│   │   ├── models.py
│   │   ├── api.py
│   │   └── __init__.py
│   ├── products/           # Prodotti
│   │   ├── models.py
│   │   ├── api.py
│   │   └── __init__.py
│   ├── sales/             # Vendite
│   │   ├── models.py
│   │   ├── api.py
│   │   └── __init__.py
│   └── accounting/        # Contabilità
│       ├── models.py
│       ├── api.py
│       └── __init__.py
├── plugins/                # Plugin sistema
│   ├── base.py
│   ├── registry.py
│   └── ...
├── cli/                    # Comandi CLI
│   ├── __init__.py
│   ├── db.py
│   └── user.py
├── migrations/             # Alembic migrations
├── tests/                  # Test
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── docker/                 # Docker files
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── nginx.conf
├── docs/                   # Documentazione
├── run.py                  # Entry point
├── setup.py                # Setup package
└── pyproject.toml         # Configurazione progetto
```

---

## 6. Stack Tecnologico Raccomandato

### 6.1 Core

| Componente | Tecnologia | Alternativa |
|------------|------------|--------------|
| Framework | Flask 3.x | FastAPI |
| ORM | SQLAlchemy 2.x | - |
| API | Flask-smorest | Pydantic + FastAPI |
| Auth | Flask-JWT-Extended | Authlib |
| Cache | Flask-Caching + Redis | - |
| Task Queue | Celery + Redis | Dramatiq |
| Migration | Alembic | - |

### 6.2 Infrastructure

| Componente | Scelta | Costo stimato |
|------------|--------|---------------|
| DB | PostgreSQL (Hetzner Cloud) | 5-10€/mese |
| Cache | Redis (Hetzner Cloud) | 2-5€/mese |
| Storage | S3 / MinIO | 1-5€/mese |
| Hosting | Hetzner Cloud VM | 5-20€/mese |
| Domain | Cloudflare | 10-15€/anno |

**Totale stimato**: ~20-40€/mese per iniziare

---

## 7. Piano di Migrazione

### Fase 1: Refactoring Base (Settimane 1-2)

1. [ ] Aggiornare struttura package
2. [ ] Implementare BaseModel con tenant_id
3. [ ] Aggiungere modello Tenant
4. [ ] Implementare sistema caching Redis
5. [ ] Aggiornare config.py

### Fase 2: Migrazione Moduli (Settimane 3-4)

1. [ ] Spostare models in core/models/
2. [ ] Migrare plugin in modules/
3. [ ] Implementare modulo base astratto
4. [ ] Creare sistema moduli con dipendenze

### Fase 3: API e Servizi (Settimane 5-6)

1. [ ] Refactoring API routes
2. [ ] Implementare rate limiting
3. [ ] Aggiungere logging strutturato
4. [ ] Implementare health checks

### Fase 4: Infrastructure (Settimane 7-8)

1. [ ] Creare Dockerfile ottimizzato
2. [ ] Configurare docker-compose
3. [ ] Implementare CI/CD base
4. [ ] Setup monitoring (Prometheus/Grafana)

---

## 8. Priorità di Sviluppo

### Must Have (MVP)

| # | Feature | Descrizione |
|---|---------|-------------|
| 1 | Multi-tenant base | Isolamento dati per tenant |
| 2 | Auth JWT | Autenticazione sicura |
| 3 | CRUD Anagrafiche | Gestione clienti/fornitori |
| 4 | CRUD Prodotti | Catalogo prodotti |
| 5 | Ordini base | Creazione ordini |

### Should Have

| # | Feature | Descrizione |
|---|---------|-------------|
| 6 | Dashboard base | Statistiche veloci |
| 7 | Filtri e ricerche | Query avanzate |
| 8 | Export dati | CSV/PDF |
| 9 | Cache | Performance |
| 10 | Audit log | Tracciamento |

### Could Have

| # | Feature | Descrizione |
|---|---------|-------------|
| 11 | Notifiche | Email/in-app |
| 12 | Webhook | Integrazioni esterne |
| 13 | API REST pubblica | Per integrazioni |
| 14 | Workflow base | Automazioni semplici |
| 15 | Multi-language | Internazionalizzazione |

---

## 9. Dipendenze Python

### requirements.txt

```
# Core
flask>=3.0.0
flask-sqlalchemy>=3.1.0
flask-migrate>=4.0.0
flask-smorest>=0.44.0
flask-marshmallow>=1.2.0
flask-jwt-extended>=4.6.0
flask-caching>=2.1.0
flask-cors>=4.0.0

# Database
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
alembic>=1.13.0

# Tasks
celery>=5.3.0
redis>=5.0.0

# Security
bcrypt>=4.1.0
python-dotenv>=1.0.0

# Utils
marshmallow-sqlalchemy>=0.29.0
python-dateutil>=2.8.0
pytz>=2024.1
gunicorn>=21.0.0
```

---

## 10. Checklist Deployment

### Pre-Deploy

- [ ] Database schema aggiornato
- [ ] Tutti i test passano
- [ ] Variabili d'ambiente configurate
- [ ] Certificati SSL validi
- [ ] Backup database automatizzato
- [ ] Monitoring configurato

### Post-Deploy

- [ ] Health check funziona
- [ ] Login utente funziona
- [ ] CRUD base funziona
- [ ] Performance accettabili
- [ ] Logg correttamente configurati

---

## 11. Glossario Tecnico

| Termine | Definizione |
|---------|-------------|
| **Tenant** | Entità (azienda/organizzazione) che utilizza il sistema |
| **Multi-tenant** | Architettura che supporta più tenant isolati |
| **Plugin** | Componente estendibile del sistema |
| **Modulo** | Unità funzionale dell'applicazione |
| **Migration** | Script per modificare lo schema database |
| **Serializer** | Conversione oggetti Python ↔ JSON |
| **Rate Limiting** | Limitazione richieste per utente/IP |

---

## 12. Riferimenti

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [Flask-smorest](https://flask-smorest.readthedocs.io/)
- [Flask-JWT-Extended](https://flask-jwt-extended.readthedocs.io/)
- [Multi-Tenant SaaS Patterns](https://docs.microsoft.com/azure/architecture/guide/multitenant/approaches/overview)

---

*Documento generato il 18 Febbraio 2026*
*Progetto: FlaskERP ERPaaS Platform*
*Documento #02 - Architettura Tecnica FlaskERP Core*
