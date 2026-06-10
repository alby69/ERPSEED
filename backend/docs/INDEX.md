# Indice Documentazione ERPSEED

> **Entry point unico** per tutta la documentazione del progetto.
> Ultimo aggiornamento: 2026-06-10

---

## 📋 Panoramica del Progetto

| Documento | Contenuto | Target |
|-----------|-----------|--------|
| [README.md](../../README.md) | Presentazione progetto, features, stack, quick start | Tutti |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Architettura sistema, pattern, struttura directory | Sviluppatori |
| [ROADMAP.md](ROADMAP.md) | Roadmap qualità, stato avanzamento, PR guidelines | Team |
| [BRANCH_STRATEGY.md](BRANCH_STRATEGY.md) | Strategia branch Git, flusso di lavoro | Sviluppatori |

## 🚀 Guide Operative

| Documento | Contenuto | Target |
|-----------|-----------|--------|
| [QUICKSTART.md](QUICKSTART.md) | Avvio rapido Docker, comandi, configurazione | Tutti |
| [USER_MANUAL.md](USER_MANUAL.md) | Manuale utente: concetti, uso piattaforma | Utenti finali |
| [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) | Setup dev, creazione moduli, pattern, testing | Sviluppatori |
| [FRONTEND_GUIDE.md](../../frontend/docs/FRONTEND_GUIDE.md) | Guida frontend: stack, struttura, best practices | Sviluppatori FE |

## 📡 Riferimento API

| Documento | Contenuto |
|-----------|-----------|
| [API.md](API.md) | Endpoint completi, autenticazione, codici errore (1029 righe) |

## 🧪 Tutorial

| Documento | Contenuto |
|-----------|-----------|
| [TUTORIAL_AI_ASSISTANT.md](TUTORIAL_AI_ASSISTANT.md) | Uso AI Assistant: configurazione LLM, comandi, troubleshooting |
| [TUTORIAL_FLEET.md](TUTORIAL_FLEET.md) | Fleet Management via GUI Builder |
| [TUTORIAL_FLEET_CLI.md](TUTORIAL_FLEET_CLI.md) | Fleet Management via CLI/curl |
| [tutorials/indirizzi.md](../tutorials/indirizzi.md) | Gestione Indirizzi, ricerca Vie con Nominatim, geocodifica |

## 📐 Piani e Analisi

| Documento | Contenuto |
|-----------|-----------|
| [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) | Piano completo blocchi ERP: atomi, aree, fasi, template CQRS |
| [archive/ERP_BLOCKS_ANALYSIS.md](archive/ERP_BLOCKS_ANALYSIS.md) | Analisi copertura ERP originale (storico) |

## 🗂️ Archivio

| Documento | Contenuto |
|-----------|-----------|
| [archive/QUESTIONS.md](archive/QUESTIONS.md) | Domande aperte risolte (storico) |
| [archive/ROADMAP_ANALYSIS.md](archive/ROADMAP_ANALYSIS.md) | Analisi roadmap superata (storico) |

---

## Mappa delle Dipendenze tra Documenti

```
README.md (root)
└── backend/docs/INDEX.md ← PARTI DA QUI
    ├── overview/
    │   ├── ARCHITECTURE.md  (pattern + struttura)
    │   ├── ROADMAP.md       (stato + priorità)
    │   └── BRANCH_STRATEGY.md
    ├── guides/
    │   ├── QUICKSTART.md    (se vuoi partire subito)
    │   ├── USER_MANUAL.md   (se sei un utente)
    │   ├── DEVELOPER_GUIDE.md (se sei uno sviluppatore)
    │   └── FRONTEND_GUIDE.md
    ├── api/
    │   └── API.md           (riferimento endpoint)
    ├── tutorials/
    │   ├── AI_ASSISTANT.md
    │   ├── FLEET_GUI.md
    │   └── FLEET_CLI.md
    └── implementation/
        └── PLAN.md          (piano esecutivo ERP)
```

## Come Estendere

Per aggiungere un nuovo documento:
1. Posizionarlo nella directory `backend/docs/`
2. Aggiungere una riga nella tabella della sezione appropriata in questo `INDEX.md`
3. Se applicabile, aggiornare anche `backend/docs/README.md` e il `README.md` radice
