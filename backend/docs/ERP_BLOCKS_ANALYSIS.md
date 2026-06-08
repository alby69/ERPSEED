# Analisi Blocchi Applicativi ERP

## 1. Stato Attuale

### Menu "Applicazioni" (Sidebar)
| Blocco | Route | Backend Module | Tipo | Stato |
|--------|-------|---------------|------|-------|
| Anagrafiche (Soggetti) | `/anagrafiche` | `modules/entities/` | Vision Archetype | ✅ |
| Ruoli | `/ruoli` | `modules/entities/` | Vision Archetype | ✅ |
| Indirizzi | `/indirizzi` | `modules/entities/` | Vision Archetype | ✅ |
| Comuni | `/comuni` | `modules/entities/comuni_routes.py` | Vision Archetype | ✅ |
| Contatti | `/contatti` | `modules/entities/` | Vision Archetype | ✅ |
| Prodotti | `/products` | `modules/products/` | CQRS | ✅ |
| Vendite | `/sales` | `modules/sales/` | CQRS | ✅ |
| Modelli dinamici (per progetto) | `/projects/:id/data/:model` | `modules/dynamic_api/` | Dynamic | ✅ |

### Backend Modules Esistenti
| Modulo | Directory | Pattern | API Exposure |
|--------|-----------|---------|-------------|
| **entities** | `modules/entities/` | MVC (Model-Schema-Route) | `/api/v1/{soggetti,ruoli,indirizzi,contatti,comuni}` |
| **products** | `modules/products/` | CQRS (ServiceAPI-Handler-Repo) | `/api/v1/products` |
| **sales** | `modules/sales/` | CQRS | `/api/v1/sales-orders` |
| **purchases** | `modules/purchases/` | CQRS | `/api/v1/purchase-orders` (backend only) |
| **analytics** | `modules/analytics/` | CQRS | `/api/v1/dashboard/*`, KPI |
| **automation** | `modules/automation/` | CQRS | `/api/v1/workflows`, `/api/v1/webhooks` |
| **ai** | `modules/ai/` | Service + Adapters | `/api/v1/ai/*` |
| **builder** | `modules/builder/` | CQRS | `/api/v1/builder/*` |
| **dynamic_api** | `modules/dynamic_api/` | Service + Routes | `/api/v1/projects/:id/data/*` |
| **gdo** | `modules/gdo/` | Service only | Tool frontend `/gdo-reconciliation` |
| **projects** | `modules/projects/` | CQRS | `/api/v1/projects/*` |
| **users** | `modules/users/` | CQRS | backend only (auth via core) |
| **system_tools** | `modules/system_tools/` | API direct | template, versioning, debug |

---

## 2. Blocchi ERP Standard vs ERPSeed Coverage

### Legenda
- ✅ **Presente** — implementato e funzionante
- ⚠️ **Parziale** — esiste struttura base ma mancano funzionalità
- 🔶 **Backend Only** — c'è il backend ma manca UI frontend
- ❌ **Mancante** — non implementato

### Area: Anagrafiche e Dati Base
| Blocco | Coverage | Note |
|--------|----------|------|
| Soggetti (Clienti/Fornitori) | ✅ | entities/ + SoggettiPage |
| Ruoli/Settori | ✅ | entities/ + RuoliPage |
| Indirizzi | ✅ | entities/ + IndirizziPage |
| Contatti | ✅ | entities/ + ContattiPage |
| Comuni/Regioni/Province | ✅ | entities/ + ComuniPage |
| Prodotti/Servizi | ✅ | products/ + Products|
| **Categorie Merceologiche** | ❌ | Manca modello categorie prodotto |
| **Listini Prezzo** | ❌ | Manca gestione listini e prezzi per cliente |
| **Aliquote IVA** | ❌ | Manca tabella aliquote IVA |
| **Unità di Misura** | ⚠️ | Solo enum in Product, manca tabella dedicata |
| **Magazzini/Depositi** | ❌ | Manca gestione sedi fisiche |
| **Conti Contabili (Piano dei Conti)** | ❌ | Plugin accounting/ abbozzato ma non integrato |

### Area: Logistica e Acquisti
| Blocco | Coverage | Note |
|--------|----------|------|
| Ordini Acquisto | 🔶 | Backend `modules/purchases/` CQRS, manca UI |
| **Richiesta d'Acquisto** | ❌ | workflow di richiesta + approvazione |
| **Preventivi Fornitori** | ❌ | RFQ con confronto prezzi |
| **Entrata Merci (DDT)** | ❌ | Documento di Trasporto in entrata |
| **Resi Acquisti** | ❌ | Gestione resi a fornitore |

### Area: Vendite e CRM
| Blocco | Coverage | Note |
|--------|----------|------|
| Ordini Vendita | ✅ | sales/ + Sales page + OrderDetail |
| **Preventivi** | ❌ | workflow preventivo → ordine |
| **Contratti** | ❌ | Contratti clienti con scadenze |
| **DDT Vendita** | ❌ | Documento di Trasporto in uscita |
| **Fatturazione** | ❌ | Emissione fatture (elettronica?) |
| **Resi Vendita** | ❌ | Gestione resi da cliente |
| **CRM (Attività, Opportunità)** | ❌ | Gestione relazione clienti |

### Area: Magazzino e Inventory
| Blocco | Coverage | Note |
|--------|----------|------|
| **Giacenze di Magazzino** | ⚠️ | ProductStockModel esiste, manca UI |
| **Movimenti di Magazzino** | ❌ | Carico/Scarico/Trasferimento |
| **Inventario Fisico** | ❌ | Conteggio e allineamento |
| **Lotto/Serial Number** | ❌ | Tracciabilità lotti |
| **Picking/Packing** | ❌ | Preparazione ordini |

### Area: Contabilità e Finanza
| Blocco | Coverage | Note |
|--------|----------|------|
| **Piano dei Conti** | ❌ | Plugin accounting/ con CoaAccount ma non integrato |
| **Prima Nota** | ❌ | Registrazione movimenti contabili |
| **Partite Clienti/Fornitori** | ❌ | Scadenzario e solleciti |
| **Fatture (Acquisto/Vendita)** | ❌ | Sia emesse che ricevute |
| **Intrastat** | ❌ | Dichiarazioni intracomunitarie |
| **Ricevute Bancarie (Ri.Ba.)** | ❌ | Incasso tramite banca |

### Area: Produzione
| Blocco | Coverage | Note |
|--------|----------|------|
| **Distinta Base (BOM)** | ❌ | Struttura prodotto finito |
| **Ciclo di Lavoro** | ❌ | Fasi produttive |
| **Ordini di Produzione** | ❌ | Pianificazione produzione |
| **MRP** | ❌ | Material Requirements Planning |
| **Controllo Qualità** | ❌ | Collaudi e certificazioni |

### Area: HR e Payroll
| Blocco | Coverage | Note |
|--------|----------|------|
| **Dipendenti** | ❌ | Plugin hr/ abbozzato ma non integrato |
| **Presenze/Timbrature** | ❌ | Rilevazione presenze |
| **Ferie e Permessi** | ❌ | Gestione richieste e saldi |
| **Buste Paga** | ❌ | Elaborazione cedolini |
| **Formazione** | ❌ | Corsi e certificazioni |

### Area: Project Management
| Blocco | Coverage | Note |
|--------|----------|------|
| Progetti | ✅ | projects/ CQRS + ProjectLayout |
| Attività/Task | ⚠️ | Possibile via Dynamic Model |
| Workflow Automation | ✅ | automation/ + WorkflowBuilder |
| Business Rules | ✅ | BusinessRulesPage |
| **Timesheet** | ❌ | Ore su commessa |
| **Budget Commessa** | ❌ | Preventivo vs consuntivo |

### Area: BI e Analytics
| Blocco | Coverage | Note |
|--------|----------|------|
| Dashboard KPI | ✅ | analytics/ + Dashboard |
| Dashboard Builder | ⚠️ | SysDashboardBuilder presente, da completare |
| Chart Builder | ✅ | SysChartBuilder + ECharts/ApexCharts/Chart.js |
| **Report Designer** | ❌ | Report personalizzabili |
| **Export Excel/PDF** | ⚠️ | PDF via xhtml2pdf, Export CSV base |

---

## 3. Raccomandazioni di Priorità e Struttura

### Criteri di Priorità
- **P0 — Critico**: Blocca flussi operativi fondamentali (es. non si può completare ciclo acquisti/vendite)
- **P1 — Alto**: Funzionalità core attese da un ERP
- **P2 — Medio**: Miglioramento significativo dell'usabilità
- **P3 — Basso**: Nice-to-have, estensioni verticali

### Fase 1 (Immediata — P0/P1)
Colmare i gap che spezzano flussi già iniziati:

| Blocco | Priorità | Sforzo | Strategy |
|--------|----------|--------|----------|
| **Aliquote IVA** | P0 | 2gg | Nuovo modulo `modules/tax/` CQRS. Tabella `tax_rates` con codice, descrizione, percentuale, iniziata/termine validità. API `/api/v1/tax-rates`. Integrato in Product. |
| **Listini Prezzo** | P0 | 3gg | Nuovo modulo `modules/pricing/` CQRS. Modello `PriceList` (nome, valuta) + `PriceListItem` (product_id, prezzo, sconto max). API `/api/v1/price-lists`. |
| **Categorie Prodotto** | P1 | 1gg | Aggiungere modello `ProductCategory` in `modules/products/domain/` con alberatura (padre-figlio). API `/api/v1/product-categories`. |
| **Ricezione Merci (DDT Acquisto)** | P1 | 5gg | Completare flusso acquisti esistente: `PurchaseOrder` → `GoodsReceipt` (DDT). Nuovo modello in `modules/purchases/`. |

### Fase 2 (Breve Termine — P1)
Completare cicli fondamentali:

| Blocco | Priorità | Sforzo | Strategy |
|--------|----------|--------|----------|
| **Fatturazione Vendita** | P1 | 10gg | Modulo `modules/invoicing/` CQRS. `Invoice` con testata/righe, numerazione automatica, stato (bozza/emessa/annullata). Integrazione con Sales per generazione da ordine. |
| **Movimenti Magazzino** | P1 | 5gg | Estendere `modules/products/` con `StockMovement` (prodotto, magazzino, quantità, tipo, riferimento). API `/api/v1/stock-movements`. |
| **Prima Nota Contabile** | P1 | 8gg | Modulo `modules/accounting/` CQRS. `JournalEntry` con testata/righe, piano dei conti, dare/avere. |
| **Scadenzario Clienti/Fornitori** | P1 | 5gg | Modello `Maturity` collegato a fatture, con data scadenza, saldo, solleciti. |

### Fase 3 (Medio Termine — P1/P2)
Blocchi verticali:

| Blocco | Priorità | Sforzo | Strategy |
|--------|----------|--------|----------|
| **CRM (Opportunità)** | P1 | 5gg | Modulo `modules/crm/` CQRS. Lead/Opportunità/Attività, pipeline kanban. |
| **Contratti** | P2 | 5gg | Modulo `modules/contracts/` CQRS. Contratto, versioni, rinnovo automatico, allegati. |
| **Dipendenti** | P2 | 5gg | Modulo `modules/hr/` CQRS. Anagrafica dipendente, contratto, documenti. |

### Fase 4 (Lungo Termine — P2/P3)
Specializzazioni verticali:

| Blocco | Priorità | Sforzo | Strategy |
|--------|----------|--------|----------|
| **Produzione (BOM + Ordini)** | P2 | 15gg | Modulo `modules/manufacturing/` CQRS |
| **MRP** | P3 | 20gg | Algoritmo esterno orchestrato via Automation |
| **Intrastat** | P3 | 5gg | Report periodici |
| **Ferie/Permessi** | P2 | 5gg | Integrato in HR con workflow approvazione |
| **GDO (complete)** | P3 | 10gg | Completare modulo GDO con UI completa |
| **E-commerce Integration** | P3 | 10gg | API per sincronizzazione catalogo/ordini |
| **Multi-currency** | P2 | 5gg | Tassi di cambio, conversione automatica in contabilità |
| **Localizzazione (IT)** | P2 | 5gg | Fattura elettronica IT, Registri IVA, Libri contabili |

---

## 4. Architettura Raccomandata per Nuovi Moduli

### Pattern Standard (CQRS)
Ogni nuovo modulo deve seguire la struttura CQRS già consolidata in products/sales/purchases:

```
modules/<nome>/
├── __init__.py
├── container.py                # Dependency Injection
├── service_api.py              # Entry point: execute(command_data)
├── api/
│   └── rest_api.py             # Flask-Smorest endpoints
├── domain/
│   ├── __init__.py
│   ├── models.py               # Domain entities (Product, Invoice, etc.)
│   └── events.py               # Domain events
├── application/
│   ├── __init__.py
│   ├── handlers.py             # Command/Query handlers
│   ├── commands/
│   │   └── __init__.py         # Command dataclasses
│   └── queries/
│       └── __init__.py         # Query dataclasses
└── infrastructure/
    ├── __init__.py
    └── repository.py           # SQLAlchemy persistence
```

### Blueprint Registration
Registrare sempre con `url_prefix=f"{API_V1_PREFIX}/..."` in `backend/__init__.py`.

### Tenant Context
Usare `TenantContext.get_tenant_id()` per tutti i nuovi endpoint (non `request.headers.get('X-Tenant-ID', default)`). Il middleware già gestisce l'estrazione tenant da JWT/header/subdomain.

### Schema Database
Usare `tenant_id` + `id` pattern. Unique constraint su `(tenant_id, code)` per entità con codice.

### Frontend
- Pagine lista in `frontend/src/pages/` con `apiClient` (`get`/`post`/`put`/`delete`)
- Route in `App.jsx` con `ProtectedRoute`
- Menu item in `Sidebar.jsx` sezione "Applicazioni"

---

## 5. Riepilogo

### Quick Win (1-3gg ciascuno)
1. **Aliquote IVA** — P0, 2gg. Necessario per qualsiasi transazione economica
2. **Categorie Prodotto** — P1, 1gg. Arricchisce il modulo prodotti esistente
3. **Listini Prezzo** — P0, 3gg. Abilita prezzi differenziati per cliente

### Fondamentali (5-10gg ciascuno)
4. **Fatturazione** — P1, 10gg. Chiude il ciclo attivo vendite
5. **Movimenti Magazzino** — P1, 5gg. Abilita la tracciabilità fisica
6. **Prima Nota** — P1, 8gg. Base della contabilità
7. **DDT Acquisto** — P1, 5gg. Chiude il ciclo passivo acquisti

### Time-to-Value Totale
Completando Fase 1 + Fase 2 (~40gg/uomo), l'ERP copre i cicli fondamentali:
```
Anagrafiche → Prodotti (con IVA e listini) → Ordini Vendita → Fattura → Movimento Magazzino → Prima Nota
                                         → Ordini Acquisto → DDT Entrata → Movimento Magazzino → Prima Nota
```

---

*Documento generato il 2026-06-08*
