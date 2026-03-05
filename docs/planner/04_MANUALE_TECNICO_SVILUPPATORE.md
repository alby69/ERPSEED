# 🛠️ Manuale Tecnico Sviluppatore FlaskERP

## Benvenuto, Developer!

FlaskERP è un ecosistema low-code "Living Code" basato su Flask (Backend) e React (Frontend). In questa guida tecnica, esploreremo come estendere e personalizzare il sistema con esempi pratici.

---

## 🏗️ Architettura Core: I Quattro Pilastri

1.  **SysModel & Fields**: Lo schema dati dinamico memorizzato nel database.
2.  **Blocks & Components**: L'interfaccia UI generata dinamicamente dal backend.
3.  **Hooks & Events**: La logica di business e l'automazione.
4.  **AI Assistant**: Il motore di generazione automatica via LLM.

---

## 📝 Esempio: Creare un Nuovo Modello Programmabilmente

Puoi creare modelli direttamente tramite il `BuilderService`.

```python
from backend.services.builder_service import BuilderService

builder_service = BuilderService()

# 1. Crea il modello
nuovo_modello = builder_service.create_model(
    project_id=1,
    name="ordini_speciali",
    title="Ordini Speciali",
    description="Modello per ordini con lavorazione custom"
)

# 2. Aggiungi i campi
builder_service.create_field(
    model_id=nuovo_modello.id,
    name="codice",
    field_type="string",
    title="Codice Ordine",
    required=True
)

builder_service.create_field(
    model_id=nuovo_modello.id,
    name="note_tecniche",
    field_type="text",
    title="Note Tecniche"
)
```

---

## ⚡ Esempio: Implementare un Hook di Business Logic

Gli Hook sono funzioni eseguite in risposta a eventi del database (before/after create, update, delete).

```python
# backend/plugins/my_plugin/plugin.py
from backend.composition.hooks import register_hook

@register_hook("ordini_speciali", "before_create")
def valida_codice_ordine(data, **kwargs):
    """Verifica che il codice inizi sempre con 'SPEC-'."""
    codice = data.get("codice", "")
    if not codice.startswith("SPEC-"):
        raise ValueError("Il codice deve iniziare con 'SPEC-'")
    return data
```

---

## 🔗 Esempio: Consumare le API Dinamiche

Ogni modello creato genera automaticamente endpoint CRUD protetti da JWT.

```bash
# Richiesta GET per la lista degli ordini speciali
curl -X GET "http://localhost:5000/api/modules/custom/ordini_speciali" \
     -H "Authorization: Bearer <your_jwt_token>"

# Risposta JSON:
# {
#   "data": [
#     {"id": 1, "codice": "SPEC-001", "note_tecniche": "Lavorazione laser"},
#     {"id": 2, "codice": "SPEC-002", "note_tecniche": "Verniciatura oro"}
#   ],
#   "total": 2
# }
```

---

## 🤖 Esempio: Usare l'AI Assistant via API

Puoi integrare l'AI in script esterni per generare configurazioni on-the-fly.

```python
import requests

url = "http://localhost:5000/api/ai/generate"
payload = {
    "request": "Aggiungi un campo 'data_consegna' di tipo date al modello ordini_speciali",
    "project_id": 1
}
headers = {"Authorization": "Bearer <token>"}

response = requests.post(url, json=payload, headers=headers)
print(response.json()["message"])
```

---

## 🧪 Testing e Qualità: Il Quality Score

Prima di pubblicare un modulo nel Marketplace, deve passare i test automatici.

```bash
# Esegui la test suite per un modello specifico
curl -X POST "http://localhost:5000/api/v1/modules/5/test" \
     -H "Authorization: Bearer <token>"
```

I test controllano:
-   **CRUD Integrity**: Creazione, lettura, modifica e cancellazione.
-   **Schema Consistency**: Corrispondenza tra DB e definizioni Builder.
-   **Hook Validation**: Corretto funzionamento della logica registrata.

---

## 🛠️ Strumenti di Sviluppo Consigliati

-   **Postman/Insomnia**: Per testare gli endpoint API.
-   **pgAdmin**: Per ispezionare gli schemi multi-tenant nel database.
-   **React DevTools**: Per ispezionare i componenti dinamici nel frontend.

*Marzo 2026*
