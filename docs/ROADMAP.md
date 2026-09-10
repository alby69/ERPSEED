# ERPSEED Roadmap di Sviluppo

> **Nota:** Questo documento definisce le priorità attive per il Q3-Q4 2026 (UX/UI, Data Model Enhancement, Command Palette).
> Le fasi storiche completate (Fasi 0-5) sono state archiviate in [docs/ARCHIVE/COMPLETED_PHASES.md](ARCHIVE/COMPLETED_PHASES.md). Per lo stato dei blocchi ERP funzionali, consulta [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md).

---

## 🚀 Priorità Correnti (Q3 - Q4 2026)

L'obiettivo strategico per il secondo semestre 2026 è l'**eccellenza operativa**, l'**esperienza utente ad alte prestazioni** e l'**allineamento dei modelli dati alle best practice ERP** (Odoo, SAP S/4HANA, NetSuite).

| Priorità | Area | Obiettivo | Stato |
|----------|------|-----------|-------|
| 🔴 Alta | Docs | Refactoring documentazione: archiviazione fasi 0-5, unificazione indici | 🔄 In corso |
| 🔴 Alta | Dati | Enhancement modelli `Sales` e `Purchases` (valute, termini pagamento, indirizzi, sconti, IVA di riga) | 🔄 In corso |
| 🔴 Alta | UX/UI | Componente `InlineEditableTable` e `ProductLookupInput` (ricerca debounced) | 🔄 In corso |
| 🟡 Media | UX/UI | Global Command Palette (`Ctrl+K` / `Cmd+K`) per navigazione ed azioni rapide | 🔄 In corso |
| 🟡 Media | UX/UI | Scorciatoie da tastiera (`Ctrl+S`, `Esc`) e Vista Mobile Card in `GenericCrudPage` | 🔄 In corso |
| 🟢 Bassa | i18n | Completamento traduzioni backend ed allineamento chiavi i18n frontend | ⏳ Pianificato |

---

## 📋 Gantt Chart Roadmap Q3-Q4 2026

```
2026 Q3 (Luglio - Settembre)
├── Refactoring Documentazione & Archiviazione
│   ├── ✅ Creazione docs/ARCHIVE/COMPLETED_PHASES.md
│   └── ✅ Aggiornamento Indice Unico e Footer (10 Settembre 2026)
├── Data Model Enhancement (Sales & Purchases)
│   ├── 🔄 Dataclass dominio (SalesOrder, PurchaseOrder, Lines)
│   ├── 🔄 Schemi SQLAlchemy & Marshmallow Repositories
│   └── 🔄 Migrazione schema database e test pytest
└── UX/UI Excellence - Parte 1
    ├── 🔄 InlineEditableTable.jsx per tabelle ordini
    └── 🔄 ProductLookupInput.jsx con autocompletamento debounced

2026 Q4 (Ottobre - Dicembre)
├── UX/UI Excellence - Parte 2
│   ├── 🔄 Global Command Palette (Ctrl+K / Cmd+K)
│   ├── 🔄 Global Keyboard Shortcuts (Ctrl+S, Esc)
│   └── 🔄 Responsive Mobile Card View su GenericCrudPage
└── i18n & Quality Optimization
    ├── ⏳ Traduzioni complete IT/EN per risposte backend
    └── ⏳ Optimization query e benchmark indici DB
```

---

## 📚 Archivio Fasi Precedenti
Per la documentazione dettagliata delle fasi di stabilizzazione, refactoring KISS/DRY, responsive design, agentificazione e sicurezza già completate:
- 👉 [Consulta lo Storico Fasi 0-5](ARCHIVE/COMPLETED_PHASES.md)

---

---

> Ultimo aggiornamento: 10 Settembre 2026 | [Torna all'Indice](INDEX.md)
