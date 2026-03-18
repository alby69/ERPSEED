# ERPSeed - Low-Code ERP Platform

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-orange)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

ERPSeed è una piattaforma ERP open-source e modulare che permette alle organizzazioni di costruire e personalizzare il proprio sistema di gestione aziendale attraverso un approccio low-code.

---

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
# OPENAI_API_KEY=your-openai-key
# ANTHROPIC_API_KEY=your-anthropic-key
EOF
```

### 4. Inizializza il Database

```bash
cd backend

# Crea l'utente admin e il tenant iniziale
python -m cli.create_admin

# Oppure esegui lo setup completo
python -m cli.setup_database
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

- API Swagger UI: http://localhost:5000/swagger-ui
- Health Check: http://localhost:5000/health

---

## 📁 Struttura del Progetto

```
erpseed/
├── backend/                    # API Backend (Flask)
│   ├── models/               # Modelli Database
│   │   ├── user.py          # User
│   │   ├── project.py       # Project
│   │   ├── product.py       # Product
│   │   ├── sales.py         # SalesOrder
│   │   ├── purchase.py      # PurchaseOrder
│   │   ├── workflow.py      # Workflow
│   │   ├── webhook.py       # Webhook
│   │   └── system/          # SysModel, SysField, etc.
│   │
│   ├── routes/              # API Endpoints
│   │   ├── projects.py
│   │   ├── dashboard.py
│   │   ├── workflows.py
│   │   └── ...
│   │
│   ├── services/            # Logica Business
│   │   ├── workflow_service.py
│   │   ├── webhook_service.py
│   │   └── ...
│   │
│   ├── cli/                 # Script CLI
│   │   ├── create_admin.py
│   │   ├── setup_database.py
│   │   └── ...
│   │
│   ├── seeds/               # Database Seeds
│   │   ├── initial.py       # Admin + Tenant
│   │   ├── comuni.py        # Dati geografici IT
│   │   └── ...
│   │
│   ├── core/                # Sistema Core
│   │   ├── api/            # Auth, Tenant, Modules
│   │   ├── models/         # Tenant, Audit, etc.
│   │   ├── services/        # Auth, Permissions
│   │   └── middleware/     # Tenant Middleware
│   │
│   ├── ai/                 # AI Assistant (Legacy)
│   ├── ai_service/          # AI CQRS (Nuovo)
│   ├── builder_service/     # No-Code Builder CQRS
│   ├── products_service/    # Products CQRS
│   ├── sales_service/       # Sales CQRS
│   ├── purchases_service/   # Purchases CQRS
│   │
│   ├── entities/            # Vision Archetypes
│   ├── plugins/             # Plugin System
│   └── shared/              # Utilities condivise
│
├── frontend/                  # React Frontend
└── docs/                     # Documentazione
```

---

## 🛠️ Comandi CLI

### Creazione Utente Admin

```bash
cd backend
python -m cli.create_admin
# Output: Crea admin@erpseed.org con password admin123
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

## 📡 API Endpoints

### Autenticazione

```
POST /api/v1/auth/login
POST /api/v1/auth/register
POST /api/v1/auth/refresh
```

### Progetti

```
GET    /projects           # Lista progetti
POST   /projects           # Crea progetto
GET    /projects/<id>     # Dettaglio progetto
PUT    /projects/<id>     # Aggiorna progetto
DELETE /projects/<id>     # Elimina progetto
```

### Dynamic API (Builder)

```
GET    /projects/<id>/data/<model_name>     # Lista records
POST   /projects/<id>/data/<model_name>     # Crea record
GET    /projects/<id>/data/<model_name>/<id> # Dettaglio
PUT    /projects/<id>/data/<model_name>/<id> # Aggiorna
DELETE /projects/<id>/data/<model_name>/<id> # Elimina
```

### Workflows

```
GET    /workflows
POST   /workflows
GET    /workflows/<id>/execute
```

### Webhooks

```
GET    /webhooks
POST   /webhooks
POST   /webhooks/<id>/trigger
```

### AI Assistant

```
POST   /ai/chat
GET    /ai/conversations
POST   /ai/generate-config
```

---

## 🔧 Configurazione AI

### Provider Supportati

1. **OpenRouter** (default) - DeepSeek, Claude, GPT
2. **OpenAI** - GPT-4, GPT-3.5
3. **Anthropic** - Claude
4. **Ollama** - Modelli locali

### Configurazione

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
```

---

## 📦 Pattern CQRS

Il progetto usa il pattern **CQRS** (Command Query Responsibility Segregation) per i moduli principali:

### Command (Modifica Stato)

```python
from backend.ai_service import SendMessageCommand, SendMessageHandler

command = SendMessageCommand(
    project_id=1,
    user_id=1,
    message="Crea un nuovo modello Cliente"
)

handler = SendMessageHandler(chat_service, tool_service)
result = handler.handle(command)
```

### Query (Lettura)

```python
from backend.ai_service import GetConversationHistoryQuery, GetConversationHistoryHandler

query = GetConversationHistoryQuery(
    project_id=1,
    limit=50
)

handler = GetConversationHistoryHandler()
conversations = handler.handle(query)
```

---

## 🔌 Plugin System

### Creare un Plugin

```python
# plugins/my_plugin/plugin.py
from backend.plugins.base import BasePlugin

class MyPlugin(BasePlugin):
    name = "my_plugin"
    version = "1.0.0"
    
    def install(self):
        # Registra routes, servizi, etc.
        pass
    
    def uninstall(self):
        # Pulisci risorse
        pass
```

### Plugin Esistenti

- `plugins/accounting/` - Modulo contabile
- `plugins/hr/` - Gestione risorse umane
- `plugins/inventory/` - Gestione magazzino

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

## 📚 Documentazione

| Documento | Descrizione |
|----------|-------------|
| [ARCHITECTURE.md](backend/docs/ARCHITECTURE.md) | Architettura completa |
| [API.md](backend/docs/API.md) | Documentazione API |

---

## 🚀 Docker

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

## 🔒 Sicurezza

- JWT con scadenza 15 minuti
- Refresh token per sessioni lunghe
- Password hash con Werkzeug
- Tenant isolation a livello middleware

---

## 📝 Licenza

MIT License - Vedi LICENSE per dettagli.

---

## 🤝 Contributing

1. Fork il repository
2. Crea un branch (`git checkout -b feature/nuova-feature`)
3. Commit (`git commit -am 'Aggiunge nuova feature'`)
4. Push (`git push origin feature/nuova-feature`)
5. Crea una Pull Request

---

**ERPSeed: Build your ERP. Your way.**
