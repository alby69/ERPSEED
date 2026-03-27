# Developer Guide - ERPSEED Backend

## Setup Locale

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ (consigliato per JSONB, SQLite supportato per dev)
- Git
- Docker (opzionale)

### 1. Clone e Installazione

```bash
# Clona il repository
git clone https://github.com/alby69/ERPSEED.git
cd ERPSEED/backend

# Crea virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Installa dipendenze
pip install -r requirements.txt
```

### 2. Configurazione

```bash
# Crea file .env
cat > .env << 'EOF'
DATABASE_URL=postgresql://user:pass@localhost:5432/erpseed
JWT_SECRET_KEY=your-super-secret-key-at-least-32-chars-long
SECRET_KEY=flask-secret-key-change-in-production
FLASK_ENV=development
FLASK_DEBUG=1
EOF
```

### 3. Avvio

```bash
# Modalità sviluppo (usa run.py nella root)
python run.py
```

L'API sarà disponibile su `http://localhost:5000` con documentazione Swagger su `http://localhost:5000/swagger-ui`.

---

## Creare un Nuovo Modulo (Pattern Command Handler)

ERPSeed utilizza un'architettura modulare. Ogni nuovo modulo deve essere creato sotto `backend/modules/` seguendo questa struttura:

```
backend/modules/myapp/
├── api/
│   └── rest_api.py        # Blueprint e Rotte Flask
├── application/
│   ├── commands/          # Classi Command (Dataclasses)
│   └── handlers.py        # Logica di business
├── domain/                # Modelli di dominio e logica pura
├── infrastructure/        # Repository o adapter esterni
└── service.py             # Facciata per l'uso interno del modulo
```

### 1. Definizione del Comando
```python
# application/commands/myapp_commands.py
@dataclass
class CreateItemCommand:
    name: str
    description: str
```

### 2. Implementazione dell'Handler
```python
# application/handlers.py
class MyappCommandHandler:
    def handle_create(self, cmd):
        item = MyModel(name=cmd.name, description=cmd.description)
        db.session.add(item)
        db.session.commit()
        return item
```

### 3. Endpoint API
```python
# api/rest_api.py
@blp.route("/")
class MyappList(MethodView):
    @blp.arguments(MySchema)
    def post(self, data):
        service = get_myapp_service()
        return service.create_item(data)
```

---

## CQRS e Read Model (JSONB)

Quando si lavora con dati che richiedono alte performance in lettura o dashboard complesse, utilizzare il **Read Model**:

1. **Scrittura**: Salva i dati normalmente tramite SQLAlchemy.
2. **Sincronizzazione**: Il sistema pubblica automaticamente eventi `record.created` / `record.updated`.
3. **Lettura**: Interroga la tabella `sys_read_models` filtrando per `model_name` e `project_id`. Il campo `data` contiene il record in formato JSONB.

Esempio query JSONB (SQL):
```sql
SELECT data->>'nome' FROM sys_read_models WHERE model_name = 'cliente';
```

---

## Testing

### Esecuzione Test

```bash
# Assicurati che PYTHONPATH sia impostato
export PYTHONPATH=.
pytest backend/tests/
```

### Struttura Test

I test si trovano in `backend/tests/` e utilizzano `pytest`. Per nuovi moduli, aggiungere un file `test_module_name.py`.

---

## Troubleshooting

- **ImportError**: ERPSeed usa import assoluti (es. `from backend.core.utils.utils import ...`). Assicurati di non usare import relativi tra moduli diversi.
- **Circular Imports**: Se due moduli dipendono l'uno dall'altro, sposta la logica comune in `backend/core/` o usa lazy imports all'interno dei metodi.
- **Database Locked**: Se usi SQLite, evita transazioni lunghe. PostgreSQL è caldamente consigliato per lo sviluppo di nuove funzionalità.

---

*Ultimo aggiornamento: 2024-05-24*
