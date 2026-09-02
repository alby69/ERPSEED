# Strategia e Piano di Integrazione AgentMesh

> **Nota:** Questo documento descrive l'architettura dell'ERP distribuito agentico e l'integrazione tra ERPSEED e AgentMesh.

---

## Visione

L'integrazione di ERPSEED con la rete `agentmesh` trasforma un sistema gestionale tradizionale in un ecosistema di agenti intelligenti distribuiti. In questa architettura, ogni modulo ERP (Sales, Inventory, etc.) non è solo una collezione di tabelle e API, ma un "Agente di Servizio" con capacità decisionali e di governance che espone la propria funzionalità tramite "Capacità" (Commands e Queries).

---

## Concetti Chiave

- **Agent**: Un modulo funzionale autonomo (es. `SalesAgent`, `WarehouseAgent`).
- **Capability**: Un tool che un agente può eseguire. Mappa 1:1 a un Command o Query CQRS.
- **Manifest**: Uno schema JSON (`/capabilities`) che descrive tutte le capacità disponibili di un agente.
- **Mesh**: Il livello di comunicazione distribuito (AgentMesh) che orchestra le interazioni tra agenti.

---

## Affinità Architetturali

| Caratteristica ERPSEED | Funzionalità AgentMesh | Sinergia |
|------------------------|------------------------|----------|
| **CQRS (Command/Query)** | **Agent Capabilities** | I comandi (es. `CreateOrder`) e le query (es. `GetStock`) vengono mappati direttamente come "Tool" invocabili dagli agenti. |
| **Multi-Tenant** | **Governance & Isolation** | AgentMesh fornisce il piano di controllo per isolare le interazioni AI tra diversi tenant, gestendo quote e permessi. |
| **No-Code Builder** | **Dynamic Tooling** | I modelli creati dinamicamente in ERPSEED generano automaticamente nuovi tool per gli agenti senza scrivere codice. |
| **Architettura a Nodi** | **Distributed Mesh** | Supporta scenari in cui i dati risiedono in nodi locali (on-premise) ma sono orchestrati da un'intelligenza centrale. |

---

## Piano di Implementazione

### Fase 1: Consolidamento e Bridge (Completato)
- Unificazione dei branch `backend` e `frontend` nel ramo `main`.
- Centralizzazione della documentazione in `docs/`.
- Stabilizzazione della logica CQRS come base per l'esposizione dei tool.

### Fase 2: Agentificazione dei Moduli (Completato / In Corso)
- **Capability Discovery**: Implementato `CapabilityRegistry` e l'endpoint `/api/v1/ai/capabilities` che esporta il manifesto in formato compatibile con AgentMesh (vedi riferimento completo in [API.md](API.md#capabilities-agentmesh-apiv1aicapabilities)).
- **Agent Gateway**: Rifattorizzato `backend/modules/ai` con l'adapter `AgentMeshAdapter` per agire come gateway verso la rete distribuita.
- **Agentification**: Mappatura dei moduli `Sales` e `Products/Inventory` tramite il decoratore `@capability`.

### Fase 3: Governance e Policy
- Configurazione dei file di policy di AgentMesh per definire i perimetri d'azione degli agenti sui dati ERP.
- Integrazione del monitoraggio dei costi AI direttamente nella dashboard amministrativa di ERPSEED.

### Fase 4: Collaborazione Multi-Agente
- Scenari di coordinamento automatico tra agenti (es. "Sales Agent" che coordina con "Inventory Agent" per verificare giacenze e suggerire riassortimenti via Event Bus).

---

## Punti di Forza e Rischi

| Punto di Forza | Beneficio |
|----------------|-----------|
| **Mappatura CQRS** | Trasforma la logica di business in tool esponibili all'AI senza dover riscrivere il codice. |
| **Disaccoppiamento** | Gli agenti possono essere eseguiti su nodi distribuiti differenti. |
| **Autodocumentante** | Il manifesto `/capabilities` si aggiorna automaticamente al variare del codice. |

| Rischio / Sfida | Mitigazione |
|-----------------|-------------|
| **Latenza** | Caching locale delle capacità; ottimizzazione del bus inter-agente. |
| **Consistenza Dati** | Utilizzo di Saga Pattern / Transazioni Distribuite via Event Bus per workflow multi-agente. |
| **Complessità** | Avvio con un "Local Mesh" monolitico prima della distribuzione su nodi remoti. |

---

## Struttura del Progetto Unificato

```
erpseed/
├── docs/                      # Documentazione centralizzata
├── backend/                   # Core Flask (CQRS + Multi-tenant)
│   ├── modules/               # Moduli ERP (Sales, HR, Magazzino, etc.)
│   │   └── ai/                # Agent Gateway (Bridge verso AgentMesh)
│   └── core/                  # Sistema base e middleware
└── frontend/                  # React UI (Visual Builder + Dashboards)
```

---

*Per la cronologia completa delle modifiche di questo documento, consulta la cronologia Git del repository.*
