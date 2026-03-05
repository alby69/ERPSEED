# AI Assistant - Guida all'Agente AI

## Introduzione

L'AI Assistant è un assistente che ti aiuta a costruire il tuo ERP usando il linguaggio naturale. Invece di dover navigare interfacce e configurare manualmente, puoi semplicemente descrivere quello che ti serve e l'AI si occupa del resto.

Questa funzionalità sfrutta il quarto pilastro di FlaskERP: il Self-Modifying Code. L'AI genera configurazioni che il sistema applica automaticamente.

---

## Come Funziona

### Flusso di Lavoro

```
Tu descrivi → AI comprende → AI genera config → Sistema applica → Risultato
```

1. **Descrivi** la tua esigenza in italiano o inglese
2. **L'AI analizza** e estrae entità, campi, relazioni
3. **L'AI genera** la configurazione per il Builder
4. **Il sistema applica** la configurazione automaticamente
5. **Il risultato** è pronto per l'uso

### Esempi Pratici

**Esempio 1: Modello Semplice**

> "Voglio un modulo per gestire i miei fornitori con nome, indirizzo, telefono e email."

L'AI genera:
- Modello "Fornitore"
- Campi: nome, indirizzo, telefono, email
- API e interfaccia

**Esempio 2: Con Relazioni**

> "Creo un modulo ordini collegato ai clienti. Ogni ordine ha data, totale e stato."

L'AI genera:
- Modello "Ordine" 
- Relazione al modulo Clienti
- Campi: data, totale, stato
- Ordine "cliente" di tipo relation

**Esempio 3: Complesso - Gestione Parco Mezzi**

> "Crea un sistema per gestione parco mezzi con veicoli, conducenti e manutenzione"

L'AI genera:
- Modello "Veicolo" (targa, marca, modello, anno, stato)
- Modello "Conducente" (nome, cognome, numero patente)
- Modello "Manutenzione" (veicolo, tipo, date, costo)
- Modello "Assegnazione" (veicolo-conducente)

---

## Stato di Implementazione

| Componente | Stato | Note |
|------------|-------|------|
| Architettura base | ✅ Completo | Service + API |
| Integrazione LLM (OpenRouter) | ✅ Completo | DeepSeek V3 |
| RAG Context Injection | ✅ Completo | Context from project schema |
| Tool Calling (CRUD) | ✅ Completo | list/create/get/update/delete su modelli |
| Tool Calling (Business Logic) | ✅ Completo | Workflow, Hooks, Scheduled Tasks |
| Tool Calling (Test Generator) | ✅ Completo | Generazione test automatici |
| Workflow update_record | ✅ Completo | DynamicApiService integration |
| Workflow create_record | ✅ Completo | DynamicApiService integration |
| Business Rules UI | ✅ Completo | Pagina frontend |
| Generazione modelli da linguaggio naturale | ✅ Completo | Genera JSON config |
| Interfaccia chat frontend | ✅ Completo | Modal con chat |
| Preview JSON modificabile | ✅ Completo | Modale con TextArea |
| Applicazione configurazione al DB | ✅ Completo | Crea modelli, campi, tabelle |
| Feedback Loop (Learning) | ✅ Completo | Salva conversazioni in DB |
| Cronologia conversazioni | ✅ Completo | UI con history panel |
| Autenticazione JWT | ✅ Abilitata | Protegge tutti gli endpoint |

---

## Utilizzo

1. Vai su **Administration → AI Assistant** nel menu
2. Descrivi il modulo che vuoi creare
3. Visualizza l'anteprima JSON
4. Modifica se necessario
5. Clicca "Applica al Progetto"

### Accesso

L'AI Assistant è accessibile dall'interfaccia principale attraverso:

- Menu **Administration → AI Assistant** (path: `/ai-assistant`)
- Un endpoint API per integrazioni

### Come Comunicare

**Sii specifico**: Più dettagli fornisci, migliore è il risultato.

**Includi**:
- Nome delle entità
- Campi necessari
- Eventuali relazioni
- Comportamenti speciali

**Esempio dettagliato**:

> "Crea un modulo 'Progetti' con: nome progetto (testo), cliente (collegato a Clienti), data inizio, data fine prevista, budget, stato (bozza, attivo, completato, sospeso), responsabile (collegato a Utenti)."

---

## Implementazione

### Architettura

L'AI Assistant è composto da:

- **Backend Service**: `backend/ai/service.py`
- **Tool Registry**: `backend/ai/tool_registry.py`
- **LLM Adapters**: `backend/ai/adapters/`
- **Context Builder (RAG)**: `backend/ai/context.py`
- **Backend API**: `backend/ai/api.py`
- **Frontend**: `frontend/src/components/ui/AIAssistant.jsx`

### Stack Tecnologico

- **LLM**: OpenRouter (default) o Anthropic Claude
- **RAG**: Context Injection dal schema del progetto
- **Tool Calling**: Sistema embedded con ToolRegistry
- **Database**: AIConversation per feedback loop
- **Frontend**: React con Ant Design (Modal, List, Input)

### Tool Registry (Embedded Tool Calling)

Il sistema implementa un **Tool Registry** che converte automaticamente i modelli dinamici (SysModel) in definizioni tool per LLM.

#### Architettura del Tool Registry

```
backend/ai/
├── tool_registry.py      # Core: mapping tipi, generazione tool
├── service.py            # AIService principale
├── context.py            # RAG Context Builder
└── adapters/
    ├── __init__.py       # Factory get_adapter()
    ├── base.py           # Interfaccia LLMAdapter
    ├── openrouter.py     # Adapter OpenRouter
    └── anthropic.py     # Adapter Anthropic
```

#### Mapping Tipi SysField → JSON Schema

| SysField.type | JSON Schema | Descrizione |
|---------------|-------------|-------------|
| `string` | `string` | Testo breve |
| `text` | `string` | Testo lungo |
| `integer` | `integer` | Numero intero |
| `decimal` | `number` | Numero decimale |
| `boolean` | `boolean` | Vero/Falso |
| `date` | `string` (format: date) | Data ISO 8601 |
| `datetime` | `string` (format: datetime) | Data e ora |
| `select` | `string` (enum) | Valori predefiniti |
| `relation` | `integer` | FK a altro modello |
| `tags` | `array` | Lista tag |
| `json` | `object` | Oggetto JSON |

#### Tool Generati per Modello

Per ogni modello pubblicato nel Builder, il sistema genera automaticamente 5 tool:

| Tool | Descrizione |
|------|-------------|
| `list_<model>` | Lista record con paginazione, filtro, ordinamento |
| `create_<model>` | Crea nuovo record |
| `get_<model>` | Ottieni singolo record per ID |
| `update_<model>` | Aggiorna record esistente |
| `delete_<model>` | Elimina record |

#### Esempio Tool Definition

```json
{
  "name": "list_clienti",
  "description": "List records from Clienti model. Supports filtering, pagination, sorting.",
  "input_schema": {
    "type": "object",
    "properties": {
      "page": {"type": "integer", "default": 1},
      "per_page": {"type": "integer", "default": 10},
      "q": {"type": "string", "description": "Search query"},
      "sort_by": {"type": "string"},
      "sort_order": {"type": "string", "enum": ["asc", "desc"]}
    }
  }
}
```

#### Formati Supportati

Il sistema supporta entrambi i formati tool:

**Anthropic**:
```json
{
  "name": "tool_name",
  "description": "...",
  "input_schema": {...}
}
```

**OpenAI** (usato da OpenRouter):
```json
{
  "type": "function",
  "function": {
    "name": "tool_name",
    "description": "...",
    "parameters": {...}
  }
}
```

#### Caching

Le definizioni tool vengono cachate per 5 minuti (configurabile). La cache viene invalidata automaticamente quando un modello viene modificato.

```python
# Configurazione cache
tool_registry.set_cache_ttl(300)  # 5 minuti
tool_registry.invalidate_cache(project_id=1)  # Invalida cache progetto
```

### Context Injection (RAG)

Il sistema costruisce automaticamente il contesto includendo:

- **Info Progetto**: nome, descrizione, titoli
- **Modelli Esistenti**: nomi, campi, tipi, relazioni
- **Blocchi UI**: blocchi personalizzati creati
- **Workflow**: workflow esistenti nel progetto
- **Conversazioni Precedenti**: per apprendimento incrementale

```python
# backend/ai/context.py
class AIContextBuilder:
    def build_context(self) -> str:
        # 1. Info progetto
        # 2. Modelli esistenti con campi
        # 3. Blocchi disponibili
        # 4. Workflow esistenti
        # 5. Cronologia conversazioni (per learning)
```

### Tool Calling (Base)

L'AI utilizza tool calling per azioni specifiche:

| Tool | Descrizione |
|------|-------------|
| `generate_json` | Genera config JSON senza applicare |
| `apply_config` | Applica la configurazione al DB |
| `create_workflow` | Crea un workflow automatico |

### Tool Calling per Business Logic

Il sistema implementa tool per creare automazioni e logica di business direttamente da linguaggio naturale.

#### Workflow Automation Tools

| Tool | Descrizione |
|------|-------------|
| `create_workflow_automation` | Crea un workflow completo con trigger, condizioni e azioni |
| `update_workflow` | Aggiorna un workflow esistente |
| `delete_workflow` | Elimina un workflow |

#### Hooks e Regole di Business

| Tool | Descrizione |
|------|-------------|
| `register_business_rule` | Registra una regola su un modello (before/after create/update/delete) |
| `list_business_rules` | Lista tutte le regole di business |
| `delete_business_rule` | Elimina una regola |

#### Scheduled Tasks

| Tool | Descrizione |
|------|-------------|
| `create_scheduled_task` | Crea un task programmato (cron-like) |
| `delete_scheduled_task` | Elimina un task programmato |

#### Notifications

| Tool | Descrizione |
|------|-------------|
| `setup_notification` | Configura notifiche automatiche per eventi |

### Validazione di Sicurezza

Tutti i tool di business logic includono validazione prima dell'esecuzione:

- **Workflow**: Validazione schema JSON, operatori consentiti
- **Hooks**: Controllo pattern pericolosi (eval, exec, etc.)
- **Scheduled Tasks**: Validazione formato cron

### AI Test Generator

L'AI può generare automaticamente test cases per validare i tuoi modelli.

#### Tool Disponibili

| Tool | Descrizione |
|------|-------------|
| `generate_test_suite` | Genera test suite completa per un modello |
| `list_test_suites` | Lista test suite disponibili |
| `run_test_suite` | Esegue una test suite |

#### Tipi di Test Generati

| Tipo | Descrizione |
|------|-------------|
| **CREATE** | Test creazione record |
| **READ** | Test lettura lista e singolo |
| **UPDATE** | Test aggiornamento |
| **DELETE** | Test eliminazione |
| **VALIDATION** | Test campi obbligatori e formati |

#### Esempio

**Input utente:**
> "Crea test per il modello Clienti"

**Risultato:**
```
Generated: Test Suite Clienti
Total test cases: 9

Test cases:
  - Create Clienti - Success
  - Create Clienti - Missing Required
  - List Clienti
  - Get Clienti by ID
  - Get Clienti - Not Found
  - Update Clienti - Success
  - Update Clienti - Not Found
  - Delete Clienti - Success
  - Delete Clienti - Not Found
```

I test vengono salvati nel DB e possono essere eseguiti tramite il **Test Runner** (`/admin/test-runner`).

### Esempi di Utilizzo

#### Esempio 1: Workflow Automation

**Input utente:**
> "Quando viene creato un ordine con totale > 1000€, invia una notifica email al manager"

**Tool generato:**
```json
{
  "name": "create_workflow_automation",
  "input": {
    "name": "approvazione_ordini_alto_valore",
    "trigger_model": "ordini",
    "trigger_event": "record.created",
    "steps": [
      {
        "step_type": "condition",
        "name": "check_importo",
        "config": {
          "field": "totale",
          "operator": "greater_than",
          "value": "1000"
        }
      },
      {
        "step_type": "notification",
        "name": "notifica_manager",
        "config": {
          "type": "email",
          "to": "manager@example.com"
        }
      }
    ]
  }
}
```

#### Esempio 2: Business Rule

**Input utente:**
> "Valida che il campo partita IVA sia sempre presente quando si crea un fornitore"

**Tool generato:**
```json
{
  "name": "register_business_rule",
  "input": {
    "model_name": "fornitori",
    "hook_type": "before_create",
    "rule_name": "partita_iva_obbligatoria",
    "action": {
      "type": "validate",
      "config": {
        "field": "partita_iva",
        "required": true
      }
    }
  }
}
```

---

### LLM Adapters

Il sistema supporta molteplici provider LLM tramite adapter:

#### Provider Supportati

| Provider | Modello Default | Configurazione |
|----------|-----------------|----------------|
| **OpenRouter** (default) | `deepseek/deepseek-chat-v3-0324` | `OPENROUTER_API_KEY` |
| **Anthropic Claude** | `claude-sonnet-4-20250514` | `ANTHROPIC_API_KEY` |

#### Configurazione

```bash
# Opzione 1: OpenRouter (default)
export LLM_PROVIDER=openrouter
export OPENROUTER_API_KEY=sk-or-...

# Opzione 2: Anthropic Claude
export LLM_PROVIDER=anthropic
export ANTHROPIC_API_KEY=sk-ant-...
```

#### Utilizzo Programmato

```python
from backend.ai.service import AIService
from backend.ai.adapters import get_adapter

# Con OpenRouter (default)
ai = AIService()

# Con Anthropic
ai = AIService(provider="anthropic")

# Direct adapter access
adapter = get_adapter("anthropic")
```

#### Estendere con Nuovi Adapter

Per aggiungere un nuovo provider:

1. Crea una classe che estende `LLMAdapter` in `backend/ai/adapters/`
2. Implementa i metodi `chat()` e `extract_tool_calls()`
3. Registrala in `backend/ai/adapters/__init__.py`

```python
from backend.ai.adapters.base import LLMAdapter, LLMResponse, ToolCall

class MyAdapter(LLMAdapter):
    @property
    def provider_name(self) -> str:
        return "my_provider"
    
    def chat(self, messages, tools=None, **kwargs) -> LLMResponse:
        # Implementa chiamata API
        pass
    
    def extract_tool_calls(self, response_data) -> List[ToolCall]:
        # Estrai tool call dalla risposta
        pass
```

---

## Endpoint API

| Endpoint | Metodo | Autenticazione | Descrizione |
|----------|--------|----------------|-------------|
| `/api/ai/generate` | POST | JWT | Genera config ERP da linguaggio naturale |
| `/api/ai/apply` | POST | JWT | Applica la configurazione generata al database |
| `/api/ai/suggestions` | POST | JWT | Ottiene suggerimenti per migliorare un modello esistente |
| `/api/ai/models` | GET | JWT | Lista i modelli LLM disponibili (es. DeepSeek, Claude) |
| `/api/ai/conversations` | GET | JWT | Recupera la cronologia delle conversazioni per il progetto |
| `/api/ai/feedback` | POST | JWT | Salva il feedback dell'utente per migliorare l'AI (Learning Loop) |

---

## Funzionalità Supportate

### Creazione Modelli

L'AI può creare:
- Modelli con tutti i tipi di campo (string, text, integer, decimal, boolean, date, select, relation)
- Relazioni tra modelli
- Validazioni (required, unique)
- Descrizioni

### Configurazione

L'AI può configurare:
- Nomi tabella (automatici dal modello)
- Label dei campi
- Descrizioni

### Feedback Loop (Apprendimento)

Il sistema salva le conversazioni per apprendimento incrementale:

1. Ogni conversazione viene salvata nel DB
2. L'utente può dare feedback (thumbs up/down)
3. Le conversazioni di successo vengono usate come contesto per richieste future

```python
# backend/models.py
class AIConversation(BaseModel):
    project_id = db.Column(db.Integer, ...)
    user_message = db.Column(db.Text, ...)
    ai_response = db.Column(db.Text, ...)
    was_successful = db.Column(db.Boolean, ...)
    user_correction = db.Column(db.Text, ...)
    context_snapshot = db.Column(db.Text, ...)
```

---

## Integrazione API

### Generazione Configurazione

```
POST /api/ai/generate
{
  "request": "Crea modulo per gestire fornitori",
  "project_id": 1
}
```

Risposta:
```json
{
  "success": true,
  "config": {
    "models": [
      {
        "name": "Fornitore",
        "table": "fornitori",
        "fields": [...]
      }
    ]
  },
  "created_models": ["Fornitore"],
  "message": "Ho creato il modello Fornitori con i campi richiesti."
}
```

### Applicazione Configurazione

```
POST /api/ai/apply
{
  "config": { ... },
  "project_id": 1
}
```

### Salvataggio Feedback

```
POST /api/ai/feedback
{
  "conversation_id": 1,
  "was_successful": true,
  "rating": 5,
  "user_correction": null
}
```

---

## Best Practices

### Per ottenere risultati migliori

1. **Inizia semplice**: Prima richieste basiche, poi complesse
2. **Sii iterativo**: Raffina il risultato passo dopo passo
3. **Verifica sempre**: Controlla ciò che l'AI ha generato
4. **Correggi**: Se qualcosa non è giusto, spiega all'AI come correggerlo
5. **Dai feedback**: Usa i pulsanti thumbs up/down per migliorare il sistema

### Esempio Conversazione

```
Tu: Crea modulo clienti
AI: Ho creato il modulo Clienti con i campi base.

Tu: Aggiungi anche partita iva e codice fiscale
AI: Ho aggiunto i campi partita_iva e codice_fiscale al modulo Clienti.

Tu: Collegalo al modulo ordini
AI: Ho creato la relazione tra Clienti e Ordini. Ora ogni cliente può avere molti ordini.

[Tu: Thumbs Up]
→ Feedback salvato per apprendimento futuro
```

---

## Test - Gestione Parco Mezzi

Esempio di test eseguito con successo:

**Richiesta**: "Crea un sistema per gestione parco mezzi con veicoli, conducenti e manutenzione"

**Risultato**: L'AI ha generato 4 modelli:
- `Veicolo` (targa, marca, modello, anno, km, stato)
- `Conducente` (nome, cognome, patente)
- `Manutenzione` (veicolo, tipo, date, costo)
- `Assegnazione` (veicolo, conducente, date)

**Workflow**:
1. Generazione → 2. Preview JSON → 3. Applica → 4. Modelli creati nel DB

---

## Roadmap

L'AI Assistant è in fase di sviluppo. Prossime funzionalità:

- [x] Generazione modelli da linguaggio naturale
- [x] Interfaccia chat
- [x] Preview JSON modificabile
- [x] Applicazione configurazione al database
- [x] RAG Context Injection
- [x] Tool Calling
- [x] Feedback Loop per apprendimento
- [ ] Generazione automatica test
- [ ] Creazione workflow (integrazione con Workflow Builder)
- [ ] Suggerimenti intelligenti
- [ ] Integrazione Marketplace

---

## Conclusione

L'AI Assistant rende FlaskERP ancora più accessibile. Anche senza conoscenze tecniche, puoi costruire il tuo sistema gestionale semplicemente descrivendo ciò che ti serve.

Il sistema impara dalle conversazioni: più lo usi, migliore sarà il risultato grazie al feedback loop.

Prova e vedrai: descrivere in linguaggio naturale quello che vuoi è spesso più veloce che cliccare tra mille opzioni.

---

## File di Riferimento

### Core AI
- Service: `backend/ai/service.py`
- Tool Registry: `backend/ai/tool_registry.py`
- Tool Executors: `backend/ai/tool_executors.py`
- Test Generator: `backend/ai/test_generator.py`
- Context Builder: `backend/ai/context.py`

### LLM Adapters
- Adapter Base: `backend/ai/adapters/base.py`
- OpenRouter Adapter: `backend/ai/adapters/openrouter.py`
- Anthropic Adapter: `backend/ai/adapters/anthropic.py`
- Adapter Factory: `backend/ai/adapters/__init__.py`

### Business Logic Components
- Hooks System: `backend/composition/hooks.py`
- Event Bus: `backend/composition/events.py`
- Workflow Models: `backend/workflows.py`
- Workflow Service: `backend/workflow_service.py`
- Webhook Triggers: `backend/webhook_triggers.py`

### Test Components
- Test Models: `backend/core/models/test_models.py`
- Test Engine: `backend/core/services/test_engine.py`
- Test Runner API: `backend/core/api/test_runner.py`

### UI
- AI Assistant: `frontend/src/pages/AIAssistantPage.jsx`
- Business Rules: `frontend/src/pages/BusinessRulesPage.jsx`
- Test Runner: `frontend/src/pages/TestRunnerPage.jsx`

### API
- API Routes: `backend/ai/api.py`
- Modello: `backend/models.py` (AIConversation, SysModel)

### Frontend
- Chat Component: `frontend/src/components/ui/AIAssistant.jsx`

### Configurazione Environment
```bash
LLM_PROVIDER=openrouter  # o "anthropic"
OPENROUTER_API_KEY=sk-or-...
ANTHROPIC_API_KEY=sk-ant-...
```

---

**Per approfondimenti tecnici sugli esempi di codice AI, consulta il [Manuale Tecnico Sviluppatore](planner/04_MANUALE_TECNICO_SVILUPPATORE.md).**

*Documento aggiornato: Marzo 2026*
