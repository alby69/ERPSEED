# FlaskERP - Concetti Fondamentali

## Panoramica del Sistema

FlaskERP è un sistema ERP modulare di nuova generazione, progettato per adattarsi alle esigenze specifiche di ogni organizzazione. A differenza dei gestionali tradizionali che impongono processi predefiniti, FlaskERP permette di modellare il sistema informativo esattamente secondo le proprie necessità.

Il cuore di FlaskERP è il **Builder**, un motore low-code integrato che consente di creare entità, campi, relazioni e viste direttamente dall'interfaccia web, senza scrivere codice. Questo rende il sistema accessibile sia agli utenti business che agli sviluppatori.

La natura multi-tenant garantisce l'isolamento completo dei dati: ogni cliente opera in uno spazio separato, potendo però condividere template e configurazioni quando necessario.

---

## I Quattro Pilastri Fondamentali

FlaskERP si basa su quattro pilastri concettuali che guidano l'architettura e lo sviluppo del sistema. Questi pilastri non sono solo teoria, ma principi implementati nel codice che rendono FlaskERP flessibile e potente.

### 1. Domain-Driven Design

Il Domain-Driven Design rappresenta il modo in cui FlaskERP organizza la conoscenza del dominio applicativo. Ogni modulo ha un contesto delimitato con un linguaggio condiviso tra sviluppatori e utenti business.

In termini pratici, questo si traduce nelle entità core del sistema:

**Soggetto** rappresenta l'entità centrale del sistema, qualsiasi persona fisica o giuridica con cui l'azienda interagisce: clienti, fornitori, dipendenti, partner. Un Soggetto può assumere molteplici Ruoli nel tempo: oggi è un Cliente, domani potrebbe diventare anche Fornitore.

**Ruolo** definisce la tipologia di relazione tra l'azienda e il Soggetto. I ruoli fondamentali includono Cliente, Fornitore, Dipendente, Prospect, Partner. Ogni ruolo può avere attributi specifici e permette di filtrare le attività per tipologia.

**Indirizzo** gestisce le localizzazioni geografiche associate ai Soggetti. Un Soggetto può avere molteplici Indirizzi: sede legale, sede operativa, magazzino, indirizzo di fatturazione.

**Contatto** rappresenta i canali di comunicazione: email, telefono, fax, cellulare, PEC. Anche questi sono multipli per ogni Soggetto.

```
Relazioni tra Entità Core:

Soggetto ─────┬──────> Ruolo (molteplici nel tempo)
               │
               ├──< Indirizzo (molteplici)
               │
               └──< Contatto (molteplici)
```

Questa struttura permette di gestire la complessità del mondo reale senza creare entità ridondanti. Un'azienda che è sia Cliente che Fornitore avrà un unico Soggetto con due Ruoli associati.

### 2. Architettura Plugin

Il secondo pilastro è l'architettura plugin, che consente di estendere il sistema senza modificare il codice core. Ogni funzionalità è incapsulata in un modulo separato che può essere attivato, disattivato o rimosso indipendentemente.

Il sistema espone un **PluginRegistry** centralizzato che gestisce la registrazione, l'attivazione e la disattivazione dei moduli. Ogni plugin dichiara le proprie dipendenze e il sistema garantisce che vengano caricate nell'ordine corretto.

I plugin comunicano tra loro attraverso un **EventBus**: quando accade qualcosa in un modulo, gli altri moduli possono reagire. Ad esempio, quando viene creato un ordine di vendita, il modulo Contabilità può automaticamente generare una scrittura contabile.

```
FlaskERP Core
    │
    ├── PluginRegistry (gestisce caricamento/disattivazione)
    │
    ├── EventBus (comunicazione tra moduli)
    │
    └── Hook System (estensione comportamenti)
           │
           ├── Accounting (contabilità)
           ├── HR (risorse umane)
           ├── Inventory (magazzino)
           └── [plugin personalizzati...]
```

Questa architettura permette di installare solo le funzionalità necessarie, riducendo la complessità per chi usa solo alcune parti del sistema, e di aggiungere nuove funzionalità senza impattare quelle esistenti.

### 3. Metaprogramming

Il terzo pilastro è il metaprogramming, la capacità del sistema di generare codice automaticamente partendo da configurazioni. Questo è il cuore del Builder.

Quando crei un nuovo modello attraverso il Builder, il sistema non si limita a salvare metadati: genera dinamicamente classi Python, schemi database, API REST e interfacce utente. Il tutto in tempo reale, senza intervento manuale.

Il metaprogramming opera su diversi livelli:

**Livello Database**: Il sistema legge la definizione del modello e genera le tabelle PostgreSQL, gestendo migrazioni automatiche quando modifichi la struttura.

**Livello API**: Per ogni entità vengono generate automaticamente le operazioni CRUD (Create, Read, Update, Delete), più eventuali endpoint personalizzati.

**Livello UI**: Il frontend riceve la definizione del modello e renderizza automaticamente form e tabelle appropriate, convalidazione inclusa.

```
Configurazione Utente
        │
        ▼
┌───────────────────┐
│   Builder Engine  │
└───────────────────┘
        │
        ├──► Database (CREATE TABLE)
        ├──► API Routes (GET/POST/PUT/DELETE)
        └──► UI Components (Form/Table)
```

Questo approccio drastically riduce il tempo necessario per creare nuove funzionalità: quello che richiederebbe giorni di sviluppo con metodi tradizionali, con FlaskERP si fa in minuti.

### 4. Self-Modifying Code

Il quarto pilastro è il codice auto-modificante, la capacità del sistema di evolversi a runtime senza richiedere riavvi o interventi manuali.

Le componenti principali di questo pilastro includono:

**Hot Reload**: Le modifiche ai moduli vengono applicate senza riavviare il server. Quando pubblichi un nuovo blocco nel Marketplace o installi un componente, diventa immediatamente disponibile.

**Expression Engine**: Il sistema può valutare espressioni dinamiche definite dagli utenti. Campi calcolati come "totale = quantità × prezzo" vengono interpretati e valutati automaticamente.

**Configurazione Runtime**: Le impostazioni vengono applicate immediatamente. Cambiare un tema, attivare un modulo, modificare permessi non richiede ricariche o riavvii.

L'integrazione con l'AI Agent (descritta nel manuale dedicato) rappresenta l'evoluzione naturale di questo pilastro: l'intelligenza artificiale genera configurazioni che il sistema applica automaticamente, realizing il sogno del "describe what you need, get what you want".

---

## Modello di Composizione

Per comprendere come FlaskERP organizza le funzionalità, immagina una gerarchia di astrazioni crescente:

**Blocco** (Block) è l'unità atomica, corrisponde a una singola entità o tabella. Ha un nome, una struttura dati, regole di validazione.

**Contenitore** (Container) aggrega blocchi correlati e fornisce un'API unificata. Ad esempio, il contenitore "Anagrafica" include i blocchi Soggetto, Ruolo, Indirizzo, Contatto.

**Modulo** (Module/Robot) è il livello funzionale completo, include uno o più contenitori con logica di business specifica. Il modulo "Vendite" gestisce l'intero ciclo di vendita.

**Applicazione** (Spaceship) è l'orchestratore che coordina tutti i moduli, gestisce autenticazione, permessi globali, configurazioni di sistema.

```
┌─────────────────────────────────────────────┐
│           APPLICAZIONE FLASKERP             │
│                                             │
│   ┌─────────────────────────────────────┐   │
│   │            MODULO VENDITE            │   │
│   │  ┌──────────────┬──────────────┐    │   │
│   │  │  Contenitore │  Contenitore │    │   │
│   │  │  Ordini      │  Clienti     │    │   │
│   │  └──────────────┴──────────────┘    │   │
│   └─────────────────────────────────────┘   │
│                                             │
│   ┌─────────────────────────────────────┐   │
│   │           MODULO MAGAZZINO           │   │
│   │  ┌──────────────┬──────────────┐    │   │
│   │  │  Contenitore │  Contenitore │    │   │
│   │  │  Prodotti    │  Movimenti   │    │   │
│   │  └──────────────┴──────────────┘    │   │
│   └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

---

## Schema di Comunicazione

I moduli comunicano attraverso due meccanismi principali:

**EventBus**: Sistema di messaggistica asincrona per eventi di business. Quando accade qualcosa di significativo, un evento viene pubblicato e tutti i moduli interessati possono reagire.

```
Ordine creato (Sales)
        │
        ▼
┌───────────────────┐
│     EventBus      │
└───────────────────┘
        │
    ┌───┴───┐
    ▼       ▼
Contabilità   Magazzino
(fattura)     (scarico)
```

**Hook System**: Punti di estensione sincroni che permettono di iniettare logica custom in momenti specifici del ciclo di vita delle entità. Gli hook più comuni includono before_create, after_create, before_update, after_delete.

---

## Stack Tecnologico

FlaskERP utilizza tecnologie moderne e consolidate:

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

Per aspetti tecnici approfonditi, consulta il manuale diBuilder e la documentazione tecnica.

---

*Documento aggiornato: Febbraio 2026*
