# Automazione e Contratti Intelligenti

Questo documento spiega come FlaskERP implementa l'automazione attraverso tre meccanismi complementari: Hook, Eventi e Workflow. Questi formano la base dell'architettura che permette agli oggetti di comunicare e reagire automaticamente agli eventi.

Per una comprensione dell'architettura generale, vedere [01_CONCETTI.md](01_CONCETTI.md).

---

## Panoramica dei Meccanismi

| Meccanismo | Quando si esegue | Chi può configurarlo | Uso principale |
|------------|------------------|---------------------|----------------|
| **Hook** | Nella stessa transazione del chiamante | Sviluppatore (codice) | Logica core, validazioni |
| **Event Bus** | Dopo il commit, in modo asincrono | Sviluppatore (codice) | Comunicazione tra moduli |
| **Workflow** | Dopo l'evento, orchestrazione complessa | Sviluppatore + Amministratore (UI) | Automazione dichiarativa |

---

## 1. Hook (Ganci)

### Cosa sono

Gli hook sono funzioni Python che vengono chiamate automaticamente in momenti specifici del ciclo di vita di un'entità. Esecuzione sincrona, nella stessa transazione del chiamante.

### Tipi disponibili

```
BEFORE_CREATE  → Prima della creazione
AFTER_CREATE  → Dopo la creazione
BEFORE_UPDATE  → Prima dell'aggiornamento
AFTER_UPDATE  → Dopo l'aggiornamento
BEFORE_DELETE  → Prima della cancellazione
AFTER_DELETE  → Dopo la cancellazione
BEFORE_VALIDATE → Prima della validazione
AFTER_VALIDATE  → Dopo la validazione
```

### Esempio 1: Calcolo automatico del totale fattura

Quando viene creata o modificata una riga fattura, il totale viene ricalcolato automaticamente:

```python
@hook("invoice_line.after_create", priority=10)
@hook("invoice_line.after_update", priority=10)
def recalculate_invoice_total(invoice_line):
    """Ricalcola il totale fattura quando una riga cambia."""
    invoice = invoice_line.invoice
    invoice.total = sum(line.amount for line in invoice.lines)
    invoice.tax = invoice.total * invoice.tax_rate / 100
    invoice.grand_total = invoice.total + invoice.tax
    db.session.commit()
```

**Flusso**:
1. L'utente salva una riga fattura
2. L'hook `after_create` viene eseguito **nella stessa transazione**
3. Il totale viene ricalcolato
4. Se fallisce, tutta l'operazione viene annullata (rollback)

### Esempio 2: Validazione stock prima dell'ordine

Prima di creare un ordine, verifica la disponibilità:

```python
@hook("order.before_create", priority=5)
def check_inventory(order):
    """Verifica disponibilità stock prima di creare l'ordine."""
    for item in order.items:
        if item.product.stock < item.quantity:
            raise ValidationError(
                f"Stock insufficiente per {item.product.name}: "
                f"richiesto {item.quantity}, disponibile {item.product.stock}"
            )
```

**Nota**: L'hook ha `priority=5` (più basso di default). Se la validazione fallisce, l'ordine non viene creato.

---

## 2. Event Bus (Eventi)

### Cosa è

Il bus eventi permette a componenti completamente separati di comunicare senza conoscersi. Un componente pubblica un evento, altri componenti si iscrivono per reagire. Esecuzione asincrona, dopo il commit della transazione.

### Caratteristiche

- **Decoupling**: i moduli non si conoscono tra loro
- **Asincrono**: gli handler vengono eseguiti dopo il commit
- **Storico**: gli eventi vengono salvati in history

### Esempio 1: Notifica amministratore

Qualsiasi parte del sistema può pubblicare eventi:

```python
# In un qualunque punto del codice (es. nel controller ordini)
EventBus.publish("order.created", {
    "order_id": 123,
    "customer": "Mario Rossi",
    "total": 1500.00
})

# Il modulo notifiche si iscrive in un altro file
def send_admin_notification(data):
    admin_email = get_settings().admin_email
    send_email(
        to=admin_email,
        subject=f"Nuovo ordine #{data['order_id']}",
        body=f"Cliente: {data['customer']}, Totale: €{data['total']}"
    )

EventBus.subscribe("order.created", send_admin_notification)
```

### Esempio 2: Sincronizzazione magazzino-contabilità

Quando un prodotto viene aggiornato, il modulo contabilità reagisce:

```python
# Nel modulo prodotti
EventBus.publish("product.updated", {
    "product_id": 456,
    "name": "Widget Pro",
    "stock": 100,
    "cost": 25.00
})

# Nel modulo accounting (file separato)
def sync_accounting_inventory(data):
    """Aggiorna i libri contabili quando il magazzino cambia."""
    accounting_entry = AccountingEntry(
        type="inventory_adjustment",
        reference_id=data["product_id"],
        amount=data["cost"] * data["stock"],
        description=f"Stock prodotto: {data['name']}"
    )
    db.session.add(accounting_entry)
    db.session.commit()

EventBus.subscribe("product.updated", sync_accounting_inventory)
```

---

## 3. Workflow (Flussi di Lavoro)

### Cosa sono

I workflow sono sequenze dichiarative di azioni condizionali. A differenza degli hook, sono configurabili via UI dall'amministratore. Rappresentano i "contratti intelligenti" del sistema.

### Componenti

```
Trigger      → Evento che avvia il workflow
Condition    → Condizione per proseguire (se/v-altrimenti)
Action       → Azione da eseguire (imposta campo, crea record, ecc.)
Notification → Notifica (email, webhook)
Delay        → Attesa prima del prossimo step
```

### Esempio 1: Approvazione ordine B2B

Workflow configurabile via UI:

```
Trigger: order.created
├── SE totale > 10000
│   ├── Step: Notifica manager (email a manager@azienda.it)
│   └── Step: Imposta stato = "pending_approval"
└── ALTRIMENTI
    ├── Step: Approva automaticamente (stato = "approved")
    └── Step: Invia conferma cliente (email)
```

In JSON (come salvato nel DB):
```json
{
  "name": "Approvazione ordine B2B",
  "trigger_event": "order.created",
  "steps": [
    {
      "type": "condition",
      "config": {
        "field": "total",
        "operator": "greater_than",
        "value": "10000"
      },
      "on_true": [
        {
          "type": "notification",
          "config": {
            "type": "email",
            "to": "manager@azienda.it",
            "subject": "Ordine richiede approvazione"
          }
        },
        {
          "type": "action",
          "config": {
            "action_type": "set_field",
            "field": "status",
            "value": "pending_approval"
          }
        }
      ],
      "on_false": [
        {
          "type": "action",
          "config": {
            "action_type": "set_field",
            "field": "status",
            "value": "approved"
          }
        },
        {
          "type": "notification",
          "config": {
            "type": "email",
            "template": "order_confirmation"
          }
        }
      ]
    }
  ]
}
```

### Esempio 2: Onboarding dipendente

```
Trigger: employee.created
├── Step: Crea account utente (email = employee.email)
├── Step: Assegna ruolo base (ruolo = "user")
├── SE ruolo == "dipendente"
│   ├── Step: Crea pratica INPS
│   ├── Step: Registra in libro paga
│   └── Step: Invia benvenuto HR
└── SE ruolo == "consulente"
    ├── Step: Crea contratto
    └── Step: Notifica amministratione
```

---

## Relazione tra i Tre Meccanismi

```
┌──────────────────────────────────────────────────────────────────┐
│                         UTENTE SALVA                             │
│                     (es. Ordine, Fattura)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                       ENTITÀ (Model/CRUD)                        │
│                  - Valida i dati                                 │
│                  - Salva nel DB                                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
   ┌───────────┐      ┌───────────┐      ┌─────────────┐
   │   HOOK    │      │   HOOK    │      │  EVENT BUS  │
   │(stessa    │      │(altro     │      │ (pubblica   │
   │ transaz.) │      │ modulo)   │      │  evento)    │
   └─────┬─────┘      └─────┬─────┘      └──────┬──────┘
         │                  │                   │
         │                  │            ┌──────┴──────┐
         │                  │            │             │
         ▼                  ▼            ▼             ▼
   ┌───────────┐      ┌───────────┐ ┌─────────┐ ┌──────────┐
   │ Validazione│      │ Logica    │ │  Hook   │ │Workflow  │
   │ core       │      │ cross-    │ │ (altro  │ │(elabor.  │
   │(es.stock)  │      │ modulo    │ │ modulo) │ │ asincr.) │
   └───────────┘      └───────────┘ └─────────┘ └──────────┘
```

**Differenze chiave**:

| Aspetto | Hook | Event Bus | Workflow |
|---------|------|-----------|----------|
| Transazione | Sincrona (stessa) | Asincrona (dopo commit) | Asincrona |
| Configurazione | Codice Python | Codice Python | UI + Codice |
| Complessità | Semplice | Media | Alta |
| Ordine esecuzione | Per priorità | Indeterminato | Sequenziale |
| Rollback se errore | Sì (transazione) | No | Parziale |

---

## Best Practice

### Quando usare gli Hook

- **Validazioni critiche** che devono bloccare l'operazione
- **Calcoli automatici** che devono essere atomici
- **Logica core** che non deve essere modificabile dall'amministratore

### Quando usare l'Event Bus

- **Comunicazione tra moduli** senza accoppiamento
- **Sincronizzazioni** che possono fallire senza bloccare l'operazione principale
- **Notifiche** che devono avvenire dopo il commit

### Quando usare i Workflow

- **Automazioni business** che devono essere configurabili dall'utente
- **Processi multi-step** con condizioni complesse
- **Approvazioni** e flussi di lavoro

---

## Implementazione

Vedere:
- [Hook Manager](../backend/composition/hooks.py)
- [Event Bus](../backend/composition/events.py)
- [Workflow Service](../backend/workflow_service.py)
- [02_BUILDER.md](02_BUILDER.md) - Per creare i modelli che generano eventi

---

*Prossimo: [02_BUILDER.md](02_BUILDER.md) - Creare moduli e campi*

---

# Appendice: Builder Visivo per Workflow

Questa sezione approfondisce come implementare il builder visivo per permettere agli amministratori di creare workflow senza scrivere codice.

## Architettura del Builder

```
┌─────────────────────────────────────────────────────────────┐
│                    UI (React/Vue)                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Canvas      │  │ Toolbox     │  │ Properties  │         │
│  │ (Drag&Drop) │  │ (Step types)│  │ (Config)    │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
└─────────┼────────────────┼────────────────┼─────────────────┘
          │                │                │
          └────────────────┼────────────────┘
                           ▼
                    ┌─────────────┐
                    │  API Layer  │
                    └──────┬──────┘
                           ▼
              ┌────────────────────────────┐
              │   Workflow Service          │
              │   (validate & execute)      │
              └────────────────────────────┘
```

## Struttura Dati

Il workflow salvato nel DB usa questa struttura:

```python
# Modelli esistenti in backend/workflows.py
class Workflow:
    name: str                      # "Approvazione ordine"
    description: str
    trigger_event: str             # "order.created"
    is_active: bool
    project_id: int                # ambito del workflow

class WorkflowStep:
    order: int                     # ordine di esecuzione
    step_type: str                # "condition", "action", "notification", "delay"
    name: str                      # nome leggibile
    config: JSON                   # configurazione specifica del tipo
```

## Tipi di Step supportati

| Step Type | Configurazione | Esempio |
|-----------|----------------|---------|
| **condition** | `field`, `operator`, `value` | `total > 1000` |
| **action** | `action_type`, `field`, `value` | `set status = "approved"` |
| **notification** | `type`, `to`, `subject`, `template` | invia email |
| **delay** | `duration`, `unit` | aspetta 24 ore |
| **webhook** | `url`, `method`, `headers`, `body` | chiama API esterna |
| **sub_workflow** | `workflow_id` | esegui altro workflow |

## Interfaccia Canvas

### Layout suggerito

```
┌──────────────────────────────────────────────────────────────┐
│  Workflow Builder                              [Salva] [Test]│
├──────────────────────────────────────────────────────────────┤
│  Trigger: [order.created ▼]                                  │
├────────────┬─────────────────────────────────────────────────┤
│  TOOLBOX   │              CANVAS                             │
│            │                                                 │
│  [Condizione]  │  ┌─────────────────────────────────────┐    │
│  [Azione]      │  │ ○──▶[Condition: totale>1000]        │    │
│  [Notifica]    │  │      │                    │         │    │
│  [Ritardo]     │  │    TRUE                 FALSE       │    │
│  [Webhook]     │  │     │                    │          │    │
│            │  │     ▼                    ▼              │    │
│            │  │  ┌──────┐           ┌──────┐            │    │
│            │  │  │Notify│           │Set    │           │    │
│            │  │  │Manager│          │status=│           │    │
│            │  │  └──────┘           │approved           │    │
│            │  │                     └──────┘            │    │
│            │  └─────────────────────────────────────────┘    │
└────────────┴─────────────────────────────────────────────────┘
```

### Proprietà del Nodo (Side Panel)

Quando selezioni un nodo nel canvas, il side panel mostra:

```
┌─────────────────────────┐
│  PROPRIETÀ NODO         │
├─────────────────────────┤
│  Tipo: Condizione       │
│  Nome: Check totale     │
├─────────────────────────┤
│  Campo: [totale ▼]      │
│  Operatore: [> ▼]       │
│  Valore: [1000]         │
└─────────────────────────┘
```

## Operatori Disponibili

### Comparazione
- `equals` - Uguale a
- `not_equals` - Diverso da
- `greater_than` - Maggiore di
- `less_than` - Minore di
- `contains` - Contiene

### Null/Empty
- `is_empty` - È vuoto
- `is_not_empty` - Non è vuoto

### Logica (per combinazioni)
- `and` - E (tutte le condizioni vere)
- `or` - O (almeno una condizione vera)

## Azioni Disponibili

### set_field
Imposta un valore su un campo:
```json
{
  "action_type": "set_field",
  "field": "status",
  "value": "approved"
}
```

### update_record
Aggiorna un record correlato:
```json
{
  "action_type": "update_record",
  "model": "invoice",
  "field": "status",
  "value": "paid",
  "where": "order_id={{order.id}}"
}
```

### create_record
Crea un nuovo record:
```json
{
  "action_type": "create_record",
  "model": "audit_log",
  "data": {
    "action": "order_approved",
    "order_id": "{{order.id}}",
    "user_id": "{{current_user.id}}"
  }
}
```

## Trigger Disponibili

Gli eventi che possono avviare un workflow:

| Evento | Descrizione | Dati disponibili |
|--------|-------------|------------------|
| `entity.created` | Qualsiasi entità creata | `{id, data, model}` |
| `entity.updated` | Qualsiasi entità aggiornata | `{id, old_data, new_data, model}` |
| `entity.deleted` | Qualsiasi entità cancellata | `{id, model}` |
| `order.created` | Ordine creato | `{order.*}` |
| `order.updated` | Ordine aggiornato | `{order.*}` |
| `invoice.created` | Fattura creata | `{invoice.*}` |
| `user.created` | Utente creato | `{user.*}` |
| `custom.*` | Eventi personalizzati |自定义 |

## Validazione in Tempo Reale

Il builder deve validare:
1. **Sintassi**: JSON valido
2. **Referenze**: Campi esistenti nel modello
3. **Cicli**: Nessun loop infinito
4. **Consistenza**: Trigger compatibile con gli step

## Esecuzione/Test

Pulsante "Test" nel builder:
1. Simula il trigger con dati di esempio
2. Esegue il workflow passo-passo
3. Mostra l'output di ogni step
4. Evidenzia errori

```python
# Esempio di test
test_data = {
    "order": {"id": 1, "total": 1500, "customer": "Mario"},
    "current_user": {"id": 5, "name": "Admin"}
}
result = WorkflowService._execute_workflow(workflow, "order.created", test_data)
```

## Implementazione Consigliata

### Frontend (React)
- **React Flow** o **@xyflow/react** per il canvas
- **Zustand** per lo stato del builder
- **React Hook Form** per le proprietà

### Backend
- Estendere `WorkflowService` con metodo `validate_workflow()`
- Aggiungere endpoint `/api/workflows/validate`
- Streaming SSE per esecuzione passo-passo

### Database
- La struttura attuale è sufficiente
- Considerare `workflow_versions` per versionamento
- Index su `trigger_event` per performance

## Prossimi Passi

1. Estendere i tipi di step (sub_workflow, HTTP request)
2. Aggiungere variabili di contesto (`{{user.name}}`, `{{date.today}}`)
3. Implementare workflow asincroni con coda (Celery)
4. ✅ Aggiungere drag&drop con React Flow [IMPLEMENTATO]
5. Versionamento dei workflow

### Implementazione Completata

Il Workflow Builder visivo è stato implementato con:

- **Frontend**: React Flow + Zustand per stato
- **Nodi personalizzati**: Trigger, Condition, Action, Notification, Delay, Webhook
- **Properties Panel**: Form dinamici per configurare ogni nodo
- **Integrazione Backend**: Save/Load workflow via API

**File creati**:
- `frontend/src/stores/workflowBuilderStore.js`
- `frontend/src/components/workflow/WorkflowNodes.jsx`
- `frontend/src/components/workflow/WorkflowPropertiesPanel.jsx`
- `frontend/src/pages/WorkflowBuilder.jsx`

**Accesso**: `/projects/:projectId/workflow-builder`

