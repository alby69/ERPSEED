# ERPSeed - Low-Code ERP Platform

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-orange)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

ERPSeed è una piattaforma ERP open-source e modulare che permette alle organizzazioni di costruire e personalizzare il proprio sistema di gestione aziendale attraverso un approccio low-code.

---

## 🚀 Quick Start

Vedi [backend/docs/QUICKSTART.md](backend/docs/QUICKSTART.md) per la guida dettagliata.

```bash
# Clona e entra
git clone https://github.com/your-repo/erpseed.git
cd erpseed

# Setup Backend
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# Crea .env con JWT_SECRET_KEY, poi:
python run.py

# Setup Frontend (in un altro terminale)
cd frontend
npm install
npm run dev
```

---

## ✨ Features

- **Low-Code Builder** - Crea entità, campi, relazioni dal browser
- **Multi-Tenant** - Progetti isolati in un'unica installazione
- **AI Assistant** - Genera configurazioni da linguaggio naturale
- **Workflow Automation** - Automatizza processi aziendali
- **Plugin System** - Estendi con moduli personalizzati
- **Marketplace** - Condividi e installa componenti

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
│   ├── core/                 # Sistema Core
│   ├── ai_service/           # AI CQRS
│   ├── builder_service/      # Builder CQRS
│   └── docs/                 # Documentazione
│
└── frontend/                  # React Frontend
```

---

## 📚 Documentazione

| Documento | Descrizione |
|-----------|-------------|
| [backend/docs/QUICKSTART.md](backend/docs/QUICKSTART.md) | Guida rapida |
| [backend/docs/ARCHITECTURE.md](backend/docs/ARCHITECTURE.md) | Architettura |
| [backend/docs/BRANCH_STRATEGY.md](backend/docs/BRANCH_STRATEGY.md) | Strategia Branch |

## 🧪 Testing

Il progetto include una suite di test completa per backend e frontend.

```bash
# Esegui tutti i test (richiede Makefile)
make test-all

# Test Backend
cd backend
pytest

# Test Frontend
cd frontend
npm test
```

---

## 🔧 Stack Tecnologico

- **Backend**: Flask 3.x + SQLAlchemy
- **API**: Flask-Smorest (OpenAPI 3.0)
- **Auth**: JWT
- **Frontend**: React + Ant Design
- **AI**: OpenRouter, OpenAI, Anthropic, Ollama

---

## 🤝 Contributing

1. Fork il repository
2. Crea un branch (`git checkout -b feature/nuova-feature`)
3. Commit (`git commit -am 'Aggiunge nuova feature'`)
4. Push (`git push origin feature/nuova-feature`)
5. Crea una Pull Request

---

## 📝 Licenza

MIT License - Vedi LICENSE per dettagli.

---

**ERPSeed: Build your ERP. Your way.**
