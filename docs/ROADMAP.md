# ERPSEED Roadmap di Sviluppo & Qualità UI/UX

> **Nota:** Questo documento definisce l'architettura, i dettagli tecnici e lo stato di completamento della Roadmap di Qualità, UX/UI e Data Model Enhancement (Q3-Q4 2026).
> Le Fasi storiche di sviluppo (Fasi 0-5) sono archiviate in [docs/ARCHIVE/COMPLETED_PHASES.md](ARCHIVE/COMPLETED_PHASES.md). Per lo stato dei blocchi ERP funzionali, consulta [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md).

---

## 🚀 Stato Roadmap (Q3 - Q4 2026) — 100% COMPLETATO

Tutti gli obiettivi strategici per il secondo semestre 2026 sono stati completati con successo, raggiungendo l'**eccellenza operativa**, un'**esperienza utente ad alte prestazioni** e l'**allineamento dei modelli dati alle best practice ERP internazionali** (Odoo, SAP S/4HANA, NetSuite).

| Priorità | Area | Obiettivo | Stato |
|----------|------|-----------|-------|
| 🔴 Alta | Docs | Refactoring documentazione: archiviazione fasi 0-5, unificazione indici e footer | ✅ Completato |
| 🔴 Alta | Dati | Enhancement modelli `Sales` e `Purchases` (valute, termini pagamento, indirizzi, sconti, IVA di riga) | ✅ Completato |
| 🔴 Alta | UX/UI | Componente `InlineEditableTable` e `ProductLookupInput` (ricerca debounced) | ✅ Completato |
| 🟡 Media | UX/UI | Global Command Palette (`Ctrl+K` / `Cmd+K`) per navigazione ed azioni rapide | ✅ Completato |
| 🟡 Media | UX/UI | Scorciatoie da tastiera (`Ctrl+S`, `Esc`) e Vista Mobile Card in `GenericCrudPage` | ✅ Completato |
| 🟢 Bassa | i18n | Completamento traduzioni backend ed allineamento chiavi i18n frontend (IT/EN) | ✅ Completato |

---

## 📐 Dettaglio Tecnico dei Pilastri della Roadmap

### 1. Refactoring Documentazione & Archiviazione Storica
- **Archiviazione Fasi 0-5**: Creazione di `docs/ARCHIVE/COMPLETED_PHASES.md` contenente lo storico dettagliato dei rilasci dal nucleo iniziale (Fase 0) fino all'agentificazione e sicurezza (Fase 5).
- **Master Entry Point**: Unificazione della navigazione in `docs/INDEX.md` con supporto bilingue (documentazione tecnica IT, manuale utente EN) e footer standardizzati su tutti i 13 documenti attivi.

### 2. Data Model Enhancement (Sales & Purchases)
- **Modelli di Dominio & CQRS**: Introduzione delle dataclass di dominio `SalesOrder`, `SalesOrderLine`, `PurchaseOrder`, e `PurchaseOrderLine` con gestione dei prezzi netti, lordi e calcolo imposte di riga.
- **Campi Enterprise estesi**:
  - `pricelist_id` (Listino prezzi associato)
  - `currency_id` (Valuta della transazione)
  - `payment_term_id` (Termine di pagamento concordato)
  - `billing_address_id` / `shipping_address_id` (Indirizzi di fatturazione e spedizione)
  - `salesperson_id` / `buyer_id` (Agente commerciale o Responsabile acquisti)
  - `customer_reference` / `supplier_reference` (Riferimenti esterni cliente/fornitore)
  - `warehouse_id` (Magazzino di destinazione/stoccaggio)
  - `landing_costs` (Oneri accessori e spese di trasporto)
  - Dettaglio riga: `tax_id` (Aliquota IVA di riga), `discount_percent` (Sconto percentuale riga), `uom_id` (Unità di misura riga), `expected_delivery_date` (Data consegna prevista).
- **ORM & Repositories**: Aggiornamento degli schemi SQLAlchemy (`backend/models/sales.py`, `backend/models/purchase.py`) e delle classi repository CQRS con contratti d'interfaccia trasparenti.

### 3. UX/UI Excellence - Componenti di Riga e Ricerca
- **`InlineEditableTable.jsx`**: Componente di tabella modificabile inline per la gestione dinamica di righe ordine e preventivo. Supporta aggiunta/rimozione immediata di righe, ricalcolo automatico di sconti, imponibile, IVA e totale documento in tempo reale.
- **`ProductLookupInput.jsx`**: Input di ricerca prodotti debounced con autocompletamento in tempo reale. Permette la selezione rapida dal catalogo articoli integrando prezzi di listino, codici SKU e barcode.

### 4. Global Command Palette (`Ctrl+K` / `Cmd+K`)
- **Navigazione ed Azioni Rapide**: Modal di comando globale (`frontend/src/components/core/CommandPalette.jsx`) attivabile da qualsiasi schermata con la combinazione `Ctrl+K` (o `Cmd+K` su macOS).
- **Capacità**:
  - Ricerca istantanea e salto diretto a tutte le 50+ pagine applicative, anagrafiche e strumenti di configurazione.
  - Scorciatoie per azioni frequenti: creazione nuovi ordini, apertura AI Assistant, cambio lingua/tema, esecuzione riconciliazione CashRec.
  - Integrazione dello stato globale via hook `useCommandPalette.js`.

### 5. Productive Keyboard Shortcuts & Responsive Mobile Card View
- **Global Keyboard Shortcuts**:
  - `Ctrl+S` / `Cmd+S`: Invio automatico del form attivo in modal o drawer per un salvataggio ultra-rapido.
  - `Esc`: Chiusura immediata di modal, drawer o dialoghi aperti senza perdita di stato.
- **Vista Mobile Card in `GenericCrudPage.jsx`**:
  - Rilevamento automatico delle dimensioni dello schermo via `useResponsive()`.
  - Conversione trasparente da tabella a griglia di `<Card>` espandibili quando si naviga da dispositivi mobile (`<992px`), garantendo un'esperienza touchscreen fluida e reattiva.

### 6. Internazionalizzazione (i18n) & Ottimizzazione Qualità
- **Allineamento Multi-lingua**: Copertura completa del dizionario in italiano (IT) ed inglese (EN) tramite `react-i18next` sul frontend e `Flask-Babel` sul backend.
- **Riconciliazione Risposte API**: Piena internazionalizzazione dei messaggi di errore, di validazione e delle notifiche di sistema.
- **Performance & Cache**: Ottimizzazione delle query ORM e caching Redis su endpoint ad alto traffico (scadenzario, registri IVA, giacenze magazzino).

---

## 📋 Gantt Chart Roadmap Q3-Q4 2026 (Stato Rilasci)

```
2026 Q3 (Luglio - Settembre)
├── Refactoring Documentazione & Archiviazione
│   ├── ✅ Creazione docs/ARCHIVE/COMPLETED_PHASES.md
│   └── ✅ Aggiornamento Indice Unico e Footer
├── Data Model Enhancement (Sales & Purchases)
│   ├── ✅ Dataclass dominio (SalesOrder, PurchaseOrder, Lines)
│   ├── ✅ Schemi SQLAlchemy & Marshmallow Repositories
│   └── ✅ Migrazione schema database e test pytest
└── UX/UI Excellence - Parte 1
    ├── ✅ InlineEditableTable.jsx per tabelle ordini
    └── ✅ ProductLookupInput.jsx con autocompletamento debounced

2026 Q4 (Ottobre - Dicembre)
├── UX/UI Excellence - Parte 2
│   ├── ✅ Global Command Palette (Ctrl+K / Cmd+K)
│   ├── ✅ Global Keyboard Shortcuts (Ctrl+S, Esc)
│   └── ✅ Responsive Mobile Card View su GenericCrudPage
└── i18n & Quality Optimization
    ├── ✅ Traduzioni complete IT/EN per risposte backend e frontend
    └── ✅ Optimization query e benchmark indici DB
```

---

## 📚 Archivio Fasi Precedenti
Per la documentazione dettagliata delle fasi di stabilizzazione, refactoring KISS/DRY, responsive design, agentificazione e sicurezza già completate:
- 👉 [Consulta lo Storico Fasi 0-5](ARCHIVE/COMPLETED_PHASES.md)

---

---

> Ultimo aggiornamento: 10 Settembre 2026 | [Torna all'Indice](INDEX.md)
