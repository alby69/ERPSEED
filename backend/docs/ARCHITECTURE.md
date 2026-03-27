# Architettura ERPSEED Backend

## Panoramica

ERPSEED è un sistema ERP moderno e modulare costruito con Flask. Utilizza un'architettura **Hybrid CQRS** (Command Query Responsibility Segregation) con supporto per:
- **Write side**: Modelli relazionali strutturati su PostgreSQL per garantire integrità e consistenza.
- **Read side**: Modelli denormalizzati in formato **PostgreSQL JSONB** per alte prestazioni in lettura e dashboard.
- **No-Code Builder**: Creazione dinamica di modelli dati e interfacce.
- **Event-Driven**: Sincronizzazione asincrona dei dati tramite EventBus.

## Stack Tecnologico

| Componente | Tecnologia |
|------------|-----------|
| Framework | Flask 3.x |
| ORM | SQLAlchemy + Flask-SQLAlchemy |
| API | Flask-Smorest (OpenAPI 3.0) |
| Read Model | PostgreSQL JSONB |
| Pattern | Command Handler / CQRS |
| Auth | Flask-JWT-Extended (JWT) |
| Realtime | Flask-SocketIO |

## Struttura del Progetto (Nuova Organizzazione Modulare)

Il backend è organizzato in modo da separare il "core" del sistema dai moduli funzionali specifici.

```
backend/
├── core/                    # SISTEMA CORE (Infrastruttura condivisa)
│   ├── api/                # Endpoints core (Auth, Tenant, System)
│   ├── models/             # Modelli base e di sistema (Tenant, Audit, Module)
│   ├── services/           # Logica core (Auth, PDF, TestEngine)
│   ├── events/             # Triggers e gestione eventi di sistema
│   ├── decorators/         # Decoratori (admin_required, tenant_required)
│   ├── schemas/            # Schemi Marshmallow base
│   └── utils/              # Utility condivise (paginazione, filtri)
│
├── modules/                 # MODULI FUNZIONALI (Dominio)
│   ├── users/              # Gestione Utenti (Command Handler)
│   ├── projects/           # Gestione Progetti (Command Handler)
│   ├── products/           # Catalogo Prodotti (Command Handler)
│   ├── sales/              # Ordini di Vendita (Command Handler)
│   ├── purchases/          # Ordini di Acquisto (Command Handler)
│   ├── builder/            # No-Code Builder (Modelli, Campi, Blocchi)
│   ├── ai/                 # AI Assistant (Integrazione LLM e Tool Calling)
│   ├── dynamic_api/        # CRUD Dinamico per modelli generati
│   ├── analytics/          # BI & Dashboards (Command Handler)
│   ├── automation/         # Workflow & Webhooks (Command Handler)
│   ├── entities/           # Archetipi Vision (Soggetti, Ruoli, Indirizzi)
│   └── system_tools/       # Tool di sistema (Templates, Versioning)
│
├── shared/                  # CODICE CONDIVISO CROSS-MODULE
│   ├── events/             # EventBus e Domain Events
│   └── handlers/           # Classi base per Command Handlers
│
├── models/                  # Modelli SQLAlchemy globali (Legacy/Compatibility)
├── services/                # Proxy per servizi modulari (Compatibility)
├── routes/                  # Punto di ingresso Blueprint (Compatibility)
│
├── __init__.py              # App factory e centralizzazione rotte /api/v1/
├── extensions.py            # Inizializzazione estensioni Flask
├── run.py                   # Entry point per lo sviluppo
└── requirements.txt         # Dipendenze Python
```

## Pattern Architetturali

### 1. Command Handler Pattern (Standard per ERPSeed)

Tutti i nuovi moduli devono seguire questo pattern per disaccoppiare l'API dalla logica di business.

```
API Route -> Command Object -> Handler -> Database/Service
```

Esempio:
- `application/commands/user_commands.py`: Definizione del comando (Dataclass).
- `application/handlers.py`: Logica di esecuzione del comando.
- `api/rest_api.py`: Endpoint Flask che trasforma la request in un Command.

### 2. Hybrid CQRS con JSONB

Per ottimizzare le letture complesse (es. Dashboard), il sistema utilizza `SysReadModel`:
1. **Scrittura**: Viene eseguita sui modelli SQL classici (`users`, `orders`, etc.).
2. **Evento**: Un trigger (`on_record_created`) pubblica un evento sull'EventBus.
3. **Proiezione**: Il `read_model_handler` riceve l'evento e aggiorna una rappresentazione JSONB denormalizzata del record.
4. **Lettura**: Le API di analytics leggono direttamente dalla colonna `data` (JSONB) evitando JOIN costose.

## Multi-Tenancy

ERPSeed implementa il multi-tenancy tramite **PostgreSQL Schema Isolation**. Ogni tenant (organizzazione) o progetto può avere il proprio schema isolato (`project_1`, `project_2`), garantendo sicurezza e pulizia dei dati.

## Autenticazione e API

Tutte le API sono centralizzate sotto il prefisso `/api/v1/` e richiedono un token JWT, ad eccezione del login e della registrazione.
Le rotte sono standardizzate per supportare:
- Paginazione automatica (Header `X-Total-Count`, `X-Pages`)
- Filtri dinamici (`?q=search_term`)
- Sorting (`?sort_by=name&sort_order=desc`)

---

*Ultimo aggiornamento: 2024-05-24 (Refactoring Modulare e CQRS)*
