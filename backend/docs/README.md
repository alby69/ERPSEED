# ERPSEED Backend Documentation

Benvenuto nella documentazione del backend ERPSEED.

## 📚 Documentazione

| Documento | Descrizione |
|-----------|-------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Architettura del sistema, pattern, struttura |
| [API.md](API.md) | Endpoint API, autenticazione, formato risposte |
| [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) | Guida per sviluppatori, setup, testing |
| [QUICKSTART.md](QUICKSTART.md) | Guida rapida Docker |
| [USER_MANUAL.md](USER_MANUAL.md) | Manuale utente |
| [ROADMAP.md](ROADMAP.md) | Roadmap e stato avanzamento |
| [TUTORIAL_AI_ASSISTANT.md](TUTORIAL_AI_ASSISTANT.md) | Tutorial AI Assistant |
| [TUTORIAL_FLEET.md](TUTORIAL_FLEET.md) | Tutorial Fleet Management |
| [TUTORIAL_FLEET_CLI.md](TUTORIAL_FLEET_CLI.md) | Tutorial Fleet CLI |
| [BRANCH_STRATEGY.md](BRANCH_STRATEGY.md) | Strategia branch Git |

## 🚀 Quick Start (Docker)

```bash
docker-compose up -d --build
```

Backend: `http://localhost:5000` | Swagger: `http://localhost:5000/swagger-ui` | Frontend: `http://localhost:5173`
**Login**: `admin@erpseed.org` / `admin123`

## 🏗️ Panoramica

ERPSEED è un sistema ERP modulare multi-tenant con:

- **Builder No-Code**: Crea modelli dati, viste, dashboard via UI
- **Multi-Tenancy**: Isolamento per tenant (header `X-Tenant-ID` / JWT / subdomain)
- **Dynamic API**: CRUD automatici per ogni modello creato
- **CQRS Modules**: Prodotti, Vendite, Acquisti con pattern Command/Query
- **Anagrafiche**: Soggetti, Ruoli, Indirizzi, Contatti, Comuni
- **Workflow Engine**: Automazione processi con step condizionali
- **Webhook System**: Integrazioni event-driven
- **AI Assistant**: Generazione configurazioni da linguaggio naturale
- **Audit Logging**: Tracciamento completo

## 📁 Struttura Progetto

```
backend/
├── core/               # Auth, Tenant, Permessi, Middleware
├── modules/            # Moduli applicativi
│   ├── entities/       #   Anagrafiche (Soggetto, Ruolo, etc.)
│   ├── products/       #   Prodotti (CQRS)
│   ├── sales/          #   Vendite (CQRS)
│   ├── purchases/      #   Acquisti (CQRS)
│   ├── analytics/      #   Dashboard e KPI
│   ├── automation/     #   Workflow e Webhook
│   ├── ai/             #   AI Assistant
│   ├── builder/        #   No-Code Builder
│   ├── dynamic_api/    #   Dynamic CRUD engine
│   ├── gdo/            #   GDO Reconciliation
│   ├── projects/       #   Progetti
│   ├── users/          #   Utenti
│   └── system_tools/   #   Template, Versioning, Debug
├── seeds/              # Script di inizializzazione DB
└── docs/               # Documentazione
```

## 🔗 Link Utili

- [Docker Setup](../docker-compose.yml)
- [Frontend Repository](../frontend/)
- [Issue Tracker](https://github.com/alby69/ERPSEED/issues)

---

Ultimo aggiornamento: 2026-06-08
