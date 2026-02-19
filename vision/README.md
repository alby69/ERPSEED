# ERPE Vision Documents

## Panoramica

Questa cartella contiene la documentazione della **visione architetturale** di ERPE (ERPEngine), un sistema ERP modulare e auto-generante.

---

## Documenti

### 1. Fondamenti Concettuali
**File:** `01_FONDAMENTI_CONCETTUALI.md`

Spiega i quattro pilastri teorici del progetto:
- **DDD** (Domain-Driven Design) - dominio come collezione di oggetti
- **Plugin Architecture** - moduli che si agganciano
- **Metaprogramming** - codice che genera codice
- **Self-Modifying Code** - codice adattivo

### 2. Tabelle Archetipiche
**File:** `02_TABELLE_ARCHETIPICHE.md`

Definisce i **mattoncini base** del sistema:
- **Livello 1:** Core Entities (Soggetto, Ruolo, Indirizzo, Contatto)
- **Livello 2:** Document Patterns (Testata, Riga, Allegato)
- **Livello 3:** Value Objects (Valuta, Unità Misura)
- **Livello 4:** System (Modulo, Container)

Include esempi di codice Python per ogni tabella.

### 3. Modello di Composizione
**File:** `03_MODELLO_COMPOSIZIONE.md`

Descrive come i mattoncini si **aggregano**:
- **Block** → Mattoncino atomico
- **Container** → Aggregatore di blocchi
- **Robot** → Modulo funzionale completo
- **Spaceship** → ERP orchestrator

Include diagrammi, pattern di comunicazione (Event Bus, Hook System).

### 4. Code-as-Data (Programmazione Adattiva)
**File:** `04_CODE_AS_DATA.md`

Esplora le tecniche per **codice che si auto-genera**:
- **Livello 1:** Metaprogramming (`type()`, metaclasses, decorators)
- **Livello 2:** Generazione dinamica (API da config)
- **Livello 3:** Self-Modifying Code (hot reload, expression engine)
- **Livello 4:** Evolutionary Code (algoritmi genetici)

Include esempi pratici eseguibili.

### 5. Builder Engine
**File:** `05_BUILDER_ENGINE.md`

Documenta il **costruttore automatico**:
- Formato template (YAML/JSON)
- Parser → Generator → Migrator → Registrar
- Interfaccia CLI e UI
- Flusso completo da template a modulo funzionante

### 6. Roadmap di Implementazione
**File:** `06_ROADMAP_IMPLEMENTAZIONE.md`

Piano di implementazione **step-by-step**:
- **Fase 1:** Fondamenta (2 settimane) - Tabelle archetipiche
- **Fase 2:** Composizione (2 settimane) - Sistema blocchi
- **Fase 3:** Builder (4 settimane) - Generatore automatico
- **Fase 4:** Code-as-Data (4 settimane) - Adattività
- **Fase 5:** Evoluzione (4+ settimane) - Auto-ottimizzazione

---

## Stato di Avanzamento

### Fase 1: Fondamenta ✅ COMPLETATO
| Deliverable | File |
|-------------|------|
| Entity Soggetto | `backend/entities/soggetto.py` |
| Entity Ruolo | `backend/entities/ruolo.py` |
| Entity Indirizzo | `backend/entities/indirizzo.py` |
| Entity Contatto | `backend/entities/contatto.py` |

### Fase 2: Composizione ✅ COMPLETATO
| Deliverable | File |
|-------------|------|
| Block Registry | `backend/composition/registry.py` |
| Container System | `backend/composition/container.py` |
| Robot/Module System | `backend/composition/robot.py` |

### Fase 3: Builder ✅ COMPLETATO
| Deliverable | File |
|-------------|------|
| Builder Engine | `backend/builder.py` |

### Fase 4: Code-as-Data ✅ COMPLETATO
| Deliverable | File |
|-------------|------|
| Expression Engine | `backend/composition/expression.py` |
| Hook System | `backend/composition/hooks.py` |
| Hot Reload | `backend/composition/hot_reload.py` |

### Fase 5: Evoluzione ✅ COMPLETATO
| Deliverable | File |
|-------------|------|
| Telemetry | `backend/evolution/telemetry.py` |
| Auto-Optimization | `backend/evolution/optimizer.py` |
| Genetic Algorithms | `backend/evolution/genetic.py` |

---

**Stato: TUTTE LE FASI COMPLETATE**

---

## Leggenda

```
📚 Teoria
🧱 Componenti  
🔧 Implementazione
📋 Gestione
```

---

## Quick Start

Per capire il progetto, leggi in ordine:

1. `01_FONDAMENTI_CONCETTUALI.md` - Cosa stiamo costruendo e perché
2. `02_TABELLE_ARCHETIPICHE.md` - I mattoncini base
3. `03_MODELLO_COMPOSIZIONE.md` - Come si compongono
4. `06_ROADMAP_IMPLEMENTAZIONE.md` - Come procediamo

Per implementare, guarda:
- `05_BUILDER_ENGINE.md` - Come funziona il generatore
- `04_CODE_AS_DATA.md` - Le tecniche da usare

---

## Riepilogo Visivo

```
┌─────────────────────────────────────────────────────────────┐
│                      ASTRONAVE (ERP)                        │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                   ROBOT (Modulo)                    │   │
│   │                                                     │   │
│   │   ┌───────────────────────────────────────────┐    │   │
│   │   │              CONTAINER                    │    │   │
│   │   │   ┌────────┐  ┌────────┐  ┌────────┐    │    │   │
│   │   │   │ MATTON │  │ MATTON │  │ MATTON │    │    │   │
│   │   │   │CINO    │  │CINO    │  │CINO    │    │    │   │
│   │   │   └────────┘  └────────┘  └────────┘    │    │   │
│   │   └───────────────────────────────────────────┘    │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                    BUILDER                          │   │
│   │   Template ──► Parser ──► Generator ──► Module     │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Contatti e Contribuzione

Questa documentazione fa parte del progetto **flaskERP**.

Per domande o suggerimenti:
- Apri una issue su GitHub
- Contatta il team di sviluppo

---

*Ultimo aggiornamento: Febbraio 2026 - Roadmap Implementazione COMPLETATA*
