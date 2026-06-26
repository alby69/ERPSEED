# ERPSeed - Quick Start Guide

## 🚀 Quick Start con Docker

### 1. Clona il Repository

```bash
git clone https://github.com/your-repo/erpseed.git
cd erpseed
```

### 2. Avvia con Docker Compose

```bash
# Costruisce le immagini e avvia tutti i servizi
docker-compose up -d --build

# Oppure usa Make (se installato)
make up
```

### 3. Attendi l'Inizializzazione

Il container `init-db` eseguirà automaticamente:
- Installazione dipendenze
- Creazione utente admin (`admin@erpseed.org`)
- Seed del database

### 4. Accedi all'Applicazione

| Servizio | URL |
|----------|-----|
| **Backend API** | http://localhost:5000 |
| **Swagger UI** | http://localhost:5000/swagger-ui |
| **Frontend** | http://localhost:5173 |

### 5. Login

- **Email**: `admin@erpseed.org`
- **Password**: `admin123` (cambiala subito!)

---

## 🛠️ Comandi Docker

### Gestione Servizi

```bash
# Avvia tutti i servizi
docker-compose up -d

# Ferma tutti i servizi
docker-compose down

# Riavvia
docker-compose restart

# Vedi i log
docker-compose logs -f

# Vedi solo i log del backend
docker-compose logs -f backend
```

### Makefile

```bash
make up         # Avvia (equivale a docker-compose up -d)
make down       # Ferma
make build      # Ricostruisce le immagini
make logs       # Vedi i log
make restart    # Riavvia
make ps         # Status servizi
make init       # Reinizializza il database
make db-reset   # Reset completo database
```

### Accesso ai Container

```bash
# Shell nel backend
docker-compose exec backend /bin/bash

# Shell nel database PostgreSQL
docker-compose exec db psql -U postgres -d erpseed

# Database Redis
docker-compose exec redis redis-cli
```

### Database

```bash
# Backup del database
docker-compose exec db pg_dump -U postgres erpseed > backup_$(date +%Y%m%d).sql

# Restore del database
cat backup.sql | docker-compose exec -T db psql -U postgres -d erpseed

# Reset completo (cancella tutto!)
docker-compose down -v
docker-compose up -d --build
```

---

## 🔧 Configurazione

### Variabili d'Ambiente

Il `docker-compose.yml` usa queste variabili di default:

```yaml
DATABASE_URL: postgresql://postgres:password@db:5432/erpseed
JWT_SECRET_KEY: a-very-secure-and-long-jwt-secret-key-for-dev-env
REDIS_URL: redis://redis:6379
FLASK_ENV: development
FLASK_DEBUG: 1
```

Per modifiche, crea un file `.env` nella root:

```bash
cat > .env << 'EOF'
POSTGRES_PASSWORD=my-secret-password
JWT_SECRET_KEY=my-super-secret-jwt-key-at-least-32-chars
EOF
```

### Configurazione AI

Per abilitare l'AI Assistant, aggiungi al `.env`:

```bash
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-...
```

### Porte

| Servizio | Porta Interna | Porta Esterna |
|----------|---------------|---------------|
| Backend | 5000 | 5000 |
| Frontend | 5173 | 5173 |
| PostgreSQL | 5432 | 5432 |
| Redis | 6379 | 6380 |

---

## 📡 API Endpoints

### Autenticazione

```bash
# Login
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@erpseed.org", "password": "admin123"}'
```

### Endpoints Principali

| Risorsa | Endpoint | Descrizione |
|---------|----------|-------------|
| Progetti | `/projects` | CRUD progetti |
| Workflows | `/workflows` | Gestione workflow |
| Webhooks | `/webhooks` | Gestione webhook |
| AI Chat | `/ai/chat` | Chat con AI |
| Dynamic CRUD | `/projects/<id>/data/<model>` | CRUD dinamico |

---

## 🧪 Testing

```bash
# Esegui i test nel container
docker-compose exec backend pytest

# Con coverage
docker-compose exec backend pytest --cov=. --cov-report=html
```

---

## 📁 Struttura

```
erpseed/
├── backend/                    # API Backend
│   ├── models/               # Modelli Database
│   ├── routes/               # API Endpoints
│   ├── services/             # Logica Business
│   ├── cli/                 # Script CLI
│   ├── seeds/                # Database Seeds
│   ├── ai_service/           # AI CQRS
│   ├── builder_service/      # Builder CQRS
│   ├── docs/                 # Documentazione
│   │   ├── ARCHITECTURE.md
│   │   └── QUICKSTART.md
│   ├── Dockerfile            # Container backend
│   └── requirements.txt
│
├── frontend/                  # React Frontend
├── docker-compose.yml        # Orchestrazione servizi
└── Makefile                 # Comandi utili
```

---

## 🔒 Sicurezza

**⚠️ Cambio password admin:**
```bash
docker-compose exec backend python -m cli.create_admin
```

---

## 🐛 Risoluzione Problemi

### Container non parte

```bash
# Verifica i log
docker-compose logs

# Ricostruisci da zero
docker-compose down -v --rmi local
docker-compose up -d --build
```

### Database connection error

```bash
# Verifica che PostgreSQL sia pronto
docker-compose ps db

# Attendi healthcheck
docker-compose up -d db
docker-compose wait db
docker-compose up -d
```

### Permessi cartelle

```bash
# Su Linux/Mac
sudo chown -R $USER:$USER backend frontend
```

---

*Ultimo aggiornamento: 2026-03-18*
