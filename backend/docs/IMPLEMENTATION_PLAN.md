# Piano di Implementazione ERP Blocks

## Indice
1. [Blocchi Primitivi (Atomi)](#1-blocchi-primitivi-atomi)
2. [Aree Funzionali e Blocchi Compositi](#2-aree-funzionali-e-blocchi-compositi)
3. [Mappa Dipendenze](#3-mappa-dipendenze)
4. [Architettura Nuovi Moduli](#4-architettura-nuovi-moduli)
5. [Frontend: Struttura Menu](#5-frontend-struttura-menu)
6. [Piano di Implementazione per Fasi](#6-piano-di-implementazione-per-fasi)
7. [Template Nuovo Modulo CQRS](#7-template-nuovo-modulo-cqrs)

---

## 1. Blocchi Primitivi (Atomi)

Sono le entità fondamentali, non scomponibili, che vengono riutilizzate per costruire tutti i blocchi compositi. Ogni atomo corrisponde a un modello dati con API CRUD di base.

| # | Primitivo | Modello Backend | Modulo | Stato |
|---|-----------|----------------|--------|-------|
| P0 | **ER Engine** | `SysModel` + `SysField` (Relazioni/FK) | `builder/` | ✅ | Gestione visiva tramite `RelationshipManagerPage` |
| P1 | **Soggetto** | `Soggetto` (PF/PG, cod.fiscale, P.IVA) | `entities/` | ✅ |
| P2 | **Ruolo** | `Ruolo` (cliente, fornitore, dipendente, lead) | `entities/` | ✅ |
| P3 | **Prodotto** | `Product` (codice, nome, SKU, barcode, UM, peso) | `products/` | ✅ |
| P4 | **Contatto** | `Contatto` (email, tel, PEC, social) | `entities/` | ✅ |
| P5 | **Indirizzo** | `Indirizzo` (via, civico, CAP, città, nazione) | `entities/` | ✅ |
| P6 | **Comune/Regione/Provincia** | `Comune`, `Regione`, `Provincia` | `entities/` | ✅ |
| P7 | **Categoria** | `ProductCategory` (albero padre-figlio) | `products/` | 🔶 Nuovo |
| P8 | **Aliquota IVA** | `TaxRate` (codice, %, data inizio/fine) | `modules/tax/` | ❌ Nuovo |
| P9 | **Unità di Misura** | `UnitOfMeasure` (codice, descrizione, simbolo) | `modules/uom/` | ❌ Nuovo |
| P10 | **Conto Contabile** | `Account` (piano dei conti, tipo, codice) | `modules/accounting/` | ⚠️ Da plugins/ |
| P11 | **Magazzino/Deposito** | `InventoryLocation` (codice, nome, indirizzo) | `modules/inventory/` | ⚠️ Da plugins/ |
| P12 | **Listino Prezzo** | `PriceList` + `PriceListItem` (prodotto, prezzo, sconto) | `modules/pricing/` | ❌ Nuovo |
| P13 | **Scadenza** | `Maturity` (data, importo, saldo, riferimento) | `modules/accounting/` | ❌ Nuovo |
| P14 | **Causale Magazzino** | `MovementReason` (codice, tipo: carico/scarico/trasf.) | `modules/inventory/` | ❌ Nuovo |
| P15 | **Unità Organizzativa** | `Department` (codice, nome, gerarchia) | `modules/hr/` | ⚠️ Da plugins/ |

---

## 2. Aree Funzionali e Blocchi Compositi

Ogni **Area** corrisponde a un submenu di "Applicazioni" nella sidebar. I blocchi sono elencati per priorità come da `ERP_BLOCKS_ANALYSIS.md`.

### Area 1: Anagrafiche e Dati Base
*Submenu: "Anagrafiche" — Icona: `<UserOutlined />`*

| Blocco | Composizione | Modulo | Priorità | Sforzo |
|--------|-------------|--------|----------|--------|
| **Soggetti** | P1 + P2 + P4 + P5 + P6 | `entities/` ✅ | — | — |
| **Ruoli** | P2 | `entities/` ✅ | — | — |
| **Indirizzi** | P5 + P6 | `entities/` ✅ | — | — |
| **Comuni** | P6 | `entities/` ✅ | — | — |
| **Contatti** | P4 | `entities/` ✅ | — | — |
| **Prodotti** | P3 + P7 + P8 + P9 + P12 | `products/` ✅ | — | — |
| **Categorie Prodotto** | P7 | `products/` 🔶 | P1 | 1gg |
| **Aliquote IVA** | P8 | `modules/tax/` ❌ | P0 | 2gg |
| **Unità di Misura** | P9 | `modules/uom/` ❌ | P1 | 1gg |
| **Listini Prezzo** | P12 + P3 | `modules/pricing/` ❌ | P0 | 3gg |
| **Piano dei Conti** | P10 | `modules/accounting/` ⚠️ | P1 | 3gg |

### Area 2: Logistica e Acquisti
*Submenu: "Acquisti" — Icona: `<ShoppingCartOutlined />`*

| Blocco | Composizione | Modulo | Priorità | Sforzo |
|--------|-------------|--------|----------|--------|
| **Ordini Acquisto** | P1(Fornitore) + P3 + P12 + Documento | `purchases/` 🔶 | P1 | 3gg (UI) |
| **Richieste d'Acquisto** | P1 + P3 + Workflow approvazione | `purchases/` ❌ | P1 | 5gg |
| **Preventivi Fornitori (RFQ)** | P1 + P3 + confronto | `purchases/` ❌ | P2 | 5gg |
| **Entrata Merci (DDT)** | PO + P3 + P11 + P14 | `purchases/` ❌ | P1 | 5gg |
| **Resi Acquisti** | PO negativo + P11 + P14 | `purchases/` ❌ | P2 | 3gg |

### Area 3: Vendite e CRM
*Submenu: "Vendite" — Icona: `<ProjectOutlined />`*

| Blocco | Composizione | Modulo | Priorità | Sforzo |
|--------|-------------|--------|----------|--------|
| **Ordini Vendita** | P1(Cliente) + P3 + P12 + P8 | `sales/` ✅ | — | — |
| **Preventivi** | Stessa struttura Ordine, stato quotazione | `sales/` ❌ | P1 | 3gg |
| **DDT Vendita** | Ordine → P11 + P14 | `sales/` ❌ | P1 | 5gg |
| **Fatturazione** | Ordine/DDT + P8 + P10 + P13 + num. automatica | `modules/invoicing/` ❌ | P1 | 10gg |
| **Resi Vendita** | Negativo su Ordine + P11 + P14 | `sales/` ❌ | P2 | 3gg |
| **CRM (Lead/Opportunità)** | P1(Lead) + pipeline kanban + attività | `modules/crm/` ❌ | P1 | 5gg |
| **Contratti** | P1 + Documento + date + rinnovo | `modules/contracts/` ❌ | P2 | 5gg |

### Area 4: Magazzino e Inventory
*Submenu: "Magazzino" — Icona: `<InboxOutlined />`*

| Blocco | Composizione | Modulo | Priorità | Sforzo |
|--------|-------------|--------|----------|--------|
| **Giacenze** | P3 + P11 + quantità | `modules/inventory/` ⚠️ | P1 | 3gg |
| **Movimenti di Magazzino** | P3 + P11 + P14 + qty + riferimento | `modules/inventory/` ❌ | P1 | 5gg |
| **Inventario Fisico** | P3 + P11 + conteggio + scostamento | `modules/inventory/` ❌ | P2 | 5gg |
| **Lotto/Serial Number** | P3 + lotto + scadenza + tracciabilità | `modules/inventory/` ❌ | P3 | 5gg |
| **Picking/Packing** | Ordine + P3 + P11 + preparazione | `modules/inventory/` ❌ | P3 | 8gg |

### Area 5: Contabilità e Finanza
*Submenu: "Contabilità" — Icona: `<DollarOutlined />`*

| Blocco | Composizione | Modulo | Priorità | Sforzo |
|--------|-------------|--------|----------|--------|
| **Piano dei Conti** | P10 (da plugins/accounting) | `modules/accounting/` ⚠️ | P1 | 3gg |
| **Prima Nota** | P10 + dare/avere + riferimento doc | `modules/accounting/` ❌ | P1 | 8gg |
| **Scadenzario/Partite** | P13 + P1 + Fattura + solleciti | `modules/accounting/` ❌ | P1 | 5gg |
| **Registri IVA** | P8 + Prima Nota + periodicità | `modules/accounting/` ❌ | P2 | 5gg |
| **Intrastat** | Report movimenti intra | `modules/accounting/` ❌ | P3 | 5gg |
| **Ri.Ba.** | P13 + banca + incasso | `modules/accounting/` ❌ | P3 | 5gg |

### Area 6: Produzione
*Submenu: "Produzione" — Icona: `<ToolOutlined />`*

| Blocco | Composizione | Modulo | Priorità | Sforzo |
|--------|-------------|--------|----------|--------|
| **Distinta Base (BOM)** | P3(padre) + P3(figli) + quantità | `modules/manufacturing/` ❌ | P2 | 5gg |
| **Ciclo di Lavoro** | Fasi + risorse + tempi | `modules/manufacturing/` ❌ | P2 | 5gg |
| **Ordini di Produzione** | BOM + date + qty + stato | `modules/manufacturing/` ❌ | P2 | 8gg |
| **MRP** | BOM + ordini + giacenze + forecast | `modules/manufacturing/` ❌ | P3 | 20gg |
| **Controllo Qualità** | P3 + lotti + collaudi | `modules/manufacturing/` ❌ | P3 | 5gg |

### Area 7: HR e Payroll
*Submenu: "HR" — Icona: `<TeamOutlined />`*

| Blocco | Composizione | Modulo | Priorità | Sforzo |
|--------|-------------|--------|----------|--------|
| **Dipendenti** | P1(PF) + ruolo dipendente + P15 | `modules/hr/` ⚠️ | P2 | 5gg |
| **Reparti** | P15 + P1(Manager) | `modules/hr/` ⚠️ | P2 | 2gg |
| **Presenze** | Dipendente + data + check-in/out | `modules/hr/` ❌ | P2 | 5gg |
| **Ferie e Permessi** | Dipendente + tipo + date + approvazione | `modules/hr/` ❌ | P2 | 5gg |
| **Formazione** | Dipendente + corso + certificazione | `modules/hr/` ❌ | P3 | 3gg |

### Area 8: Project Management
*Submenu: "Progetti" — Icona: `<ProjectOutlined />`*

| Blocco | Composizione | Modulo | Priorità | Sforzo |
|--------|-------------|--------|----------|--------|
| **Progetti** | Testata + date + stato + membri | `modules/projects/` ✅ | — | — |
| **Attività/Task** | Progetto + risorsa + date + stato | Dynamic Model ⚠️ | P1 | 3gg |
| **Timesheet** | P1 + Attività + ore + data | `modules/projects/` ❌ | P1 | 5gg |
| **Budget Commessa** | Preventivo + consuntivo + scostamento | `modules/projects/` ❌ | P2 | 5gg |
| **Workflow** | Automazione processi | `modules/automation/` ✅ | — | — |
| **Business Rules** | Regole di business | via automation ✅ | — | — |

### Area 9: BI e Analytics
*Submenu: "Analytics" — Icona: `<BarChartOutlined />`*

| Blocco | Composizione | Modulo | Priorità | Sforzo |
|--------|-------------|--------|----------|--------|
| **Dashboard KPI** | Widgets + metriche | `modules/analytics/` ✅ | — | — |
| **Dashboard Builder** | Builder visivo | `modules/analytics/` ⚠️ | P2 | 3gg |
| **Chart Builder** | Grafici (ECharts/Apex/Chart.js) | `modules/analytics/` ✅ | — | — |
| **Report Designer** | Template + dati + formati | `modules/analytics/` ❌ | P2 | 8gg |
| **Export Excel/PDF** | Dati + template | `modules/analytics/` ⚠️ | P2 | 3gg |

---

## 3. Mappa Dipendenze

```
                    ┌─────────────────┐
                    │   Soggetto P1    │◄────────────── Ruolo P2
                    │  (Anagrafica)    │
                    └──────┬──────────┘
                           │
            ┌──────────────┼──────────────┬──────────────────┐
            ▼              ▼              ▼                  ▼
       ┌─────────┐  ┌──────────┐  ┌───────────┐    ┌──────────────┐
       │Cliente  │  │Fornitore │  │Dipendente │    │    Lead      │
       │(Ruolo)  │  │(Ruolo)   │  │(Ruolo)    │    │(Ruolo+CRM)   │
       └────┬────┘  └────┬─────┘  └─────┬─────┘    └──────┬───────┘
            │            │              │                  │
            ▼            ▼              ▼                  ▼
     ┌──────────┐ ┌──────────┐  ┌────────────┐   ┌─────────────┐
     │Ordini    │ │Ordini    │  │ Presenze   │   │Opportunità  │
     │Vendita   │ │Acquisto  │  │ Ferie      │   │Pipeline CRM │
     └────┬─────┘ └────┬─────┘  └────────────┘   └─────────────┘
          │            │
          ▼            ▼
     ┌──────────┐ ┌──────────┐
     │DDT Ven.  │ │DDT Acq.  │
     │Fatture   │ │Entrata   │
     └────┬─────┘ └────┬─────┘
          │            │
          ▼            ▼
     ┌─────────────────────────────────────┐
     │        Movimenti Magazzino          │
     │  (Carico/Scarico da documento)      │
     └────────────────┬────────────────────┘
                      ▼
     ┌─────────────────────────────────────┐
     │       Prima Nota Contabile          │
     │  (Registrazione movimenti econ.)    │
     └────────────────┬────────────────────┘
                      ▼
     ┌─────────────────────────────────────┐
     │     Scadenzario / Partite           │
     └─────────────────────────────────────┘

                        ┌──────────────┐
                        │  Prodotto P3  │◄──────── Categoria P7
                        │  (Catalogo)   │◄──────── UM P9
                        └──────┬───────┘◄──────── Aliquota IVA P8
                               │
                    ┌──────────┼──────────┐
                    ▼          ▼          ▼
               ┌────────┐ ┌────────┐ ┌────────┐
               │Listini │ │BOM     │ │Giacenze│
               │P12     │ │(Produz)│ │P3+P11  │
               └────────┘ └────────┘ └────────┘
```

---

## 4. Architettura Nuovi Moduli

### Pattern Standard (CQRS)

Ogni nuovo modulo backend segue la struttura CQRS consolidata in `products/`/`sales/`/`purchases/`:

```
modules/<nome>/
├── __init__.py                # execute(command) + service singleton
├── service_api.py             # Entry point: execute(command_data)
├── container.py               # DI Container (Injector o manuale)
├── domain/
│   ├── __init__.py
│   ├── models.py              # Dataclass del modello di dominio
│   └── events.py              # Domain Events
├── application/
│   ├── __init__.py
│   ├── commands/
│   │   └── __init__.py        # Command dataclasses (Create, Update, Delete, List, Get)
│   ├── handlers.py            # Command/Query handlers
│   └── queries/
│       └── __init__.py        # Query dataclasses
├── api/
│   └── rest_api.py            # Flask-Smorest Blueprint
└── infrastructure/
    └── repository.py          # SQLAlchemy Repository
```

### Blueprint Registration

```python
from flask_smorest import Blueprint
api = Blueprint('taxes', __name__, url_prefix=f"{API_V1_PREFIX}/tax-rates")
```

### Tenant Context

```python
from core.tenant_context import TenantContext
tenant_id = TenantContext.get_tenant_id()
```

### Schema Database

```python
tenant_id = db.Column(db.String(36), nullable=False)
__table_args__ = (
    db.UniqueConstraint('tenant_id', 'code', name='uq_tenant_code'),
)
```

---

## 5. Frontend: Struttura Menu

### Sidebar.jsx — Nuova struttura "Applicazioni"

```
Applicazioni
├── Anagrafiche                    (submenu)
│   ├── Soggetti                   /anagrafiche
│   ├── Ruoli                      /ruoli
│   ├── Indirizzi                  /indirizzi
│   ├── Comuni                     /comuni
│   ├── Contatti                   /contatti
│   ├── Prodotti                   /products
│   ├── Categorie Prodotto         /product-categories        [NEW]
│   ├── Aliquote IVA              /tax-rates                  [NEW]
│   ├── Unità di Misura           /units-of-measure           [NEW]
│   ├── Listini Prezzo            /price-lists                [NEW]
│   └── Piano dei Conti           /chart-of-accounts           [NEW]
├── Acquisti                       (submenu)
│   ├── Ordini Acquisto            /purchase-orders            [UI]
│   ├── Richieste d'Acquisto      /purchase-requests           [NEW]
│   ├── DDT Entrata Merci         /goods-receipts              [NEW]
│   └── Resi Acquisti             /purchase-returns            [NEW]
├── Vendite                        (submenu)
│   ├── Ordini Vendita             /sales
│   ├── Preventivi                 /quotations                 [NEW]
│   ├── DDT Vendita               /delivery-notes             [NEW]
│   ├── Fatture                    /invoices                   [NEW]
│   ├── Resi Vendita              /sales-returns               [NEW]
│   └── CRM                        /crm                        [NEW]
├── Magazzino                      (submenu)
│   ├── Giacenze                   /stock-levels               [UI]
│   ├── Movimenti                  /stock-movements            [NEW]
│   ├── Inventari                  /inventory-counts           [NEW]
│   └── Lotti/Seriali             /lots                       [NEW]
├── Contabilità                    (submenu)
│   ├── Prima Nota                 /journal                    [NEW]
│   ├── Scadenzario                /maturities                 [NEW]
│   ├── Registri IVA              /vat-registers              [NEW]
│   └── Intrastat                  /intrastat                  [NEW]
├── Produzione                     (submenu)
│   ├── Distinte Base (BOM)       /bom                        [NEW]
│   ├── Cicli di Lavoro           /work-cycles                [NEW]
│   └── Ordini Produzione         /production-orders          [NEW]
├── HR                             (submenu)
│   ├── Dipendenti                 /employees                  [NEW]
│   ├── Reparti                    /departments                [NEW]
│   ├── Presenze                   /attendance                 [NEW]
│   └── Ferie e Permessi          /leave-requests             [NEW]
├── Progetti                       (submenu)
│   ├── Progetti                   /projects
│   ├── Attività                   (dynamic models)
│   ├── Timesheet                  /timesheet                  [NEW]
│   └── Budget Commessa            /project-budgets            [NEW]
└── Analytics                      (submenu)
    ├── Dashboard                  /dashboard
    ├── Dashboard Builder          /dashboard/builder
    ├── Chart Builder              /builder/blocks
    └── Report Designer            /reports                    [NEW]
```

### Modifiche Necessarie

1. **`frontend/src/components/Sidebar.jsx`** — Ristrutturare `appMenuItems` in sezioni annidate per Area. Aggiungere icone dedicate per ogni area. Mantenere compatibilità con `projectMenuItems` (dinamici) che vanno in fondo alla lista o nell'area Progetti.

2. **`frontend/src/components/ui/Navigation/constants.js`** — Aggiornare `DEFAULT_NAVIGATIONS.main` con la struttura ad albero per aree. Aggiungere nuove icone in `DEFAULT_ICONS`.

3. **`frontend/src/App.jsx`** — Aggiungere tutte le nuove route. Ogni nuova pagina usa `GenericCrudPage` o componente dedicato, con `ProtectedRoute`.

4. **`frontend/src/locales/*/translation.json`** — Nuove chiavi per ogni area/blocco:
   ```json
   {
     "menu": {
       "areas": {
         "anagrafiche": "Anagrafiche",
         "acquisti": "Acquisti",
         "vendite": "Vendite",
         "magazzino": "Magazzino",
         "contabilita": "Contabilità",
         "produzione": "Produzione",
         "hr": "Risorse Umane",
         "progetti": "Progetti",
         "analytics": "Analytics"
       },
       "blocks": {
         "categorie": "Categorie Prodotto",
         "aliquoteIva": "Aliquote IVA",
         "unitaMisura": "Unità di Misura",
         "listini": "Listini Prezzo",
         "pianoConti": "Piano dei Conti",
         "richiesteAcquisto": "Richieste d'Acquisto",
         "preventiviFornitori": "Preventivi Fornitori",
         "ddtEntrata": "DDT Entrata Merci",
         "resiAcquisto": "Resi Acquisti",
         "preventivi": "Preventivi",
         "ddtVendita": "DDT Vendita",
         "fatture": "Fatture",
         "resiVendita": "Resi Vendita",
         "crm": "CRM",
         "contratti": "Contratti",
         "giacenze": "Giacenze",
         "movimenti": "Movimenti di Magazzino",
         "inventari": "Inventari Fisici",
         "lotti": "Lotti e Serial Number",
         "primaNota": "Prima Nota",
         "scadenzario": "Scadenzario",
         "registriIva": "Registri IVA",
         "intrastat": "Intrastat",
         "bom": "Distinte Base",
         "cicliLavoro": "Cicli di Lavoro",
         "ordiniProduzione": "Ordini di Produzione",
         "dipendenti": "Dipendenti",
         "reparti": "Reparti",
         "presenze": "Presenze",
         "feriePermessi": "Ferie e Permessi",
         "timesheet": "Timesheet",
         "budgetCommessa": "Budget Commessa",
         "reportDesigner": "Report Designer"
       }
     }
   }
   ```

---

## 6. Piano di Implementazione per Fasi

### Fase 0 — Refactoring Sidebar e Struttura (Frontend)
*Obiettivo: Preparare la struttura a menu per accogliere tutti i blocchi*

**File da modificare:**
- `frontend/src/components/Sidebar.jsx`
- `frontend/src/components/ui/Navigation/constants.js`
- `frontend/src/components/ui/Navigation/AppSidebar.jsx`
- `frontend/src/App.jsx` (aggiungere route placeholder)
- `frontend/src/locales/*/translation.json`

### Fase 1 — Quick Win (P0/P1, ~7gg)
*Colmare i gap che spezzano flussi già iniziati*

| # | Blocco | Modulo | Sforzo | Dipende da |
|---|--------|--------|--------|-----------|
| 1 | **Aliquote IVA** | `modules/tax/` CQRS | 2gg | — |
| 2 | **Categorie Prodotto** | Estensione `products/domain/` | 1gg | — |
| 3 | **Unità di Misura** | `modules/uom/` CQRS | 1gg | — |
| 4 | **Listini Prezzo** | `modules/pricing/` CQRS | 3gg | P3 (Prodotto) |

### Fase 2 — Fondamentali (P1, ~33gg)
*Completare cicli fondamentali dell'ERP*

| # | Blocco | Modulo | Sforzo | Dipende da |
|---|--------|--------|--------|-----------|
| 5 | **Fatturazione Vendita** | `modules/invoicing/` CQRS | 10gg | Ordini, Aliquote IVA, Listini |
| 6 | **Movimenti Magazzino** | `modules/inventory/` CQRS | 5gg | Prodotti, Giacenze, Magazzini |
| 7 | **DDT Entrata Merci** | Estensione `purchases/` | 5gg | Ordini Acquisto, Magazzino |
| 8 | **Prima Nota Contabile** | `modules/accounting/` CQRS | 8gg | Piano dei Conti |
| 9 | **UI Ordini Acquisto** | Pagina frontend | 3gg | Backend `purchases/` ✅ |
| 10 | **Giacenze UI** | Pagina frontend | 2gg | Backend `plugins/inventory/` ⚠️ |

### Fase 3 — Verticali (P1/P2, ~28gg)
*Blocchi verticali di business*

| # | Blocco | Modulo | Sforzo | Dipende da |
|---|--------|--------|--------|-----------|
| 11 | **Scadenzario/Partite** | `modules/accounting/` | 5gg | Fatture, Soggetti |
| 12 | **CRM (Lead/Opportunità)** | `modules/crm/` CQRS | 5gg | Soggetti |
| 13 | **DDT Vendita** | Estensione `sales/` | 5gg | Ordini Vendita, Magazzino |
| 14 | **Preventivi** | Estensione `sales/` | 3gg | Ordini Vendita |
| 15 | **Dipendenti + Reparti** | `modules/hr/` CQRS | 5gg | Soggetti, Ruoli |
| 16 | **Contratti** | `modules/contracts/` CQRS | 5gg | Soggetti, Prodotti |

### Fase 4 — Specializzazioni (P2/P3, ~50gg)
*Estensioni verticali e nicchie*

| # | Blocco | Modulo | Sforzo |
|---|--------|--------|--------|
| 17 | **BOM + Cicli Lavoro + ODP** | `modules/manufacturing/` CQRS | 15gg | ✅ |
| 18 | **Timesheet + Budget Commessa** | `modules/projects/` | 8gg | ✅ |
| 19 | **Report Designer** | `modules/analytics/` | 8gg | ✅ |
| 20 | **HR completo (Presenze, Ferie)** | `modules/hr/` | 8gg | ✅ |
| 21 | **Registri IVA + Intrastat** | `modules/accounting/` | 8gg | ✅ |
| 22 | **Ri.Ba. + Lotti/Seriali** | `modules/accounting/` + `modules/inventory/` | 8gg | ✅ |
| 23 | **Richieste Acquisto + RFQ** | `modules/purchases/` | 8gg | ✅ |
| 24 | **MRP** | `modules/manufacturing/` | 20gg | ✅ |

---

## 7. Template Nuovo Modulo CQRS

### Struttura File

```python
# modules/<nome>/__init__.py
from .service_api import execute
from .domain.models import *
from .domain.events import *
```

```python
# modules/<nome>/service_api.py
def execute(command_data: dict) -> dict:
    from .container import get_container
    container = get_container()
    handler = container.get_command_handler(command_data)
    return handler.handle(command_data)
```

```python
# modules/<nome>/domain/models.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class EntityName:
    id: Optional[str] = None
    tenant_id: Optional[str] = None
    code: str = ""
    name: str = ""
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def validate(self) -> list[str]:
        errors = []
        if not self.code:
            errors.append("code is required")
        if not self.name:
            errors.append("name is required")
        return errors

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}

    @classmethod
    def from_dict(cls, data: dict) -> 'EntityName':
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
```

```python
# modules/<nome>/domain/events.py
from shared.domain_events import DomainEvent

class EntityCreatedEvent(DomainEvent):
    type = "entity.created"

class EntityUpdatedEvent(DomainEvent):
    type = "entity.updated"

class EntityDeletedEvent(DomainEvent):
    type = "entity.deleted"
```

```python
# modules/<nome>/application/commands/__init__.py
from dataclasses import dataclass
from typing import Optional
from shared.commands import Command, CreateCommand, UpdateCommand, DeleteCommand, QueryCommand

@dataclass
class CreateEntityCommand(CreateCommand):
    code: str = ""
    name: str = ""
    is_active: bool = True

@dataclass
class UpdateEntityCommand(UpdateCommand):
    entity_id: str = ""
    code: Optional[str] = None
    name: Optional[str] = None
    is_active: Optional[bool] = None

@dataclass
class DeleteEntityCommand(DeleteCommand):
    entity_id: str = ""

@dataclass
class GetEntityQuery(QueryCommand):
    entity_id: str = ""

@dataclass
class ListEntitiesQuery(QueryCommand):
    search: Optional[str] = None
    is_active: Optional[bool] = None
    page: int = 1
    per_page: int = 20
```

```python
# modules/<nome>/application/handlers.py
from shared.handlers import CommandHandler, CommandResult, CreateHandler, UpdateHandler, DeleteHandler, QueryHandler
from .commands import *
from ..domain.models import EntityName
from ..domain.events import EntityCreatedEvent, EntityUpdatedEvent, EntityDeletedEvent
from ..infrastructure.repository import EntityRepository

class CreateEntityHandler(CreateHandler):
    def __init__(self, repository: EntityRepository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus

    def handle(self, command: CreateEntityCommand) -> CommandResult:
        entity = EntityName.from_dict(command.to_payload())
        errors = entity.validate()
        if errors:
            return CommandResult(success=False, errors=errors)
        created = self.repository.create(entity.to_dict())
        if self.event_bus:
            self.event_bus.publish(EntityCreatedEvent(data=created))
        return CommandResult(success=True, data=created)

class ListEntitiesHandler(QueryHandler):
    def __init__(self, repository: EntityRepository):
        self.repository = repository

    def handle(self, query: ListEntitiesQuery) -> CommandResult:
        result = self.repository.list(vars(query))
        return CommandResult(success=True, data=result)
```

```python
# modules/<nome>/infrastructure/repository.py
from backend.shared.repository import BaseRepository
from backend.models import db

class EntityModel(db.Model):
    __tablename__ = 'entities'
    id = db.Column(db.String(36), primary_key=True)
    tenant_id = db.Column(db.String(36), nullable=False)
    code = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

class EntityRepository(BaseRepository):
    model_cls = EntityModel

    def create(self, data: dict) -> dict:
        instance = self.model_cls(**data)
        db.session.add(instance)
        db.session.commit()
        return instance.to_dict()

    def list(self, filters: dict) -> list:
        query = self.model_cls.query.filter_by(tenant_id=filters.get('tenant_id'))
        if filters.get('search'):
            query = query.filter(self.model_cls.name.ilike(f'%{filters["search"]}%'))
        page = filters.get('page', 1)
        per_page = filters.get('per_page', 20)
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return {
            'items': [item.to_dict() for item in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page
        }
```

```python
# modules/<nome>/api/rest_api.py
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from marshmallow import Schema, fields

api = Blueprint('entities', __name__, description='Entity Management')

class EntitySchema(Schema):
    id = fields.String(dump_only=True)
    code = fields.String(required=True)
    name = fields.String(required=True)
    is_active = fields.Boolean(dump_default=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class EntityQuerySchema(Schema):
    search = fields.String()
    is_active = fields.Boolean()
    page = fields.Integer(dump_default=1)
    per_page = fields.Integer(dump_default=20)

@api.route('/')
class EntityList(MethodView):
    @api.arguments(EntityQuerySchema, location='query')
    @api.response(200, EntitySchema(many=True))
    def get(self, args):
        from ..service_api import execute
        result = execute({'command_type': 'list', **args})
        if not result['success']:
            abort(500, message=str(result.get('errors')))
        return result['data']

    @api.arguments(EntitySchema)
    @api.response(201, EntitySchema)
    def post(self, args):
        from ..service_api import execute
        result = execute({'command_type': 'create', **args})
        if not result['success']:
            abort(400, message=str(result.get('errors')))
        return result['data']
```

---

## Appendice: Riepilogo Time-to-Value

Completando **Fase 0 + Fase 1 + Fase 2** (~47gg/uomo), l'ERP copre i cicli fondamentali:

```
Anagrafiche → Prodotti (con IVA, UM, Categorie, Listini)
    → Ordini Vendita → DDT → Fattura → Movimento Magazzino → Prima Nota → Scadenzario
    → Ordini Acquisto → DDT Entrata → Movimento Magazzino → Prima Nota → Scadenzario
```

**Legenda:**
- ✅ Esistente e funzionante
- ⚠️ Esiste struttura base, da completare
- 🔶 Backend presente, manca UI
- ❌ Da implementare
- ✅ Completato

---

## Appendice A — Analisi Copertura ERP Standard (Giugno 2026)

*A seguire l'analisi della copertura ERPSeed vs ERP standard, che ha guidato la prioritizzazione. Tutti i blocchi marcati come ❌ o 🔶 in questa analisi sono ora ✅ (completati) dopo le Fasi 3-4.*

### Legenda Originale
- ✅ **Presente** — implementato e funzionante
- ⚠️ **Parziale** — esiste struttura base ma mancano funzionalità
- 🔶 **Backend Only** — c'è il backend ma manca UI frontend
- ❌ **Mancante** — non implementato

### Area: Anagrafiche e Dati Base
| Blocco | Allora | Ora | Note |
|--------|--------|-----|------|
| Soggetti (Clienti/Fornitori) | ✅ | ✅ | entities/ + SoggettiPage |
| Ruoli/Settori | ✅ | ✅ | entities/ + RuoliPage |
| Indirizzi | ✅ | ✅ | entities/ + IndirizziPage |
| Contatti | ✅ | ✅ | entities/ + ContattiPage |
| Comuni/Regioni/Province | ✅ | ✅ | entities/ + ComuniPage |
| Prodotti/Servizi | ✅ | ✅ | products/ + Products |
| Categorie Merceologiche | ❌ | ✅ | `modules/product_categories/` |
| Listini Prezzo | ❌ | ✅ | `modules/pricing/` + PriceListsPage |
| Aliquote IVA | ❌ | ✅ | `modules/tax/` + TaxRatesPage |
| Unità di Misura | ⚠️ | ✅ | `modules/uom/` + UnitsOfMeasurePage |
| Magazzini/Depositi | ❌ | ⚠️ | Plugin inventory/ abbozzato |
| Conti Contabili (Piano dei Conti) | ❌ | ⚠️ | Plugin accounting/ presente ma non integrato |

### Area: Logistica e Acquisti
| Blocco | Allora | Ora | Note |
|--------|--------|-----|------|
| Ordini Acquisto | 🔶 | ✅ | UI PurchaseOrdersPage |
| Richiesta d'Acquisto | ❌ | ✅ | `modules/purchase_requests/` |
| Preventivi Fornitori (RFQ) | ❌ | ✅ | `modules/purchase_requests/` + RFQ tab |
| Entrata Merci (DDT) | ❌ | ✅ | `modules/goods_receipt/` |
| Resi Acquisti | ❌ | ❌ | Non ancora implementato |

### Area: Vendite e CRM
| Blocco | Allora | Ora | Note |
|--------|--------|-----|------|
| Ordini Vendita | ✅ | ✅ | sales/ (CQRS) + Sales page |
| Preventivi | ❌ | ✅ | QuotationsPage (via SalesOrder type=quote) |
| Contratti | ❌ | ✅ | `modules/contracts/` |
| DDT Vendita | ❌ | ✅ | DeliveryNotesPage (via SalesOrder type=delivery_note) |
| Fatturazione | ❌ | ✅ | `modules/invoicing/` (CQRS) |
| Resi Vendita | ❌ | ✅ | `modules/sales/` |
| CRM (Lead, Opportunità) | ❌ | ✅ | `modules/crm/` |

### Area: Magazzino e Inventory
| Blocco | Allora | Ora | Note |
|--------|--------|-----|------|
| Giacenze di Magazzino | ⚠️ | ✅ | StockLevelsPage |
| Movimenti di Magazzino | ❌ | ✅ | `modules/inventory/` + StockMovementsPage |
| Inventario Fisico | ❌ | ✅ | `modules/inventory/` |
| Lotto/Serial Number | ❌ | ✅ | `modules/lot/` + LotsPage |
| Picking/Packing | ❌ | ✅ | `modules/inventory/` |

### Area: Contabilità e Finanza
| Blocco | Allora | Ora | Note |
|--------|--------|-----|------|
| Piano dei Conti | ❌ | ⚠️ | Plugin accounting/ presente |
| Prima Nota | ❌ | ✅ | JournalPage |
| Partite Clienti/Fornitori (Scadenzario) | ❌ | ✅ | `modules/maturities/` + MaturitiesPage |
| Fatture (Acquisto/Vendita) | ❌ | ✅ | InvoicesPage + modulo CQRS invoicing |
| Registri IVA | ❌ | ✅ | `modules/vat/` + VatRegistersPage |
| Liquidazione IVA | ❌ | ✅ | `modules/vat/` (automatica da registro) |
| Intrastat | ❌ | ✅ | `modules/vat/` + IntrastatPage |
| Ricevute Bancarie (Ri.Ba.) | ❌ | ✅ | `modules/riba/` + RiBaPage |

### Area: Produzione
| Blocco | Allora | Ora | Note |
|--------|--------|-----|------|
| Distinta Base (BOM) | ❌ | ✅ | `modules/manufacturing/` |
| Ciclo di Lavoro | ❌ | ✅ | `modules/manufacturing/` |
| Ordini di Produzione (ODP) | ❌ | ✅ | `modules/manufacturing/` |
| MRP | ❌ | ✅ | `modules/mrp/` + MRPPage |
| Controllo Qualità | ❌ | ✅ | `modules/manufacturing/` |

### Area: HR e Payroll
| Blocco | Allora | Ora | Note |
|--------|--------|-----|------|
| Dipendenti | ❌ | ✅ | HR tab Employees |
| Presenze/Timbrature | ❌ | ✅ | HR tab Attendance |
| Ferie e Permessi | ❌ | ✅ | HR tab Leave |
| Buste Paga | ❌ | ❌ | Non ancora implementato |
| Formazione | ❌ | ❌ | Non ancora implementato |

### Area: Project Management
| Blocco | Allora | Ora | Note |
|--------|--------|-----|------|
| Progetti | ✅ | ✅ | projects/ CQRS |
| **ER Engine (Relazioni)**| ✅ | ✅ | Gestione visiva (XYFlow), chiavi esterne e Master-Detail |
| Workflow Automation | ✅ | ✅ | automation/ |
| Business Rules | ✅ | ✅ | BusinessRulesPage |
| Timesheet | ❌ | ✅ | `modules/project_management/` |
| Budget Commessa | ❌ | ✅ | `modules/project_management/` (KPI) |

### Area: BI e Analytics
| Blocco | Allora | Ora | Note |
|--------|--------|-----|------|
| Dashboard KPI | ✅ | ✅ | analytics/ + Dashboard |
| Dashboard Builder | ⚠️ | ⚠️ | SysDashboardBuilder presente |
| Chart Builder | ✅ | ✅ | ECharts/ApexCharts/Chart.js |
| Report Designer | ❌ | ✅ | `modules/report_designer/` |
| Export Excel/PDF | ⚠️ | ✅ | PDF via xhtml2pdf, Export CSV |

---

## Appendice B — Guida al Refactoring per Sviluppatori

Quando si modifica un modulo esistente:
1. **Verificare il BaseModel**: Assicurarsi di importare da `backend.core.models.base`.
2. **Usare BaseService**: Se il servizio fa CRUD semplice, non riscrivere i metodi, usa quelli ereditati.
3. **Disaccoppiamento**: Non importare servizi direttamente se possibile; usare il pattern `ServiceProxy` o l'iniezione tramite container.

---

*Ultimo aggiornamento: 2026-06-09*
