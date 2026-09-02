# Piano di Implementazione ERP Blocks

> **Nota:** Questo documento possiede lo stato di avanzamento e l'architettura dei 24 blocchi funzionali ERP. Per la roadmap di qualità del codice e debito tecnico (Fasi 0-4 KISS/DRY), consulta [ROADMAP.md](ROADMAP.md). Per le convenzioni di refactoring per sviluppatori, consulta [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md#convenzioni-di-refactoring).
>
> **Nota sullo Stato Attuale:** Tutti i 24 blocchi ERP pianificati nelle tabelle §1 e §2 sono stati completati e integrati nel sistema. Le tabelle sottostanti riflettono lo stato reale corrente; per il dettaglio sintetico delle fasi vedi [§8 Stato di Avanzamento Attuale](#8-stato-di-avanzamento-attuale-giugno-2026).

---

## Indice
1. [Blocchi Primitivi (Atomi)](#1-blocchi-primitivi-atomi)
2. [Aree Funzionali e Blocchi Compositi](#2-aree-funzionali-e-blocchi-compositi)
3. [Mappa Dipendenze](#3-mappa-dipendenze)
4. [Architettura Nuovi Moduli](#4-architettura-nuovi-moduli)
5. [Frontend: Struttura Menu](#5-frontend-struttura-menu)
6. [Piano di Implementazione per Fasi](#6-piano-di-implementazione-per-fasi)
7. [Template Nuovo Modulo CQRS](#7-template-nuovo-modulo-cqrs)
8. [Stato di Avanzamento Attuale](#8-stato-di-avanzamento-attuale-giugno-2026)
9. [Piano Esecutivo Dettagliato](#9-piano-esecutivo-dettagliato--fase-05)

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
| P5 | **Indirizzo** | `Indirizzo` (via, civico, CAP, città, nazione, comune_id, via_id) + `Via` (cache locale strade per comune) | `entities/` | ✅ |
| P6 | **Comune/Regione/Provincia** | `Comune`, `Regione`, `Provincia` | `entities/` | ✅ |
| P7 | **Categoria** | `ProductCategory` (albero padre-figlio) | `modules/product_categories/` | ✅ |
| P8 | **Aliquota IVA** | `TaxRate` (codice, %, data inizio/fine) | `modules/tax/` | ✅ |
| P9 | **Unità di Misura** | `UnitOfMeasure` (codice, descrizione, simbolo) | `modules/uom/` | ✅ |
| P10 | **Conto Contabile** | `Account` (piano dei conti, tipo, codice) | `modules/accounting/` | ✅ |
| P11 | **Magazzino/Deposito** | `InventoryLocation` (codice, nome, indirizzo) | `modules/inventory/` | ✅ |
| P12 | **Listino Prezzo** | `PriceList` + `PriceListItem` (prodotto, prezzo, sconto) | `modules/pricing/` | ✅ |
| P13 | **Scadenza** | `Maturity` (data, importo, saldo, riferimento) | `modules/maturities/` | ✅ |
| P14 | **Causale Magazzino** | `MovementReason` (codice, tipo: carico/scarico/trasf.) | `modules/inventory/` | ✅ |
| P15 | **Unità Organizzativa** | `Department` (codice, nome, gerarchia) | `modules/hr/` | ✅ |

---

## 2. Aree Funzionali e Blocchi Compositi

Ogni **Area** corrisponde a un submenu di "Applicazioni" nella sidebar.

### Area 1: Anagrafiche e Dati Base
*Submenu: "Anagrafiche" — Icona: `<UserOutlined />`*

| Blocco | Composizione | Modulo | Priorità | Sforzo |
|--------|-------------|--------|----------|--------|
| **Soggetti** | P1 + P2 + P4 + P5 + P6 | `entities/` ✅ | — | — |
| **Ruoli** | P2 | `entities/` ✅ | — | — |
| **Indirizzi** | P5 + P6 + `Via` (cache strade) | `entities/` ✅ | — | — |
| **Comuni** | P6 | `entities/` ✅ | — | — |
| **Contatti** | P4 | `entities/` ✅ | — | — |
| **Prodotti** | P3 + P7 + P8 + P9 + P12 | `modules/products/` ✅ | — | — |
| **Categorie Prodotto** | P7 | `modules/product_categories/` ✅ | — | — |
| **Aliquote IVA** | P8 | `modules/tax/` ✅ | — | — |
| **Unità di Misura** | P9 | `modules/uom/` ✅ | — | — |
| **Listini Prezzo** | P12 + P3 | `modules/pricing/` ✅ | — | — |
| **Piano dei Conti** | P10 | `modules/accounting/` ✅ | — | — |

### Area 2: Logistica e Acquisti
*Submenu: "Acquisti" — Icona: `<ShoppingCartOutlined />`*

| Blocco | Composizione | Modulo | Priorità | Sforzo |
|--------|-------------|--------|----------|--------|
| **Ordini Acquisto** | P1(Fornitore) + P3 + P12 + Documento | `modules/purchases/` ✅ | — | — |
| **Richieste d'Acquisto** | P1 + P3 + Workflow approvazione | `modules/purchase_requests/` ✅ | — | — |
| **Preventivi Fornitori (RFQ)** | P1 + P3 + confronto | `modules/purchase_requests/` ✅ | — | — |
| **Entrata Merci (DDT)** | PO + P3 + P11 + P14 | `modules/goods_receipt/` ✅ | — | — |
| **Resi Acquisti** | PO negativo + P11 + P14 | `modules/purchase_returns/` ✅ | — | — |

### Area 3: Vendite e CRM
*Submenu: "Vendite" — Icona: `<ProjectOutlined />`*

| Blocco | Composizione | Modulo | Priorità | Sforzo |
|--------|-------------|--------|----------|--------|
| **Ordini Vendita** | P1(Cliente) + P3 + P12 + P8 | `modules/sales/` ✅ | — | — |
| **Preventivi** | Stessa struttura Ordine, stato quotazione | `modules/sales/` ✅ | — | — |
| **DDT Vendita** | Ordine → P11 + P14 | `modules/sales/` ✅ | — | — |
| **Fatturazione** | Ordine/DDT + P8 + P10 + P13 + num. automatica | `modules/invoicing/` ✅ | — | — |
| **Resi Vendita** | Negativo su Ordine + P11 + P14 | `modules/sales/` ✅ | — | — |
| **CRM (Lead/Opportunità)** | P1(Lead) + pipeline kanban + attività | `modules/crm/` ✅ | — | — |
| **Contratti** | P1 + Documento + date + rinnovo | `modules/contracts/` ✅ | — | — |

### Area 4: Magazzino e Inventory
*Submenu: "Magazzino" — Icona: `<InboxOutlined />`*

| Blocco | Composizione | Modulo | Priorità | Sforzo |
|--------|-------------|--------|----------|--------|
| **Giacenze** | P3 + P11 + quantità | `modules/inventory/` ✅ | — | — |
| **Movimenti di Magazzino** | P3 + P11 + P14 + qty + riferimento | `modules/inventory/` ✅ | — | — |
| **Inventario Fisico** | P3 + P11 + conteggio + scostamento | `modules/inventory/` ✅ | — | — |
| **Lotto/Serial Number** | P3 + lotto + scadenza + tracciabilità | `modules/lot/` ✅ | — | — |
| **Picking/Packing** | Ordine + P3 + P11 + preparazione | `modules/inventory/` ✅ | — | — |

### Area 5: Contabilità e Finanza
*Submenu: "Contabilità" — Icona: `<DollarOutlined />`*

| Blocco | Composizione | Modulo | Priorità | Sforzo |
|--------|-------------|--------|----------|--------|
| **Piano dei Conti** | P10 | `modules/accounting/` ✅ | — | — |
| **Prima Nota** | P10 + dare/avere + riferimento doc | `modules/accounting/` ✅ | — | — |
| **Scadenzario/Partite** | P13 + P1 + Fattura + solleciti | `modules/maturities/` ✅ | — | — |
| **Registri IVA** | P8 + Prima Nota + periodicità | `modules/vat/` ✅ | — | — |
| **Intrastat** | Report movimenti intra | `modules/vat/` ✅ | — | — |
| **Ri.Ba.** | P13 + banca + incasso | `modules/riba/` ✅ | — | — |

### Area 6: Produzione
*Submenu: "Produzione" — Icona: `<ToolOutlined />`*

| Blocco | Composizione | Modulo | Priorità | Sforzo |
|--------|-------------|--------|----------|--------|
| **Distinta Base (BOM)** | P3(padre) + P3(figli) + quantità | `modules/manufacturing/` ✅ | — | — |
| **Ciclo di Lavoro** | Fasi + risorse + tempi | `modules/manufacturing/` ✅ | — | — |
| **Ordini di Produzione** | BOM + date + qty + stato | `modules/manufacturing/` ✅ | — | — |
| **MRP** | BOM + ordini + giacenze + forecast | `modules/mrp/` ✅ | — | — |
| **Controllo Qualità** | P3 + lotti + collaudi | `modules/manufacturing/` ✅ | — | — |

### Area 7: HR e Payroll
*Submenu: "HR" — Icona: `<TeamOutlined />`*

| Blocco | Composizione | Modulo | Priorità | Sforzo |
|--------|-------------|--------|----------|--------|
| **Dipendenti** | P1(PF) + ruolo dipendente + P15 | `modules/hr/` ✅ | — | — |
| **Reparti** | P15 + P1(Manager) | `modules/hr/` ✅ | — | — |
| **Presenze** | Dipendente + data + check-in/out | `modules/hr/` ✅ | — | — |
| **Ferie e Permessi** | Dipendente + tipo + date + approvazione | `modules/hr/` ✅ | — | — |
| **Formazione** | Dipendente + corso + certificazione | `modules/hr/` ✅ | — | — |

### Area 8: Project Management
*Submenu: "Progetti" — Icona: `<ProjectOutlined />`*

| Blocco | Composizione | Modulo | Priorità | Sforzo |
|--------|-------------|--------|----------|--------|
| **Progetti** | Testata + date + stato + membri | `modules/projects/` ✅ | — | — |
| **Attività/Task** | Progetto + risorsa + date + stato | `modules/project_management/` ✅ | — | — |
| **Timesheet** | P1 + Attività + ore + data | `modules/project_management/` ✅ | — | — |
| **Budget Commessa** | Preventivo + consuntivo + scostamento | `modules/project_management/` ✅ | — | — |
| **Workflow** | Automazione processi | `modules/automation/` ✅ | — | — |
| **Business Rules** | Regole di business | `modules/automation/` ✅ | — | — |

### Area 9: BI e Analytics
*Submenu: "Analytics" — Icona: `<BarChartOutlined />`*

| Blocco | Composizione | Modulo | Priorità | Sforzo |
|--------|-------------|--------|----------|--------|
| **Dashboard KPI** | Widgets + metriche | `modules/analytics/` ✅ | — | — |
| **Dashboard Builder** | Builder visivo | `modules/analytics/` ✅ | — | — |
| **Chart Builder** | Grafici (ECharts/Apex/Chart.js) | `modules/analytics/` ✅ | — | — |
| **Report Designer** | Template + dati + formati | `modules/report_designer/` ✅ | — | — |
| **Export Excel/PDF** | Dati + template | `modules/analytics/` ✅ | — | — |

---

## 3. Mappa Dipendenze

```mermaid
flowchart TD
    Soggetto["Soggetto P1 (Anagrafica)"] <-- Ruolo["Ruolo P2"]
    Soggetto --> Cliente["Cliente (Ruolo)"]
    Soggetto --> Fornitore["Fornitore (Ruolo)"]
    Soggetto --> Dipendente["Dipendente (Ruolo)"]
    Soggetto --> Lead["Lead (Ruolo+CRM)"]

    Cliente --> SalesOrders["Ordini Vendita"]
    Fornitore --> PurchaseOrders["Ordini Acquisto"]
    Dipendente --> Attendance["Presenze / Ferie"]
    Lead --> Opportunities["Opportunità Pipeline CRM"]

    SalesOrders --> OutDocs["DDT Vendita / Fatture"]
    PurchaseOrders --> InDocs["DDT Acquisto / Entrata"]

    OutDocs --> Movements["Movimenti Magazzino"]
    InDocs --> Movements

    Movements --> Accounting["Prima Nota Contabile"]
    Accounting --> Maturities["Scadenzario / Partite"]

    Prodotto["Prodotto P3 (Catalogo)"] <-- Categoria["Categoria P7"]
    Prodotto <-- UM["UM P9"]
    Prodotto <-- Tax["Aliquota IVA P8"]

    Prodotto --> Listini["Listini P12"]
    Prodotto --> BOM["BOM (Produzione)"]
    Prodotto --> Stock["Giacenze P3+P11"]
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

---

## 6. Piano di Implementazione per Fasi

### Fase 0 — Refactoring Sidebar e Struttura (Frontend)
*Obiettivo: Preparare la struttura a menu per accogliere tutti i blocchi*

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

### Fase 4 — Specializzazioni (P2/P3, ~50gg)
*Estensioni verticali e nicchie*

---

## 7. Template Nuovo Modulo CQRS

### Struttura File

```python
# modules/<nome>/__init__.py
from .service_api import execute
from .domain.models import *
from .domain.events import *
```

---

## 8. Stato di Avanzamento Attuale (Giugno 2026)

### Riepilogo Generale

Tutti i 24 blocchi ERP pianificati sono **completati e funzionanti**. Di seguito lo stato aggiornato:

| Area | Blocchi | Stato |
|------|---------|-------|
| **Anagrafiche** | Soggetti, Ruoli, Indirizzi, Contatti, Comuni, Prodotti, Categorie, Aliquote IVA, UM, Listini, **Piano dei Conti** | ✅ 11/11 |
| **Acquisti** | Ordini Acquisto, Richieste d'Acquisto, RFQ, DDT Entrata Merci, **Resi Acquisti** | ✅ 5/5 |
| **Vendite** | Ordini Vendita, Preventivi, Contratti, DDT Vendita, Fatturazione, Resi Vendita, CRM | ✅ 7/7 |
| **Magazzino** | Giacenze, Movimenti, Inventario Fisico, Lotti/Seriali, Picking/Packing | ✅ 5/5 |
| **Contabilità** | Scadenzario, **Bilancio Verifica**, Registri IVA, Liquidazione IVA, Intrastat, Ri.Ba., **Fattura Elettronica** | ✅ 7/7 |
| **Produzione** | BOM, Cicli, ODP, MRP, Controllo Qualità | ✅ 5/5 |
| **HR** | Dipendenti, Presenze, Ferie e Permessi, **Payroll**, **Formazione** | ✅ 5/5 |
| **PM** | Progetti, Timesheet, Budget Commessa, Workflow, Business Rules, ER Engine | ✅ 6/6 |
| **Analytics** | Dashboard KPI, Dashboard Builder, Chart Builder, Workflow Editor, Report Designer, Export | ✅ 6/6 |
| **Sistema** | **Marketplace**, **Import/Export**, **API Docs**, **Redis Cache** | ✅ 4/4 |

---

## 9. Piano Esecutivo Dettagliato — Fase 0→5

### Fase 0 — Stabilizzazione Critica (~3gg)
### Fase 1 — Colmare Gap Funzionali (~12gg)
### Fase 2 — HR Completo (~8gg)
### Fase 3 — Integrazione Contabilità (~8gg)
### Fase 4 — Quality & Performance (~15gg)
### Fase 5 — Estensioni (~13gg)

---

## Stato Avanzamento (2026-06-11)

| Fase | Stato | Note |
|------|-------|------|
| **Fase 0** — Stabilizzazione | ✅ **Completa** | 114 test, fix middleware/date/SQLA 2.0, plugin system fix |
| **Fase 1** — Gap Funzionali | ✅ **Completa** | Resi Acquisti (backend+test), Piano dei Conti UI, Dashboard/Workflow esistenti |
| **Fase 2** — HR Completo | ✅ **Completa** | Payroll + Formazione modelli e API, 16 test HR |
| **Fase 3** — Integrazione Contabile | ✅ **Completa** | Trial Balance UI, from-invoices, VAT/Intrastat già presenti |
| **Fase 4** — Quality & Performance | ✅ **Completa** | 134 test totali (+20), Redis caching, bug fix inventory/VAT/plugin |
| **Fase 5** — Estensioni | ✅ **Completa** | Fattura Elettronica XML, Marketplace UI, Import/Export UI, API Docs sidebar |
| **Fase 6** — Consolidamento | 🔶 **In corso** | i18n (backend gettext core, frontend Sidebar, Dashboard, Soggetti), Workflow Editor, Query Opt |

---

*Per la cronologia completa delle modifiche di questo documento, consulta la cronologia Git del repository.*
