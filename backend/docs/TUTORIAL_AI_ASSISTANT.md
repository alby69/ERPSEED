# Tutorial AI Assistant

## Come funziona l'AI Assistant

L'AI Assistant di ERPSeed permette di creare modelli, campi, viste e automazioni usando linguaggio naturale. È accessibile dall'interfaccia web (pulsante AI Assistant nella sidebar) o via API REST.

## Architettura

```
Utente (testo) → API /api/v1/ai/generations → AIService → LLM (DeepSeek/GPT/Claude) → Tool Calls
                                                                                            ↓
Utente ← Config JSON ← API ← generate_erp_config() ← Tool Results ← Esecuzione Tools
                                          ↓ (opzionale: "Applica")
API /api/v1/ai/applications → builder_service.create_model() → builder_service.create_field() → sync_schema()
```

**Flusso:**

1. L'utente scrive una richiesta in italiano (es. "Crea un modello Clienti con nome e partita IVA")
2. Il backend costruisce un **prompt contestuale** con la struttura del progetto corrente (modelli, campi, workflow esistenti)
3. Il prompt viene inviato a un **LLM** (Large Language Model) con una serie di **tool definitions**
4. Il LLM decide se:
   - **Generare un piano** (tool `generate_json`) — restituisce un JSON di configurazione da mostrare all'utente per revisione
   - **Applicare direttamente** (tool `apply_config`) — crea modelli e campi immediatamente
5. La risposta viene elaborata in un piano esecutivo e restituita al frontend
6. L'utente può modificare il piano o cliccare "Applica" per eseguirlo

## Configurazione Provider LLM

L'AI Assistant supporta 4 provider. **Il funzionamento richiede una chiave API valida.**

| Provider | Variabile d'ambiente | Come ottenere la chiave |
|----------|---------------------|-------------------------|
| **OpenRouter** (default) | `LLM_PROVIDER=openrouter` + `OPENROUTER_API_KEY` | https://openrouter.ai/keys (gratuito con crediti iniziali) |
| **OpenAI** | `LLM_PROVIDER=openai` + `OPENAI_API_KEY` | https://platform.openai.com/api-keys |
| **Anthropic** | `LLM_PROVIDER=anthropic` + `ANTHROPIC_API_KEY` | https://console.anthropic.com/ |
| **Ollama** (locale) | `LLM_PROVIDER=ollama` | Nessuna chiave — richiede Ollama in esecuzione su `http://localhost:11434` |

### Configurare OpenRouter (consigliato)

1. Vai su https://openrouter.ai/keys e crea un account
2. Genera una API key
3. Aggiungila al tuo ambiente:

```bash
# Nel docker-compose.yml, sotto environment del servizio backend:
#   - OPENROUTER_API_KEY=sk-or-v1-la-tua-chiave

# Oppure in una shell prima di avviare:
export OPENROUTER_API_KEY=sk-or-v1-la-tua-chiave
docker-compose up -d
```

### Configurare Ollama (locale, gratuito)

```bash
# Installa Ollama: https://ollama.com/download
# Scarica un modello (es. llama3):
ollama pull llama3

# Avvia Ollama:
ollama serve

# Imposta il provider nel docker-compose.yml:
#   environment:
#     - LLM_PROVIDER=ollama
#     - OLLAMA_BASE_URL=http://host.docker.internal:11434
```

## Usare l'AI Assistant via CLI

### 1. Generare una configurazione

```bash
TOKEN=$(curl -s -X POST http://localhost:5000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@erpseed.it","password":"admin123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token'))")

curl -s -X POST "http://localhost:5000/api/v1/ai/generations" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "request": "Crea un modello Fornitori con campi: ragione_sociale (stringa, obbligatorio), partita_iva (stringa, unico), telefono (stringa)",
    "projectId": 1
  }' | jq
```

Risposta attesa:
```json
{
  "success": true,
  "config": {
    "models": [
      {
        "name": "fornitori",
        "title": "Fornitori",
        "fields": [...]
      }
    ]
  },
  "message": "Ho creato il modello Fornitori con i campi richiesti.",
  "created_models": ["fornitori"]
}
```

### 2. Applicare una configurazione

Dopo aver generato e revisionato il piano, lo si applica con:

```bash
curl -s -X POST "http://localhost:5000/api/v1/ai/applications" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "models": [
      {
        "name": "fornitori",
        "title": "Fornitori",
        "fields": [
          {"name": "ragione_sociale", "type": "string", "required": true, "title": "Ragione Sociale"},
          {"name": "partita_iva", "type": "string", "is_unique": true, "title": "Partita IVA"},
          {"name": "telefono", "type": "string", "title": "Telefono"}
        ]
      }
    ]
  }' | jq
```

## Cosa può fare l'AI Assistant

| Azione | Descrizione | Tool LLM |
|--------|-------------|----------|
| Creare modelli | Modelli con campi di vari tipi (stringa, numero, data, select, relazione) | `generate_json` / `apply_config` |
| Aggiungere campi | A modelli esistenti | `generate_json` |
| Creare workflow | Automazioni condizionali (es. "Se costo > 1000, invia notifica") | `create_workflow` |
| Creare viste UI | List view, form view, kanban, dashboards | `create_ui_view`, `add_ui_component` |
| Regole di business | Validazioni e logica personalizzata | `register_business_rule` |
| Test suite | Generare test CRUD per un modello | `generate_test_suite` |

## Casi d'uso avanzati

### Modificare modelli esistenti con l'AI

L'AI Assistant può generare configurazioni che includono modifiche a modelli esistenti. Esempio — creare un modello **Brand** e trasformare il campo `brand` in una **relation** su **Vehicle**:

```
Crea un modello Brand per le marche automobilistiche, con campi:
- name (stringa, obbligatorio, unico): nome della marca
- country (stringa, opzionale): paese d'origine

Poi modifica Vehicle: aggiungi brand_id (relation → brand, label_field=name),
rimuovendo il vecchio campo brand di tipo select.
```

L'AI genererà un JSON con:
1. Un nuovo modello `Brand`
2. Una nuova definizione per `Vehicle` che include solo il campo `brand_id` (relation) e non il vecchio `brand` (select)

Dopo aver applicato la configurazione:
1. **Elimina manualmente** il vecchio campo `brand` (select) da Vehicle (Builder → modifica modello → rimuovi campo)
2. **Genera la tabella** per Brand (Application → Models → Brand → Generate Table)
3. **Genera la tabella** per Vehicle per sincronizzare il DB

### Creare modelli con relazioni (1:N)

Prompt:
```
Crea un modello Clienti con campi: nome (stringa, obbligatorio), email (stringa).
Poi crea un modello Ordini collegato a Clienti con: data (date, obbligatorio),
totale (decimal), cliente_id (relation → clienti, label_field=nome).
```

## Note importanti

- **Il progetto deve esistere** prima di usare l'AI Assistant (il `projectId` è richiesto)
- L'AI Assistant genera configurazioni JSON — le modifiche a campi esistenti (cambio tipo, cancellazione) vanno fatte manualmente dal Builder UI
- Dopo la creazione, i modelli vanno **pubblicati** (tramite "Generate Table" nell'interfaccia o chiamando `/api/v1/sys-models/{id}/generate-table`)
- La qualità della risposta dipende dal LLM utilizzato — DeepSeek via OpenRouter è il default
- Il sistema costruisce un contesto RAG (Retrieval-Augmented Generation) con la struttura del progetto corrente prima di inviare la richiesta al LLM

## Troubleshooting

**"No response from AI"** — Il provider LLM non è configurato o la chiave API non è valida. Imposta `OPENROUTER_API_KEY` o cambia provider.

**"Errore 422 (Unprocessable Entity)"** — Il frontend invia `project_id` ma il backend si aspetta `projectId`. Assicurati di usare `projectId` (camelCase) nel body JSON.

**"Errore 500 su DELETE/PUT /api/v1/sys-fields/{id}"** — Il backend non aveva i metodi `handle_update_field` e `handle_delete_field` in `BuilderCommandHandler`. Fix: aggiornare `backend/modules/builder/application/handlers.py` con le implementazioni mancanti.

**"Entity namespace for blocks..."** — Bug nel contesto che è stato fixato; se lo incontri, aggiorna il backend.

**"Conversation not found" / 422 su GET /api/v1/ai/conversations** — Il decorator Flask-Smorest necessita di `location="query"` per parametri su richieste GET. Aggiornare `api.py`.

**"/api/ai invece di /api/v1/ai"** — Il frontend normalizza automaticamente `/api/...` in `/api/v1/...`. Il backend deve avere il Blueprint registrato su `/api/v1/ai`.

**CORS bloccato** — Assicurati che il frontend sia su `http://localhost:5173` (l'unica origin permessa dal CORS di default).

**Modello resta in status "draft" dopo Generate Table** — Se il comando `sync_schema` non aggiorna lo status, verifica che `handlers.py:handle_sync_schema` esegua `model.status = "published"` dopo il successo della query SQL.

**Select field vuoto in edit form** — Se il dropdown select non mostra le opzioni, verifica che `dynamic_api_service.py:get_model_metadata` usi `require_published=False`.

**JWT scade troppo presto** — In `backend/__init__.py`, imposta `JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)` per sviluppo.
