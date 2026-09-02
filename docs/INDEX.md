# Indice Documentazione ERPSEED

> **Entry point unico** per tutta la documentazione del progetto ERPSEED.
>
> **Policy Linguistica**: La documentazione tecnica e di architettura è in italiano (IT). Il manuale utente ([USER_MANUAL.md](USER_MANUAL.md)) è in inglese (EN) per supportare gli utenti aziendali internazionali, in linea con il supporto i18n (EN/IT) della piattaforma.

---

## 📋 Panoramica e Architettura

| Documento | Contenuto | Target |
|-----------|-----------|--------|
| [README.md](../README.md) | Presentazione progetto, features, stack, avvio | Tutti |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Architettura di sistema, pattern (CQRS, Multi-Tenant), struttura repository | Sviluppatori |
| [ROADMAP.md](ROADMAP.md) | Roadmap di qualità del codice, refactoring KISS/DRY (Fasi 0-4) e priorità tecniche | Team |
| [BRANCH_STRATEGY.md](BRANCH_STRATEGY.md) | Strategia dei branch Git e flusso di lavoro monorepo | Sviluppatori |

## 🚀 Guide Operative

| Documento | Contenuto | Target |
|-----------|-----------|--------|
| [GETTING_STARTED.md](GETTING_STARTED.md) | Guida all'avvio rapido: Docker, setup locale (backend/frontend) e risoluzione problemi | Tutti |
| [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) | Guida per sviluppatori backend: creazione moduli, convenzioni di refactoring, testing, debug | Sviluppatori BE |
| [FRONTEND_GUIDE.md](FRONTEND_GUIDE.md) | Guida per sviluppatori frontend: React, Vite, Ant Design, componenti e state management | Sviluppatori FE |
| [USER_MANUAL.md](USER_MANUAL.md) | Manuale utente: concetti chiave, uso delle applicazioni, builder visivo | Utenti finali |

## 📡 Riferimento API e Integrazione Agentica

| Documento | Contenuto | Target |
|-----------|-----------|--------|
| [API.md](API.md) | Riferimento completo degli endpoint REST, autenticazione JWT, paginazione, versionamento e [Capabilities AgentMesh](API.md#capabilities-agentmesh-apiv1aicapabilities) | Sviluppatori / Integratori |
| [AGENTMESH.md](AGENTMESH.md) | Architettura ERP distribuito agentico, integrazione AgentMesh e manifesto `/capabilities` | Sviluppatori AI / System Architects |

## 📝 Changelog e Tracciamento Modifiche

| Documento | Contenuto | Target |
|-----------|-----------|--------|
| [CHANGELOG.md](../CHANGELOG.md) | Changelog di prodotto e delle release dell'applicazione | Tutti |
| [DOC_LOG.md](../DOC_LOG.md) | Registro delle modifiche e refactoring della documentazione | Maintainers / Team |

## 🧪 Tutorial

| Documento | Contenuto | Target |
|-----------|-----------|--------|
| [TUTORIAL_FLEET.md](TUTORIAL_FLEET.md) | Tutorial completo per creare un progetto di Gestione Flotta (via GUI e via CLI/curl) | Tutti |
| [TUTORIAL_AI_ASSISTANT.md](TUTORIAL_AI_ASSISTANT.md) | Guida all'uso dell'AI Assistant: configurazione LLM, prompt e risoluzione problemi | Tutti |

## 📐 Piani di Implementazione

| Documento | Contenuto | Target |
|-----------|-----------|--------|
| [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) | Piano e stato di avanzamento dei 24 blocchi funzionali ERP (anagrafiche, acquisti, vendite, magazzino, contabilità, etc.) | Team / Stakeholder |

---

## Mappa delle Dipendenze tra Documenti

```
README.md (root)
└── docs/INDEX.md (Entry Point Unico)
    ├── Panoramica & Architettura
    │   ├── ARCHITECTURE.md
    │   ├── ROADMAP.md
    │   └── BRANCH_STRATEGY.md
    ├── Guide Operative
    │   ├── GETTING_STARTED.md
    │   ├── DEVELOPER_GUIDE.md
    │   ├── FRONTEND_GUIDE.md
    │   └── USER_MANUAL.md
    ├── API & AgentMesh
    │   ├── API.md
    │   └── AGENTMESH.md
    ├── Tutorial
    │   ├── TUTORIAL_FLEET.md (GUI + CLI)
    │   └── TUTORIAL_AI_ASSISTANT.md
    └── Piani Esecutivi
        └── IMPLEMENTATION_PLAN.md
```

## Come Estendere la Documentazione

Per aggiungere un nuovo documento:
1. Posizionarlo nella directory `docs/`.
2. Aggiungere una riga nella tabella della sezione appropriata in questo `INDEX.md`.
3. Se applicabile, aggiornare il sommario nel `README.md` principale del progetto.
