# ERPSEED - Low-Code ERP Platform

## Architettura dei Branch

```
main (Docker starter)
├── docker-compose.yml    # Avvia backend + frontend via Docker
└── README.md

erpseed/backend (sviluppo backend)
└── backend/              # Codice backend Flask

erpseed/frontend (sviluppo frontend)
└── frontend/             # Codice frontend React
```

---

## Quick Start

### 1. Clona il repository
```bash
git clone https://github.com/alby69/ERPSEED.git
cd ERPSEED
```

### 2. Avvia tutto con Docker
```bash
docker compose up
```

Questo avvia:
- **PostgreSQL** su `localhost:5432`
- **Redis** su `localhost:6380`
- **Backend** su `http://localhost:5002`
- **Frontend** su `http://localhost:5173`

---

## Workflow di Sviluppo

### Per sviluppare il BACKEND

```bash
# 1. Vai sul branch backend
git checkout erpseed/backend

# 2. Fai le tue modifiche...
# es: modifica backend/models.py

# 3. Commit delle modifiche
git add .
git commit -m "feat: nuova funzionalità"

# 4. Quando vuoi aggiornare Docker, torna su main
git checkout main
git branch -f erpseed/backend erpseed/backend
git push origin main erpseed/backend
```

### Per sviluppare il FRONTEND

```bash
# 1. Vai sul branch frontend
git checkout erpseed/frontend

# 2. Fai le tue modifiche...
# es: modifica frontend/src/pages/Dashboard.jsx

# 3. Commit delle modifiche
git add .
git commit -m "fix: risolto bug nel dashboard"

# 4. Quando vuoi aggiornare Docker, torna su main
git checkout main
git branch -f erpseed/frontend erpseed/frontend
git push origin main erpseed/frontend
```

---

## Sviluppo Locale (senza Docker)

### Backend
```bash
git checkout erpseed/backend

# Crea virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Installa dipendenze
pip install -r requirements.txt

# Crea database
flask db upgrade

# Avvia server
python run.py
```

### Frontend
```bash
git checkout erpseed/frontend

# Installa dipendenze
npm install

# Avvia dev server
npm run dev
```

---

## Struttura Backend

```
backend/
├── __init__.py          # App Flask principale
├── run.py               # Entry point
├── requirements.txt      # Dipendenze Python
├── core/                # Core modules
│   ├── models/          # Modelli database
│   ├── services/        # Servizi business
│   └── api/             # API endpoints
├── builder/             # Builder ERP
├── ai/                  # AI Assistant
└── plugins/             # Plugin system
```

---

## Struttura Frontend

```
frontend/
├── src/
│   ├── pages/           # Pagine applicazione
│   ├── components/      # Componenti React
│   ├── hooks/           # Custom hooks
│   └── context/         # React contexts
├── package.json
└── vite.config.js
```

---

## Variabili d'Ambiente

```env
# Backend
DATABASE_URL=postgresql://postgres:password@localhost:5432/flaskerp
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# Frontend
VITE_API_URL=http://localhost:5002
```

---

## Link Utili

- **Backend API**: http://localhost:5002
- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:5002/api/docs

---

## Comandi Docker

```bash
# Avvia tutti i servizi
docker compose up

# Avvia in background
docker compose up -d

# Ferma tutti i servizi
docker compose down

# Ricostruisci container
docker compose build --no-cache
docker compose up

# View logs
docker compose logs -f backend
docker compose logs -f frontend
```

---

## Domande?

Per supporto, apri una issue su GitHub: https://github.com/alby69/ERPSEED/issues
