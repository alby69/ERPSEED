# ERPSEED Roadmap di Sviluppo

## Panoramica

Questa roadmap definisce le priorità di sviluppo per ERPSEED, organizzate per fasi. L'obiettivo è migliorare la qualità del codice (KISS/DRY), stabilizzare le funzionalità esistenti e aggiungere nuove feature in modo ordinato.

---

## 🚨 Fase 0: Stabilizzazione Critica (IMMEDIATA)

### Obiettivo: Rendere il progetto avviabile e testabile

| # | Task | Priorità | Complessità | Stato |
|---|------|----------|------------|-------|
| 0.1 | Riempire `requirements.txt` | 🔴 CRITICA | Bassa | ✅ COMPLETATO |
| 0.2 | Fix BaseModel duplicati | 🔴 CRITICA | Media | ⏳ TODO |
| 0.3 | Aggiungere test base | 🔴 CRITICA | Media | ⏳ TODO |
| 0.4 | Documentazione API completa | 🔴 CRITICA | Media | ✅ COMPLETATO |

### Dettagli Fase 0

#### 0.2 - Consolidare BaseModel

**Problema Attuale:**
- `backend/models.py`: BaseModel base (created_at, updated_at)
- `backend/core/models/base.py`: BaseModel avanzato (soft delete)

**Soluzione Proposta:**
```python
# backend/core/models/base.py
class BaseModel(db.Model):
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)  # Soft delete
    
    # Metodi utility
    def soft_delete(self):
        self.deleted_at = datetime.utcnow()
    
    def restore(self):
        self.deleted_at = None
    
    @classmethod
    def active(cls):
        return cls.query.filter_by(deleted_at=None)
```

---

## 🔧 Fase 1: Refactoring DRY (CORTO TERMINE)

### Obiettivo: Eliminare duplicazioni e centralizzare logica

| # | Task | Priorità | Complessità | Stato |
|---|------|----------|------------|-------|
| 1.1 | Centralizzare `paginate()` | 🟡 ALTA | Bassa | ⏳ TODO |
| 1.2 | Centralizzare `check_unique()` | 🟡 ALTA | Bassa | ⏳ TODO |
| 1.3 | Utility `safe_json_parse()` | 🟡 ALTA | Bassa | ⏳ TODO |
| 1.4 | Consolidare schemi Marshmallow | 🟡 ALTA | Media | ⏳ TODO |

### Dettagli Fase 1

#### 1.1 - Utility Paginazione

```python
# backend/utils/pagination.py
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

## 🏗️ Fase 2: Refactoring KISS (MEDIO TERMINE)

### Obiettivo: Semplificare componenti complesse

| # | Task | Priorità | Complessità | Stato |
|---|------|----------|------------|-------|
| 2.1 | Split `DynamicApiService` (945 righe) | 🟡 ALTA | Alta | ⏳ TODO |
| 2.2 | Split `dynamic_api.py` (8 classi) | 🟡 ALTA | Media | ⏳ TODO |
| 2.3 | Standardizzare pattern Service | 🟡 ALTA | Media | ⏳ TODO |
| 2.4 | Riorganizzare `__init__.py` | 🟢 MEDIA | Bassa | ⏳ TODO |

### Dettagli Fase 2

#### 2.1 - Split DynamicApiService

**Struttura Target:**
```
services/dynamic/
├── __init__.py
├── base.py              # BaseDynamicService
├── field_validator.py   # Validazione campi
├── query_builder.py     # Costruzione query
├── schema_builder.py     # Generazione schemi
├── csv_importer.py       # Import CSV
└── dynamic_service.py    # Orchestration
```

#### 2.2 - Split dynamic_api.py

**File Target:**
```
routes/
├── dynamic_api.py         # Rotte principali
├── dynamic_list.py       # DynamicDataList
├── dynamic_item.py      # DynamicDataItem
├── dynamic_meta.py      # Model metadata
└── dynamic_import.py    # Import endpoint
```

---

## 📦 Fase 3: Nuove Features (MEDIO-LUNGO TERMINE)

### Obiettivo: Espandere funzionalità in modo ordinato

| # | Feature | Priorità | Complessità | Dipendenze |
|---|---------|----------|------------|------------|
| 3.1 | Batch Import/Export UI | 🟢 MEDIA | Media | 2.2 |
| 3.2 | Workflow Visual Editor | 🟢 MEDIA | Alta | - |
| 3.3 | Dashboard Builder | 🟢 MEDIA | Media | 1.x |
| 3.4 | Plugin Store | 🟢 MEDIA | Alta | - |
| 3.5 | Multi-language Support | 🟢 MEDIA | Media | - |

### Dettagli Fase 3

#### 3.1 - Batch Import/Export

```python
# Nuovo endpoint
@blp.route("/data/<model>/export")
class ModelExport(MethodView):
    def get(self, model):
        """Export tutti i record in CSV/JSON."""
        format = request.args.get('format', 'csv')
        # ...

@blp.route("/data/<model>/import-preview")
class ImportPreview(MethodView):
    def post(self, model):
        """Preview import senza salvare."""
        # Validazione + preview
```
#### 3.2 - Workflow Visual Editor

**Backend API:**
```python
@blp.route("/workflows/<id>/canvas")
class WorkflowCanvas(MethodView):
    def get(self, id):
        """Get workflow as nodes/edges for visual editor."""
        return workflow.to_graph()
    
    def put(self, id):
        """Update workflow from nodes/edges."""
        workflow.from_graph(request.json)
```

---

## 🔒 Fase 4: Security & Performance (ONGOING)

### Obiettivo: Migliorare sicurezza e performance

| # | Task | Priorità | Complessità | Stato |
|---|------|----------|------------|-------|
| 4.1 | Rate Limiting | 🟡 ALTA | Bassa | ⏳ TODO |
| 4.2 | Input Sanitization | 🟡 ALTA | Media | ⏳ TODO |
| 4.3 | Query Optimization | 🟡 ALTA | Media | ⏳ TODO |
| 4.4 | Redis Caching | 🟢 MEDIA | Media | ⏳ TODO |
| 4.5 | API Versioning | 🟢 MEDIA | Bassa | ⏳ TODO |

---

## 📋 Gantt Semplificato

```
2026 Q1 (Gennaio - Marzo)
├── Fase 0: Stabilizzazione
│   ├── ✅ requirements.txt
│   ├── ✅ Documentazione
│   └── ⏳ BaseModel + Test
│
├── Fase 1: DRY Refactoring
│   ├── ⏳ paginate utility
│   ├── ⏳ check_unique utility
│   └── ⏳ safe_json_parse
│
└── Fase 2: KISS Refactoring
    ├── ⏳ Split DynamicApiService
    └── ⏳ Standardize Services

2026 Q2 (Aprile - Giugno)
├── Fase 2: KISS Refactoring (continua)
├── Fase 3: Nuove Features
│   ├── ⏳ Batch Import/Export
│   └── ⏳ Dashboard Builder
└── Fase 4: Security & Performance
    └── ⏳ Rate Limiting + Caching
```

---

## 🐛 Known Issues

| Issue | Workaround | Fix Pianificato |
|-------|-----------|-----------------|
| Import CSV lento con >10k record | Batch processing | Fase 3.1 |
| Memory leak con file upload grandi | Limite 10MB | Fase 4 |
| N+1 queries in list view | Eager loading | Fase 4.3 |
| Soft delete non propagato | Cascade manual | Fase 1 |

---

## 💡 Contributing

### PR Guidelines

1. **Test coverage** - Nuove features richiedono test
2. **DRY** - Evitare duplicazione codice
3. **KISS** - Mantenere funzioni semplici (<100 righe target)
4. **Documentazione** - Aggiornare docs se necessario

### Code Review Checklist

- [ ] Il codice è testato?
- [ ] Ci sono duplicazioni da eliminare?
- [ ] La funzione/classe è troppo grande?
- [ ] La documentazione è aggiornata?
- [ ] I nomi sono descrittivi?
- [ ] Error handling appropriato?

---

## 📞 Supporto

- **Issues**: https://github.com/alby69/ERPSEED/issues
- **Discussions**: https://github.com/alby69/ERPSEED/discussions
- **Email**: (da aggiungere)

---

*Ultimo aggiornamento: 2026-03-18*
