# Architettura ERPSEED Backend & Frontend

## Panoramica

ERPSEED è un sistema ERP modulare e ad alte prestazioni costruito con Flask (Backend) e React 19 + Vite + Ant Design (Frontend). Utilizza un'architettura multi-tenant con supporto per:
- Creazione dinamica di modelli dati (No-Code Builder)
- Modelli di dominio CQRS estesi (Sales, Purchases, Invoicing, Products, Projects)
- EventBus disaccoppiato con supporto Redis Pub/Sub e messaggistica interna
- Field-Level RBAC per il mascheramento granulare dei campi in base al ruolo utente
- Global Command Palette (`Ctrl+K`) e Global Search (`/api/v1/global/search`)
- Workflow automation & webhook event-driven
- AI Assistant integrato e gateway distribuito agentico (AgentMesh)

## Stack Tecnologico

| Layer | Componente | Tecnologia |
|-------|------------|-----------|
| **Backend** | Framework API | Flask 3.x + Flask-Smorest (OpenAPI 3.0) |
| | ORM | SQLAlchemy + Flask-SQLAlchemy |
| | Auth & Security | Flask-JWT-Extended (JWT) + Field-Level RBAC |
| | Serializzazione | Marshmallow |
| | Database | PostgreSQL 15 (dev: SQLite) |
| | Eventi & Pub/Sub | Redis Pub/Sub / Core EventBus (`backend/core/event_bus.py`) |
| | Cache & Realtime | Redis 7 + Flask-SocketIO (eventlet) |
| | i18n | Flask-Babel |
| **Frontend**| UI Framework | React 19 + Vite + PWA Support |
| | Component Library | Ant Design (`antd`) |
| | UX & Theme Tokens | Centralized Token Layer (`frontend/src/theme/tokens.js`) |
| | Charts | `@ant-design/charts` (Standard primario) |
| | Viste Avanzate | `KanbanView.jsx`, `PivotTable.jsx`, `ContextualDrawer.jsx`, `KnowledgeDrawer.jsx` |
| | State & Hooks | React Context + Zustand + Custom Hooks (`useCommandPalette`, `useResponsive`, `useCrudData`) |
| | i18n | `react-i18next` (EN/IT) |

## Struttura del Progetto

```
backend/
├── __init__.py              # App factory (create_app)
├── extensions.py            # Inizializzazione estensioni Flask
├── schemas.py               # Schemi Marshmallow centrali
├── container.py             # Iniezione dipendenze (Container)
├── models/                  # MODELLI DATABASE (SQLAlchemy)
│   ├── sales.py             # SalesOrder, SalesOrderLine (extended fields)
│   ├── purchase.py          # PurchaseOrder, PurchaseOrderLine (extended fields)
│   └── ...                  # Modelli anagrafici, finanziari, di produzione e sistema
│
├── core/                    # CORE SYSTEM (Auth, Tenant, Middleware, Services)
│   ├── event_bus.py         # Core EventBus con Redis Pub/Sub integration
│   ├── middleware/          # Permission & Field-Level RBAC Middleware
│   ├── api/                 # Core System & Global Search APIs (/api/v1/global/search)
│   └── services/            # Base, Permission, Tenant & Import/Export Services
├── modules/                 # MODULI APPLICATIVI (CQRS & Domain Logic)
│   ├── sales/              # Ordini Vendita & Preventivi (CQRS & Domain Dataclasses)
│   ├── purchases/          # Ordini Acquisto (CQRS & Domain Dataclasses)
│   └── ...                 # Moduli applicativi
```

## Security & Field-Level RBAC

ERPSEED implementa il controllo accessi basato su ruoli (RBAC) con mascheramento dei campi a livello di attributo:
- **`GET /api/v1/users/permissions`**: Restituisce il ruolo corrente dell'utente, l'elenco dei permessi attivi e la mappa dei campi nascosti (`hidden_fields`).
- **Field Masking Middleware (`backend/core/middleware/permission.py`)**: Maschera automaticamente campi sensibili (es. `cost_price`, `margin`, `profit_margin`) per ruoli con privilegi limitati (`user`, `viewer`).
- **`GenericCrudPage.jsx`**: Filtra dinamicamente colonne della tabella e campi dei form in base ai permessi utente.

## Global Search API & Command Palette (`Ctrl+K` / `Cmd+K`)

- **`GET /api/v1/global/search?q=<term>`**: Esegue query full-text/case-insensitive cross-entity su Soggetti, Prodotti, Ordini e Fatture, restituendo risultati strutturati `{ type, id, label, url }`.
- **Command Palette**: Esegue ricerche con debounce di 300ms e permette la navigazione contestuale ad alta velocità.

## Event System & Event Bus Interno

L'architettura supporta eventi di dominio disaccoppiati gestiti da `backend/core/event_bus.py` e Redis Pub/Sub:
- **`order.confirmed` / `sales_order.confirmed`**: La conferma di un ordine di vendita pubblica l'evento di dominio, ascoltato in modo disaccoppiato dal modulo Magazzino (`InventoryListener` per la prenotazione stock) e Fatturazione (`InvoicingListener` per la creazione bozza fattura).

---

*Per la cronologia completa delle modifiche di questo documento, consulta la cronologia Git del repository.*

---

> Ultimo aggiornamento: 21 Ottobre 2026 | [Torna all'Indice](INDEX.md)
