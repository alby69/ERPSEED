# FlaskERP - Moduli

## Stato Moduli

| Modulo | Stato | Descrizione |
|--------|-------|-------------|
| **Core Multi-Tenant** | ✅ | Tenant, User, Auth, Audit |
| **Parties** | ✅ | Soggetti, Ruoli, Indirizzi |
| **Products** | ✅ | Prodotti, Categorie, Prezzi |
| **Sales** | ✅ | Ordini, Preventivi, Consegne |
| **Inventory** | ✅ | Magazzino, Movimenti |
| **Purchases** | ✅ | Ordini fornitore |
| **Accounting** | 🟡 | Contabilità base (70%) |
| **HR** | 🟡 | Dipendenti (50%) |
| **Dashboard** | 🟡 | KPI base (40%) |

---

## Dipendenze tra Moduli

```
                    ┌─────────────┐
                    │    CORE     │
                    │  (Auth,    │
                    │   Users)    │
                    └──────┬──────┘
                           │
      ┌────────────────────┼────────────────────┐
      │                    │                    │
      ▼                    ▼                    ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  PARTIES    │    │  PRODUCTS   │    │  PARTIES    │
│ (Clienti)  │    │ (Catalogo)  │    │(Fornitori) │
└──────┬──────┘           │                   │
       │                  │                   │
       │           ┌──────┴──────┐             │
       │           ▼             ▼             ▼
       ▼     ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
┌─────────────┐ │   SALES     │ │ INVENTORY   │ │  PURCHASES  │
│   SALES     │ │  (Ordini)   │ │ (Magazzino) │ │  (Acquisti) │
└──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
       │               │               │               │
       └───────────────┴───────┬───────┴───────────────┘
                               │
                               ▼
                        ┌─────────────┐
                        │  ACCOUNTING │
                        │(Contabilità)│
                        └─────────────┘
```

---

## Modulo Parties (Anagrafiche)

### Entità

- **Party**: Anagrafica soggetto
- **PartyType**: Tipologia (cliente, fornitore)
- **PartyAddress**: Indirizzi
- **PartyContact**: Contatti
- **PartyGroup**: Gruppi/Segmenti

### API

```
GET    /api/v1/parties           # Lista
GET    /api/v1/parties/{id}      # Dettaglio
POST   /api/v1/parties           # Crea
PUT    /api/v1/parties/{id}      # Aggiorna
DELETE /api/v1/parties/{id}      # Elimina

# Indirizzi
GET    /api/v1/parties/{id}/addresses
POST   /api/v1/parties/{id}/addresses

# Contatti
GET    /api/v1/parties/{id}/contacts
POST   /api/v1/parties/{id}/contacts
```

### Funzionalità

- CRUD completo
- Ricerca avanzata (nome, partita IVA, codice fiscale)
- Validazione partita IVA italiana
- Import/Export CSV

---

## Modulo Products (Catalogo)

### Entità

- **Product**: Prodotto/Servizio
- **ProductCategory**: Categoria gerarchica
- **ProductVariant**: Varianti (taglia, colore)
- **ProductPrice**: Listino prezzi
- **PriceList**: Gestione listini

### API

```
GET    /api/v1/products          # Lista
GET    /api/v1/products/{id}    # Dettaglio
POST   /api/v1/products          # Crea
PUT    /api/v1/products/{id}     # Aggiorna
DELETE /api/v1/products/{id}     # Elimina

# Categorie
GET    /api/v1/product-categories
GET    /api/v1/product-categories/{id}/products
```

### Funzionalità

- CRUD prodotti
- Categorie gerarchiche
- Varianti prodotto
- Multiple listini prezzi
- Codici a barre

---

## Modulo Sales (Vendite)

### Flusso

```
Preventivo (Quote) ──► Ordine (Order) ──► Consegna (Delivery) ──► Fattura
     │                    │                    │                    │
     └───── conferma ────┴────── evasione ───┴────── fatturazione
```

### Entità

- **SalesQuote** / **SalesQuoteLine**: Preventivi
- **SalesOrder** / **SalesOrderLine**: Ordini cliente
- **SalesDelivery** / **SalesDeliveryLine**: Bolle consegna
- **PaymentTerm**: Termini pagamento

### API

```
# Ordini
GET    /api/v1/sales-orders
POST   /api/v1/sales-orders
GET    /api/v1/sales-orders/{id}
PUT    /api/v1/sales-orders/{id}/confirm   # Conferma ordine

# Righe
GET    /api/v1/sales-orders/{id}/lines
POST   /api/v1/sales-orders/{id}/lines
```

### Stati Ordine

- `bozza` → `confermato` → `evaso` → `completato` / `annullato`

---

## Modulo Inventory (Magazzino)

### Entità

- **InventoryLocation**: Ubicazioni magazzino
- **ProductStock**: Giacenze per ubicazione
- **StockMovement**: Movimenti (carico/scarico)
- **InventoryCount**: Inventario fisico
- **InventoryCountLine**: Righe conteggio

### API

```
# Movimenti
GET    /api/v1/stock-movements
POST   /api/v1/stock-movements  # Carico/Scarico

# Giacenze
GET    /api/v1/stock-levels

# Inventario
GET    /api/v1/inventory-counts
POST   /api/v1/inventory-counts/{id}/complete
```

---

## Modulo Purchases (Acquisti)

### Entità

- **PurchaseOrder** / **PurchaseOrderLine**: Ordini fornitore

### Flusso

```
Ordine Fornitore ──► Ricevimento Merce ──► Fattura Passiva
```

---

## Modulo Accounting (Contabilità)

### Entità

- **ChartOfAccounts**: Piano dei conti
- **Account**: Singolo conto
- **JournalEntry** / **JournalEntryLine**: Partita doppia
- **Invoice** / **InvoiceLine**: Fatture attive/passive

### Funzionante

- Piano dei conti configurabile
- Partita doppia automatica
- Report Situazione Contabile
- Trial Balance

### Mancante

- Generazione PDF fatture
- Integrazione SDI (fattura elettronica)
- Scadenzario pagamenti

---

## Modulo HR (Risorse Umane)

### Entità

- **Department**: Reparti
- **Employee**: Dipendenti
- **Attendance**: Presenze
- **LeaveRequest**: Ferie/Permessi

### Funzionante

- CRUD base dipendenti
- Presenze base

### Mancante

- Timesheet settimanale
- Calcolo stipendi
- Dashboard HR

---

*Documento aggiornato: Febbraio 2026*
