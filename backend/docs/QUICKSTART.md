# ERPSeed - Quick Start Guide

## 🚀 Quick Start

### 1. Clona il Repository

```bash
git clone https://github.com/your-repo/erpseed.git
cd erpseed
```

### 2. Configura l'Ambiente

```bash
cd backend

# Crea un virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Installa le dipendenze
pip install -r requirements.txt
```

### 3. Configura le Variabili d'Ambiente

```bash
# Crea un file .env nella cartella backend/
cat > backend/.env << 'EOF'
DATABASE_URL=sqlite:///data.db
JWT_SECRET_KEY=your-super-secret-key-at-least-32-characters-long
SECRET_KEY=flask-secret-key
FLASK_ENV=development
FLASK_DEBUG=1

# AI Configuration (opzionale)
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your-api-key
EOF
```

### 4. Inizializza il Database

```bash
cd backend

# Crea l'utente admin e il tenant iniziale
python -m cli.create_admin

# Output atteso:
# Created user: admin@erpseed.org
# Default password: admin123 (change immediately!)
```

### 5. Avvia l'Applicazione

```bash
cd backend
export JWT_SECRET_KEY="your-secret-key-at-least-32-characters-long"
flask run --host=0.0.0.0 --port=5000
```

Oppure con Python:

```bash
python run.py
```

### 6. Accedi all'API

- **Swagger UI**: http://localhost:5000/swagger-ui
- **Health Check**: http://localhost:5000/health

---

## 🛠️ Comandi CLI Disponibili

### Creazione Utente Admin

```bash
python -m cli.create_admin
```

### Setup Database Completo

```bash
python -m cli.setup_database
```

### Reset Database

```bash
python -m cli.reset_db
```

### Seeds Disponibili

```bash
# Seed iniziale (admin + tenant)
python -m seeds.initial

# Dati geografici italiani
python -m seeds.comuni

# UI Components e Actions
python -m seeds.metadata

# KPI Dashboard
python -m seeds.kpi

# Template GDO
python -m seeds.gdo_models
```

---

## 📡 API Endpoints Principali

### Autenticazione

| Metodo | Endpoint | Descrizione |
|--------|----------|-------------|
| POST | `/api/v1/auth/login` | Login utente |
| POST | `/api/v1/auth/register` | Registrazione |
| POST | `/api/v1/auth/refresh` | Refresh token |

### Progetti

| Metodo | Endpoint | Descrizione |
|--------|----------|-------------|
| GET | `/projects` | Lista progetti |
| POST | `/projects` | Crea progetto |
| GET | `/projects/<id>` | Dettaglio progetto |
| PUT | `/projects/<id>` | Aggiorna progetto |
| DELETE | `/projects/<id>` | Elimina progetto |

### Dynamic API (Builder)

| Metodo | Endpoint | Descrizione |
|--------|----------|-------------|
| GET | `/projects/<id>/data/<model>` | Lista records |
| POST | `/projects/<id>/data/<model>` | Crea record |
| GET | `/projects/<id>/data/<model>/<id>` | Dettaglio |
| PUT | `/projects/<id>/data/<model>/<id>` | Aggiorna |
| DELETE | `/projects/<id>/data/<model>/<id>` | Elimina |

### Workflows

| Metodo | Endpoint | Descrizione |
|--------|----------|-------------|
| GET | `/workflows` | Lista workflows |
| POST | `/workflows` | Crea workflow |
| GET | `/workflows/<id>/execute` | Esegui workflow |

### Webhooks

| Metodo | Endpoint | Descrizione |
|--------|----------|-------------|
| GET | `/webhooks` | Lista webhooks |
| POST | `/webhooks` | Crea webhook |
| POST | `/webhooks/<id>/trigger` | Trigger webhook |

### AI Assistant

| Metodo | Endpoint | Descrizione |
|--------|----------|-------------|
| POST | `/ai/chat` | Invia messaggio |
| GET | `/ai/conversations` | Lista conversazioni |
| POST | `/ai/generate-config` | Genera configurazione |

---

## 🔧 Configurazione AI

### Provider Supportati

1. **OpenRouter** (default) - DeepSeek, Claude, GPT-4
2. **OpenAI** - GPT-4, GPT-3.5
3. **Anthropic** - Claude
4. **Ollama** - Modelli locali

### Configurazione per Provider

```bash
# OpenRouter (consigliato - tanti modelli)
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-...

# OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...

# Anthropic
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Ollama (locale)
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

---

## 🐳 Docker

```bash
# Build e avvio
docker-compose up -d

# Rebuild
docker-compose up -d --build

# Stop
docker-compose down

# Logs
docker-compose logs -f backend
```

---

## 🧪 Testing

```bash
cd backend

# Esegui tutti i test
pytest

# Esegui test specifici
pytest tests/test_workflow_engine.py

# Con coverage
pytest --cov=. --cov-report=html
```

---

## 📁 Struttura Backend

```
backend/
├── models/                    # Modelli Database
│   ├── user.py               # User
│   ├── project.py            # Project
│   ├── product.py            # Product
│   ├── sales.py              # SalesOrder
│   ├── purchase.py           # PurchaseOrder
│   ├── workflow.py           # Workflow
│   ├── webhook.py           # Webhook
│   └── system/               # SysModel, SysField, etc.
│
├── routes/                   # API Endpoints
│   ├── projects.py
│   ├── dashboard.py
│   ├── workflows.py
│   └── ...
│
├── services/                 # Logica Business
│   ├── workflow_service.py
│   ├── webhook_service.py
│   └── ...
│
├── cli/                      # Script CLI
│   ├── create_admin.py
│   ├── setup_database.py
│   └── ...
│
├── seeds/                    # Database Seeds
│   ├── initial.py            # Admin + Tenant
│   ├── comuni.py             # Dati geografici IT
│   └── ...
│
├── core/                     # Sistema Core
│   ├── api/                  # Auth, Tenant, Modules
│   ├── models/              # Tenant, Audit, etc.
│   ├── services/             # Auth, Permissions
│   └── middleware/           # Tenant Middleware
│
├── ai/                      # AI Assistant (Legacy)
├── ai_service/               # AI CQRS
├── builder_service/          # No-Code Builder CQRS
├── products_service/         # Products CQRS
├── sales_service/            # Sales CQRS
├── purchases_service/        # Purchases CQRS
│
├── entities/                # Vision Archetypes
├── plugins/                  # Plugin System
└── shared/                   # Utilities condivise
```

---

## 🔒 Sicurezza

- JWT con scadenza 15 minuti
- Refresh token per sessioni lunghe
- Password hash con Werkzeug
- Tenant isolation a livello middleware

---

## 📚 Documentazione Aggiuntiva

| Documento | Descrizione |
|----------|-------------|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Architettura completa |
| README.md | Documentazione principale |

---

*Ultimo aggiornamento: 2026-03-18*
