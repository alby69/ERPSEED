# Architettura di ERPSeed

## Panoramica del Sistema

ERPSeed è un sistema ERP modulare di nuova generazione, progettato per adattarsi alle esigenze specifiche di ogni organizzazione. A differenza dei gestionali tradizionali che impongono processi predefiniti, ERPSeed permette di modellare il sistema informativo esattamente secondo le proprie necessità.

Il cuore di ERPSeed è il **Builder**, un motore low-code integrato che consente di creare entità, campi, relazioni e viste direttamente dall'interfaccia web, senza scrivere codice.

La natura multi-tenant garantisce l'isolamento completo dei dati: ogni progetto opera in uno spazio separato, potendo però condividere template e configurazioni quando necessario.

---

## Architettura Refactoring (2026)

ERPSeed ha completato un importante refactoring architetturale seguendo i pattern **Domain-Driven Design** e **Hexagonal Architecture**:

```
backend/
├── shared/              # Infrastruttura condivisa
│   ├── orm/           # Definizioni campi
│   ├── utils/         # Pagination, filtri, audit
│   ├── exceptions/    # Eccezioni custom
│   ├── interfaces/   # Interfacce servizi
│   └── events/       # EventBus + eventi dominio
├── ai_service/        # AI Service (Ports & Adapters)
│   ├── domain/       # Modelli, porte, servizi
│   └── adapters/    # Adapter LLM
├── builder_service/  # Builder Service (CQRS)
│   ├── domain/       # Entità, repository, eventi
│   ├── application/  # Comandi e query
│   └── infrastructure/
├── plugin_system/    # Sistema plugin
│   ├── interfaces.py
│   └── manager.py
├── container.py      # Dependency Injection Container
├── builder/         # Modulo builder (legacy)
├── ai/              # Modulo AI (legacy)
└── plugins/         # Implementazioni plugin
```

### Pattern Implementati

| Pattern                  | Componente                | Scopo                     |
| ------------------------ | ------------------------- | ------------------------- |
| **Ports & Adapters**     | `ai_service/`             | Astrazione provider LLM   |
| **CQRS**                 | `builder_service/`        | Separazione Command/Query |
| **Repository**           | `builder_service/domain/` | Astrazione accesso dati   |
| **Event-Driven**         | `shared/events/`          | Comunicazione decoupled   |
| **Dependency Injection** | `container.py`            | Gestione servizi          |
| **Plugin**               | `plugin_system/`          | Estensibilità             |

---

## Livelli Architetturali

ERPSeed è organizzato in livelli crescenti di astrazione:

```
┌─────────────────────────────────────────────────────────────────┐
│                      APPLICAZIONE ERPSEED                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              LIVELLO FUNZIONALE (Module)                │    │
│  │  Module = SysModel + Block + Hook + API                 │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              LIVELLO UI (Block)                         │    │
│  │  Block = Component + Relazioni                          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              LIVELLO DATI (SysModel)                    │    │
│  │  SysModel + SysField = Entità + Campi                   │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## I Concetti Fondamentali

### 0. AI-First Construction

A differenza dei sistemi tradizionali, ERPSeed nasce per essere costruito dall'**AI Assistant**. L'utente non configura solo tramite UI, ma descrive le proprie necessità in linguaggio naturale. L'AI interpreta i requisiti e genera automaticamente `SysModel`, `Fields` e `Blocks`, riducendo i tempi di setup del 90%.

### 1. SysModel (Entità)

Un **SysModel** è un'entità dati creata con il Builder. Corrisponde a una tabella nel database e rappresenta un concetto del business.

**Esempi**: Cliente, Ordine, Prodotto, Fattura, Dipendente

Ogni SysModel è composto da **SysField** (campi) che ne definiscono la struttura.

### 2. SysField (Campo)

Un **SysField** definisce un singolo attributo di un SysModel. Ogni campo ha:

- **Tipo**: string, text, integer, decimal, boolean, date, datetime, select, relation
- **Configurazione**: required, unique, default, validation
- **Opzioni**: per select, relation, lookup

### 3. Component (Componente UI)

Un **Component** è un'istanza di un **Archetype** in un progetto. Definisce come un'entità viene presentata nell'interfaccia.

**Archetipi disponibili**:
| Archetype | Descrizione |
|-----------|-------------|
| table | Tabella con ordinamento, filtri, paginazione |
| form | Form per inserimento/modifica dati |
| chart | Grafici (bar, line, pie, etc.) |
| kanban | Board drag-and-drop per workflow |
| metric | KPI e indicatori numerici |
| grid | Layout a griglia per dashboard |

### 4. Block (Blocco)

Un **Block** è una collezione di Component con relazioni tra loro. È l'unità minima pubblicabile nel Marketplace.

**Esempio**: "Card Cliente" = table (lista ordini) + form (dati anagi) + chartrafic (storico acquisti)

### 5. Module (Modulo)

Un **Module** è l'unità funzionale completa che combina:

- **SysModel**: le entità dati
- **Block**: le interfacce utente
- **Hook**: la logica di business (validazioni, calcoli)
- **API**: gli endpoint esposti

Quando un modulo viene pubblicato nel Marketplace, acquisisce una **Dashboard App-like**: un'interfaccia dedicata e ottimizzata (simile a una Single Page Application) che raggruppa tutti i suoi componenti in un unico ambiente di lavoro coerente.

**Esempio**: Il modulo "Vendite" include:

- SysModel: Ordine, RigaOrdine, Pagamento
- Block: ListaOrdini, FormOrdine, KanbanOrdini, StatisticheVendite
- Hook: calcolo totale, verifica stock, generazione fattura
- API: CRUD ordini, statistiche

---

## Core Block di un ERP

Ogni ERP necessita di questi **modelli fondamentali** predefiniti:

```
┌─────────────────────────────────────────────────────────────────┐
│                     CORE BLOCK (ERP Foundation)                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐                     │
│  │     SOGGETTO    │    │      RUOLO      │                     │
│  │   (Party)       │◄───│ (Cliente, Forn., │                    │
│  │                 │    │  Dipendente...) │                     │
│  └────────┬────────┘    └─────────────────┘                     │
│           │                                                     │
│     ┌─────┴─────┐                                               │
│     ▼           ▼                                               │
│ ┌─────────┐ ┌─────────┐                                         │
│ │INDIRIZZO│ │CONTATTO │  (multipli per soggetto)                │
│ │(Address)│ │(Contact)│                                         │
│ └─────────┘ └─────────┘                                         │
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐                     │
│  │    PRODOTTO     │    │    Ubicazione   │                     │
│  │   (Product)     │    │  (Warehouse)    │                     │
│  └─────────────────┘    └─────────────────┘                     │
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐                     │
│  │    UTENTE       │    │    PROGETTO     │                     │
│  │   (User)        │    │   (Project)     │                     │
│  └─────────────────┘    └─────────────────┘                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

Questi Core Block sono preinstallati e non eliminabili.

---

## Categorie dei Moduli

| Categoria       | Fornitore         | Licenza                    | Esempio                           |
| --------------- | ----------------- | -------------------------- | --------------------------------- |
| **core**        | Sistema           | Sempre disponibile         | Auth, Progetti, Builder           |
| **builtin**     | Sviluppatori core | Inclusi nell'installazione | Anagrafica, Vendite, Magazzino    |
| **premium**     | Sviluppatori core | A pagamento                | Contabilità avanzata, Produzione  |
| **marketplace** | Comunità          | Vari (gratis/pagamento)    | Template specifici, widget custom |

La categoria indica **provenienza e modello di business**, non importanza funzionale.

---

## Ciclo di Vita di un Modulo

```
draft ──► testing ──► published ──► deprecated
  │          │            │
  │          │            └──► Installabile da tutti
  │          │
  │          └──► In test, non ancora pubblicabile
  │
  └──► In fase di sviluppo/modifica
```

**Draft**: Modulo in fase di creazione o modifica
**Testing**: Test in corso, pronto per verifica
**Published**: Installabile nel proprio progetto
**Deprecated**: Non più consigliato, still installabile

---

## Sistema di Comunicazione (Automazione)

I moduli comunicano attraverso tre meccanismi complementari:

### Hook (Ganci)

Funzioni eseguite **sincronamente** nella stessa transazione del chiamante.

```
BEFORE_CREATE  → Prima della creazione
AFTER_CREATE  → Dopo la creazione
BEFORE_UPDATE  → Prima dell'aggiornamento
AFTER_UPDATE  → Dopo l'aggiornamento
BEFORE_DELETE  → Prima della cancellazione
AFTER_DELETE  → Dopo la cancellazione
```

**Uso**: Validazioni critiche, calcoli automatici, logica core

### Event Bus

Sistema di messaggistica **asincrona** per eventi di business. Un componente pubblica, altri reagiscono.

ERPSeed usa un EventBus in-memory con supporto per:

- **Eventi Standard**: model.created, record.updated, user.login, etc.
- **Eventi Custom**: Qualsiasi evento definito dal modulo
- **Sottoscrizioni**: Handler si iscrivono a tipi specifici di eventi

**Uso**: Comunicazione tra moduli senza accoppiamento, sincronizzazioni, notifiche

### Workflow

Sequenze dichiarative di azioni condizionali, configurabili via UI dall'amministratore.

**Uso**: Automazioni business, processi multi-step, approvazioni

---

## Dependency Injection Container

ERPSeed usa un Container DI centralizzato per la gestione dei servizi:

```python
from backend.container import get_container

container = get_container()
container.register('db', lambda: db)
container.register('event_bus', lambda: EventBus())

# Ottenere un servizio
user_service = container.get('user_service')
```

---

## Stack Tecnologico

| Componente | Tecnologia              |
| ---------- | ----------------------- |
| Backend    | Flask 3.x               |
| API        | Flask-smorest (OpenAPI) |
| Database   | PostgreSQL 14+          |
| ORM        | SQLAlchemy              |
| Auth       | JWT                     |
| Frontend   | React 19 + Ant Design   |
| Container  | Docker                  |

---

## Quick Start

Per iniziare a utilizzare ERPSeed:

1. **Accedi** all'interfaccia web
2. **Crea un progetto** dal menu di amministrazione
3. **Esplora i moduli disponibili** e attiva quelli necessari
4. **Usa il Builder** per creare entità custom se necessario
5. **Configura utenti e permessi**

Per aspetti tecnici approfonditi, consulta i manuali specifici.

---

## Documentazione

| Documento                                      | Descrizione                          |
| ---------------------------------------------- | ------------------------------------ |
| [02_BUILDER.md](02_BUILDER.md)                 | Creare entità, campi, relazioni      |
| [03_MODULI.md](03_MODULI.md)                   | Moduli disponibili e gestione        |
| [04_AMMINISTRAZIONE.md](04_AMMINISTRAZIONE.md) | Utenti, permessi, backup             |
| [05_MARKETPLACE.md](05_MARKETPLACE.md)         | Pubblicare e installare              |
| [06_AUTOMAZIONE.md](06_AUTOMAZIONE.md)         | Hook, Eventi, Workflow               |
| [10_AI_ASSISTANT.md](10_AI_ASSISTANT.md)       | AI Assistant per auto-configurazione |
| [12_ROADMAP.md](12_ROADMAP.md)                 | Roadmap refactoring architetturale   |

---

_Documento aggiornato: Marzo 2026_
