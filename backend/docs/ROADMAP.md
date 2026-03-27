# ERPSEED Roadmap di Sviluppo

## Panoramica

Questa roadmap definisce le priorità di sviluppo per ERPSEED. Dopo il grande refactoring verso un'architettura modulare e l'introduzione di Hybrid CQRS, l'obiettivo è consolidare queste basi e scalare le performance.

---

## ✅ Fase 1: Consolidamento Architetturale (COMPLETATA)

### Obiettivo: Modularizzazione e CQRS Base

| # | Task | Stato |
|---|------|-------|
| 1.1 | Riorganizzazione Modulare (`backend/modules/`) | ✅ |
| 1.2 | Implementazione Command Handler Pattern | ✅ |
| 1.3 | Infrastruttura JSONB Read Model | ✅ |
| 1.4 | Centralizzazione API v1 | ✅ |

---

## 🏗️ Fase 2: Performance & Scalabilità (PROSSIMI PASSI)

### Obiettivo: Sfruttare appieno il Read Model

| # | Task | Priorità | Complessità |
|---|------|----------|------------|
| 2.1 | **Read-Only API**: Implementare endpoint dedicati per leggere direttamente da JSONB | 🔴 ALTA | Media |
| 2.2 | **Advanced Projections**: Creare handler che denormalizzano record correlati (es. Ordine + Dettagli Cliente) | 🔴 ALTA | Alta |
| 2.3 | **Bulk Sync Utility**: Script CLI per rigenerare tutti i Read Model partendo dai dati SQL esistenti | 🟡 MEDIA | Media |
| 2.4 | **Redis Caching**: Aggiungere uno strato di cache davanti ai Read Model per le dashboard più pesanti | 🟢 BASSA | Media |

---

## 📦 Fase 3: Functional Expansion

### Obiettivo: Nuove feature di business

| # | Feature | Priorità | Complessità |
|---|---------|----------|------------|
| 3.1 | **Workflow Visual Editor**: Interfaccia drag & drop per configurare le automazioni | 🟡 MEDIA | Alta |
| 3.2 | **AI Insights**: Analisi predittiva dei dati partendo dai Read Model denormalizzati | 🟢 BASSA | Alta |
| 3.3 | **Plugin Market**: Sistema di installazione dinamica di nuovi blocchi e modelli | 🟢 BASSA | Alta |

---

## 🔒 Fase 4: Security & DevOps

### Obiettivo: Robustezza e Manutenibilità

| # | Task | Priorità | Complessità |
|---|------|----------|------------|
| 4.1 | **Unit Test Coverage**: Aumentare la copertura per i singoli Command Handler | 🔴 ALTA | Media |
| 4.2 | **Rate Limiting**: Proteggere le API da abusi tramite Flask-Limiter | 🟡 MEDIA | Bassa |
| 4.3 | **CI/CD Pipeline**: Automazione test e deploy su GitHub Actions | 🟡 MEDIA | Media |

---

## 💡 Contributing Guidelines

1. **Absolute Imports**: Usa sempre import assoluti (es. `from backend.core...`).
2. **Command Pattern**: Ogni nuova azione di business deve essere un Command.
3. **JSONB First**: Per nuove dashboard, progetta prima la proiezione dei dati.
4. **Documentation**: Ogni nuovo modulo deve avere un file README.md interno.

---

*Ultimo aggiornamento: 2024-05-24 (Post-Modular Refactor)*
