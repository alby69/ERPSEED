# ERPaaS - Piano di Sviluppo Moduli

## Documento #03 - Roadmap Moduli e Dipendenze

---

## 1. Stato Attuale dei Moduli

### Legenda

| Simbolo | Significato |
|---------|-------------|
| ✅ | Completato e funzionante |
| 🟡 | Funzionante con limitazioni |
| ⏳ | Non ancora iniziato |

### 1.1 Moduli Esistenti

| Modulo | Stato | Percorso | Completamento |
|--------|-------|----------|---------------|
| **Core Multi-Tenant** | ✅ | `backend/core/` | 100% |
| **Parties** | ✅ | `backend/parties.py` | 95% |
| **Products** | ✅ | `backend/products.py` | 95% |
| **Sales** | ✅ | `backend/sales.py` | 95% |
| **Inventory** | ✅ | `backend/plugins/inventory/` | 95% |
| **Purchases** | ✅ | `backend/purchases.py` | 95% |
| **Accounting** | 🟡 | `backend/plugins/accounting/` | 70% |
| **HR** | 🟡 | `backend/plugins/hr/` | 50% |
| **Dashboard** | 🟡 | `backend/dashboard.py` | 40% |
| **Base Plugin System** | ✅ | `backend/plugins/base.py` | 100% |

### 1.2 Dettaglio Moduli Esistenti

#### ✅ Core Multi-Tenant (100%)

```
Componenti:
├── BaseModel con tenant_id
├── Tenant, User, AuditLog
├── TenantContext, TenantMiddleware
├── AuthService, PermissionService
├── API Auth e Tenant
└── Test coverage ~83%
```

#### ✅ Parties (95%)

```
Entità:
├── Party (anagrafica)
├── PartyAddress (indirizzi)
├── PartyContact (contatti)
└── PartyGroup (gruppi)

Funzionalità:
├── CRUD completo
├── Ricerca e filtri
└── Filtraggio automatico tenant

Mancante: Import/Export avanzato
```

#### ✅ Products (95%)

```
Entità:
├── Product (prodotto)
├── ProductCategory (gerarchia)
├── ProductVariant (varianti)
├── ProductPrice (listini)
└── PriceList

Funzionalità:
├── CRUD completo
├── Categorie gerarchiche
├── Varianti prodotto
└── Listini multipli

Mancante: Immagini prodotto
```

#### ✅ Sales (95%)

```
Entità:
├── SalesOrder, SalesOrderLine
├── SalesQuote, SalesQuoteLine
├── SalesDelivery, SalesDeliveryLine
└── PaymentTerm

Funzionalità:
├── CRUD ordini e preventivi
├── Workflow ordine (draft→confirmed→shipped)
├── Calcoli totali automatici
└── Conversione preventivo→ordine

Mancante: PDF generazione
```

#### ✅ Inventory (95%)

```
Entità:
├── InventoryLocation
├── ProductStock
├── StockMovement
├── InventoryCount
└── InventoryCountLine

Funzionalità:
├── Movimenti carico/scarico
├── Giacenze per magazzino
├── Inventario
└── Test isolation multi-tenant
```

#### ✅ Purchases (95%)

```
Entità:
├── PurchaseOrder
└── PurchaseOrderLine

Funzionalità:
├── CRUD ordini fornitore
├── Conferma ordine
└── Ricezione merce
```

#### 🟡 Accounting (70%)

```
Entità:
├── ChartOfAccounts (Piano dei Conti)
├── Account (Conti correnti)
├── JournalEntry (Partita doppia)
├── JournalEntryLine (Righe partita)
├── Invoice (Fatture attive/passive)
└── InvoiceLine (Righe fattura)

Funzionante:
├── CRUD completo
├── Partita doppia
├── Report Trial Balance
└── Filtraggio tenant

Mancante:
- Generazione PDF fatture
- Integrazione SDI (fattura elettronica)
- Scadenzario pagamenti
- Bilancio riclassificato
```

#### 🟡 HR (50%)

```
Entità:
├── Department (Reparti)
├── Employee (Dipendenti)
├── Attendance (Presenze)
└── LeaveRequest (Ferie/permessi)

Funzionante:
├── CRUD base dipendenti
└── Presenze base

Mancante:
- Timesheet settimanale
- Calcolo stipendi
- Documenti dipendenti
- Dashboard HR
- API complete
```

#### 🟡 Dashboard (40%)

```
Funzionante:
├── KPI summary (clienti, fornitori, prodotti)
├── Sales summary per stato
├── Purchases summary per stato
└── Recent orders

Mancante:
- Grafici
- Report avanzati
- UI dedicata
```

---

## 2. Piano di Sviluppo Moduli

### 2.1 Moduli Previsti

| # | Modulo | Descrizione | Priorità | Dipendenze |
|---|--------|-------------|----------|------------|
| 1 | **Core/Base** | Utenti, Auth, Anagrafiche base | 🔴 Critica | - |
| 2 | **Parties** | Clienti, Fornitori, Contatti | 🔴 Critica | Core |
| 3 | **Products** | Catalogo prodotti/servizi | 🔴 Critica | Core |
| 4 | **Inventory** | Magazzino, movimenti stock | 🔴 Critica | Products, Parties |
| 5 | **Sales** | Ordini cliente, offerte | 🔴 Critica | Parties, Products |
| 6 | **Purchases** | Ordini fornitore | 🟡 Alta | Parties, Products |
| 7 | **Accounting** | Contabilità, fatture | 🟡 Alta | Parties (esistente) |
| 8 | **HR** | Gestione personale | 🟡 Alta | Core (esistente) |
| 9 | **Projects** | Gestione progetti | 🟢 Media | Parties, HR |
| 10 | **CRM** | Leads, pipeline vendite | 🟢 Media | Parties |
| 11 | **Dashboard** | KPI e report | 🟢 Media | Tutti |
| 12 | **Documents** | Archiviazione documenti | 🔵 Bassa | Core |
| 13 | **Manufacturing** | Distinte basi, produzione | 🔵 Bassa | Products, Inventory |
| 14 | **POS** | Punto vendita | 🔵 Bassa | Sales, Inventory |
| 15 | **E-commerce** | Negozio online | 🔵 Bassa | Products, Sales |

---

## 3. Dipendenze tra Moduli

### 3.1 Grafico Dipendenze

```
                         ┌─────────────┐
                         │    CORE     │
                         │  (Auth,    │
                         │   Users)    │
                         └──────┬──────┘
                                │
           ┌───────────────────┼───────────────────┐
           │                   │                   │
           ▼                   ▼                   ▼
    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
    │  PARTIES    │    │  PRODUCTS   │    │  PARTIES    │
    │ (Clienti,   │    │ (Catalogo)  │    │ (Fornitori) │
    │  Fornitori) │    └──────┬──────┘    └──────┬──────┘
    └──────┬──────┘           │                   │
           │                  │                   │
           │           ┌──────┴──────┐             │
           │           │             │             │
           ▼           ▼             ▼             ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │   SALES     │ │ INVENTORY   │ │  PURCHASES  │ │    CRM      │
    │  (Ordini)   │ │ (Magazzino) │ │  (Acquisti) │ │  (Leads)    │
    └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
           │               │               │               │
           └───────────────┴───────┬───────┴───────────────┘
                                   │
                                   ▼
                          ┌─────────────┐
                          │  ACCOUNTING │
                          │ (Contabilità│
                          │  Fatture)   │
                          └──────┬──────┘
                                 │
                                 ▼
                          ┌─────────────┐
                          │  PROJECTS   │
                          │ (Gestione   │
                          │  Progetti)  │
                          └─────────────┘
```

### 3.2 Tabella Dipendenze Dettagliata

| Modulo | Dipende da | Richiesto da |
|--------|------------|--------------|
| Core | - | Tutti |
| Parties | Core | Sales, Purchases, Accounting, CRM, Projects |
| Products | Core | Inventory, Sales, Purchases, POS, E-commerce |
| Inventory | Products | POS, Manufacturing |
| Sales | Parties, Products | Accounting, POS, E-commerce |
| Purchases | Parties, Products | Inventory, Accounting |
| Accounting | Parties, Sales, Purchases | Dashboard |
| HR | Core | Projects |
| Projects | Parties, HR | Dashboard |
| CRM | Parties | - |
| Dashboard | Tutti | - |

---

## 4. Roadmap di Sviluppo

### Fase 1: Fondamenta (Settimane 1-4)

**Obiettivo**: MVP funzionale con moduli essenziali

| Settimana | Modulo | Attività |
|-----------|--------|----------|
| 1 | **Core** | Refactoring auth, aggiungere tenant_id, |
| 2 | **Parties** | CRUD clienti/fornitori, ricerca, filtri |
| 3 | **Products** | CRUD prodotti, categorie, listini |
| 4 | **Sales** | Ordini cliente, righe, stati |

**Deliverable Fase 1**:
- [ ] Sistema multi-tenant funzionante
- [ ] Gestione anagrafiche completa
- [ ] Catalogo prodotti
- [ ] Creazione ordini cliente

---

### Fase 2: Operatività (Settimane 5-8)

**Obiettivo**: Gestione operativa base

| Settimana | Modulo | Attività |
|-----------|--------|----------|
| 5 | **Inventory** | Movimenti stock, giacenze, alert |
| 6 | **Purchases** | Ordini fornitore, ricevimento |
| 7 | **Accounting** | Integrazione fatture, partita doppia |
| 8 | **HR** | Dipendenti, presenze base |

**Deliverable Fase 2**:
- [ ] Gestione magazzino
- [ ] Ordini fornitore
- [ ] Contabilità base
- [ ] Gestione personale

---

### Fase 3: Crescita (Settimane 9-12)

**Obiettivo**: Funzionalità avanzate

| Settimana | Modulo | Attività |
|-----------|--------|----------|
| 9 | **Projects** | Task, milestone, tempi |
| 10 | **CRM** | Pipeline leads, attività |
| 11 | **Dashboard** | KPI, report, export |
| 12 | **Documents** | Upload, archiviazione |

**Deliverable Fase 3**:
- [ ] Gestione progetti
- [ ] CRM base
- [ ] Dashboard analitiche
- [ ] Documenti allegati

---

### Fase 4: Espansione (Settimane 13-16)

**Obiettivo**: Moduli specializzati

| Settimana | Modulo | Attività |
|-----------|--------|----------|
| 13 | **Manufacturing** | Distinte basi, cicli |
| 14 | **POS** | Punto vendita |
| 15 | **E-commerce** | Negozio base |
| 16 | **Review** | Bug fix, ottimizzazioni |

**Deliverable Fase 4**:
- [ ] Produzione
- [ ] POS
- [ ] E-commerce base

---

## 5. Template Predefiniti

### 5.1 Template Consigliati per Mercato Italiano

Basandosi sul target PMI/Freelance italiano:

| Template | Moduli Inclusi | Target | Complessità |
|----------|---------------|--------|-------------|
| **Micro** | Core + Parties + Products | Freelance, artigiani | Bassa |
| **Negozio** | Micro + Inventory + Sales | Piccolo retail | Media |
| **Profesional** | Negozio + Accounting | Commercialisti | Media |
| **Business** | Professional + HR + Projects | PMI | Alta |
| **Enterprise** | Tutti i moduli | Grandi aziende | Molto alta |

### 5.2 Template "Micro" (Priorità Massima)

```
Target: Freelance, piccoli professionisti

Moduli:
├── Core (utenti, auth)
├── Parties (clienti)
├── Products (servizi/prodotti)
└── Sales (preventivi/ordini)

Stima sviluppo: 2-3 settimane
```

### 5.3 Template "Negozio" (Seconda Priorità)

```
Target: Negozi retail, piccola distribuzione

Moduli:
├── Template Micro
├── Inventory (magazzino)
├── POS (punto vendita)
└── Basic Reporting

Stima sviluppo: 4-6 settimane
```

---

## 6. Criteri di Priorità

### 6.1 Matrice Impatto/Sforzo

```
                BASSO SFORZO          ALTO SFORZO
              ┌────────────────────┬────────────────────┐
   ALTO       │                    │                    │
   IMPATTO    │  Parties           │  Accounting        │
              │  Products          │  Inventory         │
              │  Sales             │  Projects          │
              ├────────────────────┼────────────────────┤
   BASSO      │                    │                    │
   IMPATTO    │  Documents         │  Manufacturing    │
              │  CRM               │  E-commerce        │
              │  Dashboard         │  POS               │
              └────────────────────┴────────────────────┘
```

### 6.2 Ordine di Sviluppo Raccomandato

| # | Modulo | Stato Attuale | Prossimo Step |
|---|--------|---------------|---------------|
| 1 | **Core** | ✅ Completo | Manutenzione |
| 2 | **Parties** | ✅ Completo | Manutenzione |
| 3 | **Products** | ✅ Completo | Manutenzione |
| 4 | **Sales** | ✅ Completo | PDF generation |
| 5 | **Inventory** | ✅ Completo | Manutenzione |
| 6 | **Purchases** | ✅ Completo | Manutenzione |
| 7 | **Accounting** | 🟡 70% | PDF, SDI, Scadenzario |
| 8 | **HR** | 🟡 50% | API complete, Dashboard |
| 9 | **Dashboard** | 🟡 40% | UI, Grafici, Report |
| 10 | **Projects** | ⏳ Non iniziato | Da sviluppare |
| 11 | **CRM** | ⏳ Non iniziato | Da sviluppare |
| 12 | **Documents** | ⏳ Non iniziato | Da sviluppare |
| 13 | **Manufacturing** | ⏳ Non iniziato | Futuro |
| 14 | **POS** | ⏳ Non iniziato | Futuro |
| 15 | **E-commerce** | ⏳ Non iniziato | Futuro |

---

## 7. Specifiche Moduli

### 7.1 Modulo Core

```
Modulo: CORE
Descrizione: Funzionalità base del sistema
Priorità: 🔴 Critica

Entità:
├── User (utenti sistema)
├── Tenant (aziende/clienti)
├── UserRole (ruoli)
└── UserPermission (permessi)

Funzionalità:
├── Autenticazione JWT
├── Gestione ruoli e permessi
├── Multi-tenant isolation
├── Audit log
└── API REST base
```

### 7.2 Modulo Parties

```
Modulo: PARTIES
Descrizione: Anagrafiche clienti e fornitori
Priorità: 🔴 Critica
Dipendenze: Core

Entità:
├── Party (anagrafica)
├── PartyType (tipologia)
├── PartyAddress (indirizzi)
├── PartyContact (contatti)
└── PartyGroup (gruppi)

Funzionalità:
├── CRUD anagrafiche
├── Ricerca avanzata
├── Import/export CSV
├── Validazione partita IVA
├── Validazione codice fiscale
└── Gestione indirizzi multipli
```

### 7.3 Modulo Products

```
Modulo: PRODUCTS
Descrizione: Catalogo prodotti e servizi
Priorità: 🔴 Critica
Dipendenze: Core

Entità:
├── Product (prodotto)
├── ProductCategory (categoria)
├── ProductVariant (varianti)
├── ProductPrice (listini)
└── ProductSupplier (fornitori)

Funzionalità:
├── CRUD prodotti
├── Categorie e tag
├── Varianti (taglia, colore)
├── Multiple listini prezzi
├── Codici a barre
└── Immagini prodotto
```

### 7.4 Modulo Inventory

```
Modulo: INVENTORY
Descrizione: Gestione magazzino
Priorità: 🔴 Critica
Dipendenze: Products, Parties

Entità:
├── Warehouse (magazzino)
├── StockLocation (ubicazione)
├── StockMove (movimento)
├── StockQuant (giacenza)
└── StockReservation (prenotazione)

Funzionalità:
├── Movimenti di carico/scarico
├── Giacenze per magazzino
├── Alert scorte minime
├── Inventario
├── Tracciabilità lotti
└── Valorizzazione magazzino
```

### 7.5 Modulo Sales

```
Modulo: SALES
Descrizione: Gestione vendite
Priorità: 🔴 Critica
Dipendenze: Parties, Products

Entità:
├── SalesOrder (ordine)
├── SalesOrderLine (riga)
├── SalesQuote (preventivo)
├── SalesQuoteLine (riga)
├── SalesChannel (canale)
└── SalesAnalytics (analytics)

Funzionalità:
├── Preventivi
├── Ordini cliente
├── Conversione preventivi in ordini
├── Stati ordine (draft, confirmed, shipped, done)
├── Sconti per quantità
├── Totali automatici
└── Export PDF ordine
```

---

## 8. Checklist Sviluppo Modulo

Per ogni modulo, assicurarsi di:

### 8.1 Database

- [ ] Modelli SQLAlchemy definiti
- [ ] Relazioni configurate
- [ ] Migration creata
- [ ] Indici appropriati
- [ ] Tenant_id su tutti i modelli

### 8.2 API

- [ ] Schema Marshmallow
- [ ] CRUD endpoints completi
- [ ] Validazione input
- [ ] Error handling
- [ ] Documentazione OpenAPI

### 8.3 Business Logic

- [ ] Service layer
- [ ] Logica di negocio
- [ ] Calcoli automatici
- [ ] Notifiche eventi

### 8.4 Testing

- [ ] Test unitari modelli
- [ ] Test API
- [ ] Test integrazione

### 8.5 Documentazione

- [ ] README modulo
- [ ] Schema ER
- [ ] API documentation

---

## 9. Stima Tempo per Modulo

### 9.1 Tempo per Modulo (Team 1-2 persone)

| Modulo | Sviluppo | Testing | Totale |
|--------|----------|---------|--------|
| Core | 40h | 10h | 50h |
| Parties | 24h | 6h | 30h |
| Products | 24h | 6h | 30h |
| Sales | 32h | 8h | 40h |
| Inventory | 40h | 10h | 50h |
| Purchases | 32h | 8h | 40h |
| Accounting | 48h | 12h | 60h |
| HR | 32h | 8h | 40h |
| Projects | 40h | 10h | 50h |
| CRM | 32h | 8h | 40h |
| Dashboard | 24h | 6h | 30h |
| Documents | 24h | 6h | 30h |
| Manufacturing | 48h | 12h | 60h |
| POS | 40h | 10h | 50h |
| E-commerce | 60h | 15h | 75h |

### 9.2 Roadmap Temporale Totale

```
Fase 1 (Core + Base):     ~150h  →  4 settimane
Fase 2 (Operatività):     ~180h  →  4 settimane
Fase 3 (Crescita):        ~150h  →  4 settimane
Fase 4 (Espansione):      ~215h  →  4 settimane

TOTALE:                   ~695h  →  16 settimane (~4 mesi)
```

---

## 10. Prossimi Passi

### Immediati (Questa Settimana)

1. [ ] Completare refactoring Core con multi-tenant
2. [ ] Aggiungere modello Tenant
3. [ ] Implementare Party CRUD

### Breve Termine (2-4 Settimane)

1. [ ] Completare modulo Products
2. [ ] Implementare modulo Sales base
3. [ ] Aggiungere migrazioni database

### Medio Termine (1-2 Mesi)

1. [ ] Completare accounting
2. [ ] Implementare inventory
3. [ ] Primo template funzionante ("Micro")

---

## 11. Glossario Moduli

| Termine | Definizione |
|---------|-------------|
| **Modulo** | Insieme di funzionalità correlate |
| **Entità** | Tabella/oggetto del database |
| **Template** | Insieme preconfigurato di moduli |
| **Dipendenza** | Modulo richiesto per funzionamento |
| **Migration** | Script modifica schema database |
| **Service Layer** | Logica di business separata da API |

---

*Documento generato il 18 Febbraio 2026*
*Progetto: FlaskERP ERPaaS Platform*
*Documento #03 - Piano di Sviluppo Moduli*
