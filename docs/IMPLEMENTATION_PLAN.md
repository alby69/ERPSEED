# Piano di Implementazione ERP Blocks & Stato Moduli

> **Nota:** Questo documento traccia l'architettura e lo stato dei 24 blocchi funzionali ERPSEED.
> Per lo storico delle Fasi 0-5 completate vedi [docs/ARCHIVE/COMPLETED_PHASES.md](ARCHIVE/COMPLETED_PHASES.md). Per la roadmap attiva vedi [ROADMAP.md](ROADMAP.md).

---

## Indice
1. [Blocchi Primitivi (Atomi)](#1-blocchi-primitivi-atomi)
2. [Aree Funzionali e Blocchi Compositi](#2-aree-funzionali-e-blocchi-compositi)
3. [Mappa Dipendenze](#3-mappa-dipendenze)
4. [Architettura Nuovi Moduli (CQRS)](#4-architettura-nuovi-moduli-cqrs)
5. [Stato di Avanzamento Attuale](#5-stato-di-avanzamento-attuale)

---

## 1. Blocchi Primitivi (Atomi)

| # | Primitivo | Modello Backend | Modulo | Stato |
|---|-----------|----------------|--------|-------|
| P0 | **ER Engine** | `SysModel` + `SysField` (Relazioni/FK) | `builder/` | ✅ |
| P1 | **Soggetto** | `Soggetto` (PF/PG, cod.fiscale, P.IVA) | `entities/` | ✅ |
| P2 | **Ruolo** | `Ruolo` (cliente, fornitore, dipendente, lead) | `entities/` | ✅ |
| P3 | **Prodotto** | `Product` (codice, nome, SKU, barcode, UM, peso) | `products/` | ✅ |
| P4 | **Contatto** | `Contatto` (email, tel, PEC, social) | `entities/` | ✅ |
| P5 | **Indirizzo** | `Indirizzo` (via, civico, CAP, città, nazione) | `entities/` | ✅ |
| P6 | **Comune/Regione/Provincia** | `Comune`, `Regione`, `Provincia` | `entities/` | ✅ |
| P7 | **Categoria** | `ProductCategory` (albero padre-figlio) | `modules/product_categories/` | ✅ |
| P8 | **Aliquota IVA** | `TaxRate` (codice, %, data inizio/fine) | `modules/tax/` | ✅ |
| P9 | **Unità di Misura** | `UnitOfMeasure` (codice, descrizione, simbolo) | `modules/uom/` | ✅ |
| P10 | **Conto Contabile** | `Account` (piano dei conti, tipo, codice) | `plugins/accounting/` | ✅ |
| P11 | **Magazzino/Deposito** | `InventoryLocation` (codice, nome, indirizzo) | `modules/inventory/` | ✅ |
| P12 | **Listino Prezzo** | `PriceList` + `PriceListItem` | `modules/pricing/` | ✅ |
| P13 | **Scadenza** | `Maturity` (data, importo, saldo, riferimento) | `modules/maturities/` | ✅ |
| P14 | **Causale Magazzino** | `MovementReason` (codice, tipo: carico/scarico/trasf.) | `modules/inventory/` | ✅ |
| P15 | **Unità Organizzativa** | `Department` (codice, nome, gerarchia) | `plugins/hr/` | ✅ |

---

## 2. Aree Funzionali e Blocchi Compositi

### Riepilogo Aree
1. **Anagrafiche e Dati Base** (Soggetti, Ruoli, Indirizzi, Comuni, Prodotti, Categorie, IVA, UM, Listini, Piano dei Conti) ✅
2. **Acquisti e Logistica** (Ordini, Richieste d'Acquisto, RFQ, DDT Entrata Merci, Resi) ✅
3. **Vendite e CRM** (Ordini, Preventivi, DDT, Fatturazione, Resi, CRM, Contratti) ✅
4. **Magazzino & Inventory** (Giacenze, Movimenti, Inventario Fisico, Lotti/Seriali, Picking) ✅
5. **Contabilità e Finanza** (Prima Nota, Scadenzario, Registri IVA, Intrastat, Ri.Ba, Fatturazione Elettronica XML) ✅
6. **Produzione** (BOM, Cicli di Lavoro, Ordini di Produzione, MRP, Controllo Qualità) ✅
7. **HR e Payroll** (Dipendenti, Reparti, Presenze, Ferie/Permessi, Payroll, Formazione) ✅
8. **Project Management** (Progetti, Task, Timesheet, Budget Commessa, Workflow) ✅
9. **BI e Analytics** (Dashboard KPI, Dashboard Builder, Chart Builder, Report Designer, Export) ✅

---

## 3. Mappa Dipendenze

```mermaid
flowchart TD
    Soggetto["Soggetto P1 (Anagrafica)"] <-- Ruolo["Ruolo P2"]
    Soggetto --> Cliente["Cliente (Ruolo)"]
    Soggetto --> Fornitore["Fornitore (Ruolo)"]

    Cliente --> SalesOrders["Ordini Vendita"]
    Fornitore --> PurchaseOrders["Ordini Acquisto"]

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

## 4. Architettura Nuovi Moduli (CQRS)

Ogni modulo backend segue la struttura CQRS consolidata:

```
modules/<nome>/
├── __init__.py                # execute(command) + service singleton
├── service_api.py             # Entry point: execute(command_data)
├── container.py               # DI Container
├── domain/
│   ├── models.py              # Dataclass del modello di dominio
│   └── events.py              # Domain Events
├── application/
│   ├── commands/              # Command dataclasses
│   ├── handlers.py            # Command/Query handlers
│   └── queries/               # Query dataclasses
├── api/
│   └── rest_api.py            # Flask-Smorest Blueprint
└── infrastructure/
    └── repository.py          # SQLAlchemy Repository
```

---

## 5. Stato di Avanzamento Attuale

Tutti i 24 blocchi ERP pianificati sono **completati e funzionanti**.

Per i dettagli dello storico delle implementazioni da Fase 0 a Fase 5, fai riferimento a [docs/ARCHIVE/COMPLETED_PHASES.md](ARCHIVE/COMPLETED_PHASES.md).

---

---

> Ultimo aggiornamento: 10 Settembre 2026 | [Torna all'Indice](INDEX.md)
