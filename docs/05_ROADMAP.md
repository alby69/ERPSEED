# FlaskERP - Roadmap e Stato

## Roadmap Implementazione (5 Fasi)

### Fase 1: Fondamenta (Settimane 1-2)
- [x] Refactoring entità core (Soggetto, Ruolo, Indirizzo)
- [x] Sistema ruoli avanzato
- [x] Indirizzi con geolocalizzazione

### Fase 2: Composizione (Settimane 3-4)
- [x] Block Registry
- [x] Container System
- [x] Robot/Module System

### Fase 3: Builder (Settimane 5-8)
- [x] Template Parser
- [x] Code Generator
- [x] Schema Migrator
- [x] UI Builder

### Fase 4: Code-as-Data (Settimane 9-12)
- [x] Expression Engine
- [x] Hook System
- [x] Hot Reload
- [x] Adaptive Modules

### Fase 5: Evoluzione (Settimane 13+)
- [x] Telemetry
- [x] Auto-optimization
- [x] Genetic Algorithms

---

## Obiettivi Strategici

| Anno | Obiettivo | KPI |
|------|-----------|-----|
| **2026** | MVP + Community | 100 utenti, 10 contributor |
| **2027** | Product-Market Fit | 50 tenant paganti, €5k MRR |
| **2028** | Scaling | 200 tenant, €50k MRR |
| **2029** | Market Leader IT | 500+ tenant, €200k MRR |

---

## Timeline Strategica

```
2026 (Anno 1)
├── Q1: Core + Core Modules
├── Q2: Community Launch
├── Q3: MVP Complete
└── Q4: First Paid Users

2027 (Anno 2)
├── Q1: SaaS Platform
├── Q2: Marketplace
├── Q3: Enterprise Features
└── Q4: Scale Team

2028 (Anno 3)
├── Q1: Internationalization
├── Q2: Mobile Apps
├── Q3: AI Features
└── Q4: Series A (maybe)
```

---

## Modello di Crescita

### Anno 1 - Costruire la Community

| Trimestre | Focus | Monetizzazione |
|-----------|-------|----------------|
| Q1 | FlaskERP Core v1.0 | 0€ - Open Source puro |
| Q2 | Primi moduli | 0€ - Community growth |
| Q3 | Docker Compose | Donazioni + sponsor |
| Q4 | Template preconfigurati | Template premium |

### Anno 2 - SaaS Platform

| Trimestre | Focus | Monetizzazione |
|-----------|-------|----------------|
| Q1 | Multi-tenant core | SaaS Starter (€29/m) |
| Q2 | Stripe integration | SaaS Business (€99/m) |
| Q3 | Marketplace template | Commissioni 20% |
| Q4 | Builder Studio | Pro accounts (€249/m) |

---

## Scelte Strategiche

### Database
**Raccomandazione**: Shared schema con `tenant_id`
- Pro: Semplice, economico
- Contro: Isolamento minore
- Quando cambiare: >50 tenant

### Deployment
**Raccomandazione**: Docker Compose
- Per <50 tenant è sufficiente
-升级: Docker Swarm (50-200), Kubernetes (>200)

### Payment
**Raccomandazione**: Solo Stripe
- Copre 95% casi B2B Europa

### White-label
**Raccomandazione**: Solo Enterprise (€499+/mese)

---

## Scenari di Utilizzo

### Scenario 1: Freelance/Consulente
- **Target**: Freelance, piccoli consulenti
- **Pricing**: Free (open source)

### Scenario 2: Piccola PMI
- **Target**: Negozi, artigiani
- **Pricing**: €29-99/mese

### Scenario 3: Consulente IT (Reseller)
- **Target**: Agency, system integrator
- **Pricing**: €249-499/mese

---

## Test Suite

```
tests/
├── conftest.py                    # Fixtures
├── core/                          # Test multi-tenant
│   ├── test_tenant_context.py    # 12 test
│   ├── test_auth_service.py      # 16 test
│   └── test_tenant_isolation.py  # 10 test
├── modules/                       # Test moduli
│   └── test_modules_isolation.py #  9 test
└── plugins/                       # Test plugin
    ├── test_accounting.py         #  9 test
    └── test_inventory.py          # 10 test
```

**Totale**: ~99+ test

---

## Prossime Attività

| Task | Priorità | Stato |
|------|----------|-------|
| Frontend UI - Integrazione API | Alta | Completato |
| Navigazione Unificata (Header, Breadcrumb, Back) | Alta | Completato |
| Ricerca e Ordinamento Tabelle | Alta | Completato |
| PDF Fatture | Alta | In corso |
| Test Unitari & E2E (Vitest/Playwright) | Alta | Completato |
| Gestione Temi Grafici | Media | Completato |
| Cambio Tema Real-time | Media | Completato |
| Integrazione SDI | Bassa | - |
| Scadenzario pagamenti | Bassa | - |

---

*Documento aggiornato: Febbraio 2026*
