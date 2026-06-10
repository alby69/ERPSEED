# ERPSeed - Low-Code ERP Platform

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-orange)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

ERPSeed è una piattaforma ERP open-source e modulare che permette alle organizzazioni di costruire e personalizzare il proprio sistema di gestione aziendale attraverso un approccio low-code, con architettura multi-tenant e AI integrata.

---

## 🚀 Quick Start (Docker)

```bash
git clone https://github.com/your-repo/erpseed.git && cd erpseed
docker-compose up -d --build
```

Backend: `http://localhost:5000` | Swagger: `http://localhost:5000/swagger-ui` | Frontend: `http://localhost:5173`
**Login**: `admin@erpseed.org` / `admin123` (cambiala subito!)

Vedi [backend/docs/QUICKSTART.md](backend/docs/QUICKSTART.md) per setup manuale e comandi Docker.

---

## ✨ Features

| Area | Funzionalità |
|------|-------------|
| **Low-Code Builder** | Crea modelli, campi, relazioni, viste e dashboard dal browser |
| **Multi-Tenant** | Isolamento dati per tenant con middleware automatico (JWT/header/subdomain) |
| **AI Assistant** | Genera modelli, workflow, regole da linguaggio naturale (OpenRouter/OpenAI/Anthropic/Ollama) |
| **Workflow Automation** | Automatizza processi con step: delay, HTTP request, condition, webhook, notification |
| **Dynamic API** | CRUD automatici per ogni modello creato dal builder |
| **Module System** | Plugin CQRS per estendere funzionalità (prodotti, vendite, acquisti) |
| **Anagrafiche** | Soggetti, Ruoli, Indirizzi, Contatti, Comuni (vision/archetype) |
| **GDO Reconciliation** | Strumento di riconciliazione GDO con report Excel |
| **Webhook System** | 7 event types, secret regeneration, test delivery |
| **Audit Logging** | Tracciamento completo delle operazioni |
| **Marketplace** | Condividi e installa componenti/moduli |

---

## 📁 Struttura

```
erpseed/
├── backend/                          # Flask API Backend
│   ├── __init__.py                  # App factory (create_app)
│   ├── models/                      # Modelli SQLAlchemy
│   ├── core/                        # Sistema core
│   │   ├── api/                     #   Auth, Tenant, Modules, System
│   │   ├── models/                  #   Tenant, Audit, Module
│   │   ├── services/                #   Auth, Tenant, Permission
│   │   ├── middleware/              #   TenantMiddleware, ModuleMiddleware
│   │   └── decorators/              #   @tenant_required, @admin_required
│   ├── modules/                     # Moduli applicativi (CQRS)
│   │   ├── entities/               #   Anagrafiche: Soggetto, Ruolo, Indirizzo (comune_id/via_id), Contatto, Comune, Via (cache strade), vie_routes.py (Nominatim)
│   │   ├── products/               #   Prodotti (CQRS)
│   │   ├── sales/                  #   Vendite (CQRS)
│   │   ├── purchases/              #   Acquisti (CQRS)
│   │   ├── analytics/              #   Dashboard e KPI
│   │   ├── automation/             #   Workflow e Webhook
│   │   ├── ai/                     #   AI Assistant
│   │   ├── builder/                #   No-Code Builder
│   │   ├── dynamic_api/            #   Dynamic CRUD engine
│   │   ├── gdo/                    #   GDO Reconciliation
│   │   ├── projects/               #   Progetti
│   │   ├── users/                  #   Utenti
│   │   └── system_tools/           #   Template, Versioning, Debug
│   ├── seeds/                      # Database seed scripts
│   └── docs/                       # Documentazione
│
└── frontend/                        # React + Vite + Ant Design
    ├── src/
    │   ├── pages/                  # 44 pagine (Dashboard, Anagrafiche, Prodotti, Sales, etc.)
    │   ├── components/             # 43 componenti riutilizzabili
    │   └── context/                # AuthContext, ThemeProvider
    └── docker-compose.yml          # Sviluppo con hot-reload
```

---

## 📚 Documentazione

La documentazione completa è organizzata in [backend/docs/INDEX.md](backend/docs/INDEX.md):

| Area | Documento | Contenuto |
|------|-----------|-----------|
| **Panoramica** | [ARCHITECTURE.md](backend/docs/ARCHITECTURE.md) | Architettura, pattern, struttura |
| **Guida Rapida** | [QUICKSTART.md](backend/docs/QUICKSTART.md) | Docker, setup, comandi |
| **Sviluppo** | [DEVELOPER_GUIDE.md](backend/docs/DEVELOPER_GUIDE.md) | Setup dev, creazione moduli, testing |
| **API** | [API.md](backend/docs/API.md) | Riferimento endpoint completo |
| **Manuale Utente** | [USER_MANUAL.md](backend/docs/USER_MANUAL.md) | Uso piattaforma |
| **Roadmap** | [ROADMAP.md](backend/docs/ROADMAP.md) | Stato avanzamento e priorità |
| **Piano ERP** | [IMPLEMENTATION_PLAN.md](backend/docs/IMPLEMENTATION_PLAN.md) | Piano blocchi ERP |
| **Tutorial AI** | [TUTORIAL_AI_ASSISTANT.md](backend/docs/TUTORIAL_AI_ASSISTANT.md) | Uso AI Assistant |
| **Tutorial Fleet** | [TUTORIAL_FLEET.md](backend/docs/TUTORIAL_FLEET.md) | Fleet Management via GUI |
| **Frontend** | [FRONTEND_GUIDE.md](frontend/docs/FRONTEND_GUIDE.md) | Guida sviluppo frontend |
| **Branch Git** | [BRANCH_STRATEGY.md](backend/docs/BRANCH_STRATEGY.md) | Strategia branch |

---

## 🔧 Stack Tecnologico

| Componente | Tecnologia |
|------------|-----------|
| Backend | Flask 3.x + Python 3.12 |
| ORM | SQLAlchemy + Flask-SQLAlchemy |
| API | Flask-Smorest (OpenAPI 3.0) |
| Auth | Flask-JWT-Extended (JWT + refresh token) |
| Serialization | Marshmallow |
| Database | PostgreSQL 15 (dev: SQLite) |
| Cache | Redis 7 |
| Realtime | Flask-SocketIO + eventlet |
| Frontend | React 19 + Vite + Ant Design |
| AI | OpenRouter, OpenAI, Anthropic, Ollama |
| Infrastruttura | Docker Compose, Gunicorn |

---

## 🧪 Testing

```bash
# Backend
cd backend && pytest

# Frontend
cd frontend && npm test
```

---

**ERPSeed: Build your ERP. Your way.**
