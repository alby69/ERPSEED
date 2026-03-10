# Automazione

## Panoramica

L'automazione in FlaskERP è ciò che lega i Block e i Module in un sistema funzionale. Permette ai componenti di comunicare e reagire agli eventi automaticamente.

I tre meccanismi sono:

| Meccanismo | Esecuzione | Configurazione | Uso |
|------------|------------|----------------|-----|
| **Hook** | Sincrona (stessa transazione) | Codice | Validazioni, calcoli |
| **Event Bus** | Asincrona (dopo commit) | Codice | Comunicazione tra moduli |
| **Workflow** | Orchestrazione | UI + Codice | Automazione dichiarativa |

---

## 1. Hook (Ganci)

### Cosa sono

Funzioni Python eseguite automaticamente in momenti specifici del ciclo di vita di un'entità.

### Tipi di Hook

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

### Esempio: Calcolo Totale Fattura

```python
@hook("invoice_line.after_create", priority=10)
@hook("invoice_line.after_update", priority=10)
def recalculate_invoice_total(invoice_line):
    """Ricalcola totale fattura quando una riga cambia."""
    invoice = invoice_line.invoice
    invoice.total = sum(line.amount for line in invoice.lines)
    invoice.tax = invoice.total * invoice.tax_rate / 100
    invoice.grand_total = invoice.total + invoice.tax
    db.session.commit()
```

**Flusso**:
1. Utente salva riga fattura
2. Hook eseguito **nella stessa transazione**
3. Totale ricalcolato
4. Se fallisce, tutto revertito (rollback)

### Esempio: Validazione Stock

```python
@hook("order.before_create", priority=5)
def check_inventory(order):
    """Verifica disponibilità prima di creare ordine."""
    for item in order.items:
        if item.product.stock < item.quantity:
            raise ValidationError(
                f"Stock insufficiente per {item.product.name}"
            )
```

---

## 2. Event Bus

### Cosa è

Sistema di messaggistica asincrona per comunicazione tra moduli senza accoppiamento.

### Caratteristiche

- **Decoupling**: moduli non si conoscono
- **Asincrono**: esecuzione dopo commit
- **Storico**: eventi salvati in history

### Esempio: Notifica Amministratore

```python
# Pubblicazione (in un controller)
EventBus.publish("order.created", {
    "order_id": 123,
    "customer": "Mario Rossi",
    "total": 1500.00
})

# Sottoscrizione (in un altro modulo)
def send_admin_notification(data):
    admin_email = get_settings().admin_email
    send_email(
        to=admin_email,
        subject=f"Nuovo ordine #{data['order_id']}"
    )

EventBus.subscribe("order.created", send_admin_notification)
```

### Esempio: Sincronizzazione Magazzino ↔ Contabilità

```python
# Modulo Prodotti - pubblica evento
EventBus.publish("product.updated", {
    "product_id": 456,
    "name": "Widget Pro",
    "stock": 100,
    "cost": 25.00
})

# Modulo Contabilità - reagisce
def sync_accounting_inventory(data):
    """Aggiorna libri contabili."""
    entry = AccountingEntry(
        type="inventory_adjustment",
        reference_id=data["product_id"],
        amount=data["cost"] * data["stock"],
        description=f"Stock: {data['name']}"
    )
    db.session.add(entry)
    db.session.commit()

EventBus.subscribe("product.updated", sync_accounting_inventory)
```

---

## 3. Workflow

### Cosa sono

Sequenze dichiarative di azioni condizionali, configurabili via UI dall'amministratore.

### Componenti

```
Trigger      → Evento che avvia il workflow
Condition    → Condizione (se/altrimenti)
Action       → Azione (imposta campo, crea record)
Notification → Notifica (email, webhook)
Delay        → Attesa prima del prossimo step
```

### Esempio: Approvazione Ordine B2B

**Configurazione UI**:
```
Trigger: order.created
├── SE totale > 10000
│   ├── Notifica manager (email)
│   └── Imposta stato = "pending_approval"
└── ALTRIMENTI
    ├── Approva automaticamente (stato = "approved")
    └── Invia conferma cliente (email)
```

**JSON salvato**:
```json
{
  "name": "Approvazione ordine B2B",
  "trigger_event": "order.created",
  "steps": [
    {
      "type": "condition",
      "config": {"field": "total", "operator": ">", "value": "10000"},
      "on_true": [
        {"type": "notification", "config": {"to": "manager@aziendale.it"}},
        {"type": "action", "config": {"field": "status", "value": "pending_approval"}}
      ],
      "on_false": [
        {"type": "action", "config": {"field": "status", "value": "approved"}},
        {"type": "notification", "config": {"template": "order_confirmation"}}
      ]
    }
  ]
}
```

### Esempio: Onboarding Dipendente

```
Trigger: employee.created
├── Crea account utente (email = employee.email)
├── Assegna ruolo base (ruolo = "user")
├── SE ruolo == "dipendente"
│   ├── Crea pratica INPS
│   ├── Registra in libro paga
│   └── Invia benvenuto HR
└── SE ruolo == "consulente"
    ├── Crea contratto
    └── Notifica amministrazione
```

---

## Relazione tra i Tre Meccanismi

```
┌─────────────────────────────────────────────────────────────────┐
│                         UTENTE SALVA                             │
│                    (es. Ordine, Fattura)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                       ENTITÀ (Model/CRUD)                        │
│                  - Valida i dati                                 │
│                  - Salva nel DB                                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                   │
          ▼                  ▼                   ▼
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
    │ Validazione│     │ Logica    │ │  Hook   │ │Workflow  │
    │ core       │     │ cross-    │ │ (altro  │ │(elabor.  │
    │(es.stock)  │     │ modulo    │ │ modulo) │ │ asincr.) │
    └───────────┘      └───────────┘ └─────────┘ └──────────┘
```

### Differenze Chiave

| Aspetto | Hook | Event Bus | Workflow |
|---------|------|-----------|----------|
| Transazione | Sincrona | Asincrona | Asincrona |
| Configurazione | Codice | Codice | UI + Codice |
| Complessità | Semplice | Media | Alta |
| Ordine | Per priorità | Indeterminato | Sequenziale |
| Rollback | Sì | No | Parziale |

---

## Best Practice

### Quando usare Hook

- Validazioni critiche (deve bloccare se errore)
- Calcoli automatici (atomici)
- Logica core (non modificabile)

### Quando usare Event Bus

- Comunicazione tra moduli
- Sincronizzazioni (possono fallire)
- Notifiche post-commit

### Quando usare Workflow

- Automazioni configurabili dall'utente
- Processi multi-step
- Approvazioni e flussi

---

## Workflow Builder Visivo

FlaskERP include un builder visivo per creare workflow senza codice.

### Accesso

`/projects/:projectId/workflow-builder`

### Componenti UI

- **Canvas**: Area di drag&drop
- **Toolbox**: Tipi di step disponibili
- **Properties Panel**: Configurazione nodo

### Tipi di Step

| Step | Configurazione |
|------|----------------|
| **condition** | field, operator, value |
| **action** | action_type, field, value |
| **notification** | type, to, subject, template |
| **delay** | duration, unit |
| **webhook** | url, method, headers, body |

---

## Trigger Disponibili

| Evento | Descrizione |
|--------|-------------|
| `entity.created` | Qualsiasi entità creata |
| `entity.updated` | Qualsiasi entità aggiornata |
| `entity.deleted` | Qualsiasi entità cancellata |
| `order.created` | Ordine creato |
| `order.updated` | Ordine aggiornato |
| `invoice.created` | Fattura creata |
| `user.created` | Utente creato |

---

## Implementazione

L'EventBus è implementato in `backend/shared/events/event_bus.py`:

```python
from backend.shared.events import get_event_bus, DomainEvent

event_bus = get_event_bus()

# Pubblicazione
event_bus.publish(DomainEvent(
    event_type="order.created",
    payload={"order_id": 123, "total": 1500.00}
))

# Sottoscrizione
def handle_order_created(event):
    print(f"Ordine creato: {event.payload}")

event_bus.subscribe("order.created", handle_order_created)
```

Vedi anche [12_ROADMAP.md](12_ROADMAP.md) per dettagli sul refactoring.

---

*Documento aggiornato: Marzo 2026*
