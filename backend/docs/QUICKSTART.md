# ERPSeed - Quick Start Guide

## 🚀 Quick Start

### Opzione 1: Docker (Consigliato)

```bash
# Clona il repository
git clone https://github.com/your-repo/erpseed.git
cd erpseed

# Avvia tutti i servizi
docker-compose up -d

# Oppure usa Make
make up
```

**Accesso:**
- **Backend API**: http://localhost:5000
- **Swagger UI**: http://localhost:5000/swagger-ui
- **Frontend**: http://localhost:5173

**Comandi utili:**
```bash
make logs        # Vedi i log
make down        # Ferma i servizi
make db-reset    # Reset database
make shell-backend  # Shell nel container
```

---

### Opzione 2: Sviluppo Locale

#### 1. Prerequisiti

- Python 3.10+
- PostgreSQL 14+ (oppure usa SQLite)
- Node.js 18+ (per frontend)

#### 2. Setup Backend

```bash
cd backend

# Crea virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Installa dipendenze
pip install -r requirements.txt

# Crea file .env
cat > .env << 'EOF'
DATABASE_URL=sqlite:///data.db
JWT_SECRET_KEY=your-super-secret-key-at-least-32-characters-long
SECRET_KEY=flask-secret-key
FLASK_ENV=development
FLASK_DEBUG=1
EOF

# Inizializza il database
python -m cli.create_admin

# Avvia
python run.py
```

#### 3. Setup Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## 🛠️ Comandi CLI

### Backend Docker

```bash
# Accedi al container
docker-compose exec backend /bin/bash

# Esegui comandi CLI
docker-compose exec backend python -m cli.create_admin
docker-compose exec backend python -m seeds.initial
docker-compose exec backend python -m seeds.metadata
```

### Backend Locale

```bash
# Crea utente admin
python -m cli.create_admin

# Setup completo database
python -m cli.setup_database

# Reset database
python -m cli.reset_db

# Seed iniziale
python -m seeds.initial

# Seed geografici italiani
python -m seeds.comuni

# Seed UI components
python -m seeds.metadata

# Seed KPI
python -m seeds.kpi
```

---

## 📡 API Endpoints

### Accesso

Dopo l'avvio, visita:
- **Swagger UI**: http://localhost:5000/swagger-ui
- **Health Check**: http://localhost:5000/health

### Autenticazione

```
POST /api/v1/auth/login
Body: {"email": "admin@erpseed.org", "password": "admin123"}
```

### Endpoints Principali

| Risorsa | Endpoint |
|---------|---------|
| Progetti | `/projects` |
| Workflows | `/workflows` |
| Webhooks | `/webhooks` |
| AI Chat | `/ai/chat` |
| Dynamic CRUD | `/projects/<id>/data/<model>` |

---

## 🔧 Configurazione AI

### Variabili d'Ambiente

```bash
# OpenRouter (default - tanti modelli)
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

## 🐳 Docker Avanzato

### Build Immagine

```bash
docker-compose build
```

### Reset Completo

```bash
# Rimuovi tutto e ricomincia
make clean
make up
```

### Database PostgreSQL Locale

```bash
# Connettiti al database
docker-compose exec db psql -U postgres -d erpseed

# Backup
docker-compose exec db pg_dump -U postgres erpseed > backup.sql

# Restore
cat backup.sql | docker-compose exec -T db psql -U postgres -d erpseed
```

---

## 🧪 Testing

```bash
# Docker
docker-compose exec backend pytest

# Locale
cd backend
pytest
```

---

## 📁 Struttura Backend

```
backend/
├── models/               # Modelli Database
│   ├── user.py
│   ├── project.py
│   └── system/          # SysModel, SysField, etc.
│
├── routes/               # API Endpoints
│   ├── projects.py
│   ├── workflows.py
│   └── ...
│
├── services/             # Logica Business
│   ├── workflow_service.py
│   └── ...
│
├── cli/                  # Script CLI
│   ├── create_admin.py
│   └── setup_database.py
│
├── seeds/                # Database Seeds
│   ├── initial.py
│   ├── comuni.py
│   └── ...
│
├── core/                 # Sistema Core
│   ├── api/             # Auth, Tenant
│   ├── models/          # Tenant, Audit
│   └── middleware/     # Tenant Middleware
│
├── ai_service/           # AI CQRS
├── builder_service/      # Builder CQRS
├── products_service/     # Products CQRS
└── ...
```

---

## 🔒 Sicurezza

- JWT con scadenza 15 minuti
- Refresh token per sessioni lunghe
- Tenant isolation
- Password hash con Werkzeug

**⚠️ Cambio password admin:**
```bash
# Docker
docker-compose exec backend python -m cli.create_admin

# Locale
python -m cli.create_admin
```

---

*Ultimo aggiornamento: 2026-03-18*
