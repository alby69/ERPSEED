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
| [ROADMAP.md](ROADMAP.md) | Roadmap Q3-Q4 2026: UX/UI Excellence, Command Palette, Data Model Enhancements (100% Completata) | Team |

## 🚀 Guide Operative

| Documento | Contenuto | Target |
|-----------|-----------|--------|
| [GETTING_STARTED.md](GETTING_STARTED.md) | Guida all'avvio rapido: Docker, setup locale (backend/frontend) e risoluzione problemi | Tutti |
| [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) | Guida per sviluppatori backend: workflow branch Git, creazione moduli, refactoring, testing, debug | Sviluppatori BE |
| [FRONTEND_GUIDE.md](FRONTEND_GUIDE.md) | Guida per sviluppatori frontend: React, Vite, Ant Design, Command Palette, componenti e state management | Sviluppatori FE |
| [USER_MANUAL.md](USER_MANUAL.md) | Manuale utente: concetti chiave, uso delle applicazioni, builder visivo | Utenti finali |

## 📡 Riferimento API e Integrazione Agentica

| Documento | Contenuto | Target |
|-----------|-----------|--------|
| [API.md](API.md) | Riferimento completo degli endpoint REST, autenticazione JWT, paginazione, versionamento e Capabilities AgentMesh | Sviluppatori / Integratori |
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

## 📐 Piani di Implementazione & Archivio

| Documento | Contenuto | Target |
|-----------|-----------|--------|
| [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) | Piano e stato di avanzamento dei 24 blocchi funzionali ERP | Team / Stakeholder |
| [ARCHIVE/COMPLETED_PHASES.md](ARCHIVE/COMPLETED_PHASES.md) | Archivio storico delle fasi di sviluppo completate (Fasi 0-5) | Maintainers |

---

## Mappa delle Dipendenze tra Documenti

```
README.md (root)
└── docs/INDEX.md (Entry Point Unico)
    ├── Panoramica & Architettura
    │   ├── ARCHITECTURE.md
    │   └── ROADMAP.md
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
    └── Piani Esecutivi & Archivio
        ├── IMPLEMENTATION_PLAN.md
        └── ARCHIVE/COMPLETED_PHASES.md
```

---

> Ultimo aggiornamento: 10 Settembre 2026 | [Torna all'Indice](INDEX.md)
