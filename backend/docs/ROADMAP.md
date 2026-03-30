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
| # | Task | Priorità | Complessità | Stato |
|---|------|----------|------------|-------|
| 1.1 | Centralizzare `paginate()` | 🟡 ALTA | Bassa | ⏳ TODO |
| 1.2 | Centralizzare `check_unique()` | 🟡 ALTA | Bassa | ⏳ TODO |
| 1.3 | Utility `safe_json_parse()` | 🟡 ALTA | Bassa | ⏳ TODO |
| 1.4 | Consolidare schemi Marshmallow | 🟡 ALTA | Media | ⏳ TODO |

### Dettagli Fase 1

#### 1.1 - Utility Paginazione

```python
# backend.core.utils.utils/pagination.py
def paginate_response(query, page=1, per_page=20):
    """
    Centralizza logica paginazione.

    Returns:
        tuple: (data, headers_dict)
    """
    pagination = query.paginate(
        page=page,
        per_page=min(per_page, 100),  # Max 100
        error_out=False
    )

    headers = {
        'X-Total-Count': str(pagination.total),
        'X-Pages': str(pagination.pages),
        'X-Current-Page': str(pagination.page),
        'X-Per-Page': str(pagination.per_page),
    }

    return pagination.items, headers
```

#### 1.2 - BaseService

```python
# backend/services/base.py
class BaseService:
    def __init__(self, db):
        self.db = db

    def paginate(self, query, page=1, per_page=20):
        return paginate_response(query, page, per_page)

    def check_unique(self, model, field, value, exclude_id=None):
        """Verifica unicità valore su campo."""
        query = model.query.filter_by(**{field: value})
        if exclude_id:
            query = query.filter(model.id != exclude_id)
        return query.first() is None

    def soft_delete(self, instance):
        instance.deleted_at = datetime.utcnow()
        self.db.session.commit()
```

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
