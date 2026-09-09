# ERPSeed - Low-Code ERP Platform

[![CI/CD Pipeline](https://github.com/alby69/ERPSEED/actions/workflows/ci.yml/badge.svg)](https://github.com/alby69/ERPSEED/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-orange)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

ERPSeed è una piattaforma ERP open-source e modulare che permette alle organizzazioni di costruire e personalizzare il proprio sistema di gestione aziendale attraverso un approccio low-code, con architettura multi-tenant e AI integrata.

---

## 🚀 Quick Start (Docker)

```bash
git clone https://github.com/alby69/ERPSEED.git && cd ERPSEED
docker-compose up -d --build
```

Backend: `http://localhost:5000` | Swagger: `http://localhost:5000/swagger-ui` | Frontend: `http://localhost:5173`
**Login**: `admin@erpseed.org` / `admin123` (cambiala subito!)

Vedi [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) per setup manuale e comandi Docker.

---

## ✨ Features

| Area | Funzionalità |
|------|-------------|
| **Low-Code Builder** | Crea modelli, campi, relazioni, viste e dashboard dal browser |
| **Multi-Tenant** | Isolamento dati per tenant con middleware automatico (JWT/header/subdomain) |
| **AI Assistant** | Genera modelli, workflow, regole da linguaggio naturale (OpenRouter/OpenAI/Anthropic/Ollama) |
| **Workflow Automation** | Automatizza processi con step: delay, HTTP request, condition, webhook, notification |
| **Dynamic API** | CRUD automatici per ogni modello creato dal builder |
| **Module System** | Plugin CQRS per estendere funzionalità (prodotti, vendite, acquisti, resi) |
| **Anagrafiche** | Soggetti, Ruoli, Indirizzi, Contatti, Comuni (vision/archetype) |
| **Contabilità** | Prima Nota, Scadenzario, Bilancio Verifica, Registri IVA, Liquidazione IVA, Intrastat, Ri.Ba. |
| **Fattura Elettronica** | Generazione XML FatturaElettronicaPA 1.2 da fatture emesse |
| **HR** | Dipendenti, Presenze, Ferie, Buste Paga (Payroll), Formazione, Certificazioni |
| **Acquisti** | Ordini, Richieste, DDT Entrata, **Resi Acquisti** |
| **Magazzino** | Giacenze, Movimenti, Inventario, Lotti/Seriali, Ubicazioni |
| **Produzione** | BOM, Cicli, ODP, MRP |
| **CRM** | Lead, Opportunità, Contratti |
| **CashRec** | Riconciliazione Casse (CashRec) 100% client-side con report Excel |
| **Webhook System** | 7 event types, secret regeneration, test delivery |
| **Audit Logging** | Tracciamento completo delle operazioni |
| **Cache Redis** | Flask-Caching su endpoint GET frequenti (maturities, VAT, inventory) |
| **Marketplace** | Condividi e installa componenti/moduli |
| **Import/Export** | Import/Export batch di progetti (SysModel, Block, Workflow, Module) |
| **Multi-Language** | Supporto per internazionalizzazione (i18n) EN/IT |

---

## 📁 Struttura

```
erpseed/
├── backend/                          # Flask API Backend
│   ├── __init__.py                  # App factory (create_app)
│   ├── models/                      # Modelli SQLAlchemy
│   ├── core/                        # Sistema core (API, Models, Services, Middleware)
│   │   ├── api/                     #   Auth, Tenant, Modules, System, Import/Export
│   │   ├── models/                  #   Tenant, Audit, Module, Modulo
│   │   ├── services/                #   Auth, Tenant, Permission, File Processing, PDF
│   │   └── middleware/              #   TenantMiddleware, ModuleMiddleware
│   ├── modules/                     # Moduli applicativi (CQRS & Domain Logic)
│   │   ├── entities/               #   Anagrafiche: Soggetto, Ruolo, Indirizzo, Contatto, Comune, Via
│   │   ├── products/               #   Prodotti (CQRS)
│   │   ├── sales/                  #   Vendite & Preventivi (CQRS)
│   │   ├── purchases/              #   Acquisti (CQRS)
│   │   ├── purchase_returns/       #   Resi Acquisti
│   │   ├── invoicing/              #   Fatturazione (CQRS)
│   │   ├── fattura_elettronica/    #   Generazione XML FatturaElettronicaPA 1.2
│   │   ├── crm/                    #   Lead & Opportunità
│   │   ├── contracts/              #   Contratti
│   │   ├── inventory/              #   Magazzino: Giacenze, Movimenti, Causali
│   │   ├── manufacturing/          #   Produzione: BOM, Cicli, ODP
│   │   ├── mrp/                    #   Material Requirements Planning
│   │   ├── maturities/             #   Scadenzario & Partite
│   │   ├── vat/                    #   Registri IVA & Intrastat
│   │   ├── riba/                   #   Ricevute Bancarie
│   │   ├── analytics/              #   Dashboard, KPI & Reporting
│   │   ├── automation/             #   Workflow Engine & Webhooks
│   │   ├── ai/                     #   AI Assistant & Agent Gateway (AgentMesh)
│   │   ├── builder/                #   No-Code Builder
│   │   ├── dynamic_api/            #   Dynamic CRUD engine
│   │   ├── logistics/              #   Servizi Logistici e Routing
│   │   ├── projects/               #   Progetti (CQRS)
│   │   ├── users/                  #   Utenti & Ruoli (CQRS)
│   │   └── system_tools/           #   Template, Versioning, Debug
│   ├── plugins/                    # Plugin estensibili (Accounting, HR, Inventory)
│   └── seeds/                      # Database seed scripts
│
├── docs/                            # Documentazione centralizzata (13 file attivi)
│
└── frontend/                        # React 19 + Vite + Ant Design
    ├── src/
    │   ├── pages/                  # 50+ pagine applicative (Dashboard, Anagrafiche, Sales, HR, CashRec, etc.)
    │   ├── components/             # Componenti UI (archetypes, charts, core, ui, workflow)
    │   ├── context/                # AuthContext, ThemeContext, NotificationContext
    │   ├── hooks/                  # Custom hooks (useColumnManager, useResponsive, useCrudData)
    │   ├── lib/cashrec/            # Motore CashRec 100% client-side
    │   ├── theme/                  # Token di design centralizzati (tokens.js)
    │   └── locales/                # Internazionalizzazione i18n (EN/IT)
    └── docker-compose.yml          # Sviluppo con hot-reload
```

---

## 📚 Documentazione

La documentazione completa è organizzata in [docs/INDEX.md](docs/INDEX.md):

| Area | Documento | Contenuto |
|------|-----------|-----------|
| **Panoramica** | [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Architettura, pattern, struttura |
| **Guida Rapida** | [GETTING_STARTED.md](docs/GETTING_STARTED.md) | Docker, setup locale, comandi |
| **Sviluppo Backend** | [DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md) | Setup dev, convenzioni refactoring, moduli, testing |
| **Sviluppo Frontend** | [FRONTEND_GUIDE.md](docs/FRONTEND_GUIDE.md) | Guida sviluppo React/Vite/UI |
| **API** | [API.md](docs/API.md) | Riferimento endpoint completo |
| **AgentMesh AI** | [AGENTMESH.md](docs/AGENTMESH.md) | Architettura ERP distribuito agentico |
| **Manuale Utente** | [USER_MANUAL.md](docs/USER_MANUAL.md) | Uso piattaforma e builder |
| **Roadmap Qualità** | [ROADMAP.md](docs/ROADMAP.md) | Refactoring KISS/DRY e priorità |
| **Piano ERP** | [IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md) | Stato avanzamento 24 blocchi ERP |
| **Tutorial Fleet** | [TUTORIAL_FLEET.md](docs/TUTORIAL_FLEET.md) | Fleet Management via GUI & CLI |
| **Tutorial AI** | [TUTORIAL_AI_ASSISTANT.md](docs/TUTORIAL_AI_ASSISTANT.md) | Uso AI Assistant |

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

La suite di test viene eseguita automaticamente ad ogni push/PR via GitHub Actions (`.github/workflows/ci.yml`).

```bash
# Backend (166+ test unitari e di integrazione)
cd backend && pytest

# Backend (con coverage)
cd backend && pytest --cov=.

# Frontend
cd frontend && npm run test:run
```

---

**ERPSeed: Build your ERP. Your way.**
