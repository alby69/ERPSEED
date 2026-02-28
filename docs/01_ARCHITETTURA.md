# Architettura di FlaskERP

## Panoramica del Sistema

FlaskERP è un sistema ERP modulare di nuova generazione, progettato per adattarsi alle esigenze specifiche di ogni organizzazione. A differenza dei gestionali tradizionali che impongono processi predefiniti, FlaskERP permette di modellare il sistema informativo esattamente secondo le proprie necessità.

Il cuore di FlaskERP è il **Builder**, un motore low-code integrato che consente di creare entità, campi, relazioni e viste direttamente dall'interfaccia web, senza scrivere codice.

La natura multi-tenant garantisce l'isolamento completo dei dati: ogni progetto opera in uno spazio separato, potendo però condividere template e configurazioni quando necessario.

---

## Livelli Architetturali

FlaskERP è organizzato in livelli crescenti di astrazione:

```
┌─────────────────────────────────────────────────────────────────┐
│                      APPLICAZIONE FLASKERP                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              LIVELLO FUNZIONALE (Module)                │   │
│  │  Module = SysModel + Block + Hook + API                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              LIVELLO UI (Block)                         │   │
│  │  Block = Component + Relazioni                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              LIVELLO DATI (SysModel)                    │   │
│  │  SysModel + SysField = Entità + Campi                  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## I Concetti Fondamentali

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
│                     CORE BLOCK (ERP Foundation)                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │     SOGGETTO    │    │      RUOLO      │                    │
│  │   (Party)       │◄───│ (Cliente, Forn., │                    │
│  │                 │    │  Dipendente...) │                    │
│  └────────┬────────┘    └─────────────────┘                    │
│           │                                                      │
│     ┌─────┴─────┐                                              │
│     ▼           ▼                                              │
│ ┌─────────┐ ┌─────────┐                                        │
│ │INDIRIZZO│ │CONTATTO │  (multipli per soggetto)            │
│ │(Address)│ │(Contact)│                                        │
│ └─────────┘ └─────────┘                                        │
│                                                                  │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │    PRODOTTO    │    │    Ubicazione  │                    │
│  │   (Product)    │    │  (Warehouse)    │                    │
│  └─────────────────┘    └─────────────────┘                    │
│                                                                  │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │    UTENTE      │    │    PROGETTO     │                    │
│  │   (User)       │    │   (Project)    │                    │
│  └─────────────────┘    └─────────────────┘                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

Questi Core Block sono preinstallati e non eliminabili.

---

## Categorie dei Moduli

| Categoria | Fornitore | Licenza | Esempio |
|-----------|-----------|---------|---------|
| **core** | Sistema | Sempre disponibile | Auth, Progetti, Builder |
| **builtin** | Sviluppatori core | Inclusi nell'installazione | Anagrafica, Vendite, Magazzino |
| **premium** | Sviluppatori core | A pagamento | Contabilità avanzata, Produzione |
| **marketplace** | Comunità | Vari (gratis/pagamento) | Template specifici, widget custom |

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

**Uso**: Comunicazione tra moduli senza accoppiamento, sincronizzazioni, notifiche

### Workflow

Sequenze dichiarative di azioni condizionali, configurabili via UI dall'amministratore.

**Uso**: Automazioni business, processi multi-step, approvazioni

---

## Stack Tecnologico

| Componente | Tecnologia |
|------------|------------|
| Backend | Flask 3.x |
| API | Flask-smorest (OpenAPI) |
| Database | PostgreSQL 14+ |
| ORM | SQLAlchemy |
| Auth | JWT |
| Frontend | React 19 + Ant Design |
| Container | Docker |

---

## Quick Start

Per iniziare a utilizzare FlaskERP:

1. **Accedi** all'interfaccia web
2. **Crea un progetto** dal menu di amministrazione
3. **Esplora i moduli disponibili** e attiva quelli necessari
4. **Usa il Builder** per creare entità custom se necessario
5. **Configura utenti e permessi**

Per aspetti tecnici approfonditi, consulta i manuali specifici.

---

## Documentazione

| Documento | Descrizione |
|-----------|-------------|
| [02_BUILDER.md](02_BUILDER.md) | Creare entità, campi, relazioni |
| [03_MODULI.md](03_MODULI.md) | Moduli disponibili e gestione |
| [04_AMMINISTRAZIONE.md](04_AMMINISTRAZIONE.md) | Utenti, permessi, backup |
| [05_MARKETPLACE.md](05_MARKETPLACE.md) | Pubblicare e installare |
| [06_AUTOMAZIONE.md](06_AUTOMAZIONE.md) | Hook, Eventi, Workflow |

---

*Documento aggiornato: Febbraio 2026*
