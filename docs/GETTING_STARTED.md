# ERPSeed - Getting Started Guide

Guida all'installazione e avvio rapido di ERPSeed, sia con Docker che in ambiente locale.

---

## 🚀 Quick Start con Docker

### 1. Clona il Repository

```bash
git clone https://github.com/alby69/ERPSEED.git
cd ERPSEED
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

## 🛠️ Setup Locale (senza Docker)

### Prerequisiti

- Python 3.11+
- Node.js 18+ (per il frontend)
- PostgreSQL 15+ (opzionale, SQLite di default per sviluppo)
- Git

### 1. Setup Backend

```bash
cd backend

# Crea virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Installa dipendenze
pip install -r requirements.txt
```

### 2. Configurazione Ambiente

Crea un file `.env` nella cartella `backend/`:

```bash
cat > .env << 'EOF'
DATABASE_URL=sqlite:///data.db
JWT_SECRET_KEY=your-super-secret-key-at-least-32-chars-long
SECRET_KEY=flask-secret-key-change-in-production
FLASK_ENV=development
FLASK_DEBUG=1
EOF
```

### 3. Inizializzazione Database

```bash
# Crea tabelle e applica migrazioni
flask db init
flask db migrate
flask db upgrade

# Seed dati iniziali
python -m cli.create_default_project
```

### 4. Avvio Server Backend

```bash
python run.py
# Oppure: flask run --host=0.0.0.0 --port=5000
```

### 5. Setup e Avvio Frontend

In un nuovo terminale:

```bash
cd frontend
npm install
npm run dev
```

L'applicazione sarà accessibile su `http://localhost:5173`.

---

## ⚙️ Configurazione Avanzata

### Variabili d'Ambiente Principali

| Variabile | Valore di Default | Descrizione |
|-----------|-------------------|-------------|
| `DATABASE_URL` | `sqlite:///data.db` | Stringa di connessione database |
| `JWT_SECRET_KEY` | - | Chiave per firma token JWT (min. 32 caratteri) |
| `REDIS_URL` | `redis://redis:6379` | Server Redis per la cache |
| `FLASK_ENV` | `development` | Ambiente Flask (`development` / `production`) |
| `FLASK_DEBUG` | `1` | Modalità debug attivi/disattivi |
| `VITE_API_URL` | `http://localhost:5000` | (Frontend) URL endpoint base per API backend |

### Configurazione AI Assistant

Per abilitare l'AI Assistant, aggiungi al file `.env`:

```bash
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-...
```

### Porte Utilizzate

| Servizio | Porta Interna | Porta Esterna |
|----------|---------------|---------------|
| Backend | 5000 | 5000 |
| Frontend | 5173 | 5173 |
| PostgreSQL | 5432 | 5432 |
| Redis | 6379 | 6380 |

---

## 🐳 Comandi Utili Docker e Makefile

### Gestione Servizi Docker

```bash
docker-compose up -d        # Avvia tutti i servizi
docker-compose down      # Ferma tutti i servizi
docker-compose restart   # Riavvia tutti i servizi
docker-compose logs -f   # Visualizza i log
```

### Makefile Shortcut

```bash
make up         # Avvia (equivale a docker-compose up -d)
make down       # Ferma
make build      # Ricostruisce le immagini
make logs       # Visualizza log
make restart    # Riavvia
make ps         # Status dei servizi
make init       # Reinizializza il database
make db-reset   # Reset completo del database
```

### Accesso ai Container

```bash
# Shell nel container backend
docker-compose exec backend /bin/bash

# Shell PostgreSQL
docker-compose exec db psql -U postgres -d erpseed

# CLI Redis
docker-compose exec redis redis-cli
```

---

## 📡 Riferimento Struttura e API

Per la struttura dettagliata del progetto vedi [ARCHITECTURE.md](ARCHITECTURE.md#struttura-del-progetto).

### First Request (Test API)

```bash
# Login via API
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@erpseed.org", "password": "admin123"}'
```

---

## 🔒 Sicurezza

**⚠️ Cambio password admin consigliato dopo il primo avvio:**
```bash
docker-compose exec backend python -m cli.create_admin
```

---

## 🐛 Risoluzione Problemi

### Container non parte

```bash
# Verifica log di errore
docker-compose logs backend

# Ricostruisci le immagini senza cache
docker-compose down -v --rmi local
docker-compose up -d --build
```

### Database connection error

```bash
# Verifica che il container PostgreSQL sia attivo
docker-compose ps db
```

### Permessi cartelle (Linux/Mac)

```bash
sudo chown -R $USER:$USER backend frontend
```

---

*Per la cronologia completa delle modifiche di questo documento, consulta la cronologia Git del repository.*
