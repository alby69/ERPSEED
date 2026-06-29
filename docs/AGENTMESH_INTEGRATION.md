# Piano di Integrazione ERPSEED + AgentMesh

## Visione: ERP Distribuito Agentico

L'integrazione di ERPSEED con la rete `agentmesh` trasforma un sistema gestionale tradizionale in un ecosistema di agenti intelligenti distribuiti. In questa architettura, ogni modulo ERP non è solo una collezione di tabelle e API, ma un "Agente di Servizio" con capacità decisionali e di governance.

### 1. Affinità Architetturali

| Caratteristica ERPSEED | Funzionalità AgentMesh | Sinergia |
|------------------------|------------------------|----------|
| **CQRS (Command/Query)** | **Agent Capabilities** | I comandi (es. `CreateOrder`) e le query (es. `GetStock`) vengono mappati direttamente come "Tool" che gli agenti possono invocare. |
| **Multi-Tenant** | **Governance & Isolation** | AgentMesh fornisce il piano di controllo per isolare le interazioni AI tra diversi tenant, gestendo quote e permessi. |
| **No-Code Builder** | **Dynamic Tooling** | I modelli creati dinamicamente in ERPSEED generano automaticamente nuovi tool per gli agenti senza scrivere codice. |
| **Architettura a Nodi** | **Distributed Mesh** | Supporta scenari in cui i dati risiedono in nodi locali (on-premise) ma sono orchestrati da un'intelligenza centrale. |

---

### 2. Piano di Implementazione Tecnico

#### Fase 1: Consolidamento e "Bridge" (Completato)
- Unificazione dei branch `backend` e `frontend` nel ramo `main`.
- Centralizzazione della documentazione in `/docs`.
- Stabilizzazione della logica CQRS come base per l'esposizione dei tool.

#### Fase 2: Agentificazione dei Moduli (IN CORSO)
- **Capability Discovery**: Implementato `CapabilityRegistry` e l'endpoint `/api/v1/ai/capabilities` che esporta il manifesto in formato compatibile con AgentMesh.
- **Agent Gateway**: Rifattorizzato `backend/modules/ai` con l'adapter `AgentMeshAdapter` per agire come gateway verso la rete distribuita.
- **Agentification**: Iniziata l'agentificazione dei moduli `Sales` e `Products/Inventory` tramite decoratore `@capability`.

#### Fase 3: Governance e Policy
- Configurazione dei file di policy di AgentMesh per definire i perimetri d'azione degli agenti sui dati ERP.
- Integrazione del monitoraggio dei costi AI direttamente nella dashboard amministrativa di ERPSEED.

#### Fase 4: Collaborazione Multi-Agente
- Implementare scenari in cui un "Sales Agent" coordina automaticamente con un "Inventory Agent" tramite il bus di AgentMesh per risolvere conflitti di stock o suggerire approvvigionamenti.

---

### 3. Struttura del Progetto Unificato

```
erpseed/
├── docs/                      # DOCUMENTAZIONE CENTRALIZZATA
├── backend/                   # CORE FLASK (CQRS + Multi-tenant)
│   ├── modules/               # Moduli ERP (Sales, HR, Magazzino, etc.)
│   │   └── ai/                # Agent Gateway (Bridge verso AgentMesh)
│   └── core/                  # Sistema base e middleware
└── frontend/                  # REACT UI (Visual Builder + Dashboards)
```

### 4. Vantaggi della Migrazione a Main
- **Single Source of Truth**: Fine della frammentazione tra branch specialistici.
- **Atomic Commits**: Le modifiche che coinvolgono sia logica che UI possono essere sottomesse in un unico commit.
- **CI/CD Semplificata**: Un unico pipeline di test per l'intero ecosistema.

---
*Documento generato per il consolidamento del progetto ERPSEED.*
