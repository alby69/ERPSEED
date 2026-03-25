# ERPSeed - Quick Start Guide

## 🚀 Quick Start

### 1. Clona il Repository

```bash
git clone https://github.com/alby69/ERPSEED.git
cd ERPSEED
```

### 2. Setup Backend

```bash
cd backend

# Crea virtual environment
python -m venv venv
source venv/bin/activate

# Installa dipendenze
pip install -r requirements.txt

# Crea file .env
cat > .env << 'EOF'
DATABASE_URL=sqlite:///data.db
JWT_SECRET_KEY=your-super-secret-key-at-least-32-chars-long
SECRET_KEY=flask-secret-key
FLASK_ENV=development
EOF

# Avvia il server
python run.py
```

### 3. Accedi all'Applicazione

| Servizio | URL |
|----------|-----|
| **Backend API** | http://localhost:5000 |
| **Swagger UI** | http://localhost:5000/swagger-ui |

---

## 🔧 Configurazione

### Variabili d'Ambiente

```bash
# Database
DATABASE_URL=sqlite:///data.db
# oppure PostgreSQL
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# JWT (obbligatorio, min 32 caratteri)
JWT_SECRET_KEY=your-super-secret-key-at-least-32-chars-long

# Flask
FLASK_ENV=development
FLASK_DEBUG=1

# AI (opzionale)
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-...
```

---

## 📡 API Endpoints

### Endpoints CQRS

| Risorsa | Endpoint | Descrizione |
|---------|----------|-------------|
| Soggetti | `/api/entities/soggetti` | Clienti/Fornitori |
| Ruoli | `/api/entities/ruoli` | Ruoli soggetti |
| Indirizzi | `/api/entities/indirizzi` | Indirizzi |
| Contatti | `/api/entities/contatti` | Contatti |
| Marketplace | `/api/marketplace` | Marketplace blocks |
| Geographic | `/api/geographic` | Dati geografici Italia |
| AI Chat | `/api/ai/chat` | Chat con AI |

### Headers Necessari

```bash
# Per tutte le richieste (tranne autenticazione)
curl -X GET http://localhost:5000/api/entities/soggetti \
  -H "Authorization: Bearer <jwt_token>" \
  -H "X-Tenant-ID: 1"
```

---

## 📁 Struttura Backend

```
backend/
├── domain/                  # Modelli puri (dataclass)
│   ├── entities/          # Soggetto, Ruolo
│   └── marketplace/       # Category, BlockListing
│
├── application/           # CQRS Commands/Handlers
│   ├── entities/
│   └── marketplace/
│
├── infrastructure/        # SQLAlchemy Models + Repositories
│   ├── entities/
│   ├── marketplace/
│   └── builder/
│
├── endpoints/            # REST API Endpoints
│   ├── entities.py       # Soggetto, Ruolo, Indirizzo, Contatto
│   ├── marketplace.py
│   ├── geographic.py     # Regioni, Province, Comuni
│   ├── products.py
│   ├── sales.py
│   └── purchases.py
│
├── core/                 # Sistema Core
│   ├── api/             # Auth, Tenant, Modules
│   └── models/         # BaseModel, Tenant
│
├── shared/              # Utilities condivise
│   ├── events/          # EventBus
│   ├── decorators/      # @tenant_required
│   └── utils/          # Helper functions
│
├── plugins/             # Plugin System
│   ├── inventory/       # Gestione magazzino
│   ├── accounting/      # Contabilità
│   └── hr/             # Risorse Umane
│
└── tests/              # Test Suite
```

---

## 🧪 Testing

```bash
# Esegui tutti i test
pytest

# Test specifico
pytest tests/test_entities_cqrs.py -v

# Con coverage
pytest --cov=backend --cov-report=html
```

---

## 🐛 Risoluzione Problemi

### ModuleNotFoundError

```bash
# Verifica PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python run.py
```

### Database locked

```bash
# Riavvia o usa PostgreSQL
rm data.db
flask db upgrade
```

---

*Ultimo aggiornamento: 2026-03-19*
